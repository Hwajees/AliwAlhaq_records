import os
from pyrogram import Client
from tgcalls import GroupCall

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message()
async def join_leave_handler(client, message):
    if message.text == "/join" and message.from_user:
        gc = GroupCall(client, GROUP_ID)
        await gc.start()
        await message.reply("✅ دخلت المحادثة الصوتية")
    elif message.text == "/leave" and message.from_user:
        await gc.stop()
        await message.reply("❌ خرجت من المحادثة الصوتية")

app.run()
