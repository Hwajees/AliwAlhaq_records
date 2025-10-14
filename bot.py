import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

# --- إعدادات من متغيرات البيئة ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHANNEL = os.environ.get("CHANNEL")  # يمكن أن يكون @اسم_القناة
GROUP = int(os.environ.get("GROUP_ID"))

# --- إنشاء Client Userbot ---
app = Client(
    "userbot",
    session_string=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

# حالة التسجيل
recording = False
current_title = None
audio_file_path = None

# --- التحقق إذا كان المستخدم مشرف ---
async def is_user_admin(chat_id, user_id):
    try:
        async for member in app.get_chat_members(chat_id, filter="administrators"):
            if member.user.id == user_id:
                return True
        return False
    except Exception:
        return False

# --- إرسال ملف للقناة ---
async def send_audio_to_channel(title):
    global audio_file_path
    if not audio_file_path or not os.path.exists(audio_file_path):
        return False, "❌ حدث خطأ: الملف الصوتي غير موجود"
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        caption = f"🎙 التسجيل: {title}\n📅 التاريخ: {now}\n👥 المجموعة: {GROUP}"
        await app.send_audio(CHANNEL, audio_file_path, caption=caption)
        os.remove(audio_file_path)  # حذف الملف بعد الإرسال
        return True, f"✅ تم إرسال التسجيل للقناة: {title}"
    except Exception as e:
        return False, f"❌ حدث خطأ أثناء إرسال الملف: {str(e)}"

# --- الرسائل الواردة ---
@app.on_message(filters.chat(GROUP) & filters.text)
async def handle_messages(client, message: Message):
    global recording, current_title, audio_file_path
    user_id = message.from_user.id
    text = message.text.strip()

    # التحقق من الصلاحية
    is_admin = await is_user_admin(message.chat.id, user_id)

    # أوامر المشرف فقط
    if is_admin:
        if text.startswith("سجل المحادثة"):
            title = text.replace("سجل المحادثة", "").strip() or "بدون عنوان"
            recording = True
            current_title = title
            audio_file_path = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{title}.ogg"
            # هنا فقط ننشئ الملف الفارغ كتجربة، لاحقاً يمكن التسجيل الحقيقي
            with open(audio_file_path, "wb") as f:
                f.write(b"")  
            await message.reply(f"✅ بدأ التسجيل: {title}")
            return

        if text.startswith("أوقف التسجيل"):
            if not recording:
                await message.reply("❌ لا يوجد تسجيل جاري")
                return
            recording = False
            success, reply_text = await send_audio_to_channel(current_title)
            await message.reply(reply_text)
            current_title = None
            audio_file_path = None
            return

        if text.startswith("/testfile"):
            # إرسال ملف تجريبي للقناة
            test_file = "test_audio.ogg"
            if not os.path.exists(test_file):
                await message.reply("❌ الملف التجريبي غير موجود")
                return
            try:
                await app.send_audio(CHANNEL, test_file, caption="🔹 اختبار الإرسال من اليوزبوت")
                await message.reply("✅ تم إرسال الملف التجريبي للقناة.")
            except Exception as e:
                await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {str(e)}")
            return

    else:
        # الرد على الأعضاء العاديين
        if text:
            await message.reply("❌ ليس لديك الصلاحية")

# --- تشغيل اليوزبوت ---
if __name__ == "__main__":
    print("🚀 Starting userbot...")
    app.run()
