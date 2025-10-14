import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters

# === متغيرات البيئة من Render ===
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
CHANNEL_ID = os.getenv("CHANNEL_ID") or ""
GROUP_ID = int(os.getenv("GROUP_ID"))

# تنظيف الـ @ من القناة إذا كانت موجودة
if CHANNEL_ID.startswith("@"):
    CHANNEL_ID = CHANNEL_ID[1:]

# إنشاء تطبيق Pyrogram
app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# === متغيرات التحكم في التسجيل ===
is_recording = False
record_title = ""
record_start_time = None

# ==== التحقق من كون المستخدم مشرفًا في المجموعة ====
async def is_user_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False

# ==== استقبال الرسائل في المجموعة ====
@app.on_message(filters.chat(GROUP_ID))
async def handle_messages(client, message):
    global is_recording, record_title, record_start_time

    # تجاهل رسائل الأعضاء العاديين
    if not await is_user_admin(message.chat.id, message.from_user.id):
        return

    text = message.text or ""

    # === بدء التسجيل ===
    if text.lower().startswith("سجل المحادثة"):
        try:
            record_title = text.split(" ", 2)[-1].strip()
            if not record_title:
                await message.reply("❌ الرجاء كتابة اسم بعد الأمر.")
                return
            is_recording = True
            record_start_time = datetime.now()
            await message.reply(f"✅ بدأ التسجيل: {record_title}")
        except Exception as e:
            await message.reply(f"❌ خطأ أثناء البدء: {e}")

    # === إيقاف التسجيل ===
    elif text.lower().startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("❌ لا يوجد تسجيل قيد التشغيل.")
            return

        is_recording = False
        record_end_time = datetime.now()

        filename = f"{record_start_time.strftime('%Y-%m-%d_%H-%M')}_{record_title}.ogg"
        filepath = f"./{filename}"

        # إنشاء ملف تجريبي صغير (كتم صوت فقط)
        with open(filepath, "wb") as f:
            f.write(b"\x00" * 1000)

        try:
            await app.send_document(
                chat_id=CHANNEL_ID,
                document=filepath,
                caption=(
                    f"🎙 التسجيل: {record_title}\n"
                    f"📅 التاريخ: {record_start_time.strftime('%Y-%m-%d %H:%M')}\n"
                    f"👥 المجموعة: {message.chat.id}"
                ),
            )
            await message.reply(f"✅ تم إرسال التسجيل للقناة: {record_title}")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

        # حذف الملف بعد الإرسال
        if os.path.exists(filepath):
            os.remove(filepath)

    # === أمر اختبار الملف ===
    elif text.lower().startswith("/testfile"):
        try:
            test_path = "./testfile.ogg"
            # إنشاء ملف اختباري إذا لم يكن موجودًا
            if not os.path.exists(test_path):
                with open(test_path, "wb") as f:
                    f.write(b"\x00" * 1000)

            await app.send_document(
                chat_id=CHANNEL_ID,
                document=test_path,
                caption="🔹 اختبار الإرسال من اليوزربوت"
            )
            await message.reply("✅ تم إرسال الملف التجريبي للقناة.")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

# === تشغيل التطبيق ===
print("✅ Userbot is running...")
app.run()
