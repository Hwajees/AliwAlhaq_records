import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# ==========================
# إعدادات اليوزربوت
# ==========================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

pending_archives = {}

# ==========================
# دالة فحص إذا المستخدم مشرف
# ==========================
async def is_admin(chat_id, user_id):
    try:
        async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.user.id == user_id:
                return True
        return False
    except Exception:
        return False


# ==========================
# عند استلام صوت من مشرف في المجموعة
# ==========================
@app.on_message(filters.chat(GROUP_ID) & (filters.audio | filters.voice))
async def handle_voice(client, message):
    user = message.from_user
    if not user:
        return

    if not await is_admin(GROUP_ID, user.id):
        return

    # تحميل الصوت مؤقتاً
    file_path = await message.download()
    pending_archives[user.id] = {
        "file": file_path,
        "title": getattr(message.audio, "title", "تسجيل بدون عنوان"),
    }

    me = await client.get_me()  # نستخدمها كما كانت تعمل سابقاً
    username = me.username or "userbot"

    # ✅ الزر الذي نجح سابقاً
    await message.reply_text(
        "تم استلام المقطع الصوتي ✅\nاضغط الزر للمتابعة في المحادثة الخاصة.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📥 المتابعة في الخاص",
                        url=f"https://t.me/{username}?start=archive_{user.id}"
                    )
                ]
            ]
        ),
    )


# ==========================
# عند بدء الأرشفة في الخاص
# ==========================
@app.on_message(filters.private & filters.command("start"))
async def handle_private(client, message):
    user = message.from_user
    args = message.command

    if len(args) > 1 and args[1].startswith("archive_"):
        user_id = int(args[1].split("_")[1])
        if user.id != user_id:
            await message.reply_text("❌ هذا الرابط ليس مخصصاً لك.")
            return

        if user_id not in pending_archives:
            await message.reply_text("⚠️ لا يوجد ملف جاهز للأرشفة.")
            return

        data = pending_archives.pop(user_id)
        file_path = data["file"]
        title = data["title"]

        await message.reply_text("🎧 جاري أرشفة المقطع...")

        caption = (
            f"🎙 العنوان: {title}\n"
            f"👤 المشرف: {user.first_name}\n"
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"👥 المجموعة: {message.chat.id}"
        )

        try:
            await client.send_audio(CHANNEL_ID, audio=file_path, caption=caption)
            await message.reply_text("✅ تم إرسال التسجيل إلى القناة بنجاح.")
        except Exception as e:
            await message.reply_text(f"❌ حدث خطأ أثناء الأرشفة:\n{e}")
    else:
        await message.reply_text("👋 أرسل التسجيل في المجموعة واضغط الزر للمتابعة هنا.")


# ==========================
# Flask لتشغيل Render
# ==========================
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Userbot is running fine ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🚀 Starting userbot...")
    threading.Thread(target=run_flask).start()
    app.run()
