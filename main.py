import os
import threading
import random
import requests
from urllib.parse import urlparse, parse_qs, unquote
from flask import Flask, request, jsonify

TOKEN = "8874819641:AAEh685J2apsLj9cgIoeGXKt0NFcgZURl20"
URL = f"https://api.telegram.org/bot{TOKEN}/"

# Force Channel Join Settings
CHANNEL_USERNAME = "@Dragon_Scripterr"
CHANNEL_URL = "https://t.me/Dragon_Scripterr"

app = Flask(__name__)
user_tasks = {}

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        res = requests.post(URL + "sendMessage", json=payload, timeout=10)
        return res.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def edit_message(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(URL + "editMessageText", json=payload, timeout=10)
    except Exception as e:
        print(f"Error editing message: {e}")

def check_user_subscription(chat_id):
    try:
        res = requests.get(f"{URL}getChatMember", params={"chat_id": CHANNEL_USERNAME, "user_id": chat_id}, timeout=10)
        data = res.json()
        if data.get("ok"):
            status = data["result"].get("status")
            if status in ["member", "administrator", "creator"]:
                return True
    except Exception:
        pass
    return False

def get_join_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "📢 Join Channel", "url": CHANNEL_URL}],
            [{"text": "🔄 Check Membership", "callback_data": "check_subscription"}]
        ]
    }

