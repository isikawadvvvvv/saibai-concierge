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
    FlexMessage # FlexMessageを送信するために、これを追加
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from supabase import create_client, Client

# --- 初期設定 ---
app = Flask(__name__)

# LINE Botの設定
line_config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
line_handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

# Supabaseデータベースの設定
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# 植物の成長データを格納するデータベース
PLANT_DATABASE = {
    'ミニトマト': {
        'base_temp': 10.0,
        'image_url': 'https://www.ja-town.com/shop/g/g3501-0000021-001/img/g3501-0000021-001_2.jpg', # 画像URLを追加
        'events': [
            {'gdd': 300, 'advice': '最初の追肥のタイミングです！', 'product_name': 'トマトの追肥用肥料', 'affiliate_link': '【ここにAmazonで取得した商品リンクを入れる】'},
            {'gdd': 900, 'advice': '収穫の時期が近づいています！'}
        ]
    },
    'きゅうり': {
        'base_temp': 12.0,
        'image_url': 'https://www.shuminoengei.jp/images/concierge/qa_plant_image/296_001.jpg', # 画像URLを追加
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
    
    # 返信用のメッセージオブジェクトを準備（最初は空）
    reply_message = None

    # ユーザーがDBに存在するか確認、存在しなければ新規登録してチュートリアルを返す
    user_response = supabase.table('users').select('id').eq('id', user_id).execute()
    if not user_response.data:
        supabase.table('users').insert({'id': user_id}).execute()
        reply_message = TextMessage(text="""はじめまして！
僕は、あなたの植物栽培を科学的にサポートする「栽培コンシェルジュ」です。

まずは、育てたい作物の名前の後に「を追加」と付けて送ってください。
（例：ミニトマトを追加）""")

    # --- コマンド処理 ---
    elif 'を追加' in user_message:
        plant_name = user_message.replace('を追加', '').strip()
        if plant_name:
            new_plant = {'user_id': user_id, 'plant_name': plant_name, 'start_date': str(datetime.date.today())}
            supabase.table('user_plants').insert(new_plant).execute()
            reply_message = TextMessage(text=f"「{plant_name}」を新しい作物として登録しました！")
        else:
            reply_message = TextMessage(text="作物名を指定してください。（例：ミニトマトを追加）")

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
                # 画像をセット
                flex_template['hero']['url'] = plant_info_from_db['image_url']
                # 植物名をセット
                flex_template['body']['contents'][0]['text'] = f"{plant_name}の栽培状況"
                
                # 栽培日数を計算してセット
                start_date = datetime.datetime.strptime(found_plant['start_date'], '%Y-%m-%d').date()
                today = datetime.date.today()
                days_passed = (today - start_date).days + 1
                flex_template['body']['contents'][1]['contents'][0]['contents'][1]['text'] = f"{days_passed}日目"

                # 積算温度を計算してセット
                weather_data = get_weather_data(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
                if weather_data:
                    base_temp = plant_info_from_db['base_temp']
                    gdd = calculate_gdd(weather_data, base_temp)
                    flex_template['body']['contents'][1]['contents'][1]['contents'][1]['text'] = f"{gdd:.1f}℃・日"
                
                # 3. FlexMessageオブジェクトを作成
                reply_message = FlexMessage(alt_text=f"{plant_name}の状態をお知らせします", contents=flex_template)

            else: # PLANT_DATABASEに情報がない場合
                reply_message = TextMessage(text=f"申し訳ありません、「{plant_name}」の栽培データがまだありません。")
        else:
            reply_message = TextMessage(text=f"「{plant_name_to_check}」という作物は登録されていません。")

    else: # どのコマンドにも一致しない場合
        reply_message = TextMessage(text="「〇〇を追加」で登録、「〇〇の状態」で確認できます。使い方が分からない場合は「ヘルプ」と送ってください。")

    # --- メッセージ送信 ---
    # reply_messageに何かしらメッセージがセットされていれば、それを送信する
    if reply_message:
        with ApiClient(line_config) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[reply_message]
                )
            )

if __name__ == "__main__":
    app.run(port=5001)