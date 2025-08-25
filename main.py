# main.py

# --- 標準ライブラリ・外部ライブラリ ---
import os
import datetime
import requests
from dotenv import load_dotenv
from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler

# --- LINE SDK ---
from linebot.v3 import WebhookHandler
# ...(中略)... 同じimport文は省略 ...
from linebot.v3.messaging import DatetimePickerAction, URIAction

# --- 外部サービス ---
from supabase import create_client, Client

# --- 自作モジュール ---
from plant_data import PLANT_DATABASE
from flex_messages import (
    create_plant_list_carousel, create_date_selection_message,
    create_initial_products_message, create_status_flex_message
)

# --- 初期設定 ---
load_dotenv()
app = Flask(__name__)
# ...(中略)... LINEとSupabaseの初期設定は同じ ...

# --- ヘルパー関数 (calculate_gdd, get_weather_data) ---
# ...(中略)... 元のコードと同じ ...

# --- スケジューラ: 通知機能 ---
def check_and_send_notifications():
    print(f"--- {datetime.datetime.now()}: Running daily checks ---")
    with app.app_context():
        try:
            # 1. GDDイベント通知 (元のロジック)
            # ...(中略)...

            # 2. 【課題2】水やりリマインダー
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            plants_res = supabase.table('user_plants').select('id, user_id, plant_name').execute()
            for plant in plants_res.data:
                action_res = supabase.table('plant_actions').select('id').eq('user_plant_id', plant['id']).eq('action_type', 'log_watering').gte('created_at', yesterday.isoformat()).execute()
                if not action_res.data:
                    # 過去24時間に水やり記録がない場合
                    message = TextMessage(text=f"【水やりリマインダー💧】\n『{plant['plant_name']}』の水やりは記録しましたか？\nもし水やりをしたら、忘れずに記録してくださいね！")
                    with ApiClient(line_config) as api_client:
                        MessagingApi(api_client).push_message(PushMessageRequest(to=plant['user_id'], messages=[message]))
        except Exception as e:
            print(f"通知チェック中にエラーが発生: {e}")


# --- LINE Bot メインロジック ---
@app.route("/callback", methods=['POST'])
# ...(中略)... callback関数は同じ ...

def get_or_create_user(user_id):
    user_res = supabase.table('users').select('*').eq('id', user_id).single().execute()
    if not user_res.data:
        supabase.table('users').insert({'id': user_id, 'state': 'normal'}).execute()
        return {'id': user_id, 'state': 'normal'}, True # 新規ユーザーフラグを立てる
    return user_res.data, False

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    user, is_new_user = get_or_create_user(user_id)
    
    with ApiClient(line_config) as api_client:
        line_bot_api = MessagingApi(api_client)

        if is_new_user:
            welcome_msg = TextMessage(text="はじめまして！\nあなたの植物栽培を科学的にサポートする「栽培コンシェルジュ」です。\nまずは「追加」と送って、育てる作物を登録しましょう！")
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[welcome_msg]))
            return

        # 【課題8】柔軟なコマンド解釈
        matched_plant = next((p for p in PLANT_DATABASE if p in text), None)
        if matched_plant and "追加" in text:
             # 「ミニトマトを追加」のような完全一致を優先
             reply_message_obj = create_date_selection_message(matched_plant)
        elif text in ["追加", "登録"]:
             items = [QuickReplyItem(action=MessageAction(label=p, text=f"{p}を追加")) for p in PLANT_DATABASE.keys()]
             reply_message_obj = TextMessage(text="どの作物を登録しますか？", quick_reply=QuickReply(items=items))
        elif text == "一覧":
             plants = supabase.table('user_plants').select('*').eq('user_id', user_id).order('id').execute().data
            if not plants:
                reply_message_obj = TextMessage(text="まだ植物が登録されていません。「追加」から新しい仲間を迎えましょう！")
            else:
                reply_message_obj = create_plant_list_carousel(plants, PLANT_DATABASE)
        elif text == "場所設定":
            # ...(中略)... 元のコードと同じ ...
        else:
            reply_message_obj = TextMessage(text="「一覧」または「追加」と送ってみてくださいね。分からなければ「ヘルプ」とどうぞ！")

        if reply_message_obj:
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

# ... handle_location_message は同じ ...

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    
    # 日付ピッカーからのPostbackを処理
    if event.postback.params and 'date' in event.postback.params:
        data_str = event.postback.data
        data = dict(p.split('=') for p in data_str.split('&'))
        plant_name = data.get('plant_name')
        start_date = event.postback.params['date']
        # この後の処理は 'set_start_date' アクションに合流させる
        action = 'set_start_date'
    else:
        data = dict(p.split('=') for p in event.postback.data.split('&'))
        action = data.get('action')
        start_date = None # 初期化

    with ApiClient(line_config) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_message_obj = None

        if action == 'set_start_date':
            # 【課題1】栽培開始日の設定
            plant_name = data.get('plant_name')
            
            if start_date: # 日付ピッカーからの場合
                pass
            else: # 今日・昨日のボタンからの場合
                date_param = data.get('date')
                if date_param == 'today':
                    start_date = datetime.date.today().strftime('%Y-%m-%d')
                elif date_param == 'yesterday':
                    start_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            
            if plant_name and start_date:
                # ユーザーが初めて植物を登録するかチェック
                plant_count_res = supabase.table('user_plants').select('id', count='exact').eq('user_id', user_id).execute()
                is_first_plant = plant_count_res.count == 0

                new_plant = {'user_id': user_id, 'plant_name': plant_name, 'start_date': start_date}
                supabase.table('user_plants').insert(new_plant).execute()
                
                reply_messages = [TextMessage(text=f"「{plant_name}」を{start_date}から栽培開始として登録しました！\n「一覧」で確認できます。")]
                
                # 【課題3】能動的な場所設定の促し
                user = supabase.table('users').select('latitude').eq('id', user_id).single().execute().data
                if is_first_plant and not user.get('latitude'):
                    location_prompt = TextMessage(
                        text="ありがとうございます！\nより正確な予測のため、あなたの栽培エリアの位置情報を教えてくれませんか？",
                        quick_reply=QuickReply(items=[QuickReplyItem(action=LocationAction(label="位置情報を送信する"))])
                    )
                    reply_messages.append(location_prompt)

                # 【課題7】初期投資アイテムの提案
                plant_info = PLANT_DATABASE.get(plant_name, {})
                initial_products = plant_info.get('initial_products')
                if initial_products:
                    product_message = create_initial_products_message(plant_name, initial_products)
                    if product_message:
                        reply_messages.append(product_message)

                line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=reply_messages))
                return # 複数のメッセージを送信したのでここで終了

        elif action == 'show_log':
            # 【課題9】お手入れ履歴の改善 (ページネーション)
            plant_id, plant_name = int(data.get('plant_id')), data.get('plant_name')
            offset = int(data.get('offset', 0))
            limit = 5
            
            actions_res = supabase.table('plant_actions').select('*', count='exact').eq('user_plant_id', plant_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            if not actions_res.data:
                reply_text = f"「{plant_name}」のお手入れ記録はまだありません。"
            else:
                log_texts = [f"【{plant_name}のお手入れ履歴】"]
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

        # ... その他のPostbackアクションは元のコードと同様 ...

        if reply_message_obj:
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

# --- アプリケーション起動とスケジューラ設定 ---
if __name__ == "__main__":
    # ...(中略)... 元のコードと同じ ...