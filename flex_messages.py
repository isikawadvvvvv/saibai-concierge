# flex_messages.py
import datetime
import requests
from linebot.v3.messaging import (
    FlexMessage, FlexBubble, FlexCarousel, FlexBox, FlexText, FlexImage, FlexButton, FlexSeparator,
    PostbackAction, MessageAction, DatetimePickerAction, URIAction, TextMessage, QuickReply, QuickReplyItem
)

def create_welcome_message():
    bubble = FlexBubble(
        header=FlexBox(
            layout='vertical',
            contents=[
                FlexText(text="はじめまして！", weight='bold', size='xl', align='center')
            ]
        ),
        body=FlexBox(
            layout='vertical',
            spacing='md',
            contents=[
                FlexText(text="あなたの植物栽培を科学的にサポートする「栽培コンシェルジュ」です。", wrap=True, size='sm'),
                FlexText(text="まずは下のボタンから、育てる作物を登録してみましょう！", wrap=True, size='sm', margin='md')
            ]
        ),
        footer=FlexBox(
            layout='vertical',
            spacing='sm',
            contents=[
                FlexButton(
                    style='primary',
                    color='#00B900',
                    action=MessageAction(label='🌱 作物を追加する', text='追加')
                ),
                FlexButton(
                    style='secondary',
                    action=MessageAction(label='使い方を見る (ヘルプ)', text='ヘルプ')
                ),
            ]
        )
    )
    return FlexMessage(alt_text="はじめまして！栽培コンシェルジュです。", contents=bubble)

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

def create_status_flex_message(user_id, plant, plant_info, supabase_client):
    # ★★★ ここから修正 ★★★
    if plant_info is None:
        # もしplant_infoがNone（データベースに情報がない）なら、エラーメッセージを返す
        return TextMessage(text=f"申し訳ありません、「{plant.get('plant_name', '不明な作物')}」の栽培データが見つかりませんでした。お手数ですが、一度削除して再登録をお試しください。")
    # ★★★ 修正ここまで ★★★

    user_res = supabase_client.table('users').select('latitude, longitude').eq('id', user_id).single().execute()
    user_data = user_res.data or {}
    lat = user_data.get('latitude', 35.66)
    lon = user_data.get('longitude', 139.65)

    start_date = datetime.datetime.strptime(plant['start_date'], '%Y-%m-%d').date()
    today = datetime.date.today()

    weather_data = get_weather_data(lat, lon, start_date, today)
    gdd = calculate_gdd(weather_data, plant_info['base_temp']) if weather_data else 0

    next_event = next((ev for ev in plant_info.get('events', []) if gdd < ev['gdd']), None)
    
    header_contents = [FlexText(text=plant['plant_name'], weight='bold', size='xl', margin='md')]
    basic_info_contents = [
        FlexBox(layout='baseline', spacing='sm', contents=[FlexText(text='栽培日数', color='#aaaaaa', size='sm', flex=3), FlexText(text=f"{(today - start_date).days + 1}日目", wrap=True, color='#666666', size='sm', flex=5)]),
        FlexBox(layout='baseline', spacing='sm', contents=[FlexText(text='積算温度', color='#aaaaaa', size='sm', flex=3), FlexText(text=f"{gdd:.1f}℃・日", wrap=True, color='#666666', size='sm', flex=5)])
    ]

    care_info_contents = [
        FlexSeparator(margin='xl'),
        FlexText(text="お手入れの目安", weight='bold', size='md', margin='lg'),
        FlexBox(layout='vertical', margin='md', spacing='sm', contents=[
            FlexBox(layout='baseline', spacing='sm', contents=[
                FlexText(text='💧水やり', color='#aaaaaa', size='sm', flex=3),
                FlexText(text=plant_info.get('watering_freq', '---'), wrap=True, color='#666666', size='sm', flex=5)
            ]),
            FlexBox(layout='baseline', spacing='sm', contents=[
                FlexText(text='🌱追肥', color='#aaaaaa', size='sm', flex=3),
                FlexText(text=plant_info.get('fertilizer_freq', '---'), wrap=True, color='#666666', size='sm', flex=5)
            ])
        ])
    ]

    progress_contents = []
    if next_event:
        progress = (gdd / next_event['gdd']) * 100 if next_event['gdd'] > 0 else 100
        days_to_event = (next_event['gdd'] - gdd) / plant_info.get('avg_gdd_per_day', 15) if plant_info.get('avg_gdd_per_day', 15) > 0 else 0
        progress_contents.extend([
            FlexSeparator(margin='xl'),
            FlexText(text=f"次の作業：{next_event['advice']}", weight='bold', size='md', margin='lg', wrap=True),
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
            FlexText(text="Q：どんなアドバイス？", weight='bold', size='sm', color='#555555'),
            FlexText(text=advice_what, wrap=True, size='sm'),
            FlexSeparator(margin='md'),
            FlexText(text="Q：どうすればいい？", weight='bold', size='sm', color='#555555', margin='sm'),
            FlexText(text=advice_how, wrap=True, size='sm'),
        ])
    ])
    advice_contents.extend([FlexSeparator(margin='xl'), advice_box])
    
    recommendation_contents = []
    if next_event and next_event.get('product_name'):
        recommendation_contents.extend([
            FlexSeparator(margin='lg'),
            FlexBox(layout='vertical', margin='md', contents=[
                FlexText(text=next_event.get('recommendation_reason', ''), size='xs', wrap=True, margin='md', color='#666666'),
                FlexButton(
                    style='link',
                    height='sm',
                    action=URIAction(
                        label="おすすめの商品を見る",
                        uri=next_event['affiliate_link']
                    ),
                    margin='sm',
                    color='#1E88E5'
                )
            ])
        ])

    bubble = FlexBubble(
        hero=FlexImage(url=plant_info.get('image_url', 'https://example.com/placeholder.jpg'), size='full', aspect_ratio='20:13', aspect_mode='cover'),
        body=FlexBox(layout='vertical', spacing='lg', contents=[
            *header_contents,
            FlexBox(layout='vertical', margin='lg', spacing='md', contents=basic_info_contents),
            *care_info_contents,
            *progress_contents,
            *advice_contents,
            *recommendation_contents
        ]),
        footer=FlexBox(layout='vertical', spacing='md', contents=[
            FlexSeparator(),
            FlexButton(style='primary', height='sm', action=PostbackAction(label="💧 水やりを記録する", data=f"action=log_watering&plant_id={plant['id']}"), color="#42a5f5"),
            FlexButton(style='primary', height='sm', action=PostbackAction(label="🌱 追肥を記録する", data=f"action=log_fertilizer&plant_id={plant['id']}"), color="#66bb6a")
        ]))
    return FlexMessage(alt_text=f"{plant['plant_name']}の状態", contents=bubble)


