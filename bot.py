# bot.py
import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

# =======================
# المتغيرات الأساسية
# =======================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))  # معرف المجموعة
CHANNEL_ID = os.environ.get("CHANNEL_ID")   # اسم القناة أو معرفها

# =======================
# تهيئة اليوزربوت
# =======================
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# =======================
# متغير لتخزين حالة التسجيل
# =======================
recording = False
record_name = ""
record_file = None

# =======================
# دالة للتحقق من المشرف
# =======================
async def is_user_admin(chat_id, user_id):
    try:
        async for member in app.get_chat_members(chat_id, filter="administrators"):
            if member.user.id == user_id:
                return True
    except Exception:
        return False
    return False

# =======================
# بدء التسجيل
# =======================
@app.on_message(filters.chat(GROUP_ID) & filters.text & filters.command("سجل", prefixes=["/"]))
async def start_recording(client: Client, message: Message):
    global recording, record_name, record_file
    if await is_user_admin(message.chat.id, message.from_user.id):
        if len(message.command) > 1:
            record_name = " ".join(message.command[1:])
        else:
            record_name = "تسجيل"
        recording = True
        record_file = f"{record_name}.ogg"
        await message.reply(f"✅ بدأ التسجيل: {record_name}")
    else:
        # لا نرسل رسالة للأعضاء العاديين
        return

# =======================
# إيقاف التسجيل وإرسال الملف للقناة
# =======================
@app.on_message(filters.chat(GROUP_ID) & filters.text & filters.command("أوقف", prefixes=["/"]))
async def stop_recording(client: Client, message: Message):
    global recording, record_name, record_file
    if await is_user_admin(message.chat.id, message.from_user.id):
        if not recording:
            await message.reply("❌ لا يوجد تسجيل جاري.")
            return
        recording = False
        # تحقق من وجود الملف المحلي قبل الإرسال
        if record_file and os.path.exists(record_file):
            try:
                await client.send_audio(
                    chat_id=CHANNEL_ID,
                    audio=record_file,
                    caption=f"🎙 التسجيل: {record_name}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
                )
                await message.reply(f"✅ تم إرسال التسجيل للقناة: {record_name}")
            except Exception as e:
                await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")
        else:
            await message.reply(f"❌ لم يتم العثور على الملف: {record_file}")
        record_name = ""
        record_file = None
    else:
        return

# =======================
# أمر اختبار ملف (اختياري)
# =======================
@app.on_message(filters.chat(GROUP_ID) & filters.text & filters.command("testfile", prefixes=["/"]))
async def send_test_file(client: Client, message: Message):
    if await is_user_admin(message.chat.id, message.from_user.id):
        test_file = "test.ogg"
        if os.path.exists(test_file):
            try:
                await client.send_audio(chat_id=CHANNEL_ID, audio=test_file)
                await message.reply("✅ تم إرسال الملف التجريبي للقناة.")
            except Exception as e:
                await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")
        else:
            await message.reply("❌ لم يتم العثور على الملف التجريبي في المشروع.")
    else:
        return

# =======================
# تشغيل البوت
# =======================
app.run()
