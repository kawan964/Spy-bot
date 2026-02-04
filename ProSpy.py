import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message

# --- زانیارییە تایبەتەکانی تۆ ---
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"
ADMIN_ID = 7414272224

app = Client(
    "spy_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=enums.ParseMode.MARKDOWN
)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id == ADMIN_ID:
        await message.reply_text(
            "**سڵاو گەورەم، بەخێربێیتەوە!**\n\n"
            "بۆتەکەت ئێستا لەسەر سێرڤەری **Render** بە تەواوی کار دەکات.\n"
            "ئێستا دەتوانیت فەرمانەکان بەکاربهێنیت."
        )
    else:
        await message.reply_text("⚠️ ئەم بۆتە تایبەتە و تەنها ئەدمین دەتوانێت بەکاری بهێنێت.")

@app.on_message(filters.command("help") & filters.user(ADMIN_ID))
async def help_cmd(client, message):
    help_text = (
        "**لیستی فەرمانەکان:**\n\n"
        "1️⃣ `/id` - وەرگرتنی ئایدی چات\n"
        "2️⃣ `/info` - زانیاری دەربارەی بۆت\n"
        "3️⃣ `/broadcast` - ناردنی نامە بۆ هەمووان\n"
        "4️⃣ `/stats` - ئاماری بەکارهێنەران"
    )
    await message.reply_text(help_text)

@app.on_message(filters.all & filters.private)
async def spy_mod(client, message: Message):
    # ئەگەر ئەدمین نەبوو، هەرچی بنێرێت بۆ ئەدمینی دەنێرێتەوە
    if message.from_user.id != ADMIN_ID:
        user_info = f"👤 **نامەی نوێ لە:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
        user_info += f"🆔 **ئایدی:** `{message.from_user.id}`\n\n"
        
        if message.text:
            user_info += f"💬 **ناوەرۆک:**\n{message.text}"
            await client.send_message(ADMIN_ID, user_info)
        else:
            # بۆ ناردنی وێنە یان فایلیش بۆ ئەدمین
            await message.forward(ADMIN_ID)
            await client.send_message(ADMIN_ID, user_info)

print("--- [ System Online - Render Server ] ---")

if __name__ == "__main__":
    app.run()
