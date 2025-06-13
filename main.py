import requests
import json
import datetime
import os
from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

# LINEの秘密の鍵
configuration = Configuration(access_token='7dQLyzXDVBh93eYIthjFLTNySlMBoL6rDts6RgChWxg1rmVT6XlniNcZqx3R7rukiAIgIE3Ki9CWwA+wWl8vciXlI8Wrb9aenRVRDV2UWK/HNJU9MJWR+y+/FvEhxe+VNeNLJ3pmqqIGquco2qLmkwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('bd7f776cf56097724ce3c10ed2b3d5f2')

# ユーザーの状態を記憶する簡易データベース
user_states = {}

# --- ここからが新しい神の視点（関数） ---
def get_weather_data(start_date, end_date):
    """ 指定された期間の最高・最低気温データを取得する関数 """
    # 東京（世田谷）の緯度経度
    latitude = 35.66
    longitude = 139.65
    
    # APIからデータを取得
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min&start_date={start_date}&end_date={end_date}&timezone=Asia%2FTokyo"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
        return None

def calculate_gdd(weather_data):
    """ 天気データから積算温度を計算する関数 """
    if not weather_data or 'daily' not in weather_data:
        return 0

    max_temps = weather_data['daily']['temperature_2m_max']
    min_temps = weather_data['daily']['temperature_2m_min']
    
    gdd = 0
    # 生物学的下限温度（ミニトマトの場合）
    base_temp = 10.0

    for max_t, min_t in zip(max_temps, min_temps):
        if max_t is not None and min_t is not None:
            avg_temp = (max_t + min_t) / 2
            if avg_temp > base_temp:
                gdd += (avg_temp - base_temp)
    
    return gdd
# --- ここまでが新しい神の視点（関数） ---


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id
    reply_text = ""

    if user_message == "ミニトマト":
        start_date = datetime.date.today()
        user_states[user_id] = {
            'plant': 'ミニトマト',
            'start_date': start_date
        }
        reply_text = f"ミニトマトを登録しました！\n栽培開始日: {start_date.strftime('%Y年%m月%d日')}\n\n現在の状況を知りたい時は「状態」と送ってください。"
        print(f"【登録完了】 User: {user_id}, Data: {user_states[user_id]}")

    elif user_message == "状態":
        if user_id in user_states:
            state = user_states[user_id]
            plant_name = state['plant']
            start_date = state['start_date']
            today = datetime.date.today()
            
            # 栽培日数の計算
            days_passed = (today - start_date).days + 1

            # 天気データを取得
            weather_data = get_weather_data(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
            
            if weather_data:
                # 積算温度を計算
                gdd = calculate_gdd(weather_data)
                reply_text = f"【{plant_name}の栽培状況】\n栽培{days_passed}日目です。\n現在の積算温度は、約{gdd:.1f}℃・日です！"
            else:
                reply_text = "申し訳ありません、気象データを取得できませんでした。"
        else:
            reply_text = "まだ植物が登録されていません。「ミニトマト」と入力して栽培を開始してください。"
            
    else:
        reply_text = "「ミニトマト」で栽培開始、「状態」で状況を確認できます。"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    app.run(port=5001)