def create_plant_list_carousel(plants, plant_database):
    bubbles = []
    for plant in plants:
        plant_info = plant_database.get(plant['plant_name'], {})
        bubble = FlexBubble(
            hero=FlexImage(
                url=plant_info.get('image_url', 'https://example.com/placeholder.jpg'),
                size='full', aspect_ratio='4:3', aspect_mode='cover',
                action=PostbackAction(label='status', data=f"action=show_status&plant_id={plant['id']}")
            ),
            body=FlexBox(layout='vertical', spacing='md', contents=[
                FlexText(text=plant['plant_name'], weight='bold', size='xl'),
                FlexText(text=f"栽培開始: {plant['start_date']}", size='sm', color='#AAAAAA')
            ]),
            footer=FlexBox(layout='vertical', spacing='sm', contents=[
                FlexButton(style='primary', color='#00B900', action=PostbackAction(label='📈 状態を見る', data=f"action=show_status&plant_id={plant['id']}")),
                FlexButton(style='secondary', action=PostbackAction(label='📝 お手入れ履歴', data=f"action=show_log&plant_id={plant['id']}&plant_name={plant['plant_name']}&offset=0")),
                FlexButton(style='secondary', action=PostbackAction(label='🗑️ 削除', data=f"action=confirm_delete&plant_id={plant['id']}&plant_name={plant['plant_name']}"))
            ])
        )
        bubbles.append(bubble)
    return FlexMessage(alt_text='登録植物一覧', contents=FlexCarousel(contents=bubbles))

def create_date_selection_message(plant_name):
    return TextMessage(
        text=f"「{plant_name}」はいつ植えましたか？\n（過去の日付も選択できます）",
        quick_reply=QuickReply(items=[
            QuickReplyItem(action=PostbackAction(label="今日", data=f"action=set_start_date&plant_name={plant_name}&date=today")),
            QuickReplyItem(action=PostbackAction(label="昨日", data=f"action=set_start_date&plant_name={plant_name}&date=yesterday")),
            QuickReplyItem(action=DatetimePickerAction(label="日付を選択", data=f"action=set_start_date&plant_name={plant_name}", mode="date"))
        ])
    )

def create_initial_products_message(plant_name, products):
    bubbles = []
    for product in products:
        bubble = FlexBubble(
            body=FlexBox(layout='vertical', spacing='md', contents=[
                FlexText(text=f"「{plant_name}」栽培の準備", weight='bold', size='lg', wrap=True),
                FlexText(text="まずはこちらから揃えませんか？", size='sm', color='#666666', wrap=True),
                FlexSeparator(margin='lg'),
                FlexText(text=product['name'], weight='bold', margin='md'),
                FlexText(text=product['reason'], size='xs', wrap=True, color='#AAAAAA'),
                FlexButton(style='link', action=URIAction(label="商品を見る (Amazon)", uri=product['link']), margin='md')
            ])
        )
        bubbles.append(bubble)

    if not bubbles:
        return None

    return FlexMessage(alt_text=f"{plant_name}のおすすめ商品", contents=FlexCarousel(contents=bubbles))