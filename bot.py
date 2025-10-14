import os
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

# معرف القناة (يمكن أن يكون بدون @)
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# معرف المجموعة للتفاعل معها (GROUP_ID)
GROUP_ID = int(os.environ.get("GROUP_ID"))

app = Client(
    session_name=STRING_SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
)

# متغيرات التسجيل
recording = False
current_file_name = ""

async def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if member.user.id == user_id:
            return True
    return False

@app.on_message(filters.chat(GROUP_ID))
async def handle_messages(client: Client, message: Message):
    global recording, current_file_name

    user_id = message.from_user.id

    # فقط المشرف يمكنه استخدام الأوامر
    is_admin = await is_user_admin(message.chat.id, user_id)

    if not is_admin:
        return  # لا تتفاعل مع الأعضاء العاديين إطلاقًا

    text = message.text or ""

    # بدء التسجيل
    if text.startswith("سجل المحادثة"):
        recording = True
        current_file_name = text.replace("سجل المحادثة", "").strip() or "تسجيل"
        await message.reply_text(f"✅ بدأ التسجيل: {current_file_name}")

    # إيقاف التسجيل
    elif text.startswith("أوقف التسجيل"):
        if recording:
            recording = False
            try:
                file_path = f"{current_file_name}.ogg"
                # إرسال الملف إلى القناة
                await app.send_message(
                    CHANNEL_ID,
                    f"🎙 التسجيل: {current_file_name}\n"
                    f"📅 التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"👥 المجموعة: {GROUP_ID}"
                )
                if os.path.exists(file_path):
                    await app.send_audio(CHANNEL_ID, file_path)
                await message.reply_text(f"✅ تم إرسال التسجيل للقناة: {current_file_name}")
            except Exception as e:
                await message.reply_text(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

# لتجربة إرسال ملف تجريبي
@app.on_message(filters.chat(GROUP_ID) & filters.command("testfile"))
async def send_test_file(client: Client, message: Message):
    user_id = message.from_user.id
    is_admin = await is_user_admin(message.chat.id, user_id)
    if not is_admin:
        return

    try:
        test_file_path = "test_audio.ogg"
        await app.send_audio(CHANNEL_ID, test_file_path)
        await message.reply_text("✅ تم إرسال الملف التجريبي للقناة.")
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

app.run()
