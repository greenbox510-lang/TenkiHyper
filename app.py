from dotenv import load_dotenv
import os
from flask import Flask, jsonify, request, Response, render_template, url_for
import json
import random
import sys

# weather.py の関数をインポート
from weather import get_weather_condition


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
print("DEBUG: dotenv_path =", dotenv_path)  # 確認用
load_dotenv(dotenv_path=dotenv_path)


# .env を読み込む
load_dotenv()

# 環境変数からキーを取得
API_KEY = os.getenv("OWM_API_KEY")

app = Flask(__name__)
@app.route("/")

def index():
    
    return "OK"

    print("DEBUG img_filename:", img_filename)

    return render_template("index.html",
                           weather=condition,
                           character_image=img_filename)
app.config["JSON_AS_ASCII"] = False

def normalize_condition(raw_condition: str) -> str:
    """
    受け取った天気表記を内部基準に統一する。
    内部基準: 「晴天」「曇り」「雨」「雪」
    未知は曇り扱い（デフォルト）。
    """
    if not isinstance(raw_condition, str):
        return "曇り"
    s = raw_condition.strip()
    mapping = {
        "晴れ": "晴天",
        "快晴": "晴天",
        "Clear": "晴天",
        "晴天": "晴天",
        "曇天": "曇り",
        "Clouds": "曇り",
        "曇り": "曇り",
        "Rain": "雨",
        "雨": "雨",
        "Snow": "雪",
        "雪": "雪",
    }
    # conditionが未定義ならデフォルト画像
    return mapping.get(s, "曇り")

# 追加①: 天気ごとのキャラ画像切替関数
# -------------------------------
def get_character_image(condition):
    mapping = {
        "晴天": "sunny.png",
        "雨": "rain.png",
        "雪": "snow.png"
    }
    # conditionが未定義ならデフォルト画像
    return mapping.get(condition, "character.png")

def get_character_image_filename(condition: str) -> str:
    mapping = {
        "晴天": "sunny.png",
        "雨": "rain.png",
        "雪": "snow.png",
        # 曇りはデフォルト画像に落とす
    }
    return mapping.get(condition, "character.png")

# ここに weather.py を組み込む
@app.route("/api/weather")
def weather():
    # --- 追加: 例外処理と状況ログを追加 ---
    try:
        # 注記: get_weather_condition のシグネチャが「都市名のみ」の想定なので "Kyoto" を渡す
        # もし APIキーが必要なら weather.py 側で環境変数から読む設計にしている前提
        condition = get_weather_condition("Kyoto")
        return Response(
            json.dumps({"weather": condition}, ensure_ascii=False),
            mimetype="application/json")
            

    except Exception as e:
        # --- 追加: エラー時にもJSONを返して原因を把握できるようにする ---
        print("ERROR: /api/weather failed:", repr(e))
        return Response(
             json.dumps({"error": "failed to get weather", "detail": str(e)}, ensure_ascii=False),
             mimetype="application/json")
    
@app.route("/api/quiz")
def quiz():
    try:
        
        raw = get_weather_condition("Kyoto")
        condition = normalize_condition(raw)  # ← 修正: 正規化を適用
        img_filename = get_character_image_filename(condition)

        print("DEBUG RESPONSE:", {
            "weather": condition,
            "character_image": img_filename
        })

        # -------------------------------
        # 追加③: 画像URLをサーバ側で組み立てて返す
        # -------------------------------
        img_url = url_for('static', filename=f'images/{img_filename}', _external=False)

        questions = [
            {
                "question": "平安京遷都の日の天気は？",
                "choices": ["快晴", "雨天", "曇天"],
                "answer": "快晴"
            },
            {
                "question": "京都で最古の公式気象観測が始まったのはいつ？",
                "choices": ["1880年", "1600年", "1945年"],
                "answer": "1880年"
            }
        ]

# ランダムに1問選ぶ
        q = random.choice(questions)

        return Response(
            json.dumps({
                "weather": condition,
                "character_image": img_filename,
                "quiz": {
                    "question": q["question"],
                    "options": q["choices"],
                    "answer": q["answer"]
                }
            }, ensure_ascii=False),
            mimetype="application/json"
        )
    
    

    except Exception as e:
        print("ERROR: /api/quiz failed:", repr(e))
        return Response(
            json.dumps({"error": "failed to generate quiz", "detail": str(e)}, 500,ensure_ascii=False),
                mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
