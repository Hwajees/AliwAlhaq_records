# bot.py
import os
import asyncio
import logging
import threading
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from mutagen import File as MutagenFile  # لاستخراج مدة المقطع

# -----------------------------
# الإعدادات الأساسية
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("userbot")

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = os.environ.get("CHANNEL_ID")
USERNAME = os.environ.get("USERNAME")
PORT = int(os.environ.get("PORT", 10000))

# -----------------------------
# إنشاء Pyrogram Client
# -----------------------------
app_client = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

# -----------------------------
# تهيئة Flask
# -----------------------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Userbot Flask server running and healthy!"

# -----------------------------
# حالة المستخدمين المؤقتة
# -----------------------------
user_states = {}
ALLOWED_COMMANDS = ["الارشيف", "الأرشيف"]

# -----------------------------
# وظائف Pyrogram (نفس السابق)
# -----------------------------
async def is_user_admin(chat_id, user_id):
    try:
        async for member in app_client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.user.id == user_id:
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking admin: {e}")
        return False


@app_client.on_message(filters.chat(GROUP_ID) & filters.text)
async def handle_archive_command(client, message):
    if message.text.strip() not in ALLOWED_COMMANDS:
        return
    user = message.from_user
    if not user:
        return
    if not await is_user_admin(GROUP_ID, user.id):
        return
    private_url = f"https://t.me/{USERNAME}?start=archive_{user.id}"
    caption = f"تم استلام طلب أرشفة المقطع ✅\nاضغط هنا للمحادثة الخاصة مع البوت: {private_url}"
    await message.reply_text(caption, disable_web_page_preview=True)


@app_client.on_message(filters.private & (filters.audio | filters.voice))
async def receive_audio_private(client, message):
    user_id = message.from_user.id
    file_path = await message.download()
    user_states[user_id] = {'file': file_path}
    await message.reply_text("✅ تم استلام المقطع الصوتي الخاص بك.\nالآن أرسل عنوان المقطع:")


@app_client.on_message(filters.private & filters.text)
async def receive_text_private(client, message):
    user_id = message.from_user.id
    if user_id not in user_states:
        await message.reply_text("❌ لم يتم العثور على حالة المستخدم. أرسل الملف أولًا.")
        return

    state = user_states[user_id]

    if 'title' not in state:
        state['title'] = message.text.strip()
        await message.reply_text("حسنًا ✅، الآن أرسل اسم المتحدث:")
        return

    if 'speaker' not in state:
        state['speaker'] = message.text.strip()
        await archive_to_channel(user_id, message)
        return


async def archive_to_channel(user_id, message):
    state = user_states.get(user_id)
    if not state:
        await message.reply_text("❌ حدث خطأ: لم يتم العثور على حالة المستخدم.")
        return

    file_path = state['file']
    title = state['title']
    speaker = state['speaker']
    date = datetime.now().strftime('%Y-%m-%d %H:%M')

    try:
        audio = MutagenFile(file_path)
        duration_seconds = int(audio.info.length)
        duration_text = str(timedelta(seconds=duration_seconds))
        if duration_seconds < 3600:
            duration_text = "00:" + ":".join(duration_text.split(":")[-2:])
    except:
        duration_text = "00:00:00"

    caption = (
        f"🎙 العنوان: {title}\n\n"
        f"👤 المتحدث: {speaker}\n\n"
        f"⏱ مدة المقطع: {duration_text}\n\n"
        f"📅 التاريخ: {date}\n\n"
        f"👥 المجموعة: @AliwAlhaq"
    )

    try:
        await app_client.send_audio(
            chat_id=f"@{CHANNEL_ID}",
            audio=file_path,
            caption=caption
        )
        await message.reply_text("✅ تم أرشفة المقطع بنجاح في القناة.")
    except Exception as e:
        await message.reply_text(f"❌ خطأ أثناء الأرشفة: {e}")

    os.remove(file_path)
    user_states.pop(user_id, None)

# -----------------------------
# Thread لتشغيل Pyrogram في الخلفية
# -----------------------------
def run_userbot():
    async def start_userbot():
        async with app_client:
            logger.info("🚀 Userbot connected and now polling messages...")
            await asyncio.get_event_loop().create_future()
        except Exception as e:
            logger.error(f"❌ Error starting userbot: {e}")
        
    asyncio.run(start_userbot())

threading.Thread(target=run_userbot, daemon=True).start()

# -----------------------------
# Flask Webhook-style endpoint
# -----------------------------
@flask_app.route("/webhook", methods=["POST"])
def webhook_endpoint():
    """
    هذا endpoint لا يتصل فعليًا مع Telegram،
    لكنه يسمح لك بإرسال إشعارات أو اختبارات من خدمات خارجية مستقبلًا.
    """
    data = request.get_json(silent=True)
    logger.info(f"📩 Webhook data received: {data}")
    return jsonify({"status": "received"}), 200

# -----------------------------
# تشغيل Flask فقط
# -----------------------------
if __name__ == "__main__":
    logger.info(f"🌐 Running Flask server on port {PORT}")
    flask_app.run(host="0.0.0.0", port=PORT)




