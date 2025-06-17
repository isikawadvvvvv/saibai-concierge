import sys
import traceback

print("="*30)
print("== ライブラリの内部調査を開始します ==")
print("="*30)

try:
    # 問題のモジュールの中身を直接確認する
    import linebot.v3.messaging
    print(">>> 'linebot.v3.messaging' のインポートには成功しました。")
    print(">>> モジュールの中身を一覧表示します:")
    # sorted()でアルファベット順に表示して見やすくする
    print(sorted(dir(linebot.v3.messaging)))
    print("---")
    
    # 本来のインポートを試みる
    from linebot.v3.messaging import BubbleContainer
    print(">>> 'BubbleContainer'のインポートに成功！")

except ImportError:
    print(">>> 'BubbleContainer' のインポートでエラーが発生しました。")
    print("--- エラー詳細 ---")
    # 詳細なエラー情報をログに出力する
    traceback.print_exc(file=sys.stdout)
    print("--------------------")

except Exception as e:
    print(f">>> 予期せぬエラーが発生しました: {e}")
    traceback.print_exc(file=sys.stdout)

finally:
    print("="*30)
    print("== ライブラリの内部調査を終了します ==")
    print("="*30)


from dotenv import load_dotenv
load_dotenv()

import os
import datetime
import requests
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    ApiException,
    # ↓↓↓ 名前が変更された FlexBubble をインポートします
    FlexBubble,
    # ↓↓↓ FlexMessageの各部品(コンポーネント)をインポートします
    BoxComponent,
    TextComponent,
    ImageComponent,
    ButtonComponent,
    SeparatorComponent,
    PostbackAction
)
from supabase import create_client, Client

