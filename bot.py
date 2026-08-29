import os
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "auto_accept_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    text = (
        "I'm alive!\n"
        "I can approve new join requests in chats. "
        "Just add me in the chat with invite users permission."
    )
    await message.reply_text(text)

# Jab koi join request bhejega
@app.on_chat_join_request()
async def accept_join_request(client, chat_join_request: ChatJoinRequest):
    chat = chat_join_request.chat
    user = chat_join_request.from_user
    
    try:
        # 1. Pehle request ko accept karein
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        
        # 2. Phir user ko personal chat mein verification message bhejein button ke sath
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

# Jab user "I'm not a Robot" button par click karega
@app.on_callback_query(filters.regex("verify_user"))
async def verify_callback(client, callback_query: CallbackQuery):
    # User ko "Done" ka popup ya message dikhayein
    await callback_query.answer("Verified successfully!", show_alert=True)
    await callback_query.message.edit_text("Done ✅")

print("Bot is starting with verification...")
app.run()
