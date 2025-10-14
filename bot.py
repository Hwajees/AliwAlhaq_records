import os
from datetime import datetime
from pyrogram import Client, filters

# -----------------------------
# إعدادات من المتغيرات البيئية (Render)
# -----------------------------
# تأكد أنك أضفت هذه المتغيرات في إعدادات الخدمة على Render
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

# يمكن أن يكون CHANNEL_ID رقماً (مثل -100123...) أو اسم المستخدم للقناة "@MyChannel"
CHANNEL_ID_RAW = os.environ.get("CHANNEL_ID")

# يمكن أن يكون GROUP_ID رقماً (مثل -100123...) أو اسم المستخدم للمجموعة "@mygroup"
GROUP_ID_RAW = os.environ.get("GROUP_ID")

# تحويل القيم الرقمية إلى int (إن أمكن) وإلا نتركها كسلاسل (username)
def parse_peer(raw):
    if raw is None:
        return None
    raw = raw.strip()
    # لو يبدأ بـ @ نتركه كسلسلة
    if raw.startswith("@"):
        return raw
    # محاولة تحويل إلى int
    try:
        return int(raw)
    except Exception:
        return raw

CHANNEL_ID = parse_peer(CHANNEL_ID_RAW)
GROUP_ID = parse_peer(GROUP_ID_RAW)

# -----------------------------
# إنشاء اليوزربوت (Client)
# -----------------------------
# نستخدم session name "userbot" مع session_string (تحويل حساب حقيقي لـ userbot)
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# -----------------------------
# متغيرات حالة التسجيل
# -----------------------------
is_recording = False
current_title = None
current_file = None  # مسار الملف المحلي (.ogg) الذي سنرفع منه

# اسم ملف الاختبار الموجود داخل المشروع (رفعته انت: test_audio.ogg)
TEST_FILE = "test_audio.ogg"

# -----------------------------
# دوال مساعدة
# -----------------------------
async def is_user_admin(chat_id, user_id):
    """
    تحقق إن كان user_id مشرف أو منشئ في chat_id.
    نستخدم get_chat_member للحصول على الحالة مباشرة (لا نستخدم filters خاطئة).
    """
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        # أي خطأ نعتبره ليس مشرفاً
        return False

def make_caption(title, group_id):
    return (
        f"🎙 التسجيل: {title}\n"
        f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"👥 المجموعة: {group_id}"
    )

# -----------------------------
# التعامل مع أوامر داخل المجموعة المحددة فقط
# -----------------------------
# نستخدم filters.chat(GROUP_ID) — يعمل سواء كان Group ID رقماً أو username
@app.on_message(filters.chat(GROUP_ID) & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    # تأكد أن الرسالة من مستخدم فعلي (ليس قناة/بوت)
    if not message.from_user:
        return

    user_id = message.from_user.id
    text = (message.text or "").strip()

    # فقط المشرفين يسمح لهم بالأوامر — الأعضاء العاديون *لا* يُرد عليهم إطلاقًا
    if not await is_user_admin(message.chat.id, user_id):
        return  # تجاهل تام للأعضاء العاديين

    # --- أمر: بدء التسجيل ---
    # الشكل: "سجل المحادثة" أو "سجل المحادثة <العنوان>"
    if text.startswith("سجل المحادثة"):
        # إذا كان تسجيل جارٍ لا نبدأ آخر
        if is_recording:
            await message.reply_text("⚠️ التسجيل جارٍ بالفعل!")
            return

        # استخراج العنوان (إن وُجب)
        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        # نعين الملف الحالي إلى ملف الاختبار (في المستقبل ستحل محله ملف التسجيل الحقيقي)
        current_title = title
        current_file = os.path.join(os.getcwd(), TEST_FILE)
        is_recording = True

        await message.reply_text(f"✅ بدأ التسجيل: {title}")
        return

    # --- أمر: إيقاف التسجيل ---
    # الشكل: "أوقف التسجيل"
    if text == "أوقف التسجيل":
        if not is_recording:
            await message.reply_text("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        # نتحقق أن الملف موجود وحجمه > 0
        if not current_file or not os.path.exists(current_file):
            await message.reply_text("❌ حدث خطأ: ملف التسجيل غير موجود على الخادم.")
            # نعيد حالة التسجيل إلى False حتى لا نعلق
            is_recording = False
            current_title = None
            current_file = None
            return

        size = os.path.getsize(current_file)
        if size == 0:
            await message.reply_text("❌ حدث خطأ: حجم الملف يساوي 0 بايت.")
            is_recording = False
            current_title = None
            current_file = None
            return

        # نحاول إرسال الملف إلى القناة — يمكن CHANNEL_ID أن يكون رقمياً أو username
        try:
            caption = make_caption(current_title, message.chat.id)

            # أفضل خيار هنا: نرسل الملف كـ document لكي يبقى كما هو (.ogg)
            await app.send_document(
                chat_id=CHANNEL_ID,
                document=current_file,
                caption=caption
            )

            await message.reply_text(f"✅ تم إرسال التسجيل للقناة: {current_title}")

        except Exception as e:
            # نُظهر للمشرف سبب الفشل
            await message.reply_text(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

        # إعادة تعيين المتغيرات
        is_recording = False
        current_title = None
        current_file = None
        return

    # --- أمر اختياري لإرسال ملف الاختبار يدوياً (/testfile) ---
    # مفيد للاختبار: المشرف يكتب /testfile في الجروب فيرسل الملف للتأكد
    if text == "/testfile":
        # فقط للمشرف
        try:
            file_path = os.path.join(os.getcwd(), TEST_FILE)
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                await message.reply_text("❌ ملف الاختبار غير موجود أو فارغ على الخادم.")
                return

            await app.send_document(chat_id=CHANNEL_ID, document=file_path,
                                    caption=f"🔹 اختبار الإرسال من اليوزربوت\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            await message.reply_text("✅ تم إرسال الملف التجريبي للقناة.")
        except Exception as e:
            await message.reply_text(f"❌ حدث خطأ أثناء إرسال الملف: {e}")
        return

    # إن وصلت إلى هنا: لا نفعل أي شيء مع رسائل المشرف غير الأوامر أعلاه
    return

# -----------------------------
# تشغيل اليوزربوت
# -----------------------------
if __name__ == "__main__":
    print("✅ Starting userbot...")
    app.run()
