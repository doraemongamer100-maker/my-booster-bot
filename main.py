import os
import requests
from flask import Flask, request

TOKEN = "8874819641:AAGy9IGxvZqXPjNuhUEHDXH5N8juCTcuE2s"
URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

user_tasks = {}

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    res = requests.post(URL + "sendMessage", json=payload)
    return res.json()

def edit_message(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(URL + "editMessageText", json=payload)

def get_tasks_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "1. Grow", "callback_data": "select_task_grow"}]
        ]
    }

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "Bot is active and running successfully!", 200
        
    data = request.get_json()
    if not data:
        return "OK", 200
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            welcome_text = "🚀 *Welcome*\n\n1️⃣ Select Task\n2️⃣ Send Tracking URL\n3️⃣ Wait for confirmation\n\n👉 *Choose task below*"
            send_message(chat_id, welcome_text, reply_markup=get_tasks_keyboard())
            
        elif text.startswith("http://") or text.startswith("https://"):
            selected_task = user_tasks.get(chat_id, "Grow")
            
            # Accurate Click ID extraction specifically targeting click_id=
            click_id = "Not Found"
            if "click_id=" in text:
                try:
                    parts = text.split("click_id=")[1]
                    click_id = parts.split("&")[0]
                except:
                    pass
            elif "clickid=" in text:
                try:
                    parts = text.split("clickid=")[1]
                    click_id = parts.split("&")[0]
                except:
                    pass

            init_msg = send_message(chat_id, f"🚀 *Processing Task...*\n\n🎯 Task: *{selected_task}*\n🆔 Click ID: `{click_id}`\n\n⏳ Hitting Postback...")
            
            # Postback Hit with exact click_id value
            postback_url = f"https://pb.iskyworker.com/pb/lsr?transaction_id={click_id}"
            pb_status = "Failed"
            pb_response_text = ""
            
            try:
                pb_res = requests.get(postback_url, timeout=10)
                pb_response_text = pb_res.text.strip()
                pb_status = f"Status {pb_res.status_code}"
            except Exception as e:
                pb_response_text = str(e)
                pb_status = "Error"

            final_text = (
                f"✅ *Successfully Your Task Completed*\n\n"
                f"🎯 Task: *{selected_task}*\n"
                f"🆔 Click ID: `{click_id}`\n"
                f"🟢 Postback Status: *{pb_status}*\n"
                f"📄 *PB Response:* `{pb_response_text}`"
            )
            
            if init_msg and "result" in init_msg:
                msg_id = init_msg["result"]["message_id"]
                edit_message(chat_id, msg_id, final_text)
            else:
                send_message(chat_id, final_text)
        else:
            send_message(chat_id, "❌ *Invalid URL*\n\nPlease send a valid tracking URL.")
            
    elif "callback_query" in data:
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        message_id = cq["message"]["message_id"]
        query_id = cq["id"]
        data_str = cq["data"]
        
        requests.post(URL + "answerCallbackQuery", json={"callback_query_id": query_id})
        
        if data_str == "start_menu":
            welcome_text = "🚀 *Select Task*\n\n👉 *Choose task below*"
            edit_message(chat_id, message_id, welcome_text, reply_markup=get_tasks_keyboard())
            
        elif data_str == "select_task_grow":
            selected_task = "Grow"
            user_tasks[chat_id] = selected_task
            
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:*\n`http://click.hopemobi.net/click?id=...&click_id=YOUR_ID`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)
            
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
