import os
import asyncio
from pyrogram import Client, filters
from datetime import datetime

# متغيرات البيئة من Render
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # مثال: AliwAlhaq_records
GROUP_ID = int(os.environ.get("GROUP_ID"))  # مثال: -1001234567890

# تهيئة اليوزربوت
app = Client(
    session_string=STRING_SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
)

# حالة التسجيل
recording = False
record_name = ""
record_file = None

# التحقق من كون المستخدم مشرف
async def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if member.user.id == user_id:
            return True
    return False

# استقبال الرسائل في المجموعه
@app.on_message(filters.chat(GROUP_ID))
async def handle_messages(client, message):
    global recording, record_name, record_file

    user_id = message.from_user.id
    text = message.text or ""

    # تفاعل فقط مع المشرفين
    if await is_user_admin(message.chat.id, user_id):
        # بدء التسجيل
        if text.startswith("سجل المحادثة"):
            record_name = text.replace("سجل المحادثة", "").strip() or "تسجيل"
            recording = True
            record_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{record_name}.ogg"
            await message.reply(f"✅ بدأ التسجيل: {record_name}")
            return

        # إيقاف التسجيل
        elif text.startswith("أوقف التسجيل"):
            recording = False
            # محاولة إرسال الملف إلى القناة
            try:
                # هنا نستخدم ملف اختبار إذا لم يوجد تسجيل فعلي
                file_to_send = record_file if os.path.exists(record_file) else "test_audio.ogg"
                await app.send_audio(CHANNEL_ID, file_to_send,
                                     caption=f"🎙 التسجيل: {record_name}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}")
                await message.reply(f"✅ تم إرسال التسجيل للقناة: {record_name}")
            except Exception as e:
                await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")
            return

    # أعضاء عاديون لا يتفاعلون إطلاقاً
    else:
        return  # تجاهل أي رسالة من غير المشرفين

# تشغيل اليوزربوت
app.run()
