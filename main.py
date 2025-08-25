# main.py

import os
import datetime
import requests
from dotenv import load_dotenv
from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent, LocationMessageContent, FollowEvent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    PushMessageRequest,
    TextMessage, FlexMessage, ApiException,
    PostbackAction, MessageAction, QuickReply, QuickReplyItem,
    LocationAction, URIAction, FlexBubble, FlexBox, FlexText, FlexButton
)
from supabase import create_client, Client
from plant_data import PLANT_DATABASE
from flex_messages import (
    create_plant_list_carousel, create_date_selection_message,
    create_initial_products_message, create_status_flex_message,
    create_welcome_message
)

# --- 初期設定 ---
load_dotenv()
app = Flask(__name__)
line_config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# --- ヘルパー関数 ---
def get_weather_data(latitude, longitude, start_date, end_date):
    s_date = start_date.strftime('%Y-%m-%d')
    e_date = end_date.strftime('%Y-%m-%d')
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min&start_date={s_date}&end_date={e_date}&timezone=Asia%2FTokyo"
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

# --- プッシュ通知の心臓部 ---
def check_and_send_notifications():
    print(f"--- {datetime.datetime.now()}: Running daily notification check ---")
    with app.app_context():
        try:
            plants_to_check_res = supabase.table('user_plants').select('*, users(latitude, longitude)').execute()
            plants_to_check = plants_to_check_res.data
            
            if not plants_to_check:
                return

            for plant in plants_to_check:
                user_id, user_info, plant_name = plant.get('user_id'), plant.get('users'), plant.get('plant_name')
                plant_info_db = PLANT_DATABASE.get(plant_name)
                
                if not plant_info_db or not user_info:
                    continue

                # 水やりリマインダー
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                watering_res = supabase.table('plant_actions').select('id').eq('user_plant_id', plant['id']).eq('action_type', 'log_watering').gte('created_at', yesterday.isoformat()).execute()
                if not watering_res.data:
                    message_text = f"【水やりリマインダー💧】\n『{plant['plant_name']}』の水やりは記録しましたか？\n忘れずに記録しましょう！"
                    push_message = TextMessage(text=message_text, quick_reply=QuickReply(items=[QuickReplyItem(action=MessageAction(label="一覧", text="一覧"))]))
                    with ApiClient(line_config) as api_client:
                        MessagingApi(api_client).push_message(PushMessageRequest(to=user_id, messages=[push_message]))

                # GDDイベント通知
                lat, lon = user_info.get('latitude', 35.66), user_info.get('longitude', 139.65)
                start_date = datetime.datetime.strptime(plant['start_date'], '%Y-%m-%d').date()
                today = datetime.date.today()
                weather_data = get_weather_data(lat, lon, start_date, today)
                gdd = calculate_gdd(weather_data, plant_info_db['base_temp']) if weather_data else 0
                
                notified_gdds = plant.get('notified_gdds') or []
                for event in plant_info_db.get('events', []):
                    event_gdd = event['gdd']
                    if gdd >= event_gdd and event_gdd not in notified_gdds:
                        advice = event['advice']
                        message_text = f"【栽培コンシェルジュからのお知らせ】\n\n『{plant_name}』が新しい成長段階に到達しました！\n\n「{advice}」\n\n「一覧」から詳しい情報や、具体的な作業内容を確認してくださいね。"
                        push_message = TextMessage(text=message_text, quick_reply=QuickReply(items=[QuickReplyItem(action=MessageAction(label="育ち具合を見る", text="一覧"))]))
                        with ApiClient(line_config) as api_client:
                            MessagingApi(api_client).push_message(PushMessageRequest(to=user_id, messages=[push_message]))
                        notified_gdds.append(event_gdd)
                        supabase.table('user_plants').update({'notified_gdds': notified_gdds}).eq('id', plant['id']).execute()
                        break
        except Exception as e:
            print(f"通知チェック中にエラーが発生: {e}")

# --- LINE Botのメインロジック ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def get_or_create_user(user_id):
    user_res = supabase.table('users').select('*').eq('id', user_id).single().execute()
    if not user_res.data:
        supabase.table('users').insert({'id': user_id}).execute()
        return {'id': user_id}, True
    return user_res.data, False

