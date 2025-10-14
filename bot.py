import os
from datetime import datetime
from pyrogram import Client, filters

# -----------------------------
# إعدادات البوت (من متغيرات البيئة)
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# -----------------------------
# متغيرات التسجيل
# -----------------------------
is_recording = False
current_title = ""
current_file = ""

# -----------------------------
# دالة مساعدة لتنسيق الاسم
# -----------------------------
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

# -----------------------------
# التعامل مع أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    # تأكد أن الرسالة من نفس المجموعة المحددة
    if str(message.chat.id) != str(GROUP_ID):
        return

    # تجاهل أي رسالة لا تحتوي أوامرنا
    if not message.text.startswith(("سجل المحادثة", "أوقف التسجيل")):
        return

    # التحقق من هوية المرسل (مالك أو مشرف فقط)
    if not message.from_user:
        # في حال كان مرسل كقناة أو مشرف مجهول
        try:
            member = await app.get_chat_member(message.chat.id, message.sender_chat.id)
            if member.status not in ("creator", "administrator"):
                await message.reply("❌ لا يمكن التحقق من هويتك — استخدم الأمر من حسابك الشخصي.")
                return
        except Exception:
            await message.reply("❌ لا يمكن التحقق من هويتك — أرسل الأمر من حسابك الشخصي.")
            return
    else:
        # تحقق من صلاحية المستخدم
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ("creator", "administrator"):
            await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر (خاص بالمشرفين).")
            return

    text = message.text.strip()

    # --- بدء التسجيل ---
    if text.startswith("سجل المحادثة"):
        if is_recording:
            await message.reply("⚠️ يوجد تسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.ogg"
        is_recording = True

        await message.reply(f"🎙 ✅ بدأ التسجيل بعنوان: {title}\n(الحالة: تسجيل مفعل)")

    # --- إيقاف التسجيل ---
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        caption = (
            f"🎙 التسجيل: {current_title}\n"
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"👥 المجموعة: {GROUP_ID}"
        )

        # في هذه النسخة لا يوجد تسجيل فعلي بعد
        if os.path.exists(current_file):
            try:
                await app.send_voice(CHANNEL_ID, voice=current_file, caption=caption)
                os.remove(current_file)
                await message.reply(f"✅ تم إيقاف التسجيل وإرساله للقناة: {current_title}")
            except Exception as e:
                await message.reply(f"❌ فشل إرسال الملف: {e}")
        else:
            await app.send_message(
                CHANNEL_ID,
                f"📌 (سجل تلقائي) {caption}\n— ملاحظة: لا يوجد ملف فعلي في هذه النسخة."
            )
            await message.reply(f"✅ تم إيقاف التسجيل (لم يكن هناك ملف فعلي ليُرسل).")

# -----------------------------
# تشغيل اليوزربوت
# -----------------------------
if __name__ == "__main__":
    print("✅ Starting userbot...")
    app.run()
