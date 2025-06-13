import requests
import json

# Open-MeteoのAPIエンドポイントURL
# 東京の緯度(latitude=35.66)と経度(longitude=139.65)を指定
# 今日の最高気温(temperature_2m_max)と最低気温(temperature_2m_min)を要求
url = "https://api.open-meteo.com/v1/forecast?latitude=35.66&longitude=139.65&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo"

try:
    # APIにリクエストを送信して、データを取得する
    response = requests.get(url)
    response.raise_for_status()  # エラーがあればここで例外を発生させる

    # 取得したJSONデータをPythonの辞書に変換する
    data = response.json()

    # 必要なデータを抽出して表示
    today = data['daily']['time'][0]
    max_temp = data['daily']['temperature_2m_max'][0]
    min_temp = data['daily']['temperature_2m_min'][0]

    print("【気象データ受信成功！】")
    print(f"日付: {today}")
    print(f"最高気温: {max_temp}℃")
    print(f"最低気温: {min_temp}℃")

except requests.exceptions.RequestException as e:
    print(f"エラー：APIへのリクエストに失敗しました。 {e}")
except json.JSONDecodeError:
    print("エラー：受信したデータをJSONとして解析できませんでした。")
except KeyError:
    print("エラー：受信したデータに必要なキーが見つかりませんでした。")