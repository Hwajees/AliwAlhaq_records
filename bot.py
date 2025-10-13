import os
import subprocess
from datetime import datetime
from pyrogram import Client, filters

# -----------------------------
# إعداد المتغيرات من البيئة
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))  # رقم القناة فقط
GROUP_ID = int(os.environ.get("GROUP_ID"))      # رقم المجموعة

# -----------------------------
# تهيئة البوت
# -----------------------------
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# -----------------------------
# المتغيرات العالمية
# -----------------------------
is_recording = False
current_title = ""
current_file = ""

# -----------------------------
# دالة للتحقق من صلاحيات المشرف
# -----------------------------
async def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if member.user.id == user_id:
            return True
    return False

# -----------------------------
# دالة لتنظيف اسم الملف
# -----------------------------
def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in "_- ")

# -----------------------------
# أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    if str(message.chat.id) != str(GROUP_ID):
        return

    if not await is_user_admin(message.chat.id, message.from_user.id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return

    text = message.text.strip()

    # بدء التسجيل
    if text.startswith("سجل المحادثة"):
        if is_recording:
            await message.reply("⚠️ التسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.raw"
        is_recording = True
        await message.reply(f"✅ بدأ التسجيل: {title}")

    # إيقاف التسجيل
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        mp3_file = current_file.replace(".raw", ".mp3")
        # تحويل RAW إلى MP3
        subprocess.run([
            "ffmpeg", "-y", "-i", current_file, "-vn", "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_file
        ])

        caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
        await app.send_audio(CHANNEL_ID, audio=mp3_file, caption=caption)

        os.remove(current_file)
        os.remove(mp3_file)
        await message.reply(f"✅ تم إيقاف التسجيل وحفظ الملف: {current_title}")

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    app.run()
