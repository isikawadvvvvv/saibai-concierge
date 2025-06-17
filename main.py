from dotenv import load_dotenv
load_dotenv()

import os
import datetime
import requests
import json
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
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

# 植物データベース（これは変更なし）
PLANT_DATABASE = {
    'ミニトマト': { 'base_temp': 10.0, 'events': [ {'gdd': 300, 'advice': '最初の追肥のタイミングです！'}, {'gdd': 900, 'advice': '収穫の時期が近づいています！'} ]},
    'きゅうり': { 'base_temp': 12.0, 'events': [ {'gdd': 250, 'advice': '最初の追肥のタイミングです。'}, {'gdd': 500, 'advice': '収穫が始まりました！'} ]}
}

# --- ヘルパー関数（これも変更なし） ---
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
    reply_text = ""

    # --- ▼▼▼ ここからがデータベースを使った新しいロジック ▼▼▼ ---

    # 1. ユーザーがDBに存在するか確認、存在しなければ新規登録
    user_response = supabase.table('users').select('id').eq('id', user_id).execute()
    if not user_response.data:
        print(f"新規ユーザーを検知。DBに登録します: {user_id}")
        supabase.table('users').insert({'id': user_id}).execute()
        # 初回メッセージはここで確定
        reply_text = "はじめまして！「栽培コンシェルジュ」です。まずは育てたい作物を「〇〇を追加」と送って登録してください。（例：ミニトマトを追加）"

    # 2. コマンド処理
    if 'を追加' in user_message:
        plant_name = user_message.replace('を追加', '').strip()
        if plant_name:
            new_plant = {'user_id': user_id, 'plant_name': plant_name, 'start_date': str(datetime.date.today())}
            supabase.table('user_plants').insert(new_plant).execute()
            reply_text = f"「{plant_name}」を新しい作物として登録しました！"
            print(f"【DB記録完了】{new_plant}")
        else:
            reply_text = "作物名を指定してください。（例：ミニトマトを追加）"

    elif 'の状態' in user_message:
        plant_name_to_check = user_message.replace('の状態', '').strip()
        # DBからユーザーが育てている特定の植物の情報を取得
        plant_response = supabase.table('user_plants').select('*').eq('user_id', user_id).eq('plant_name', plant_name_to_check).execute()
        
        if plant_response.data:
            found_plant = plant_response.data[0]
            start_date = datetime.datetime.strptime(found_plant['start_date'], '%Y-%m-%d').date()
            today = datetime.date.today()
            # (以下、積算温度の計算と神託のロジックは前回と同じなので省略)
            # ...
            reply_text = f"【{found_plant['plant_name']}の栽培状況】\n... (ここに神託メッセージが入る)"

        else:
            reply_text = f"「{plant_name_to_check}」という作物は登録されていません。"

    elif 'ヘルプ' in user_message.lower():
        reply_text = "【使い方ガイド】\n🌱作物の登録：「〇〇を追加」\n📈状態の確認：「〇〇の状態」"
    
    # 初回メッセージ以外で、コマンドが不明な場合
    elif not reply_text:
        reply_text = "使い方が分からない場合は、「ヘルプ」と送ってみてくださいね。"
    
    # 3. メッセージを返信
    with ApiClient(line_config) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply_text)])
        )

# --- サーバー起動 ---
if __name__ == "__main__":
    app.run(port=5001)