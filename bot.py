import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

# --- إعدادات من متغيرات البيئة ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHANNEL = os.environ.get("CHANNEL")  # @اسم_القناة أو -100xxxx
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
        from pyrogram.enums import ChatMembersFilter
        async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.user.id == user_id:
                return True
        return False
    except Exception:
        return False

# --- إرسال ملف للقناة ---
async def send_audio_to_channel(title, file_path):
    try:
        if not os.path.exists(file_path):
            return False, "❌ الملف الصوتي غير موجود"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        caption = f"🎙 التسجيل: {title}\n📅 التاريخ: {now}\n👥 المجموعة: {GROUP}"
        await app.send_audio(CHANNEL, file_path, caption=caption)
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

    # التعامل فقط مع أوامر المشرفين
    if is_admin:
        if text.startswith("سجل المحادثة"):
            title = text.replace("سجل المحادثة", "").strip() or "بدون عنوان"
            recording = True
            current_title = title
            audio_file_path = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{title}.ogg"
            # إنشاء ملف فارغ كتجربة
            with open(audio_file_path, "wb") as f:
                f.write(b"")
            await message.reply(f"✅ بدأ التسجيل: {title}")
            return

        if text.startswith("أوقف التسجيل"):
            if not recording:
                await message.reply("❌ لا يوجد تسجيل جاري")
                return
            recording = False
            success, reply_text = await send_audio_to_channel(current_title, audio_file_path)
            if success:
                os.remove(audio_file_path)
            current_title = None
            audio_file_path = None
            await message.reply(reply_text)
            return

        if text.startswith("/testfile"):
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

# --- تشغيل اليوزبوت ---
if __name__ == "__main__":
    print("🚀 Starting userbot...")
    app.run()