# --- 初期設定 ---
app = Flask(__name__)
line_config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
line_handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# 植物データベース
PLANT_DATABASE = {
    'ミニトマト': {
        'base_temp': 10.0,
        'image_url': 'https://www.ja-town.com/shop/g/g3501-0000021-001/img/g3501-0000021-001_2.jpg',
        'events': [
            {'gdd': 300, 'advice': '最初の追肥のタイミングです！', 'product_name': 'トマトの追肥用肥料', 'affiliate_link': 'https://amzn.to/40aoawy'},
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

    user_response = supabase.table('users').select('id').eq('id', user_id).execute()
    if not user_response.data:
        supabase.table('users').insert({'id': user_id}).execute()
        reply_message_obj = TextMessage(text="""はじめまして！
僕は、あなたの植物栽培を科学的にサポートする「栽培コンシェルジュ」です。
まずは、育てたい作物の名前の後に「を追加」と付けて送ってください。
（例：ミニトマトを追加）""")
    elif 'を追加' in user_message:
        plant_name = user_message.replace('を追加', '').strip()
        if plant_name and plant_name in PLANT_DATABASE:
            new_plant = {'user_id': user_id, 'plant_name': plant_name, 'start_date': str(datetime.date.today())}
            supabase.table('user_plants').insert(new_plant).execute()
            reply_message_obj = TextMessage(text=f"「{plant_name}」を新しい作物として登録しました！")
        elif plant_name:
            reply_message_obj = TextMessage(text=f"申し訳ありません、「{plant_name}」の栽培データはまだありません。")
        else:
            reply_message_obj = TextMessage(text="作物名を指定してください。（例：ミニトマトを追加）")
            
    elif 'の状態' in user_message:
        plant_name_to_check = user_message.replace('の状態', '').strip()
        plant_response = supabase.table('user_plants').select('*').eq('user_id', user_id).eq('plant_name', plant_name_to_check).order('id', desc=True).limit(1).execute()
        
        if plant_response.data:
            found_plant = plant_response.data[0]
            plant_name = found_plant['plant_name']
            plant_info_from_db = PLANT_DATABASE.get(plant_name)
            
            if plant_info_from_db:
                start_date = datetime.datetime.strptime(found_plant['start_date'], '%Y-%m-%d').date()
                today = datetime.date.today()
                days_passed = (today - start_date).days + 1
                weather_data = get_weather_data(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
                gdd = calculate_gdd(weather_data, plant_info_from_db['base_temp']) if weather_data else 0
                
                next_event_advice = "全てのイベントが完了しました！収穫を楽しんでください。"
                recommendation_text = ""
                for ev in plant_info_from_db.get('events', []):
                    if gdd < ev['gdd']:
                        next_event_advice = f"次のイベントは「{ev['advice']}」(目安: {ev['gdd']}℃・日)"
                        if 'product_name' in ev and ev.get('affiliate_link'):
                            recommendation_text = f"\n\n💡ヒント：\n「{ev['product_name']}」がおすすめです。\n詳細はこちら：\n{ev['affiliate_link']}"
                        break

                # ↓↓↓ ここが修正箇所です！ BubbleContainer -> FlexBubble に変更
                bubble = FlexBubble(
                    hero=ImageComponent(url=plant_info_from_db.get('image_url', 'https://example.com/placeholder.jpg'), size='full', aspect_ratio='20:13', aspect_mode='cover'),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(text=f"{plant_name}の栽培状況", weight='bold', size='xl'),
                            BoxComponent(
                                layout='vertical', margin='lg', spacing='sm',
                                contents=[
                                    BoxComponent(layout='baseline', spacing='sm', contents=[
                                            TextComponent(text='栽培日数', color='#aaaaaa', size='sm', flex=2),
                                            TextComponent(text=f"{days_passed}日目", wrap=True, color='#666666', size='sm', flex=5) ]),
                                    BoxComponent(layout='baseline', spacing='sm', contents=[
                                            TextComponent(text='積算温度', color='#aaaaaa', size='sm', flex=2),
                                            TextComponent(text=f"{gdd:.1f}℃・日", wrap=True, color='#666666', size='sm', flex=5) ])]),
                            BoxComponent(layout='vertical', margin='lg', contents=[
                                    TextComponent(text='次のイベント', size='md', weight='bold'),
                                    TextComponent(text=next_event_advice, wrap=True, margin='md'),
                                    TextComponent(text=recommendation_text, wrap=True, margin='sm', size='sm') ])]),
                    footer=BoxComponent(
                        layout='vertical', spacing='sm',
                        contents=[
                            ButtonComponent(style='link', height='sm', action=PostbackAction(label="💧 水やりを記録する", data=f"action=log_watering&plant_id={found_plant['id']}")),
                            ButtonComponent(style='link', height='sm', action=PostbackAction(label="🌱 追肥を記録する", data=f"action=log_fertilizer&plant_id={found_plant['id']}"))
                        ]))
                reply_message_obj = FlexMessage(alt_text=f"{plant_name}の状態", contents=bubble)
        else:
            reply_message_obj = TextMessage(text=f"「{plant_name_to_check}」は登録されていません。")
            
    elif 'ヘルプ' in user_message.lower():
        reply_message_obj = TextMessage(text="""【使い方ガイド】
🌱作物の登録：「〇〇を追加」
（例：ミニトマトを追加）

📈状態の確認：「〇〇の状態」
（例：ミニトマトの状態）""")
    else:
        reply_message_obj = TextMessage(text="使い方が分からない場合は、「ヘルプ」と送ってみてくださいね。")

    if reply_message_obj:
        with ApiClient(line_config) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

@line_handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    postback_data_str = event.postback.data
    params = dict(p.split('=') for p in postback_data_str.split('&'))
    action_type = params.get('action')
    plant_id = params.get('plant_id')
    reply_text = "エラーが発生しました。"
    if action_type and plant_id:
        action_log = {'user_plant_id': int(plant_id), 'action_type': action_type}
        supabase.table('plant_actions').insert(action_log).execute()
        
        if action_type == 'log_watering':
            reply_text = '水やりを記録しました！'
        elif action_type == 'log_fertilizer':
            reply_text = '追肥を記録しました！'

    with ApiClient(line_config) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply_text)]))

if __name__ == "__main__":
    app.run(port=5001)