# flex_messages.py
from linebot.v3.messaging import (
    FlexMessage, FlexBubble, FlexCarousel, FlexBox, FlexText, FlexImage, FlexButton, FlexSeparator,
    PostbackAction, MessageAction, DatetimePickerAction, URIAction, TextMessage, QuickReply, QuickReplyItem
)
import datetime
import requests

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

# ... その他の関数は変更なし ...
def create_status_flex_message(user_id, plant, plant_info, supabase_client):
    # ... (変更なし) ...
    pass

def create_plant_list_carousel(plants, plant_database):
    # ... (変更なし) ...
    pass

def create_date_selection_message(plant_name):
    # ... (変更なし) ...
    pass

def create_initial_products_message(plant_name, products):
    # ... (変更なし) ...
    pass