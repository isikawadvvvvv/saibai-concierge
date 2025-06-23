from dotenv import load_dotenv
load_dotenv()

import os
import datetime
import requests
import json
from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler # スケジューラ機能

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent, LocationMessageContent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    PushMessageRequest,
    TextMessage, FlexMessage, ApiException, FlexBubble, FlexCarousel,
    PostbackAction, MessageAction, QuickReply, QuickReplyItem,
    LocationAction
)
from linebot.v3.messaging.models import (
    FlexBox, FlexText, FlexImage, FlexButton, FlexSeparator, FlexSpan
)
from supabase import create_client, Client

# --- 初期設定 ---
app = Flask(__name__)
line_config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# --- Ver.2.0 植物データベース ---
PLANT_DATABASE = {
    'ミニトマト': {
        'base_temp': 10.0, 'image_url': 'https://images.pexels.com/photos/7208483/pexels-photo-7208483.jpeg', 'avg_gdd_per_day': 15,
        'events': [{'gdd': 300, 'advice': '最初の追肥のタイミングです！', 'what': 'N-P-Kが8-8-8などのバランスが良い化成肥料', 'how': '一株あたり約10g（大さじ1杯程度）を、株元から少し離して円を描くように与えます。', 'product_name': 'トマトの追肥用肥料', 'affiliate_link': 'https://amzn.to/40aoawy', 'recommendation_reason': 'この時期は実をつけ始める大切な時期。バランスの取れた栄養が、甘くて美味しいトマトを育てる秘訣です。'}, {'gdd': 900, 'advice': '収穫まであと少し！', 'what': '水やり管理', 'how': '土の表面が乾いたら、朝のうちにたっぷりと与えましょう。実が赤くなり始めたら、少し乾燥気味にすると糖度が上がります。'}]
    },
    'きゅうり': {
        'base_temp': 12.0, 'image_url': 'https://images.pexels.com/photos/7543157/pexels-photo-7543157.jpeg', 'avg_gdd_per_day': 20,
        'events': [{'gdd': 250, 'advice': '最初の追肥のタイミングです。', 'what': '化成肥料', 'how': '株元にパラパラと少量まき、土と軽く混ぜ合わせます。'}, {'gdd': 500, 'advice': '収穫が始まりました！', 'what': 'こまめな収穫', 'how': '実がなり始めたら、2週間に1回ほどのペースで追肥を続けると、長く収穫を楽しめます。'}]
    },
    'なす': {
        'base_temp': 12.0, 'image_url': 'https://images.unsplash.com/photo-1639428134238-b548770d4b77?q=80&w=987&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'avg_gdd_per_day': 18,
        'events': [{'gdd': 350, 'advice': '最初の追肥のタイミングです。', 'what': '化成肥料', 'how': '株の周りに円を描くように肥料を与えましょう。'}, {'gdd': 800, 'advice': '最初の実がなり始めました！', 'what': '継続的な追肥', 'how': 'ここからは肥料切れに注意し、2週間に1回のペースで追肥を続けるのがおすすめです。', 'product_name': 'なす用の肥料', 'affiliate_link': 'https://amzn.to/4cblYJV', 'recommendation_reason': '「なすは水と肥料で育つ」と言われるほど栄養が必要です。実をつけ続けるためのスタミナを補給しましょう。'}]
    },
    'ピーマン': {
        'base_temp': 15.0, 'image_url': 'https://images.pexels.com/photos/4943441/pexels-photo-4943441.jpeg', 'avg_gdd_per_day': 16,
        'events': [{'gdd': 400, 'advice': '一番花が咲いたら追肥のサインです！', 'what': '化成肥料', 'how': '株元に少量与えます。'}, {'gdd': 900, 'advice': '実がなり始めました。', 'what': '水やり管理', 'how': '乾燥に注意し、水やりを欠かさないようにしましょう。', 'product_name': '野菜用の液体肥料', 'affiliate_link': 'https://amzn.to/3Rj7sC9', 'recommendation_reason': '液体肥料は即効性があり、すぐに栄養を届けたいこの時期にぴったりです。'}]
    },
    'えだまめ': {
        'base_temp': 10.0, 'image_url': 'https://images.pexels.com/photos/2551790/pexels-photo-2551790.jpeg', 'avg_gdd_per_day': 18,
        'events': [{'gdd': 250, 'advice': '花が咲き始めたら、追肥のタイミングです。', 'what': 'リン酸・カリウムが多めの肥料', 'how': '窒素分が多いと葉ばかり茂るので注意。株元に軽く一握り与えましょう。'}, {'gdd': 600, 'advice': 'さやが膨らんできました！収穫が楽しみですね。', 'what': '水やり', 'how': '乾燥はさやの成長に影響します。特にこの時期は水を切らさないようにしましょう。'}]
    },
    'しそ': {
        'base_temp': 15.0, 'image_url': 'https://images.pexels.com/photos/13532392/pexels-photo-13532392.jpeg', 'avg_gdd_per_day': 12,
        'events': [{'gdd': 150, 'advice': '本葉が10枚以上になったら、摘心（てきしん）をしましょう。', 'what': '一番上の芽', 'how': '先端をハサミでカットすると、脇芽が増えて収穫量がアップします。'}, {'gdd': 300, 'advice': '収穫が始まります！葉が茂ってきたら、2週間に1回程度の追肥を。', 'what': '液体肥料', 'how': '規定の倍率に薄めたものを、水やり代わりに与えると手軽です。'}]
    }
}


