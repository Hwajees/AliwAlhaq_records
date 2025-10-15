import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatMembersFilter
from flask import Flask
import threading
import math

# -----------------------------
# إعدادات Userbot
# -----------------------------
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Client("archiver_userbot", session_string=SESSION_STRING)

# -----------------------------
# قاموس مؤقت لتخزين بيانات المقطع لكل مشرف
# -----------------------------
pending_audio = {}

# -----------------------------
# دوال مساعدة
# -----------------------------
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

async def is_user_admin(chat_id, user_id):
    try:
        async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.user.id == user_id:
                return True
        return False
    except Exception as e:
        print("Error checking admin:", e)
        return False

# -----------------------------
# رصد الرسائل الصوتية في المجموعة
# -----------------------------
@app.on_message(filters.chat(GROUP_ID) & (filters.audio | filters.voice))
async def handle_audio(client: Client, message: Message):
    user = message.from_user
    is_admin = await is_user_admin(message.chat.id, user.id)
    if not is_admin:
        return  # تجاهل غير المشرفين

    # حفظ الرسالة مؤقتًا
    file_info = {
        "message": message,
        "title": message.audio.title if message.audio else None,
        "duration": message.audio.duration if message.audio else message.voice.duration,
        "state": "ask_title"
    }
    pending_audio[user.id] = file_info

    # زر للمحادثة الخاصة
    bot_username = (await client.get_me()).username
await message.reply_text(
    f"تم استلام المقطع الصوتي ✅\n"
    f"اضغط هنا للمحادثة الخاصة مع البوت: https://t.me/{bot_username}?start=archive"
)

# -----------------------------
# التفاعل في المحادثة الخاصة لجمع العنوان والمتحدث
# -----------------------------
@app.on_message(filters.private & filters.user(list(pending_audio.keys())))
async def private_interaction(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in pending_audio:
        return

    audio_info = pending_audio[user_id]
    state = audio_info.get("state", "ask_title")

    # السؤال عن العنوان
    if state == "ask_title":
        await message.reply_text("📌 اكتب العنوان الجديد للمقطع الصوتي أو اكتب 'تخطي' للاحتفاظ بالعنوان الحالي.")
        audio_info["state"] = "waiting_title"
        return

    if state == "waiting_title":
        if message.text.lower() != "تخطي":
            audio_info["title"] = message.text
        audio_info["state"] = "ask_speaker"
        await message.reply_text("🗣️ اكتب اسم المتحدث الرئيسي في المقطع الصوتي:")
        return

    # السؤال عن اسم المتحدث
    if state == "ask_speaker":
        audio_info["speaker"] = message.text
        msg = audio_info["message"]
        title = audio_info.get("title") or "بدون عنوان"
        speaker = audio_info.get("speaker")
        duration_sec = audio_info.get("duration") or 0
        duration_min = duration_sec // 60
        duration_sec_rem = duration_sec % 60
        group_name = (await client.get_chat(GROUP_ID)).title
        caption = f"""🎵 عنوان المقطع: {title}
🗣️ المتحدث: {speaker}
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
⏱️ المدة: {duration_min} دقيقة و {duration_sec_rem} ثانية
👥 المجموعة: {group_name}"""

        # رفع الصوت للقناة
        try:
            if msg.audio:
                await client.send_audio(CHANNEL_ID, audio=msg.audio.file_id, caption=caption)
            else:
                await client.send_voice(CHANNEL_ID, voice=msg.voice.file_id, caption=caption)
            # حذف الرسالة من المجموعة
            try:
                await msg.delete()
            except:
                pass
            await message.reply_text("✅ تم أرشفة المقطع وحذفه من المجموعة.")
        except Exception as e:
            await message.reply_text(f"❌ حدث خطأ أثناء رفع المقطع: {e}")

        # إزالة من القاموس المؤقت
        pending_audio.pop(user_id)

# -----------------------------
# رسالة /start في المحادثة الخاصة
# -----------------------------
@app.on_message(filters.command("start") & filters.private)
async def start_msg(client: Client, message: Message):
    await message.reply_text("مرحبًا! هذا Userbot مسؤول عن أرشفة المقاطع الصوتية للمجموعة.")

# -----------------------------
# Flask للحفاظ على الخدمة نشطة على Render
# -----------------------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Userbot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render يرسل هذا المتغير
    flask_app.run(host="0.0.0.0", port=port)

# -----------------------------
# تشغيل Userbot + Flask
# -----------------------------
if __name__ == "__main__":
    print("🚀 Starting userbot...")
    threading.Thread(target=run_flask).start()
    app.run()

