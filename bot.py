import os
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Yahan aap apna Telegram User ID daal sakte hain taaki broadcast command sirf aap chala sakein
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0)) 

app = Client(
    "auto_accept_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Simple memory storage (Database bhi use kar sakte hain, abhi ke liye basic variable hai)
total_approved = 0
users_list = set()

# /start command
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    # User ko list mein save kar lete hain broadcast ke liye
    users_list.add(message.from_user.id)
    
    text = (
        "I'm alive!\n\n"
        "I can approve new join requests in chats. "
        "Just add me in the chat with invite users permission.\n\n"
        "Use /stats to check my performance!"
    )
    await message.reply_text(text)

# Auto accept join request handler
@app.on_chat_join_request()
async def accept_join_request(client: Client, chat_join_request: ChatJoinRequest):
    global total_approved
    chat = chat_join_request.chat
    user = chat_join_request.from_user
    
    try:
        # 1. Request approve karein
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        total_approved += 1
        users_list.add(user.id)
        
        # 2. User ko verification message bhejein
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("I'm not a Robot ✅", callback_data="verify_user")]]
        )
        
        await client.send_message(
            chat_id=user.id,
            text=f"Hello {user.first_name},\n\nConfirm that you are not a robot by clicking the below button.",
            reply_markup=button
        )
    except Exception as e:
        print(f"Error: {e}")

# Verification Callback Handler
@app.on_callback_query(filters.regex("verify_user"))
async def verify_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("Verified successfully!", show_alert=True)
    await callback_query.message.edit_text("Done ✅")

# /stats command (Total requests kitni accept hui hain dekhne ke liye)
@app.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    text = (
        f"📊 **Bot Statistics:**\n\n"
        f"• Total Requests Approved: `{total_approved}`\n"
        f"• Total Users Interacted: `{len(users_list)}`"
    )
    await message.reply_text(text)

# /broadcast command (Admin sabhi users ko message bhej sakega)
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_command(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to broadcast!")
        return
    
    sent = 0
    failed = 0
    
    broadcast_msg = message.reply_to_message
    for user_id in users_list:
        try:
            await broadcast_msg.copy(chat_id=user_id)
            sent += 1
        except Exception:
            failed += 1
            
    await message.reply_text(f"Broadcast Completed!\n\nSent: {sent}\nFailed: {failed}")

print("Advanced Bot is starting...")
app.run()
