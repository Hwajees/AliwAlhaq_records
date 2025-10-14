from pyrogram import Client, filters
from datetime import datetime
import os

# إعدادات اليوزربوت
app = Client("userbot_session")

# إعدادات القناة الهدف
TARGET_CHANNEL_ID = -1001234567890  # ← غيّر هذا إلى معرف قناتك

# متغيرات التشغيل
recording = False
current_title = None
test_audio_path = "test_audio.ogg"  # الملف التجريبي الموجود داخل مجلد المشروع

# 🟩 دالة التحقق إن كان المستخدم مشرفاً
async def is_user_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


# 🟦 بدء التسجيل
@app.on_message(filters.regex(r"^سجل المحادثة (.+)"))
async def start_recording(client, message):
    global recording, current_title
    if not await is_user_admin(message.chat.id, message.from_user.id):
        return  # تجاهل العضو العادي تماماً

    current_title = message.matches[0].group(1).strip()
    recording = True
    await message.reply_text(f"✅ بدأ التسجيل: {current_title}")


# 🟥 إيقاف التسجيل
@app.on_message(filters.regex(r"^أوقف التسجيل$"))
async def stop_recording(client, message):
    global recording, current_title
    if not await is_user_admin(message.chat.id, message.from_user.id):
        return  # تجاهل العضو العادي تماماً

    if not recording:
        await message.reply_text("⚠️ لا يوجد تسجيل نشط حالياً.")
        return

    recording = False

    # تحقق من وجود الملف التجريبي
    if not os.path.exists(test_audio_path):
        await message.reply_text("❌ لم يتم العثور على ملف التسجيل التجريبي في المجلد.")
        return

    try:
        # معلومات الإرسال
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        caption = (
            f"🎙 التسجيل: {current_title}\n"
            f"📅 التاريخ: {timestamp}\n"
            f"👥 المجموعة: {message.chat.id}"
        )

        await app.send_audio(
            chat_id=TARGET_CHANNEL_ID,
            audio=test_audio_path,
            caption=caption
        )

        await message.reply_text(f"✅ تم إرسال التسجيل للقناة: {current_title}")

    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ أثناء إرسال الملف: {e}")


# 🚫 تجاهل كل رسائل الأعضاء العاديين الأخرى
@app.on_message(filters.text)
async def ignore_members(client, message):
    if not await is_user_admin(message.chat.id, message.from_user.id):
        return  # لا يرد عليهم إطلاقاً


print("✅ Userbot is running...")
app.run()
