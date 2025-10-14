import os
from datetime import datetime
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

is_recording = False
current_title = ""
current_file = ""


def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)


async def is_admin(chat_id, user_id):
    """
    يفحص إن كان المستخدم أو القناة مشرفًا فعلاً في المجموعة.
    """
    try:
        admins = await app.get_chat_administrators(chat_id)
        admin_ids = [a.user.id for a in admins if a.user]
        return user_id in admin_ids
    except Exception as e:
        print("خطأ في جلب قائمة المشرفين:", e)
        return False


@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    if message.chat.id != GROUP_ID:
        return

    # تجاهل أي شيء ليس أوامرنا
    if not message.text.startswith(("سجل المحادثة", "أوقف التسجيل")):
        return

    # تحديد هوية المرسل
    if message.from_user:
        sender_id = message.from_user.id
        sender_name = message.from_user.first_name
    elif message.sender_chat:
        sender_id = message.sender_chat.id
        sender_name = message.sender_chat.title
    else:
        return

    # التحقق من كونه مشرفًا
    if not await is_admin(GROUP_ID, sender_id):
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
            await app.send_voice(CHANNEL_ID, voice=current_file, caption=caption)
            os.remove(current_file)
            await message.reply("✅ تم إيقاف التسجيل وإرساله للقناة.")
        else:
            await app.send_message(CHANNEL_ID, f"📌 {caption}\n⚠️ لا يوجد ملف صوتي فعلي.")
            await message.reply("✅ تم إيقاف التسجيل (تسجيل رمزي فقط).")


if __name__ == "__main__":
    print("✅ Userbot started and waiting for commands...")
    app.run()
