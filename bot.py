import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BHARATPE_LINK = os.environ.get("BHARATPE_LINK", "https://bharatpe.me/yourlink")
PAID_CHANNEL_ID = int(os.environ.get("PAID_CHANNEL_ID", "-100xxxxxxxxx"))

app = Client(
    "paid_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Store pending verification users temporarily
pending_users = set()

@app.on_message(filters.command("start"))
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pay via BharatPe", url=BHARATPE_LINK)],
        [InlineKeyboardButton("✅ Send UTR Number", callback_data="enter_utr")]
    ])
    await message.reply_text(
        "👋 Welcome!\n\n"
        "Is paid video ko dekhne ke liye:\n"
        "1. **Pay via BharatPe** button par click karke kisi bhi UPI app se payment karein.\n"
        "2. Payment karne ke baad **Send UTR Number** par click karke 12-digit ka UPI Ref / UTR number bhejein.",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("enter_utr"))
async def ask_utr(client, callback_query):
    user_id = callback_query.from_user.id
    pending_users.add(user_id)
    await callback_query.message.reply_text(
        "✍️ Kripya apne payment ka **12-digit ka UTR / Reference Number** yahan chat me type karke bhej dein (jaise: 4235xxxxxxxx):"
    )

@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_utr(client, message):
    user_id = message.from_user.id
    if user_id in pending_users:
        utr_text = message.text.strip()
        pending_users.remove(user_id)
        
        # Yahan bot aapko (admin ko) ya log me UTR bhej sakta hai, ya filhal auto-verify maan kar link de sakta hai
        try:
            invite_link = await client.create_chat_invite_link(
                chat_id=PAID_CHANNEL_ID,
                member_limit=1
            )
            await message.reply_text(
                f"🎉 UTR Received: `{utr_text}`\n\nAapki payment verify ho gayi hai! Yeh raha aapka single-use private channel ka link:\n\n{invite_link.invite_link}"
            )
        except Exception as e:
            await message.reply_text("⚠️ Kuch error aaya hai. Kripya admin se contact karein.")

app.run()
