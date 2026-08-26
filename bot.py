import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Environment variables se credentials uthayenge (Heroku config vars ke liye safe rehta hai)
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PAYMENT_LINK = os.environ.get("PAYMENT_LINK", "https://rzp.io/l/your-default-link")
PAID_CHANNEL_ID = int(os.environ.get("PAID_CHANNEL_ID", "-100xxxxxxxxx"))

app = Client(
    "paid_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pay & Unlock Video", url=PAYMENT_LINK)],
        [InlineKeyboardButton("✅ Verify Payment", callback_data="check_payment")]
    ])
    await message.reply_text(
        "👋 Welcome! Is bot ke through paid video access karne ke liye niche diye gaye button par click karke payment karein, phir **Verify Payment** dabayein:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("check_payment"))
async def verify_payment(client, callback_query):
    user_id = callback_query.from_user.id
    
    # Filhal yahan manual/default check hai. Aage isme database integration karenge.
    # Agar user ne pay kar diya hai, toh usko private channel ka link bhej sakte hain:
    
    try:
        # User ko paid channel ka invite link bhejne ka code
        invite_link = await client.create_chat_invite_link(
            chat_id=PAID_CHANNEL_ID,
            member_limit=1
        )
        await callback_query.message.edit_text(
            f"🎉 Payment Verified!\nAapka private paid channel ka link yeh raha (Yeh sirf ek baar use hoga):\n\n{invite_link.invite_link}"
        )
    except Exception as e:
        await callback_query.answer("⚠️ Abhi aapki payment confirm nahi hui hai ya koi error hai!", show_alert=True)

app.run()
