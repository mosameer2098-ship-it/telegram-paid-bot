import os
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest

# Environment variables se credentials uthayenge taaki security bani rahe
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

@app.on_chat_join_request()
async def accept_join_request(client, chat_join_request: ChatJoinRequest):
    chat = chat_join_request.chat
    user = chat_join_request.from_user
    
    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    except Exception as e:
        print(f"Error: {e}")

print("Bot is starting...")
app.run()