def get_tasks_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "1. Grow", "callback_data": "select_task_grow"}],
            [{"text": "2. Solitaire", "callback_data": "select_task_solitaire"}],
            [{"text": "3. Policy Bazaar", "callback_data": "select_task_policy"}],
            [{"text": "4. Policy Bazaar 2", "callback_data": "select_task_policy2"}],
            [{"text": "5. Condivio", "callback_data": "select_task_condivio"}],
            [{"text": "6. Uni", "callback_data": "select_task_uni"}],
            [{"text": "7. Amazon", "callback_data": "select_task_amazon"}],
            [{"text": "8. Vivago", "callback_data": "select_task_vivago"}],
            [{"text": "9. Rapid Rupee", "callback_data": "select_task_rapid"}],
            [{"text": "10. Novio", "callback_data": "select_task_novio"}],
            [{"text": "11. Aspro Bonds", "callback_data": "select_task_aspro"}],
            [{"text": "12. Truemads", "callback_data": "select_task_truemads"}],
            [{"text": "13. Incred", "callback_data": "select_task_incred"}],
            [{"text": "14. Candy Crush", "callback_data": "select_task_candy"}],
            [{"text": "15. Jar", "callback_data": "select_task_jar"}],
            [{"text": "16. Rapid Rupee (New)", "callback_data": "select_task_rapid_new"}],
            [{"text": "17. Xm360", "callback_data": "select_task_xm360"}],
            [{"text": "18. Bharat Pe", "callback_data": "select_task_bharatpe"}],
            [{"text": "19. FirstCry", "callback_data": "select_task_firstcry"}],
            [{"text": "20. Xm 14rs", "callback_data": "select_task_xm_14rs"}]
        ]
    }

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "Bot is active and running successfully!", 200
        
    try:
        data = request.get_json(silent=True)
        if not data:
            return "OK", 200
        
        print(f"Received Update: {data}")
        
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            
            if not check_user_subscription(chat_id):
                send_message(chat_id, "⚠️ *Access Denied!*\n\nYou must join our channel first to use this bot.", reply_markup=get_join_keyboard())
                return "OK", 200
            
            if text == "/start":
                welcome_text = "🚀 *Welcome*\n\n1️⃣ Select Task\n2️⃣ Send Tracking URL / Click ID\n3️⃣ Wait for confirmation\n\n👉 *Choose task below*"
                send_message(chat_id, welcome_text, reply_markup=get_tasks_keyboard())
                
            else:
                selected_task = user_tasks.get(chat_id, "Grow")
                
                click_id = "Not Found"
                postback_url = ""
                headers = {}

                client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                if client_ip:
                    headers['X-Forwarded-For'] = client_ip
                    headers['X-Real-IP'] = client_ip

                if selected_task == "Xm 14rs":
                    if text.startswith("http://") or text.startswith("https://"):
                        if "transaction_id=" in text:
                            try: click_id = text.split("transaction_id=")[1].split("&")[0]
                            except: click_id = text.strip()
                        elif "clickid=" in text:
                            try: click_id = text.split("clickid=")[1].split("&")[0]
                            except: click_id = text.strip()
                        else:
                            click_id = text.strip()
                    else:
                        click_id = text.strip()
                    postback_url = f"http://tracking.gridadss.com/conv?yeahmobi_install&event=install&transaction_id={click_id}"

                elif selected_task == "Grow":
                    if "click_id=" in text:
                        try: click_id = text.split("click_id=")[1].split("&")[0]
                        except: pass
                    elif "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    postback_url = f"http://pb.iskyworker.com/pb/lsr?transaction_id={click_id}"

                elif selected_task == "Policy Bazaar 2":
                    if "aff_sub=" in text:
                        try: click_id = text.split("aff_sub=")[1].split("&")[0]
                        except: pass
                    elif "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    postback_url = f"http://pb.iskyworker.com/pb/lsr?transaction_id={click_id}"

                elif selected_task == "Jar":
                    if "sub1=" in text:
                        try: click_id = text.split("sub1=")[1].split("&")[0]
                        except: pass
                    elif "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    postback_url = f"https://smartconnect.fusetracking.com/pb?tid={click_id}"

                elif selected_task == "Rapid Rupee (New)":
                    if "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    postback_url = f"http://fpb.bigflymobi.com/v1/api/event?event_name=yogqjh&adv_click_id={click_id}"
                    random_ip = f"{random.randint(103, 199)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
                    headers['X-Forwarded-For'] = random_ip
                    headers['X-Real-IP'] = random_ip

                elif selected_task == "Xm360":
                    if "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    elif "click_id=" in text:
                        try: click_id = text.split("click_id=")[1].split("&")[0]
                        except: pass
                    postback_url = f"https://post.clickscot.com/acquisition?security_token=36399a458c8980278778&click_id={click_id}"

                elif selected_task == "Bharat Pe":
                    if "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    elif "click_id=" in text:
                        try: click_id = text.split("click_id=")[1].split("&")[0]
                        except: pass
                    postback_url = f"https://offers-mobtions.affise.com/postback?goal=first_txn_success&clickid={click_id}"

                elif selected_task == "FirstCry":
                    if "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    elif "aff_sub1=" in text:
                        try: click_id = text.split("aff_sub1=")[1].split("&")[0]
                        except: pass
                    postback_url = f"http://cpipb.melodong.com?adv=1000444&clickid={click_id}"

                elif selected_task in ["Solitaire", "Policy Bazaar", "Amazon", "Rapid Rupee", "Novio", "Candy Crush"]:
                    if "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    elif "label=" in text:
                        try: click_id = text.split("label=")[1].split("&")[0]
                        except: pass
                    elif "p1=" in text:
                        try: click_id = text.split("p1=")[1].split("&")[0]
                        except: pass
                    postback_url = f"http://postback.milengine.com/?adv=1000444&clickid={click_id}"

                elif selected_task in ["Condivio", "Uni", "Aspro Bonds", "Truemads", "Incred"]:
                    if "clickid=" in text:
                        try: click_id = text.split("clickid=")[1].split("&")[0]
                        except: pass
                    elif "click_id=" in text:
                        try: click_id = text.split("click_id=")[1].split("&")[0]
                        except: pass
                    elif "p1=" in text:
                        try: click_id = text.split("p1=")[1].split("&")[0]
                        except: pass
                    postback_url = f"http://pb.imxbidding.net/pb/lsr?transaction_id={click_id}"

                pb_status = "Failed"
                pb_response_text = ""
                task_success = False
                
                try:
                    pb_res = requests.get(postback_url, headers=headers, timeout=10)
                    raw_response = pb_res.text.strip()
                    pb_status = f"Status {pb_res.status_code}"
                    
                    if "http://" in raw_response or "https://" in raw_response:
                        pb_response_text = "Success (URL hidden)"
                    else:
                        pb_response_text = raw_response

                    if pb_res.status_code == 200:
                        task_success = True
                except Exception as e:
                    pb_response_text = "Connection Error"
                    pb_status = "Connection Error"

                if task_success:
                    final_text = (
                        f"✅ *Task Bypass Successful*\n\n"
                        f"🎯 Task: *{selected_task}*\n"
                        f"🆔 Click ID: `{click_id}`\n"
                        f"🟢 Postback Status: *{pb_status}*\n"
                        f"📄 *PB Response:* `{pb_response_text}`"
                    )
                else:
                    final_text = (
                        f"❌ *Failed*\n\n"
                        f"🎯 Task: *{selected_task}*\n"
                        f"🆔 Click ID: `{click_id}`\n"
                        f"🔴 Postback Status: *{pb_status}*\n"
                        f"📄 *Error Details:* `{pb_response_text}`"
                    )
                
                send_message(chat_id, final_text)
                
        elif "callback_query" in data:
            cq = data["callback_query"]
            chat_id = cq["message"]["chat"]["id"]
            message_id = cq["message"]["message_id"]
            query_id = cq["id"]
            data_str = cq["data"]
            
            print(f"Callback Clicked: {data_str}")
            
            try:
                requests.post(URL + "answerCallbackQuery", json={"callback_query_id": query_id}, timeout=5)
            except:
                pass
            
            if data_str == "check_subscription":
                if check_user_subscription(chat_id):
                    welcome_text = "🚀 *Welcome*\n\n1️⃣ Select Task\n2️⃣ Send Tracking URL / Click ID\n3️⃣ Wait for confirmation\n\n👉 *Choose task below*"
                    edit_message(chat_id, message_id, welcome_text, reply_markup=get_tasks_keyboard())
                else:
                    try:
                        requests.post(URL + "answerCallbackQuery", json={
                            "callback_query_id": query_id,
                            "text": "❌ You haven't joined the channel yet!",
                            "show_alert": True
                        }, timeout=5)
                    except:
                        pass
                return "OK", 200

            if not check_user_subscription(chat_id):
                edit_message(chat_id, message_id, "⚠️ *Access Denied!*\n\nYou must join our channel first to use this bot.", reply_markup=get_join_keyboard())
                return "OK", 200

            task_mapping = {
                "select_task_grow": "Grow",
                "select_task_solitaire": "Solitaire",
                "select_task_policy": "Policy Bazaar",
                "select_task_policy2": "Policy Bazaar 2",
                "select_task_jar": "Jar",
                "select_task_rapid_my": "Rapid Rupee",
                "select_task_rapid_new": "Rapid Rupee (New)",
                "select_task_xm360": "Xm360",
                "select_task_bharatpe": "Bharat Pe",
                "select_task_firstcry": "FirstCry",
                "select_task_xm_14rs": "Xm 14rs",
                "select_task_condivio": "Condivio",
                "select_task_uni": "Uni",
                "select_task_amazon": "Amazon",
                "select_task_vivago": "Vivago",
                "select_task_rapid": "Rapid Rupee",
                "select_task_novio": "Novio",
                "select_task_aspro": "Aspro Bonds",
                "select_task_truemads": "Truemads",
                "select_task_incred": "Incred",
                "select_task_candy": "Candy Crush"
            }

            if data_str == "start_menu":
                welcome_text = "🚀 *Select Task*\n\n👉 *Choose task below*"
                edit_message(chat_id, message_id, welcome_text, reply_markup=get_tasks_keyboard())
            elif data_str in task_mapping:
                selected_task = task_mapping[data_str]
                user_tasks[chat_id] = selected_task
                text = f"✅ *Task Selected*\n🎯 *{selected_task}*\n\n*Send your Click ID or tracking URL now*"
                keyboard = {"inline_keyboard": [[{"text": "🔄 Change Task", "callback_data": "start_menu"}]]}
                edit_message(chat_id, message_id, text, reply_markup=keyboard)
                
    except Exception as e:
        print(f"Webhook error: {e}")
        
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
                
