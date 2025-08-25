# flex_messages.py
from linebot.v3.messaging import (
    FlexMessage, FlexBubble, FlexCarousel, FlexBox, FlexText, FlexImage, FlexButton, FlexSeparator,
    PostbackAction, MessageAction, DatetimePickerAction
)

# create_status_flex_message関数は長いため、ここでは省略。内容は元のmain.pyと同じ。
# ただし、PLANT_DATABASEを引数で受け取るように変更する。
def create_status_flex_message(user_id, plant, plant_info, gdd, supabase_client):
    # ... (元のコードをここに移植) ...
    pass

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
        text=f"「{plant_name}」をいつ植えましたか？",
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