# --- ヘルパー関数 ---
def get_weather_data(latitude=35.66, longitude=139.65, start_date=None, end_date=None):
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

# --- 状態表示カードを作成する関数 ---
def create_status_flex_message(user_id, plant_id, plant_name, start_date_str):
    plant_info = PLANT_DATABASE.get(plant_name)
    if not plant_info:
        return TextMessage(text=f"「{plant_name}」の情報が見つかりません。")

    user = supabase.table('users').select('latitude, longitude').eq('id', user_id).single().execute().data
    lat = user.get('latitude') or 35.66
    lon = user.get('longitude') or 139.65

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    today = datetime.date.today()
    weather_data = get_weather_data(latitude=lat, longitude=lon, start_date=start_date, end_date=today)
    gdd = calculate_gdd(weather_data, plant_info['base_temp']) if weather_data else 0

    next_event = next((ev for ev in plant_info.get('events', []) if gdd < ev['gdd']), None)
    
    header_contents = [FlexText(text=plant_name, weight='bold', size='xl', margin='md')]
    basic_info_contents = [
        FlexBox(layout='baseline', spacing='sm', contents=[FlexText(text='栽培日数', color='#aaaaaa', size='sm', flex=3), FlexText(text=f"{(today - start_date).days + 1}日目", wrap=True, color='#666666', size='sm', flex=5)]),
        FlexBox(layout='baseline', spacing='sm', contents=[FlexText(text='積算温度', color='#aaaaaa', size='sm', flex=3), FlexText(text=f"{gdd:.1f}℃・日", wrap=True, color='#666666', size='sm', flex=5)])
    ]
    progress_contents = []
    if next_event:
        progress = (gdd / next_event['gdd']) * 100
        days_to_event = (next_event['gdd'] - gdd) / plant_info.get('avg_gdd_per_day', 15)
        progress_contents.extend([
            FlexSeparator(margin='xl'),
            FlexText(text="次のイベントへの進捗", size='md', weight='bold', margin='lg'),
            FlexBox(layout='vertical', margin='md', contents=[
                FlexText(text=f"{progress:.0f}%", size='sm', color='#555555'),
                FlexBox(layout='vertical', margin='sm', background_color='#E0E0E0', corner_radius='5px', height='10px', contents=[
                    FlexBox(layout='vertical', background_color='#4CAF50', corner_radius='5px', height='100%', width=f'{min(progress, 100)}%', contents=[])
                ]),
                FlexText(text=f"予測: あと約{max(0, days_to_event):.0f}日 ({next_event['gdd']} GDD)", size='xs', color='#AAAAAA', margin='sm', align='end')
            ])
        ])
    
    advice_contents = []
    advice_title = "栽培完了！"
    advice_what = "お疲れ様でした！"
    advice_how = "収穫を楽しんでくださいね。"
    if next_event:
        advice_title = next_event['advice']
        advice_what = next_event.get('what', '---')
        advice_how = next_event.get('how', '---')
    advice_box = FlexBox(layout='vertical', margin='lg', spacing='md', contents=[
        FlexText(text=advice_title, weight='bold', wrap=True, size='lg', color='#1E88E5'),
        FlexBox(layout='vertical', margin='lg', spacing='sm', contents=[
            FlexText(text="何を", weight='bold', size='sm', color='#555555'), FlexText(text=advice_what, wrap=True, size='sm'),
            FlexSeparator(margin='md'),
            FlexText(text="どうやって", weight='bold', size='sm', color='#555555', margin='sm'), FlexText(text=advice_how, wrap=True, size='sm'),
        ])
    ])
    advice_contents.extend([FlexSeparator(margin='xl'), advice_box])
    
    recommendation_contents = []
    if next_event and next_event.get('product_name'):
        recommendation_contents.extend([
            FlexSeparator(margin='lg'),
            FlexBox(layout='vertical', margin='md', contents=[
                FlexText(text="💡 おすすめアイテム", weight='bold', size='md', margin='sm'),
                FlexText(text=next_event.get('recommendation_reason', ''), size='xs', wrap=True, margin='md', color='#666666'),
                FlexButton(style='link', height='sm', action=MessageAction(label=f"商品を見る: {next_event['product_name']}", text=f"おすすめ商品「{next_event['product_name']}」のリンクはこちらです！\n{next_event['affiliate_link']}"), margin='sm', color='#1E88E5')
            ])
        ])

    bubble = FlexBubble(
        hero=FlexImage(url=plant_info.get('image_url', 'https://example.com/placeholder.jpg'), size='full', aspect_ratio='20:13', aspect_mode='cover'),
        body=FlexBox(layout='vertical', spacing='lg', contents=[
            *header_contents,
            FlexBox(layout='vertical', margin='lg', spacing='md', contents=basic_info_contents),
            *progress_contents, *advice_contents, *recommendation_contents
        ]),
        footer=FlexBox(layout='vertical', spacing='md', contents=[
            FlexSeparator(),
            FlexButton(style='primary', height='sm', action=PostbackAction(label="💧 水やりを記録する", data=f"action=log_watering&plant_id={plant_id}"), color="#42a5f5"),
            FlexButton(style='primary', height='sm', action=PostbackAction(label="🌱 追肥を記録する", data=f"action=log_fertilizer&plant_id={plant_id}"), color="#66bb6a")
        ]))
    return FlexMessage(alt_text=f"{plant_name}の状態", contents=bubble)

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    reply_message_obj = None

    user = supabase.table('users').select('id').eq('id', user_id).single().execute().data
    if not user:
        supabase.table('users').insert({'id': user_id}).execute()
        reply_message_obj = TextMessage(text="""はじめまして！
僕は、あなたの植物栽培を科学的にサポートする「栽培コンシェルジュ」です。
まずは「追加」と送って、育てる作物を登録しましょう！""")
    
    elif user_message == "一覧":
        plants = supabase.table('user_plants').select('*').eq('user_id', user_id).order('id', desc=False).limit(12).execute().data
        if not plants:
            reply_message_obj = TextMessage(text="まだ植物が登録されていません。「追加」から新しい仲間を迎えましょう！")
        else:
            bubbles = []
            for plant in plants:
                plant_info = PLANT_DATABASE.get(plant['plant_name'], {})
                bubble = FlexBubble(
                    hero=FlexImage(url=plant_info.get('image_url', 'https://example.com/placeholder.jpg'), size='full', aspect_ratio='4:3', aspect_mode='cover', action=PostbackAction(label='status', data=f"action=show_status&plant_id={plant['id']}")),
                    body=FlexBox(layout='vertical', spacing='md', contents=[
                        FlexText(text=plant['plant_name'], weight='bold', size='xl'),
                        FlexText(text=f"栽培開始: {plant['start_date']}", size='sm', color='#AAAAAA')
                    ]),
                    footer=FlexBox(layout='vertical', spacing='sm', contents=[
                        FlexButton(style='primary', color='#00B900', action=PostbackAction(label='📈 状態を見る', data=f"action=show_status&plant_id={plant['id']}")),
                        FlexButton(style='secondary', action=PostbackAction(label='📝 お手入れ履歴', data=f"action=show_log&plant_id={plant['id']}&plant_name={plant['plant_name']}")),
                        FlexButton(style='secondary', action=PostbackAction(label='🗑️ 削除', data=f"action=confirm_delete&plant_id={plant['id']}&plant_name={plant['plant_name']}"))
                    ])
                )
                bubbles.append(bubble)
            reply_message_obj = FlexMessage(alt_text='登録植物一覧', contents=FlexCarousel(contents=bubbles))

    elif user_message == "場所設定":
        reply_message_obj = TextMessage(
            text="あなたの栽培エリアの天気をより正確に予測するため、位置情報を教えてください。\n（チャット画面下部の「+」から位置情報を送信してください）",
            quick_reply=QuickReply(items=[QuickReplyItem(action=LocationAction(label="位置情報を送信する"))])
        )

    elif user_message in ["追加", "登録", "作物を追加"]:
        items = []
        for plant_name in PLANT_DATABASE.keys():
            items.append(QuickReplyItem(action=MessageAction(label=plant_name, text=f"{plant_name}を追加")))
        reply_message_obj = TextMessage(text="どの作物を登録しますか？", quick_reply=QuickReply(items=items))

    elif 'を追加' in user_message:
        plant_name = user_message.replace('を追加', '').strip()
        if plant_name and plant_name in PLANT_DATABASE:
            new_plant = {'user_id': user_id, 'plant_name': plant_name, 'start_date': str(datetime.date.today())}
            supabase.table('user_plants').insert(new_plant).execute()
            reply_message_obj = TextMessage(text=f"「{plant_name}」を新しい作物として登録しました！\nさっそく「一覧」と送って、確認してみましょう。")
        else:
            reply_message_obj = TextMessage(text=f"申し訳ありません、「{plant_name}」の栽培データはまだありません。")
            
    elif 'の状態' in user_message:
        plant_name_to_check = user_message.replace('の状態', '').strip()
        plant_response = supabase.table('user_plants').select('*').eq('user_id', user_id).eq('plant_name', plant_name_to_check).order('id', desc=True).limit(1).execute()
        if plant_response.data:
            plant = plant_response.data[0]
            reply_message_obj = create_status_flex_message(user_id, plant['id'], plant['plant_name'], plant['start_date'])
        else:
            reply_message_obj = TextMessage(text=f"「{plant_name_to_check}」は登録されていません。「一覧」で確認してください。")
            
    elif 'ヘルプ' in user_message.lower():
        reply_message_obj = TextMessage(text="""【使い方ガイド】
🌱作物の登録：「追加」と送信
（ボタンでカンタン登録！）

📈植物の管理：「一覧」と送信
（状態確認、履歴、削除ができます）

📍場所の登録：「場所設定」と送信
（天気予報の精度が上がります）""")
    else:
        reply_message_obj = TextMessage(text="「一覧」または「追加」と送ってみてくださいね。分からなければ「ヘルプ」とどうぞ！")

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
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data = dict(p.split('=') for p in event.postback.data.split('&'))
    action = data.get('action')
    reply_message_obj = None

    with ApiClient(line_config) as api_client:
        line_bot_api = MessagingApi(api_client)
        if action == 'show_status':
            plant_id = int(data.get('plant_id'))
            plant = supabase.table('user_plants').select('*').eq('id', plant_id).single().execute().data
            if plant: reply_message_obj = create_status_flex_message(user_id, plant['id'], plant['plant_name'], plant['start_date'])
        
        elif action == 'show_log':
            plant_id, plant_name = int(data.get('plant_id')), data.get('plant_name')
            actions = supabase.table('plant_actions').select('*').eq('user_plant_id', plant_id).order('created_at', desc=True).limit(5).execute().data
            if not actions:
                reply_text = f"「{plant_name}」のお手入れ記録はまだありません。"
            else:
                log_texts = [f"【{plant_name}の最近のお手入れ履歴】"]
                for act in actions:
                    action_time = datetime.datetime.fromisoformat(act['created_at']).strftime('%-m/%-d %H:%M')
                    action_type = "💧水やり" if act['action_type'] == 'log_watering' else "🌱追肥"
                    log_texts.append(f"・{action_time} {action_type}")
                reply_text = "\n".join(log_texts)
            reply_message_obj = TextMessage(text=reply_text)
            
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

