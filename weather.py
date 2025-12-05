import requests
import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv("OWM_API_KEY")
print("DEBUG: API_KEY =", API_KEY)

def get_weather_condition(city="Kyoto"):
    # --- 修正: timeout を短めに設定し、例外処理を追加 ---
    try:
        if not API_KEY:
            print("ERROR: API_KEY is None. Check your .env file.")
            return "error"

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("DEBUG: OWM response =", data)  # ← 追加

        # --- 追加: weather 配列が空の場合の安全対策 ---
        if "weather" not in data or len(data["weather"]) == 0:
            return "unknown"
        
        # --- 修正: description をそのまま返す ---
        description = data["weather"][0]["description"]
        return description
        
    
    except Exception as e:
        # --- 追加: エラー時にログを出して fallback 値を返す ---
        print("ERROR in get_weather_condition:", repr(e))
        return "error"