import os
from datetime import datetime
from pyrogram import Client, filters

# -----------------------------
# إعدادات اليوزربوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH"))
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# -----------------------------
# متغيرات التسجيل
# -----------------------------
is_recording = False
current_title = ""
current_file = ""

# -----------------------------
# دوال مساعدة
# -----------------------------
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

async def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if member.user.id == user_id:
            return True
    return False

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
            await message.reply("⚠️ يوجد تسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        is_recording = True

        # هنا في الواقع يجب أن يبدأ التسجيل الصوتي من المكالمة الصوتية
        # يمكنك لاحقًا دمج pytgcalls أو tgcalls لتسجيل المكالمة فعليًا
        await message.reply(f"🎙 بدأ التسجيل بعنوان: {title}")

    # إيقاف التسجيل
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(current_title)}.ogg"

        # مبدئيًا سنرسل ملف وهمي أو نستخدم التسجيل الحقيقي لاحقًا
        caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
        await app.send_message(CHANNEL_ID, caption)

        await message.reply(f"✅ تم إيقاف التسجيل وإرساله إلى القناة.")

# -----------------------------
# تشغيل اليوزربوت
# -----------------------------
if __name__ == "__main__":
    app.run()