@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    get_or_create_user(user_id)
    welcome_message = create_welcome_message()
    with ApiClient(line_config) as api_client:
        MessagingApi(api_client).reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[welcome_message])
        )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    reply_message_obj = None

    get_or_create_user(user_id)

    matched_plant = next((p for p in PLANT_DATABASE if p in text), None)
    if matched_plant:
        reply_message_obj = create_date_selection_message(matched_plant)
    elif text in ["追加", "登録", "作物を追加"]:
        items = [QuickReplyItem(action=MessageAction(label=p, text=p)) for p in PLANT_DATABASE.keys()]
        reply_message_obj = TextMessage(text="どの作物を登録しますか？", quick_reply=QuickReply(items=items))
    elif text == "一覧":
        # 【修正点】orderを 'id' の降順（新しい順）に変更
        plants = supabase.table('user_plants').select('*').eq('user_id', user_id).order('id', desc=True).execute().data
        if not plants:
            reply_message_obj = TextMessage(text="まだ植物が登録されていません。「追加」から新しい仲間を迎えましょう！")
        else:
            reply_message_obj = create_plant_list_carousel(plants, PLANT_DATABASE)
    elif text == "場所設定":
        reply_message_obj = TextMessage(
            text="あなたの栽培エリアの天気をより正確に予測するため、位置情報を教えてください。\n（チャット画面下部の「+」から位置情報を送信してください）",
            quick_reply=QuickReply(items=[QuickReplyItem(action=LocationAction(label="位置情報を送信する"))])
        )
    elif 'ヘルプ' in text.lower():
        reply_message_obj = TextMessage(text="""【使い方ガイド】
🌱作物の登録：「追加」と送信
（ボタンでカンタン登録！）

📈植物の管理：「一覧」と送信
（状態確認、履歴、削除ができます）

📍場所の登録：「場所設定」と送信
（天気予報の精度が上がります）""")
    else:
        # リッチメニューからのタップを想定し、不明なテキストには応答しないようにする
        # reply_message_obj = TextMessage(text="「一覧」または「追加」と送ってみてくださいね。分からなければ「ヘルプ」とどうぞ！")
        pass

    if reply_message_obj:
        with ApiClient(line_config) as api_client:
            line_bot_api = MessagingApi(api_client)
            try:
                line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))
            except ApiException as e:
                print(f"API Error: status={e.status}, body={e.body}")

