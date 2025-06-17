from dotenv import load_dotenv
load_dotenv()

import os
import datetime
import requests
import json
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent

# --- ▼▼▼ ここが最終的なインポート文 ▼▼▼ ---
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    # BubbleContainerは、ここではなく、専用の場所から持ってくる
)
# BubbleContainerは、'flex_message'という専用の保管庫から持ってくる！
from linebot.v3.flex_message import BubbleContainer
# --- ▲▲▲ ここまでが最終的なインポート文 ▲▲▲ ---

from supabase import create_client, Client

# --- 初期設定 ---
app = Flask(__name__)
line_config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
line_handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# (PLANT_DATABASEとヘルパー関数は変更ないため、コードを省略)
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
    # (この関数の他の部分は、お前のコードのままで完璧なので省略)
    # 修正するのは、`elif 'の状態' in user_message:`の中の、FlexMessageを作成する部分だけだ
    user_id = event.source.user_id
    user_message = event.message.text
    reply_message_obj = None

    user_response = supabase.table('users').select('id').eq('id', user_id).execute()
    if not user_response.data:
        # (省略)
        pass # ここは変更なし
    elif 'を追加' in user_message:
        # (省略)
        pass # ここは変更なし
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
                # (テンプレートのパーソナライズ部分は省略)
                # ...
                
                # --- ▼▼▼ これが、全ての元凶を断つ、最後の修正だ ▼▼▼ ---
                try:
                    # 辞書データ（flex_template）を、専用のBubbleContainerオブジェクトに変換する
                    bubble_container = BubbleContainer.from_dict(flex_template)

                    # FlexMessageのcontentsには、この完成した容器オブジェクトを渡す
                    reply_message_obj = FlexMessage(
                        alt_text=f"{plant_name}の状態をお知らせします",
                        contents=bubble_container
                    )
                except Exception as e:
                    print(f"Flex Message作成エラー: {e}")
                    reply_message_obj = TextMessage(text="メッセージの作成中にエラーが発生しました。")
                # --- ▲▲▲ ここまでが最後の修正だ ▲▲▲ ---
            else:
                reply_message_obj = TextMessage(text=f"「{plant_name}」の栽培データがありません。")
        else:
            reply_message_obj = TextMessage(text=f"「{plant_name_to_check}」は登録されていません。")
    else:
        # (省略)
        pass # ここは変更なし

    if reply_message_obj:
        with ApiClient(line_config) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

# (Postbackイベントの処理関数は省略)

if __name__ == "__main__":
    app.run(port=5001)