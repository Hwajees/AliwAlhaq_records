import os
from datetime import datetime
from pyrogram import Client, filters

# -----------------------------
# إعدادات البوت من Render
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
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
# دالة مساعدة
# -----------------------------
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

async def is_admin(chat_id, user_or_chat):
    """
    تفحص إن كان المستخدم أو القناة مشرفًا في المجموعة.
    """
    try:
        member = await app.get_chat_member(chat_id, user_or_chat)
        return member.status in ("creator", "administrator")
    except Exception:
        return False

# -----------------------------
# أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    if str(message.chat.id) != str(GROUP_ID):
        return  # تجاهل المجموعات الأخرى

    # تجاهل أي نص غير أوامرنا
    if not message.text.startswith(("سجل المحادثة", "أوقف التسجيل")):
        return

    # التحقق من المرسل
    sender_id = None
    sender_name = "مجهول"

    if message.from_user:
        sender_id = message.from_user.id
        sender_name = message.from_user.first_name
    elif message.sender_chat:
        sender_id = message.sender_chat.id
        sender_name = message.sender_chat.title

    if not sender_id or not await is_admin(message.chat.id, sender_id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر (خاص بالمشرفين).")
        return

    text = message.text.strip()

    # ------------------ بدء التسجيل ------------------
    if text.startswith("سجل المحادثة"):
        if is_recording:
            await message.reply("⚠️ يوجد تسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.ogg"
        is_recording = True

        await message.reply(f"✅ بدأ التسجيل بعنوان: {title}\n👤 بأمر من: {sender_name}")

    # ------------------ إيقاف التسجيل ------------------
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        caption = (
            f"🎙 التسجيل: {current_title}\n"
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"👥 المجموعة: {GROUP_ID}\n"
            f"👤 المشرف: {sender_name}"
        )

        if os.path.exists(current_file):
            try:
                await app.send_voice(CHANNEL_ID, voice=current_file, caption=caption)
                os.remove(current_file)
                await message.reply(f"✅ تم إيقاف التسجيل وإرساله للقناة.")
            except Exception as e:
                await message.reply(f"❌ فشل إرسال الملف: {e}")
        else:
            await app.send_message(CHANNEL_ID, f"📌 {caption}\n⚠️ لا يوجد ملف صوتي فعلي.")
            await message.reply(f"✅ تم إيقاف التسجيل (تسجيل افتراضي فقط).")

# -----------------------------
# تشغيل اليوزربوت
# -----------------------------
if __name__ == "__main__":
    print("✅ Userbot started and waiting for commands...")
    app.run()
