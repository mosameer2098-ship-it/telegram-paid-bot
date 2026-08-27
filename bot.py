import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
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
    await message.reply_text("👋 Welcome! Bot is running successfully.")

@app.on_message(filters.command("paylink"))
async def create_pay_link(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("⛔ Yeh command sirf Admin use kar sakta hai!")
        return
        
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("⚠️ Kripya price batayein. Use aise karein:\n`/paylink 50`")
            return
        
        amount = args[1]
        
        # Ab hum button nahi, seedha text me payment link aur niche UTR ka chota button denge
        pay_url = f"https://mercury.phonepe.com/pay?pa=BHARATPE.8I0E1X0W7K37600@fbpe&am={amount}&cu=INR"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Payment Karne ke Baad UTR Bhejein", callback_data="enter_utr")]
        ])
        
        await message.reply_text(
            f"🎬 **Paid Video Payment Link**\n\n"
            f"💰 Price: ₹{amount}\n\n"
            f"👉 **Payment karne ke liye is link par click karein:**\n{pay_url}\n\n"
            f"Payment karne ke baad niche wale button par click karke UTR number bhej dein.",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: {str(e)}")

@app.on_callback_query(filters.regex("enter_utr"))
async def ask_utr(client, callback_query):
    user_id = callback_query.from_user.id
    pending_users.add(user_id)
    await callback_query.message.reply_text(
        "✍️ Kripya apne payment ka **12-digit ka UTR / Reference Number** yahan chat me bhej dein:"
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
                f"🎉 UTR Received: `{utr_text}`\n\nAapki payment verify ho gayi hai! Yeh raha aapka private channel ka link:\n\n{invite_link.invite_link}"
            )
        except Exception as e:
            await message.reply_text("⚠️ Kuch error aaya hai. Kripya admin se contact karein.")

if __name__ == "__main__":
    app.run()
