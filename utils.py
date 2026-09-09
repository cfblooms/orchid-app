import datetime
import os
import pandas as pd
import requests

# ⚠️ 請換成您自己的 Google Apps Script 網布網址
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzySOZuB7x9_MvFo6AoX-6cFb17q-ZS4waZHaRo-xu_rnX7MNxE6UPZuVbwqVTHU6nX/exec"

if not os.path.exists("photos"):
    os.makedirs("photos")


def get_data(sheet_name):
    if not WEB_APP_URL or "你的網址" in WEB_APP_URL:
        return pd.DataFrame()
    try:
        response = requests.get(f"{WEB_APP_URL}?sheet={sheet_name}")
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def append_data(sheet_name, row_data):
    try:
        payload = {"sheet": sheet_name, "action": "append", "data": row_data}
        response = requests.post(WEB_APP_URL, json=payload)
        return response.json().get("status") == "success"
    except Exception:
        return False


def update_data(sheet_name, record_id, row_data):
    try:
        payload = {
            "sheet": sheet_name,
            "action": "update",
            "id": record_id,
            "data": row_data,
        }
        response = requests.post(WEB_APP_URL, json=payload)
        return response.json().get("status") == "success"
    except Exception:
        return False


def delete_data(sheet_name, record_id):
    try:
        payload = {"sheet": sheet_name, "action": "delete", "id": record_id}
        response = requests.post(WEB_APP_URL, json=payload)
        return response.json().get("status") == "success"
    except Exception:
        return False


def get_next_id(prefix, sheet_name):
    today_str = datetime.datetime.now().strftime("%m%d")
    df = get_data(sheet_name)
    if df.empty or len(df.columns) == 0:
        return f"{prefix}{today_str}01"
    try:
        id_col = df.columns[0]
        base_pattern = f"{prefix}{today_str}"
        matching = df[df[id_col].astype(str).str.startswith(base_pattern, na=False)]
        return f"{prefix}{today_str}{len(matching) + 1:02d}"
    except Exception:
        return f"{prefix}{today_str}01"