@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location_message(event):
    user_id = event.source.user_id
    lat = event.message.latitude
    lon = event.message.longitude
    supabase.table('users').update({'latitude': lat, 'longitude': lon}).eq('id', user_id).execute()
    reply_message_obj = TextMessage(text="位置情報を登録しました！これからはあなたの場所に合わせて、より正確な予測をお届けします。")
    with ApiClient(line_config) as api_client:
        MessagingApi(api_client).reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data_str = event.postback.data
    data = dict(p.split('=') for p in data_str.split('&'))
    action = data.get('action')
    reply_message_obj = None

    if event.postback.params and 'date' in event.postback.params:
        action = 'set_start_date'

    with ApiClient(line_config) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        if action == 'set_start_date':
            plant_name = data.get('plant_name')
            start_date = event.postback.params.get('date') if event.postback.params else None
            
            if start_date is None:
                date_param = data.get('date')
                if date_param == 'today':
                    start_date = datetime.date.today().strftime('%Y-%m-%d')
                elif date_param == 'yesterday':
                    start_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            
            if plant_name and start_date:
                plant_count_res = supabase.table('user_plants').select('id', count='exact').eq('user_id', user_id).execute()
                is_first_plant = plant_count_res.count == 0

                new_plant = {'user_id': user_id, 'plant_name': plant_name, 'start_date': start_date}
                supabase.table('user_plants').insert(new_plant).execute()
                
                reply_messages = [TextMessage(text=f"「{plant_name}」を{start_date}から栽培開始として登録しました！\n「一覧」で確認できます。")]
                
                line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=reply_messages))

                user_res = supabase.table('users').select('latitude').eq('id', user_id).single().execute()
                user = user_res.data
                if is_first_plant and (not user or not user.get('latitude')):
                    location_prompt = TextMessage(
                        text="ありがとうございます！\nより正確な予測のため、あなたの栽培エリアの位置情報を教えてくれませんか？",
                        quick_reply=QuickReply(items=[QuickReplyItem(action=LocationAction(label="位置情報を送信する"))])
                    )
                    line_bot_api.push_message(PushMessageRequest(to=user_id, messages=[location_prompt]))

                plant_info = PLANT_DATABASE.get(plant_name, {})
                initial_products = plant_info.get('initial_products')
                if initial_products:
                    product_message = create_initial_products_message(plant_name, initial_products)
                    if product_message:
                        line_bot_api.push_message(PushMessageRequest(to=user_id, messages=[product_message]))
                return

        elif action == 'show_status':
            plant_id = int(data.get('plant_id'))
            plant_res = supabase.table('user_plants').select('*').eq('id', plant_id).single().execute()
            plant = plant_res.data
            if plant:
                plant_info = PLANT_DATABASE.get(plant['plant_name'])
                reply_message_obj = create_status_flex_message(user_id, plant, plant_info, supabase)

        elif action == 'show_log':
            plant_id, plant_name = int(data.get('plant_id')), data.get('plant_name')
            offset = int(data.get('offset', 0))
            limit = 5
            actions_res = supabase.table('plant_actions').select('*', count='exact').eq('user_plant_id', plant_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            if not actions_res.data and offset == 0:
                reply_text = f"「{plant_name}」のお手入れ記録はまだありません。"
            else:
                log_texts = [f"【{plant_name}のお手入れ履歴】"] if offset == 0 else []
                for act in actions_res.data:
                    action_time = datetime.datetime.fromisoformat(act['created_at']).strftime('%-m/%-d %H:%M')
                    action_type = "💧水やり" if act['action_type'] == 'log_watering' else "🌱追肥"
                    log_texts.append(f"・{action_time} {action_type}")
                reply_text = "\n".join(log_texts)
            
            quick_reply_items = []
            if actions_res.count > offset + limit:
                next_offset = offset + limit
                quick_reply_items.append(QuickReplyItem(action=PostbackAction(label="さらに過去の履歴を見る", data=f"action=show_log&plant_id={plant_id}&plant_name={plant_name}&offset={next_offset}")))
            reply_message_obj = TextMessage(text=reply_text, quick_reply=QuickReply(items=quick_reply_items) if quick_reply_items else None)
        
        elif action == 'confirm_delete':
            plant_id, plant_name = data.get('plant_id'), data.get('plant_name')
            bubble = FlexBubble(
                body=FlexBox(layout='vertical', spacing='md', contents=[
                    FlexText(text=f"「{plant_name}」を本当に削除しますか？", wrap=True, weight='bold', size='md'),
                    FlexText(text="お手入れ履歴もすべて削除され、元に戻すことはできません。", size='sm', color='#AAAAAA', wrap=True)
                ]),
                footer=FlexBox(layout='horizontal', spacing='sm', contents=[
                    FlexButton(style='primary', color='#ff5555', action=PostbackAction(label='はい、削除します', data=f"action=delete&plant_id={plant_id}")),
                    FlexButton(style='secondary', action=PostbackAction(label='いいえ', data='action=cancel_delete'))
                ]))
            reply_message_obj = FlexMessage(alt_text='削除の確認', contents=bubble)

        elif action == 'delete':
            plant_id = int(data.get('plant_id'))
            supabase.table('plant_actions').delete().eq('user_plant_id', plant_id).execute()
            supabase.table('user_plants').delete().eq('id', plant_id).execute()
            reply_message_obj = TextMessage(text="削除しました。")
            
        elif action == 'cancel_delete':
            reply_message_obj = TextMessage(text="操作をキャンセルしました。")
        
        elif 'log_' in action:
            plant_id = int(data.get('plant_id'))
            action_log = {'user_plant_id': plant_id, 'action_type': action}
            supabase.table('plant_actions').insert(action_log).execute()
            reply_text = '💧水やりを記録しました！' if action == 'log_watering' else '🌱追肥を記録しました！'
            reply_message_obj = TextMessage(text=reply_text)

        if reply_message_obj:
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

# --- アプリケーション起動とスケジューラ設定 ---
if __name__ == "__main__":
    scheduler = BackgroundScheduler(daemon=True, timezone='Asia/Tokyo')
    scheduler.add_job(check_and_send_notifications, 'cron', hour=8)
    scheduler.start()
    
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, use_reloader=False)