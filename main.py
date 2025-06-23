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
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, FlexMessage, ApiException, FlexBubble,
    PostbackAction, MessageAction, QuickReply, QuickReplyItem
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
        'base_temp': 10.0,
        'image_url': 'https://images.pexels.com/photos/7208483/pexels-photo-7208483.jpeg',
        'avg_gdd_per_day': 15, # 1日あたりの平均的な積算温度（予測に利用）
        'events': [
            {'gdd': 300, 'advice': '最初の追肥のタイミングです！',
             'what': 'N-P-Kが8-8-8などのバランスが良い化成肥料',
             'how': '一株あたり約10g（大さじ1杯程度）を、株元から少し離して円を描くように与えます。',
             'product_name': 'トマトの追肥用肥料', 'affiliate_link': 'https://amzn.to/40aoawy',
             'recommendation_reason': 'この時期は実をつけ始める大切な時期。バランスの取れた栄養が、甘くて美味しいトマトを育てる秘訣です。'},
            {'gdd': 900, 'advice': '収穫まであと少し！', 'what': '水やり管理', 'how': '土の表面が乾いたら、朝のうちにたっぷりと与えましょう。実が赤くなり始めたら、少し乾燥気味にすると糖度が上がります。'}
        ]
    },
    'きゅうり': {
        'base_temp': 12.0,
        'image_url': 'https://images.pexels.com/photos/7543157/pexels-photo-7543157.jpeg',
        'avg_gdd_per_day': 20,
        'events': [
            {'gdd': 250, 'advice': '最初の追肥のタイミングです。', 'what': '化成肥料', 'how': '株元にパラパラと少量まき、土と軽く混ぜ合わせます。'},
            {'gdd': 500, 'advice': '収穫が始まりました！', 'what': 'こまめな収穫', 'how': '実がなり始めたら、2週間に1回ほどのペースで追肥を続けると、長く収穫を楽しめます。'}
        ]
    },
    'なす': {
        'base_temp': 12.0,
        'image_url': 'https://images.unsplash.com/photo-1639428134238-b548770d4b77?q=80&w=987&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        'avg_gdd_per_day': 18,
        'events': [
            {'gdd': 350, 'advice': '最初の追肥のタイミングです。', 'what': '化成肥料', 'how': '株の周りに円を描くように肥料を与えましょう。'},
            {'gdd': 800, 'advice': '最初の実がなり始めました！', 'what': '継続的な追肥', 'how': 'ここからは肥料切れに注意し、2週間に1回のペースで追肥を続けるのがおすすめです。', 'product_name': 'なす用の肥料', 'affiliate_link': 'https://amzn.to/4cblYJV', 'recommendation_reason': '「なすは水と肥料で育つ」と言われるほど栄養が必要です。実をつけ続けるためのスタミナを補給しましょう。'}
        ]
    },
    'ピーマン': {
        'base_temp': 15.0,
        'image_url': 'https://images.pexels.com/photos/4943441/pexels-photo-4943441.jpeg',
        'avg_gdd_per_day': 16,
        'events': [
            {'gdd': 400, 'advice': '一番花が咲いたら追肥のサインです！', 'what': '化成肥料', 'how': '株元に少量与えます。'},
            {'gdd': 900, 'advice': '実がなり始めました。', 'what': '水やり管理', 'how': '乾燥に注意し、水やりを欠かさないようにしましょう。', 'product_name': '野菜用の液体肥料', 'affiliate_link': 'https://amzn.to/3Rj7sC9', 'recommendation_reason': '液体肥料は即効性があり、すぐに栄養を届けたいこの時期にぴったりです。'}
        ]
    },
    'えだまめ': {
        'base_temp': 10.0,
        'image_url': 'https://images.pexels.com/photos/2551790/pexels-photo-2551790.jpeg',
        'avg_gdd_per_day': 18,
        'events': [
            {'gdd': 250, 'advice': '花が咲き始めたら、追肥のタイミングです。', 'what': 'リン酸・カリウムが多めの肥料', 'how': '窒素分が多いと葉ばかり茂るので注意。株元に軽く一握り与えましょう。'},
            {'gdd': 600, 'advice': 'さやが膨らんできました！収穫が楽しみですね。', 'what': '水やり', 'how': '乾燥はさやの成長に影響します。特にこの時期は水を切らさないようにしましょう。'}
        ]
    },
    'しそ': {
        'base_temp': 15.0,
        'image_url': 'https://images.pexels.com/photos/13532392/pexels-photo-13532392.jpeg',
        'avg_gdd_per_day': 12,
        'events': [
            {'gdd': 150, 'advice': '本葉が10枚以上になったら、摘心（てきしん）をしましょう。', 'what': '一番上の芽', 'how': '先端をハサミでカットすると、脇芽が増えて収穫量がアップします。'},
            {'gdd': 300, 'advice': '収穫が始まります！葉が茂ってきたら、2週間に1回程度の追肥を。', 'what': '液体肥料', 'how': '規定の倍率に薄めたものを、水やり代わりに与えると手軽です。'}
        ]
    }
}


