import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

# المتغيرات البيئية
SESSION_STRING = os.environ.get("SESSION_STRING")  # session string لليوزربوت
GROUP_ID = int(os.environ.get("GROUP_ID"))        # ايدي المجموعة
CHANNEL_ID = os.environ.get("CHANNEL_ID")         # اسم القناة @AliwAlhaq_records

# إنشاء اليوزربوت
app = Client(
    name="userbot",
    session_string=SESSION_STRING,
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH")
)

# حالة التسجيل
is_recording = False
recording_name = ""

# التحقق من المشرف
async def is_user_admin(chat_id: int, user_id: int) -> bool:
    try:
        async for member in app.get_chat_members(chat_id, filter="administrators"):
            if member.user.id == user_id:
                return True
    except Exception:
        return False
    return False

# التعامل مع الرسائل داخل المجموعة
@app.on_message(filters.chat(GROUP_ID))
async def handle_messages(client: Client, message: Message):
    global is_recording, recording_name

    # فقط المشرف يمكنه الأوامر
    if await is_user_admin(message.chat.id, message.from_user.id):
        text = message.text or ""

        # بدء التسجيل
        if text.startswith("سجل المحادثة"):
            recording_name = text.replace("سجل المحادثة", "").strip()
            if recording_name:
                is_recording = True
                await message.reply(f"✅ بدأ التسجيل: {recording_name}")
            else:
                await message.reply("❌ يجب كتابة اسم التسجيل بعد الأمر.")

        # إيقاف التسجيل
        elif text.startswith("أوقف التسجيل"):
            if is_recording:
                is_recording = False
                # اسم الملف التجريبي
                test_file = f"{recording_name}.ogg"
                # تحقق من وجود الملف
                if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
                    await app.send_audio(
                        chat_id=CHANNEL_ID,
                        audio=test_file,
                        caption=f"🎙 التسجيل: {recording_name}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
                    )
                    await message.reply(f"✅ تم إرسال التسجيل للقناة: {recording_name}")
                else:
                    await message.reply("❌ حدث خطأ أثناء إرسال الملف: الملف غير موجود أو فارغ.")
            else:
                await message.reply("❌ لم يكن هناك تسجيل جاري.")

    # الأعضاء العاديين: لا يتفاعل البوت معهم نهائيًا
    else:
        return  # لا يفعل شيئًا

# تشغيل البوت
app.run()
