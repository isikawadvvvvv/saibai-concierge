from dotenv import load_dotenv
load_dotenv()

import os
import datetime
import requests
import json
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent # Postbackを処理するための新しい武器
)
from supabase import create_client, Client

# --- 初期設定 ---
app = Flask(__name__)
line_config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
line_handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# 植物の成長データを格納するデータベース
PLANT_DATABASE = {
    'ミニトマト': {
        'base_temp': 10.0,
        'image_url': 'https://www.ja-town.com/shop/g/g3501-0000021-001/img/g3501-0000021-001_2.jpg',
        'events': [
            {'gdd': 300, 'advice': '最初の追肥のタイミングです！', 'product_name': 'トマトの追肥用肥料', 'affiliate_link': '【お前が取得したアフィリエイトリンク】'},
            {'gdd': 900, 'advice': '収穫の時期が近づいています！'}
        ]
    },
    'きゅうり': {
        'base_temp': 12.0,
        'image_url': 'https://www.shuminoengei.jp/images/concierge/qa_plant_image/296_001.jpg',
        'events': [
            {'gdd': 250, 'advice': '最初の追肥のタイミングです。'},
            {'gdd': 500, 'advice': '収穫が始まりました！'}
        ]
    }
}

# --- ヘルパー関数 ---
def get_weather_data(start_date, end_date):
    url = f"https://api.open-meteo.com/v1/forecast?latitude=35.66&longitude=139.65&daily=temperature_2m_max,temperature_2m_min&start_date={start_date}&end_date={end_date}&timezone=Asia%2FTokyo"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"APIリクエストエラー: {e}")
        return None

def calculate_gdd(weather_data, base_temp=10.0):
    if not weather_data or 'daily' not in weather_data: return 0
    gdd = 0
    for max_t, min_t in zip(weather_data['daily']['temperature_2m_max'], weather_data['daily']['temperature_2m_min']):
        if max_t is not None and min_t is not None:
            avg_temp = (max_t + min_t) / 2
            if avg_temp > base_temp: gdd += (avg_temp - base_temp)
    return gdd

# --- LINE Botのメインロジック ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    reply_message_obj = None

    # ユーザーがDBに存在するか確認、存在しなければ新規登録してチュートリアルを返す
    user_response = supabase.table('users').select('id').eq('id', user_id).execute()
    if not user_response.data:
        supabase.table('users').insert({'id': user_id}).execute()
        reply_message_obj = TextMessage(text="""はじめまして！
僕は、あなたの植物栽培を科学的にサポートする「栽培コンシェルジュ」です。
まずは、育てたい作物の名前の後に「を追加」と付けて送ってください。
（例：ミニトマトを追加）""")
    elif 'を追加' in user_message:
        plant_name = user_message.replace('を追加', '').strip()
        if plant_name:
            new_plant = {'user_id': user_id, 'plant_name': plant_name, 'start_date': str(datetime.date.today())}
            supabase.table('user_plants').insert(new_plant).execute()
            reply_message_obj = TextMessage(text=f"「{plant_name}」を新しい作物として登録しました！")
        else:
            reply_message_obj = TextMessage(text="作物名を指定してください。（例：ミニトマトを追加）")
     # 「〇〇の状態」というメッセージを検知
    elif 'の状態' in user_message:
        plant_name_to_check = user_message.replace('の状態', '').strip()
        
        plant_response = supabase.table('user_plants').select('*').eq('user_id', user_id).eq('plant_name', plant_name_to_check).order('id', desc=True).limit(1).execute()
        
        if plant_response.data:
            found_plant = plant_response.data[0]
            plant_name = found_plant['plant_name']
            
            # 1. 設計図（JSONファイル）を読み込む
            with open('flex_message_templates/plant_status_card.json', 'r', encoding='utf-8') as f:
                flex_template = json.load(f)

            # 2. 設計図をユーザーのデータで書き換える
            plant_info_from_db = PLANT_DATABASE.get(plant_name)
            if plant_info_from_db:
                flex_template['hero']['url'] = plant_info_from_db.get('image_url', 'https://example.com/placeholder.jpg')
                flex_template['body']['contents'][0]['text'] = f"{plant_name}の栽培状況"
                
                start_date = datetime.datetime.strptime(found_plant['start_date'], '%Y-%m-%d').date()
                today = datetime.date.today()
                days_passed = (today - start_date).days + 1
                flex_template['body']['contents'][1]['contents'][0]['contents'][1]['text'] = f"{days_passed}日目"

                weather_data = get_weather_data(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
                if weather_data:
                    base_temp = plant_info_from_db['base_temp']
                    gdd = calculate_gdd(weather_data, base_temp)
                    flex_template['body']['contents'][1]['contents'][1]['contents'][1]['text'] = f"{gdd:.1f}℃・日"
                    
                    next_event_advice = "全てのイベントが完了しました！"
                    for ev in plant_info_from_db.get('events', []):
                        if gdd < ev['gdd']:
                            next_event_advice = f"次のイベントは「{ev['advice']}」(目安: {ev['gdd']}℃・日)"
                            if 'product_name' in ev and 'affiliate_link' in ev:
                                next_event_advice += f"\n\n💡ヒント：\nこのタイミングには「{ev['product_name']}」がおすすめです。\n詳細はこちら：\n{ev['affiliate_link']}"
                            break
                    flex_template['body']['contents'][2]['contents'][1]['text'] = next_event_advice
                
                for button in flex_template['footer']['contents']:
                    if button.get('action', {}).get('type') == 'postback':
                        button['action']['data'] = button['action']['data'].replace('__PLANT_ID__', str(found_plant['id']))
                
                # --- ▼▼▼ ここが最後の修正ポイント ▼▼▼ ---
                # 3. 辞書データを、LINEライブラリが理解できる「FlexContainer」オブジェクトに変換する
                flex_container_obj = FlexContainer.new_from_json_dict(flex_template)

                # 4. FlexSendMessageオブジェクトを作成する。contentsには、変換したオブジェクトを入れる
                reply_message_obj = FlexSendMessage(
                    alt_text=f"{plant_name}の状態をお知らせします",
                    contents=flex_container_obj # ここが flex_template から変わっている！
                )
                # --- ▲▲▲ ここまでが最後の修正ポイント ▲▲▲ ---
                reply_message_obj = FlexMessage(alt_text=f"{plant_name}の状態", contents=flex_template)
            else:
                reply_message_obj = TextMessage(text=f"「{plant_name}」の栽培データがありません。")
        else:
            reply_message_obj = TextMessage(text=f"「{plant_name_to_check}」は登録されていません。")
    else:
        reply_message_obj = TextMessage(text="「〇〇を追加」で登録、「〇〇の状態」で確認できます。")

    if reply_message_obj:
        with ApiClient(line_config) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

# --- 新しい神経回路：Postbackイベントの処理 ---
@line_handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    postback_data_str = event.postback.data

    # 'action=log_watering&plant_id=1' のようなデータを解析
    params = dict(p.split('=') for p in postback_data_str.split('&'))
    action_type = params.get('action')
    plant_id = params.get('plant_id')

    reply_text = "エラーが発生しました。"
    if action_type and plant_id:
        action_log = {'user_plant_id': int(plant_id), 'action_type': action_type}
        supabase.table('plant_actions').insert(action_log).execute()
        print(f"【行動記録】 User: {user_id}, Action: {action_log}")
        reply_text = f"{action_type}を記録しました！"

    with ApiClient(line_config) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply_text)]))

# --- サーバー起動 ---
if __name__ == "__main__":
    app.run(port=5001)