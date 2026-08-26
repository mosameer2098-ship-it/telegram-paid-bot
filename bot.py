import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Logging enable karein taaki terminal me dikhe ki bot kya kar raha hai
logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BHARATPE_UPI = os.environ.get("BHARATPE_UPI", "BHARATPE.8I0E1X0W7K37600@fbpe")
PAID_CHANNEL_ID = int(os.environ.get("PAID_CHANNEL_ID", "-100xxxxxxxxx"))
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

pending_users = set()

@app.on_message(filters.command("start"))
async def start_command(client, message):
    print(f"Received /start from user: {message.from_user.id}") # Heroku logs me check karne ke liye
    await message.reply_text(
        "👋 Welcome! Bot is active and running successfully.\n\n"
        "Aapko paid video ka link channel par mil jayega."
    )

@app.on_message(filters.command("paylink"))
async def create_pay_link(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("⛔ Yeh command sirf Channel Admin use kar sakta hai!")
        return
        
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("⚠️ Kripya price batayein. Use aise karein:\n`/paylink 50`")
            return
        
        amount = args[1]
        bharatpe_url = f"upi://pay?pa={BHARATPE_UPI}&pn=KahaniyonKaGhar&am={amount}&cu=INR"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💳 Pay ₹{amount} via BharatPe", url=bharatpe_url)],
            [InlineKeyboardButton("✅ Send UTR Number", callback_data="enter_utr")]
        ])
        
        await message.reply_text(
            f"🎬 **Paid Video Payment Link Created!**\n\n"
            f"💰 Price: ₹{amount}\n"
            f"Yeh link apne channel par post karein.",
            reply_markup=keyboard
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: {str(e)}")

@app.on_callback_query(filters.regex("enter_utr"))
async def ask_utr(client, callback_query):
    user_id = callback_query.from_user.id
    pending_users.add(user_id)
    await callback_query.message.reply_text(
        "✍️ Kripya apne payment ka **12-digit ka UTR / Reference Number** yahan chat me bhej dein (jaise: 4235xxxxxxxx):"
    )

@app.on_message(filters.text & ~filters.command(["start", "paylink"]))
async def handle_utr(client, message):
    user_id = message.from_user.id
    if user_id in pending_users:
        utr_text = message.text.strip()
        pending_users.remove(user_id)
        
        try:
            invite_link = await client.create_chat_invite_link(
                chat_id=PAID_CHANNEL_ID,
                member_limit=1
            )
            await message.reply_text(
                f"🎉 UTR Received: `{utr_text}`\n\nAapki payment verify ho gayi hai! Yeh raha aapka private channel ka link (Single-use):\n\n{invite_link.invite_link}"
            )
        except Exception as e:
            await message.reply_text("⚠️ Kuch error aaya hai. Kripya admin se contact karein.")

if __name__ == "__main__":
    print("Starting bot...")
    app.run()
