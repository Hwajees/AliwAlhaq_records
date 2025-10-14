import os
from datetime import datetime
from threading import Thread

from flask import Flask
from pyrogram import Client, filters

# -----------------------------
# تحميل متغيرات البيئة
# -----------------------------
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = os.environ.get("GROUP_ID")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
PORT = int(os.environ.get("PORT", 10000))

# تحقق أساسي من المتغيرات المطلوبة
missing = []
for name, val in (("API_ID", API_ID), ("API_HASH", API_HASH), ("SESSION_STRING", SESSION_STRING),
                  ("GROUP_ID", GROUP_ID), ("CHANNEL_ID", CHANNEL_ID)):
    if not val:
        missing.append(name)
if missing:
    raise SystemExit(f"ERROR: المتغيرات التالية مفقودة في البيئة: {', '.join(missing)}")

# تحويل بعض القيم إلى أعداد صحيحة إن كانت أرقام
try:
    API_ID = int(API_ID)
except Exception:
    raise SystemExit("ERROR: API_ID يجب أن يكون رقماً صحيحاً")

try:
    GROUP_ID = int(GROUP_ID)
    CHANNEL_ID = int(CHANNEL_ID)
except Exception:
    raise SystemExit("ERROR: GROUP_ID و CHANNEL_ID يجب أن يكونا أرقام (استخدم -100...)")

# -----------------------------
# تهيئة Pyrogram (حساب المستخدم عبر SESSION_STRING)
# -----------------------------
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# -----------------------------
# Flask لمراقبة الخدمة (healthcheck)
# -----------------------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Userbot is running ✅"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

# -----------------------------
# متغيرات الحالة للتسجيل
# -----------------------------
is_recording = False
current_title = ""
current_file = ""   # لاحقًا سيشير لمسار الملف المسجل (عند إضافة التسجيل الفعلي)

def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip().replace(" ", "_")

async def is_user_admin(chat_id: int, user_id: int) -> bool:
    """
    التحقق إن كان user_id مشرفًا في chat_id.
    نستخدم async for لأن get_chat_members يعيد مولدًا غير قابل للـ await مباشرة.
    """
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if getattr(member.user, "id", None) == user_id:
            return True
    return False

# -----------------------------
# معالج رسائل المجموعة (أوامر المشرفين)
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    # تأكد أن الرسالة من نفس المجموعة المعرفة في المتغيرات
    if str(message.chat.id) != str(GROUP_ID):
        return

    # بعض الرسائل قد تأتي بدون from_user (مثلاً anonymous). نتعامل مع الحالة.
    if not message.from_user:
        await message.reply("❌ لا يمكن التحقق من هويتك — أرسل الأمر من حسابك الشخصي.")
        return

    # تحقق إن المرسل مشرف
    sender_id = message.from_user.id
    if not await is_user_admin(message.chat.id, sender_id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر. (فقط المشرفون مسموح لهم)")
        return

    text = message.text.strip()

    # --- بدأ التسجيل ---
    if text.startswith("سجل المحادثة"):
        if is_recording:
            await message.reply("⚠️ يوجد تسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        # نحتفظ باسم ملف افتراضي. لاحقًا عند إضافة ميزة التسجيل الحقيقية، نكتب الملف الفعلي هنا.
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.ogg"
        is_recording = True

        await message.reply(f"🎙 ✅ بدأ التسجيل بعنوان: {title}\n(الحالة: تسجيل مفعل)")

        # ملاحظة: هنا **لن** نبدأ تسجيلًا فعليًا الآن — هذه النقطة نربطها لاحقًا بـ pytgcalls أو py-tgcalls.

    # --- إيقاف التسجيل ---
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        # في هذه النسخة الاختبارية: إذا كان ملف التسجيل موجودًا فعليًا على القرص سيرسل، وإلا سيرسل رسالة مؤقتة.
        caption = (f"🎙 التسجيل: {current_title}\n"
                   f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                   f"👥 المجموعة: {GROUP_ID}")

        # إذا الملف موجود ارسله كـ voice (ogg) أو كملف عادي
        if os.path.exists(current_file):
            try:
                # إرسال كـ voice (احتفظ بنفس الصيغة)
                await app.send_voice(CHANNEL_ID, voice=current_file, caption=caption)
                # نمسح الملف بعد الإرسال إن رغبت
                os.remove(current_file)
                await message.reply(f"✅ تم إيقاف التسجيل وإرساله للقناة: {current_title}")
            except Exception as e:
                await message.reply(f"❌ فشل إرسال الملف: {e}")
        else:
            # لا توجد ملف فعلي — نكتفي بإعلام المشرف بأن التسجيل أوقف وإرسال وصف للأرشفة
            await app.send_message(CHANNEL_ID, f"📌 (سجل تلقائي) {caption}\n— ملاحظة: لا يوجد ملف فعلي في هذه النسخة.")
            await message.reply(f"✅ تم إيقاف التسجيل (لم يكن هناك ملف فعلي ليُرسل).")

# -----------------------------
# تشغيل اليوزربوت و Flask (health)
# -----------------------------
if __name__ == "__main__":
    # شغّل Flask في thread منفصل ليتحقق Render من أن الخدمة حية
    Thread(target=run_flask, daemon=True).start()

    print("✅ Starting userbot...")
    app.run()
