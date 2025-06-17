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
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    ApiException
)
from supabase import create_client, Client

# --- 初期設定 ---
app = Flask(__name__)
line_config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
line_handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# (PLANT_DATABASEとヘルパー関数は変更なし)
PLANT_DATABASE = {
    'ミニトマト': { 'base_temp': 10.0, 'image_url': 'https://www.ja-town.com/shop/g/g3501-0000021-001/img/g3501-0000021-001_2.jpg', 'events': [ {'gdd': 300, 'advice': '最初の追肥のタイミングです！'}, {'gdd': 900, 'advice': '収穫の時期が近づいています！'} ]},
    'きゅうり': { 'base_temp': 12.0, 'image_url': 'https://www.shuminoengei.jp/images/concierge/qa_plant_image/296_001.jpg', 'events': [ {'gdd': 250, 'advice': '最初の追肥のタイミングです。'}, {'gdd': 500, 'advice': '収穫が始まりました！'} ]}
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
    user_id = event.source.user_id
    user_message = event.message.text
    reply_message_obj = None

    if 'の状態' in user_message:
        plant_name_to_check = user_message.replace('の状態', '').strip()
        plant_response = supabase.table('user_plants').select('*').eq('user_id', user_id).eq('plant_name', plant_name_to_check).order('id', desc=True).limit(1).execute()
        
        if plant_response.data:
            found_plant = plant_response.data[0]
            plant_name = found_plant['plant_name']
            plant_info_from_db = PLANT_DATABASE.get(plant_name)
            
            if plant_info_from_db:
                # 1. 設計図（JSON）を文字列として読み込む
                with open('flex_message_templates/plant_status_card.json', 'r', encoding='utf-8') as f:
                    flex_template_str = f.read()

                # 2. 必要なデータを計算
                start_date = datetime.datetime.strptime(found_plant['start_date'], '%Y-%m-%d').date()
                today = datetime.date.today()
                days_passed = (today - start_date).days + 1
                weather_data = get_weather_data(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
                gdd = calculate_gdd(weather_data, plant_info_from_db['base_temp']) if weather_data else 0
                
                next_event_advice = "全てのイベントが完了しました！"
                for ev in plant_info_from_db.get('events', []):
                    if gdd < ev['gdd']:
                        next_event_advice = f"次のイベントは「{ev['advice']}」(目安: {ev['gdd']}℃・日)"
                        break

                # 3. 文字列置換で、プレースホルダーを実際のデータに書き換える
                flex_template_str = flex_template_str.replace('__IMAGE_URL__', plant_info_from_db.get('image_url', ''))
                flex_template_str = flex_template_str.replace('__PLANT_NAME__', plant_name)
                flex_template_str = flex_template_str.replace('__DAYS_PASSED__', str(days_passed))
                flex_template_str = flex_template_str.replace('__GDD__', f"{gdd:.1f}")
                flex_template_str = flex_template_str.replace('__NEXT_EVENT_ADVICE__', next_event_advice)
                flex_template_str = flex_template_str.replace('__PLANT_ID__', str(found_plant['id']))
                
                # 4. 完成した文字列を、JSON（辞書）に変換する
                flex_contents = json.loads(flex_template_str)

                # 5. FlexMessageオブジェクトを作成
                reply_message_obj = FlexMessage(alt_text=f"{plant_name}の状態", contents=flex_contents)
        else:
            reply_message_obj = TextMessage(text=f"「{plant_name_to_check}」は登録されていません。")
    # (他のelifやelseのロジックは省略。お前のコードのままでOK)
    else:
        # ...
        pass

    if reply_message_obj:
        with ApiClient(line_config) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

# (Postbackイベントの処理関数は省略)
@line_handler.add(PostbackEvent)
def handle_postback(event):
    # ...
    pass

if __name__ == "__main__":
    app.run(port=5001)