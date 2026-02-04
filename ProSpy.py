from pyrogram import Client, filters

# زانیارییەکانی تۆ
API_ID = 38225812
API_HASH = "aff3c308c587f18a5975910fbcf68366"
BOT_TOKEN = "8424748782:AAG0VELUlOfabsayVic2SpUAR-hWsh-nnf0"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("سڵاو گەورەم! بۆتەکەت بە سەرکەوتوویی لە گیتھەب کار دەکات. 🔥")

print("بۆتەکە دەستی پێ کرد...")
app.run()
