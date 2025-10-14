import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.input_audio import InputAudio

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # مثال: "@AliwAlhaq_records"

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
pytgcalls = PyTgCalls(app)

# -----------------------------
# متغيرات تسجيل الصوت
# -----------------------------
is_recording = False
current_title = ""
current_file = ""
voice_chat_id = None  # سيتم حفظ معرف المحادثة الصوتية

# -----------------------------
# دوال مساعدة
# -----------------------------
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

async def is_user_admin(chat_id, user_id):
    try:
        async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.user.id == user_id:
                return True
        return False
    except Exception as e:
        print("Error checking admin:", e)
        return False

# -----------------------------
# أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file, voice_chat_id

    if str(message.chat.id) != str(GROUP_ID):
        return

    user_id = message.from_user.id
    text = message.text.strip()
    is_admin = await is_user_admin(message.chat.id, user_id)

    # -------- تسجيل المحادثة --------
    if text.startswith("سجل المحادثة"):
        if not is_admin:
            return  # لا يرد على الأعضاء العاديين

        if is_recording:
            await message.reply("⚠️ التسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.ogg"
        is_recording = True

        # الانضمام للمحادثة الصوتية
        try:
            voice_chat_id = GROUP_ID
            await pytgcalls.join_group_call(
                GROUP_ID,
                InputStream(InputAudio("input.raw")),  # ملف صوتي فارغ لتشغيل البث
            )
            await message.reply(f"✅ بدأ التسجيل: {title}")
        except Exception as e:
            await message.reply(f"❌ فشل الانضمام للمحادثة الصوتية: {e}")
            is_recording = False

    # -------- إيقاف التسجيل --------
    elif text.startswith("أوقف التسجيل"):
        if not is_admin:
            return

        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False

        # إغلاق البث الصوتي
        try:
            await pytgcalls.leave_group_call(GROUP_ID)
        except Exception as e:
            print("❌ خطأ عند الخروج من المحادثة الصوتية:", e)

        # إرسال ملف تجريبي للقناة
        test_file = "test_audio.ogg"
        if not os.path.exists(test_file):
            await message.reply("❌ الملف التجريبي غير موجود.")
            return

        try:
            caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
            await app.send_audio(CHANNEL_ID, audio=test_file, caption=caption)
            await message.reply(f"✅ تم إرسال التسجيل للقناة: {current_title}")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

# -----------------------------
# الأحداث الصوتية
# -----------------------------
@pytgcalls.on_stream_end()
async def stream_end_handler(update: Update):
    print("🎙 انتهاء البث الصوتي")

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    app.start()
    pytgcalls.start()
    print("🚀 Userbot + Voice Bot started")
    idle()
