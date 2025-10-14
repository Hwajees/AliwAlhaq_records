import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pytgcalls import PyTgCalls

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call = PyTgCalls(app)

# -----------------------------
# دالة التحقق من المشرف
# -----------------------------
async def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

# -----------------------------
# التعامل مع أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    if str(message.chat.id) != str(GROUP_ID):
        return

    user_id = message.from_user.id
    text = message.text.strip()
    is_admin = await is_user_admin(message.chat.id, user_id)

    if text.startswith("سجل المحادثة"):
        if not is_admin:
            return

        # صعود البوت للمحادثة الصوتية باستخدام ملف صوت صامت
        await call.join_group_call(GROUP_ID, "silence.mp3")
        await message.reply("🎙 البوت انضم للمحادثة الصوتية بنجاح! ✅")

    elif text.startswith("أوقف التسجيل"):
        if not is_admin:
            return

        await call.leave_group_call(GROUP_ID)
        await message.reply("🛑 تم خروج البوت من المحادثة الصوتية!")

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    print("🚀 Starting userbot...")
    app.run()

