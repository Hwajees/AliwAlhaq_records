import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import Message

# إعدادات البيئة
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_NAME = os.environ.get("SESSION_NAME", "userbot_session")
GROUP_ID = int(os.environ.get("GROUP_ID"))           # ايدي المجموعة
CHANNEL_ID = os.environ.get("CHANNEL_ID")            # اسم القناة @اسم_القناة

# مسارات الملفات
RECORDINGS_DIR = "./recordings"
TEST_AUDIO = "./test_audio.ogg"

# إعداد اليوزربوت
app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

# حالة التسجيل
recording = False
current_title = ""

# تحقق من كون المستخدم مشرف أو مالك
async def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

# بدء التسجيل
async def start_recording(title):
    global recording, current_title
    recording = True
    current_title = title

# إيقاف التسجيل وإرسال الملف للقناة
async def stop_recording():
    global recording, current_title
    recording = False
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{current_title}.ogg"
    filepath = os.path.join(RECORDINGS_DIR, filename)

    # إذا كان الملف موجود أرسل الملف التجريبي
    if os.path.exists(TEST_AUDIO):
        try:
            await app.send_audio(
                CHANNEL_ID,
                TEST_AUDIO,
                caption=f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
            )
            return True
        except Exception as e:
            return f"❌ حدث خطأ أثناء إرسال الملف: {e}"
    else:
        return f"❌ ملف الاختبار غير موجود: {TEST_AUDIO}"

# التعامل مع الرسائل
@app.on_message(filters.chat(GROUP_ID))
async def handle_messages(client, message: Message):
    global recording, current_title

    user_id = message.from_user.id
    is_admin = await is_user_admin(GROUP_ID, user_id)

    if not is_admin:
        return  # تجاهل الرسائل من الأعضاء العاديين

    text = message.text or ""

    if text.startswith("سجل المحادثة"):
        title = text.replace("سجل المحادثة", "").strip()
        await start_recording(title)
        await message.reply(f"✅ بدأ التسجيل: {title}")

    elif text.startswith("أوقف التسجيل"):
        result = await stop_recording()
        if result is True:
            await message.reply(f"✅ تم إرسال التسجيل للقناة: {current_title}")
        else:
            await message.reply(result)

# تشغيل اليوزربوت
app.run()