# --- プッシュ通知の心臓部 ---
def check_and_send_notifications():
    print("--- Running daily notification check ---")
    with app.app_context():
        try:
            plants_to_check = supabase.table('user_plants').select('*, users(*)').execute().data
            if not plants_to_check:
                print("No plants to check."); return

            for plant in plants_to_check:
                user_id, user_info, plant_name, plant_info = plant['user_id'], plant['users'], plant['plant_name'], PLANT_DATABASE.get(plant['plant_name'])
                if not plant_info or not user_info: continue

                lat, lon = user_info.get('latitude', 35.66), user_info.get('longitude', 139.65)
                start_date, today = datetime.datetime.strptime(plant['start_date'], '%Y-%m-%d').date(), datetime.date.today()
                
                weather_data = get_weather_data(latitude=lat, longitude=lon, start_date=start_date, end_date=today)
                gdd = calculate_gdd(weather_data, plant_info['base_temp']) if weather_data else 0
                notified_gdds = plant.get('notified_gdds') or []

                for event_info in plant_info.get('events', []):
                    event_gdd = event_info['gdd']
                    if gdd >= event_gdd and event_gdd not in notified_gdds:
                        print(f"Sending notification to {user_id} for {plant_name} at GDD {event_gdd}")
                        advice = event_info['advice']
                        message_text = f"【栽培コンシェルジュからのお知らせ】\n\n『{plant_name}』が新しい成長段階に到達しました！\n\n「{advice}」\n\n「一覧」から詳しい情報や、具体的な作業内容を確認してくださいね。"
                        push_message = TextMessage(text=message_text, quick_reply=QuickReply(items=[QuickReplyItem(action=MessageAction(label="植物一覧を見る", text="一覧"))]))

                        with ApiClient(line_config) as api_client:
                            MessagingApi(api_client).push_message(PushMessageRequest(to=user_id, messages=[push_message]))

                        notified_gdds.append(event_gdd)
                        supabase.table('user_plants').update({'notified_gdds': notified_gdds}).eq('id', plant['id']).execute()
                        break
        except Exception as e:
            print(f"Error during notification check: {e}")

# --- アプリケーション起動とスケジューラ設定 ---
if __name__ == "__main__":
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(check_and_send_notifications, 'cron', hour=8, timezone='Asia/Tokyo')
    scheduler.start()
    
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, use_reloader=False)