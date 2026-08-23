import os
import time
import requests
from flask import Flask, request

TOKEN = "8874819641:AAGy9IGxvZqXPjNuhUEHDXH5N8juCTcuE2s"
URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(URL + "sendMessage", json=payload)

def get_tasks_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "1. Elo Elo", "callback_data": "select_task_0"}],
            [{"text": "2. Jari Jar", "callback_data": "select_task_1"}],
            [{"text": "3. Super Money 💰", "callback_data": "select_task_2"}],
            [{"text": "4. Curie Digi", "callback_data": "select_task_3"}],
            [{"text": "35. Vivago", "callback_data": "select_task_4"}],
            [{"text": "36. Grow Rvr", "callback_data": "select_task_5"}]
        ]
    }

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            welcome_text = "🚀 *Welcome*\n\n1️⃣ Select Task\n2️⃣ Send Tracking URL\n3️⃣ Wait for confirmation\n\n👉 *Choose task below*"
            send_message(chat_id, welcome_text, reply_markup=get_tasks_keyboard())
        elif text.startswith("http://") or text.startswith("https://"):
            click_id = "6a8860ce7789396658953bb3"
            steps_output = "\n".join([f"{s}. Step {s} ✅" for s in range(1, 11)])
            final_text = f"🆔 `{click_id}`    100%\n\n🟢 (10/10)\n\n🎯 Step Completed\n🟢 SUCCESS (200)\n\n*Steps:*\n{steps_output}"
            send_message(chat_id, final_text)
        else:
            send_message(chat_id, "❌ *Invalid URL*\n\nSend /start and select task")
            
    elif "callback_query" in data:
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        query_id = cq["id"]
        requests.post(URL + "answerCallbackQuery", json={"callback_query_id": query_id})
        
        text = "✅ *Task Selected*\n🎯 Task\n\n*Send your tracking URL*\n\n📌 *Example:*\n`https://app.adjust.com...`"
        keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
        requests.post(URL + "editMessageText", json={
            "chat_id": chat_id,
            "message_id": cq["message"]["message_id"],
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": keyboard
        })
        
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
