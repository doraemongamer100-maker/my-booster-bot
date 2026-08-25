import os
import time
import threading
import requests
from urllib.parse import urlparse, parse_qs, unquote
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
            [{"text": "1. Grow", "callback_data": "select_task_grow"}],
            [{"text": "2. Solitaire", "callback_data": "select_task_solitaire"}],
            [{"text": "3. Policy Bazaar", "callback_data": "select_task_policy"}],
            [{"text": "4. Condivio", "callback_data": "select_task_condivio"}],
            [{"text": "5. Uni", "callback_data": "select_task_uni"}],
            [{"text": "6. Amazon", "callback_data": "select_task_amazon"}],
            [{"text": "7. Vivago", "callback_data": "select_task_vivago"}],
            [{"text": "8. Rapid Rupee", "callback_data": "select_task_rapid"}],
            [{"text": "9. Novio", "callback_data": "select_task_novio"}],
            [{"text": "10. Aspro Bonds", "callback_data": "select_task_aspro"}],
            [{"text": "11. Truemads", "callback_data": "select_task_truemads"}],
            [{"text": "12. Incred", "callback_data": "select_task_incred"}],
            [{"text": "13. Candy Crush", "callback_data": "select_task_candy"}]
        ]
    }

def process_vivago_events(chat_id, text):
    try:
        parsed_url = urlparse(text)
        query_params = parse_qs(parsed_url.query)
        
        click_id = "Not Found"
        events = []
        
        for key, values in query_params.items():
            val = values[0]
            if "mobvista_clickid" in val or "clickid" in key.lower():
                if "mobvista_clickid=" in val:
                    sub_params = parse_qs(val.replace('&', ';'))
                    if "mobvista_clickid" in sub_params:
                        click_id = sub_params["mobvista_clickid"][0]
                elif "clickid=" in val:
                    try:
                        click_id = val.split("clickid=")[1].split("&")[0]
                    except:
                        pass
            if key.startswith("event_callback_") or "install_callback" in key:
                decoded_val = unquote(val)
                if "event_name=" in decoded_val:
                    try:
                        e_name = decoded_val.split("event_name=")[1].split("&")[0]
                        if e_name and e_name not in events:
                            events.append(e_name)
                    except:
                        pass
                elif "install_callback" in key and "mobvista_install" in decoded_val:
                    if "install" not in events:
                        events.append("install")
                        
        if click_id == "Not Found":
            if "mobvista_clickid=" in text:
                try:
                    click_id = text.split("mobvista_clickid=")[1].split("&")[0]
                except:
                    pass
            elif "clickid=" in text:
                try:
                    click_id = text.split("clickid=")[1].split("&")[0]
                except:
                    pass

        if not events:
            events = ["install", "sign_up", "iap_purchase", "session"]

        init_msg = send_message(chat_id, f"🚀 *Processing Vivago Task...*\n\n🆔 Click ID: `{click_id}`\n📋 Total Events Found: `{len(events)}`\n⏳ *Sending events with 5s delay each...*")
        
        results_log = []
        success_count = 0
        
        for index, ev in enumerate(events):
            if index > 0:
                if init_msg and "result" in init_msg:
                    msg_id = init_msg["result"]["message_id"]
                    for remaining in range(5, 0, -1):
                        edit_message(chat_id, msg_id, f"🚀 *Processing Vivago Task...*\n\n🆔 Click ID: `{click_id}`\n⏳ *Waiting {remaining}s before next event ({ev})...*")
                        time.sleep(1)
                else:
                    time.sleep(5)
                
            pb_url = f"http://stat.advcorp.net/event?clickid={click_id}&event_name={ev}"
            try:
                res = requests.get(pb_url, timeout=10)
                if res.status_code == 200:
                    success_count += 1
                    results_log.append(f"✅ `{ev}`: Success")
                else:
                    results_log.append(f"❌ `{ev}`: Status {res.status_code}")
            except Exception as e:
                results_log.append(f"❌ `{ev}`: Error")

        logs_str = "\n".join(results_log)
        final_text = (
            f"✅ *Vivago Task Completed*\n\n"
            f"🆔 Click ID: `{click_id}`\n"
            f"📊 Successful Hits: `{success_count}/{len(events)}`\n\n"
            f"📄 *Details:*\n{logs_str}"
        )
        
        if init_msg and "result" in init_msg:
            msg_id = init_msg["result"]["message_id"]
            edit_message(chat_id, msg_id, final_text)
        else:
            send_message(chat_id, final_text)
            
    except Exception as ex:
        send_message(chat_id, f"❌ *Error processing Vivago URL:* `{str(ex)}`")

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
            
            if selected_task == "Vivago":
                threading.Thread(target=process_vivago_events, args=(chat_id, text)).start()
                return "OK", 200

            click_id = "Not Found"
            postback_url = ""

            if selected_task == "Grow":
                if "click_id=" in text:
                    try:
                        click_id = text.split("click_id=")[1].split("&")[0]
                    except:
                        pass
                elif "clickid=" in text:
                    try:
                        click_id = text.split("clickid=")[1].split("&")[0]
                    except:
                        pass
                postback_url = f"http://pb.iskyworker.com/pb/lsr?transaction_id={click_id}"

            elif selected_task in ["Solitaire", "Policy Bazaar", "Amazon", "Rapid Rupee", "Novio", "Candy Crush"]:
                if "clickid=" in text:
                    try:
                        click_id = text.split("clickid=")[1].split("&")[0]
                    except:
                        pass
                elif "label=" in text:
                    try:
                        click_id = text.split("label=")[1].split("&")[0]
                    except:
                        pass
                elif "p1=" in text:
                    try:
                        click_id = text.split("p1=")[1].split("&")[0]
                    except:
                        pass
                postback_url = f"http://postback.milengine.com/?adv=1000444&clickid={click_id}"

            elif selected_task in ["Condivio", "Uni", "Aspro Bonds", "Truemads", "Incred"]:
                if "clickid=" in text:
                    try:
                        click_id = text.split("clickid=")[1].split("&")[0]
                    except:
                        pass
                elif "click_id=" in text:
                    try:
                        click_id = text.split("click_id=")[1].split("&")[0]
                    except:
                        pass
                elif "p1=" in text:
                    try:
                        click_id = text.split("p1=")[1].split("&")[0]
                    except:
                        pass
                postback_url = f"http://pb.imxbidding.net/pb/lsr?transaction_id={click_id}"

            init_msg = send_message(chat_id, f"🚀 *Processing Task...*\n\n🎯 Task: *{selected_task}*\n🆔 Click ID: `{click_id}`\n⏳ *Waiting 5 seconds before hitting postback...*")
            
            # 5 seconds live countdown on bot
            if init_msg and "result" in init_msg:
                msg_id = init_msg["result"]["message_id"]
                for remaining in range(5, 0, -1):
                    edit_message(chat_id, msg_id, f"🚀 *Processing Task...*\n\n🎯 Task: *{selected_task}*\n🆔 Click ID: `{click_id}`\n⏳ *Waiting {remaining} seconds...*")
                    time.sleep(1)
            else:
                time.sleep(5)

            pb_status = "Failed"
            pb_response_text = ""
            task_success = False
            
            try:
                pb_res = requests.get(postback_url, timeout=10)
                pb_response_text = pb_res.text.strip()
                pb_status = f"Status {pb_res.status_code}"
                if pb_res.status_code == 200:
                    task_success = True
            except Exception as e:
                pb_response_text = str(e)
                pb_status = "Connection Error"

            if task_success:
                final_text = (
                    f"✅ *Successfully Your Task Completed*\n\n"
                    f"🎯 Task: *{selected_task}*\n"
                    f"🆔 Click ID: `{click_id}`\n"
                    f"🟢 Postback Status: *{pb_status}*\n"
                    f"📄 *PB Response:* `{pb_response_text}`"
                )
            else:
                final_text = (
                    f"❌ *Task Failed (Postback Error)*\n\n"
                    f"🎯 Task: *{selected_task}*\n"
                    f"🆔 Click ID: `{click_id}`\n"
                    f"🔴 Postback Status: *{pb_status}*\n"
                    f"📄 *Error Details:* `{pb_response_text}`"
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
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `http://click.hopemobi.net/`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)
            
        elif data_str == "select_task_solitaire":
            selected_task = "Solitaire"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://app.adjust.com/`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)
            
        elif data_str == "select_task_policy":
            selected_task = "Policy Bazaar"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://t.clickscot.com/`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)
            
        elif data_str == "select_task_condivio":
            selected_task = "Condivio"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://track.paddlewaver.com/`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_uni":
            selected_task = "Uni"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://track.paddlewaver.com/`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_amazon":
            selected_task = "Amazon"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://t.clickscot.com`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_vivago":
            selected_task = "Vivago"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://app.adjust.com`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_rapid":
            selected_task = "Rapid Rupee"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://t.clickscot.com`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_novio":
            selected_task = "Novio"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://t.clickscot.com`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_aspro":
            selected_task = "Aspro Bonds"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://track.paddlewaver.com`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_truemads":
            selected_task = "Truemads"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://track.paddlewaver.com`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_incred":
            selected_task = "Incred"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://track.paddlewaver.com`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)

        elif data_str == "select_task_candy":
            selected_task = "Candy Crush"
            user_tasks[chat_id] = selected_task
            text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your tracking URL now*\n\n📌 *Example:* `https://app.appsflyer.com`"
            keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
            edit_message(chat_id, message_id, text, reply_markup=keyboard)
            
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
                    
