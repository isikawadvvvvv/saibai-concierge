from dotenv import load_dotenv
load_dotenv()

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
configuration = Configuration(access_token=os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

# ユーザーの状態を記憶する簡易データベース
user_states = {}

# --- ▼▼▼ ここからが新しい知識 ▼▼▼ ---
# 植物の成長データを格納するデータベース
PLANT_DATABASE = {
    'ミニトマト': {
        'base_temp': 10.0,  # 生物学的下限温度
        'events': [
            {'gdd': 300, 'advice': '最初の追肥のタイミングです！'},
            {'gdd': 600, 'advice': '実が大きくなる時期です。2回目の追肥を行いましょう。'},
            {'gdd': 900, 'advice': '収穫の時期が近づいています！最初の実が赤くなり始めたら収穫開始です。'}
        ]
    },
    'きゅうり': {
        'base_temp': 12.0,
        'events': [
            {'gdd': 250, 'advice': '植え付けから約1ヶ月、最初の追肥のタイミングです。'},
            {'gdd': 500, 'advice': '収穫が始まりました！ここからは2週間に1回のペースで追肥を続けましょう。'}
        ]
    }
    # ここに、他の作物のデータを追加していく
}
# --- ▲▲▲ ここまでが新しい知識 ▲▲▲ ---

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

def calculate_gdd(weather_data, base_temp=10.0): # base_tempを引数として受け取る
    """ 天気データから積算温度を計算する関数 """
    if not weather_data or 'daily' not in weather_data:
        return 0

    max_temps = weather_data['daily']['temperature_2m_max']
    min_temps = weather_data['daily']['temperature_2m_min']
    
    gdd = 0
    
    for max_t, min_t in zip(max_temps, min_temps):
        if max_t is not None and min_t is not None:
            avg_temp = (max_t + min_t) / 2
            if avg_temp > base_temp:
                gdd += (avg_temp - base_temp)
    
    return gdd


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

     # ステップ1：まず、ユーザーが初めてか確認し、必要なら空のデータを作る
    # これで、ユーザーは「顧客名簿」に登録される
    if user_id not in user_states:
        user_states[user_id] = {'plants': []}

    # ステップ2：次に、顧客の「注文（コマンド）」を聞く
    # これで、新規ユーザーの最初のメッセージも、コマンドとして正しく処理される
    if 'を追加' in user_message:
        print("「追加」コマンドを検知。")
        plant_name = user_message.replace('を追加', '').strip()
        new_plant = {'id': len(user_states[user_id]['plants']) + 1, 'name': plant_name, 'start_date': datetime.date.today()}
        user_states[user_id]['plants'].append(new_plant)
        reply_text = f"「{plant_name}」を新しい作物として登録しました！"
        print(f"【作物追加】 User: {user_id}, New Data: {user_states[user_id]}")

    elif 'の状態' in user_message:
        print("「状態」コマンドを検知。")
        # (このブロックの中身は、お前のコードのままで完璧なので省略)
        plant_name_to_check = user_message.replace('の状態', '').strip()
        found_plant = None
        for p in user_states[user_id]['plants']:
            if p['name'] == plant_name_to_check:
                found_plant = p
                break
        if found_plant:
            plant_name = found_plant['name']
            start_date = found_plant['start_date']
            today = datetime.date.today()
            if plant_name in PLANT_DATABASE:
                plant_data = PLANT_DATABASE[plant_name]
                base_temp = plant_data['base_temp']
                weather_data = get_weather_data(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
                if weather_data:
                    gdd = calculate_gdd(weather_data, base_temp)
                    next_event_advice = "全てのイベントが完了しました！"
                    for ev in plant_data['events']:
                        if gdd < ev['gdd']:
                            next_event_advice = f"次のイベントは「{ev['advice']}」(積算温度: {ev['gdd']}℃・日)です。"
                            break
                    reply_text = f"【{plant_name}の栽培状況】\n栽培{(today - start_date).days + 1}日目\n現在の積算温度：約{gdd:.1f}℃・日\n\n{next_event_advice}"
                else:
                    reply_text = "申し訳ありません、気象データを取得できませんでした。"
            else:
                reply_text = f"申し訳ありません、「{plant_name}」の栽培データがまだありません。"
        else:
            reply_text = f"「{plant_name_to_check}」という作物は登録されていません。"

    elif 'ヘルプ' in user_message.lower():
        print("ヘルプコマンドを検知。")
        reply_text = """【使い方ガイド】
🌱作物の登録：「〇〇を追加」
（例：ミニトマトを追加）

📈状態の確認：「〇〇の状態」
（例：ミニトマトの状態）"""

    # どのコマンドにも一致しなかった場合
    else:
        # 新規ユーザーの最初のメッセージがコマンドでない場合、ここでチュートリアルを返す
        if len(user_states[user_id]['plants']) == 0:
             reply_text = """はじめまして！
僕は、あなたの植物栽培を科学的にサポートする「栽培コンシェルジュ」です。

まずは、育てたい作物の名前の後に「を追加」と付けて送ってください。
（例：ミニトマトを追加）"""
        else:
            reply_text = "使い方が分からない場合は、「ヘルプ」と送ってみてくださいね。"


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