# --- ヘルパー関数 ---
def get_weather_data(start_date, end_date):
    # 東京(世田谷)の固定座標。将来的にはユーザー設定に対応させたい。
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
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
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
            reply_message_obj = TextMessage(text=f"「{plant_name}」を新しい作物として登録しました！")
        else:
            reply_message_obj = TextMessage(text=f"申し訳ありません、「{plant_name}」の栽培データはまだありません。")
            
    elif 'の状態' in user_message:
        plant_name_to_check = user_message.replace('の状態', '').strip()
        plant_response = supabase.table('user_plants').select('*').eq('user_id', user_id).eq('plant_name', plant_name_to_check).order('id', desc=True).limit(1).execute()

        if plant_response.data:
            found_plant = plant_response.data[0]
            plant_name = found_plant['plant_name']
            plant_info = PLANT_DATABASE.get(plant_name)
            
            if plant_info:
                start_date = datetime.datetime.strptime(found_plant['start_date'], '%Y-%m-%d').date()
                today = datetime.date.today()
                weather_data = get_weather_data(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
                gdd = calculate_gdd(weather_data, plant_info['base_temp']) if weather_data else 0

                # --- 次のイベント情報と予測を計算 ---
                next_event = None
                for ev in plant_info.get('events', []):
                    if gdd < ev['gdd']:
                        next_event = ev
                        break

                progress_contents = []
                if next_event:
                    progress = (gdd / next_event['gdd']) * 100
                    gdd_remaining = next_event['gdd'] - gdd
                    days_to_event = gdd_remaining / plant_info.get('avg_gdd_per_day', 15)

                    progress_bar = FlexBox(layout='vertical', margin='md', contents=[
                        FlexText(text=f"次のイベントまで {progress:.0f}%", size='sm', color='#555555'),
                        FlexBox(layout='vertical', margin='sm', background_color='#E0E0E0', corner_radius='5px', height='10px', contents=[
                            FlexBox(layout='vertical', background_color='#00B900', corner_radius='5px', height='100%', width=f'{min(progress, 100)}%')
                        ]),
                        FlexText(text=f"予測: あと約{days_to_event:.0f}日 ({next_event['gdd']} GDD)", size='xs', color='#AAAAAA', margin='sm', align='end')
                    ])
                    progress_contents.append(progress_bar)
                
                # --- アドバイス部分を作成 ---
                advice_contents = []
                advice_title = "栽培完了！"
                advice_text = "お疲れ様でした！収穫を楽しんでくださいね。"
                if next_event:
                    advice_title = next_event['advice']
                    advice_text = ""
                    if next_event.get('what'):
                        advice_text += f"【何を】\n{next_event['what']}\n\n"
                    if next_event.get('how'):
                        advice_text += f"【どうやって】\n{next_event['how']}"
                
                advice_contents.append(FlexText(text=advice_title, weight='bold', wrap=True, margin='lg', size='lg'))
                if advice_text:
                    advice_contents.append(FlexText(text=advice_text, wrap=True, margin='md', size='sm', color='#333333'))
                
                # --- おすすめ商品部分を作成 ---
                recommendation_contents = []
                if next_event and next_event.get('product_name'):
                    recommendation_contents.extend([
                        FlexSeparator(margin='lg'),
                        FlexText(text="💡ヒント", weight='bold', margin='lg'),
                        FlexText(text=next_event.get('recommendation_reason', ''), size='sm', wrap=True, margin='md'),
                        FlexButton(
                            style='link',
                            height='sm',
                            action=MessageAction(label=f"おすすめ商品: {next_event['product_name']}", text=f"おすすめ商品「{next_event['product_name']}」のリンクはこちらです！\n{next_event['affiliate_link']}")
                        )
                    ])

                # --- 全体を組み立ててFlexMessageを作成 ---
                bubble = FlexBubble(
                    hero=FlexImage(url=plant_info.get('image_url', 'https://example.com/placeholder.jpg'), size='full', aspect_ratio='20:13', aspect_mode='cover'),
                    body=FlexBox(
                        layout='vertical',
                        contents=[
                            FlexText(text=f"{plant_name}の栽培状況", weight='bold', size='xl'),
                            FlexBox(layout='vertical', margin='lg', spacing='sm', contents=[
                                FlexBox(layout='baseline', spacing='sm', contents=[
                                    FlexText(text='栽培日数', color='#aaaaaa', size='sm', flex=2),
                                    FlexText(text=f"{(today - start_date).days + 1}日目", wrap=True, color='#666666', size='sm', flex=5)
                                ]),
                                FlexBox(layout='baseline', spacing='sm', contents=[
                                    FlexText(text='積算温度', color='#aaaaaa', size='sm', flex=2),
                                    FlexText(text=f"{gdd:.1f}℃・日", wrap=True, color='#666666', size='sm', flex=5)
                                ])
                            ]),
                            *progress_contents,
                            *advice_contents,
                            *recommendation_contents
                        ]),
                    footer=FlexBox(
                        layout='vertical', spacing='sm',
                        contents=[
                            FlexButton(style='link', height='sm', action=PostbackAction(label="💧 水やりを記録する", data=f"action=log_watering&plant_id={found_plant['id']}")),
                            FlexButton(style='link', height='sm', action=PostbackAction(label="🌱 追肥を記録する", data=f"action=log_fertilizer&plant_id={found_plant['id']}"))
                        ]))
                reply_message_obj = FlexMessage(alt_text=f"{plant_name}の状態", contents=bubble)
        else:
            reply_message_obj = TextMessage(text=f"「{plant_name_to_check}」は登録されていません。")
            
    elif 'ヘルプ' in user_message.lower():
        reply_message_obj = TextMessage(text="""【使い方ガイド】
🌱作物の登録：「追加」と送信してください
（ボタンが表示されます）

📈状態の確認：「〇〇の状態」
（例：ミニトマトの状態）""")
    else:
        reply_message_obj = TextMessage(text="使い方が分からない場合は、「ヘルプ」と送ってみてくださいね。")

    if reply_message_obj:
        with ApiClient(line_config) as api_client:
            line_bot_api = MessagingApi(api_client)
            try:
                line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message_obj]))
            except ApiException as e:
                print(f"API Error: {e.status_code}")
                print(e.body)

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    postback_data_str = event.postback.data
    params = dict(p.split('=') for p in postback_data_str.split('&'))
    action_type = params.get('action')
    plant_id = params.get('plant_id')
    reply_text = "エラーが発生しました。"
    if action_type and plant_id:
        action_log = {'user_plant_id': int(plant_id), 'action_type': action_type}
        supabase.table('plant_actions').insert(action_log).execute()
        
        if action_type == 'log_watering':
            reply_text = '水やりを記録しました！'
        elif action_type == 'log_fertilizer':
            reply_text = '追肥を記録しました！'

    with ApiClient(line_config) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply_text)]))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)