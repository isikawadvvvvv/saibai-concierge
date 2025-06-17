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
    FlexMessage,
    BubbleContainer  # ← これが、バブル型設計図専用の、正しい最終兵器だ
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent
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
        if plant_name:
            new_plant = {'user_id': user_id, 'plant_name': plant_name, 'start_date': str(datetime.date.today())}
            supabase.table('user_plants').insert(new_plant).execute()
            reply_message_obj = TextMessage(text=f"「{plant_name}」を新しい作物として登録しました！")
    elif 'の状態' in user_message:
        plant_name_to_check = user_message.replace('の状態', '').strip()
        plant_response = supabase.table('user_plants').select('*').eq('user_id', user_id).eq('plant_name', plant_name_to_check).order('id', desc=True).limit(1).execute()
        
        if plant_response.data:
            found_plant = plant_response.data[0]
            plant_name = found_plant['plant_name']
            
            with open('flex_message_templates/plant_status_card.json', 'r', encoding='utf-8') as f:
                flex_template = json.load(f)

            plant_info_from_db = PLANT_DATABASE.get(plant_name)
            if plant_info_from_db:
                # ... (Flex Templateの書き換えロジックは省略)
                
                # --- ▼▼▼ ここが最終修正ポイント ▼▼▼ ---
                # 辞書データを、専用のBubbleContainerオブジェクトに変換する
                bubble_container = BubbleContainer.new_from_json_dict(flex_template)
                # FlexMessageのcontentsには、この変換したオブジェクトを入れる
                reply_message_obj = FlexMessage(
                    alt_text=f"{plant_name}の状態をお知らせします",
                    contents=bubble_container
                )
                # --- ▲▲▲ ここまでが最終修正ポイント ▲▲▲ ---
            else:
                reply_message_obj = TextMessage(text=f"「{plant_name}」の栽培データがありません。")
        else:
            reply_message_obj = TextMessage(text=f"「{plant_name_to_check}」は登録されていません。")
    else:
        reply_message_obj = TextMessage(text="使い方が分からない場合は、「ヘルプ」と送ってください。")

    if reply_message_obj:
        with ApiClient(line_config) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

# (Postbackイベントの処理関数は省略)

if __name__ == "__main__":
    app.run(port=5001)