import telebot
import json
import os
from datetime import datetime, time, timedelta
import time as t

# ================= CONFIG =================
TOKEN = os.getenv("8228216368:AAGbqcZrYWjnbpZ5_HoAMdp7MH_ud5o-Niw")
USER_FILE = "users.json"

# Daily reset
RESET_HOUR = 14
RESET_MINUTE = 30

# Event end
EVENT_END = datetime.now() + timedelta(days=5, hours=23, minutes=59, seconds=59)

bot = telebot.TeleBot(TOKEN)

# ================= LOAD USERS =================
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        try:
            users = json.load(f)
        except:
            users = {}
else:
    users = {}

# ================= FUNCTIONS =================
def get_reset_datetime(now=None):
    if not now:
        now = datetime.now()
    reset = datetime.combine(now.date(), time(RESET_HOUR, RESET_MINUTE))
    if now < reset:
        reset -= timedelta(days=1)
    return reset

def can_claim(user_id):
    user_key = str(user_id)
    now = datetime.now()
    reset_time = get_reset_datetime(now)

    if user_key not in users:
        return True

    last_claim = datetime.fromisoformat(users[user_key])
    return last_claim < reset_time

def next_claim_remaining():
    now = datetime.now()
    reset = datetime.combine(now.date(), time(RESET_HOUR, RESET_MINUTE))
    if now >= reset:
        reset += timedelta(days=1)
    return reset - now

# ================= BOT HANDLER =================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_key = str(user_id)
    now = datetime.now()

    # Event end check
    if now >= EVENT_END:
        bot.send_message(
            user_id,
            f"⏰ Event has ended!\nEvent end time: {EVENT_END}\n(Local Time: {datetime.now()})"
        )
        return

    # Daily claim check
    if can_claim(user_id):

        text = (
            "📢 Mobile Legends Event\n\n"
            "✅ သင့် link:\n"
            "https://docs.google.com/forms/d/e/1FAIpQLSfjOL5F-U8_3rcZqAln2OVcvQlTiYx8WQNLIZHgwYZxC5_qoQ/viewform\n"
            f"⏰ Event end time: {EVENT_END}\n"
            f"🕒 Local Time: {datetime.now()}"
        )

        try:
            bot.send_message(user_id, text)

            users[user_key] = now.isoformat()
            with open(USER_FILE, "w") as f:
                json.dump(users, f)

        except Exception as e:
            bot.send_message(
                user_id,
                f"⚠️ Internet ပြဿနာရှိနေပါတယ်\n(Local Time: {datetime.now()})"
            )

    else:
        remaining = next_claim_remaining()
        h, remainder = divmod(remaining.seconds, 3600)
        m, s = divmod(remainder, 60)

        bot.send_message(
            user_id,
            f"⏰ သင်သည် ယနေ့လက်ခံပြီးသားဖြစ်ပါသည်\n\n"
            f"နောက်တစ်ကြိမ် ရယူနိုင်မည့်အချိန်\n"
            f"{h} နာရီ {m} မိနစ် {s} စက္ကန့်"
        )

# ================= POLLING =================
print("Bot is running...")

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Internet error:", e)
        t.sleep(5)
