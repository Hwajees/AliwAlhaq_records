from pyrogram import Client, filters
from datetime import datetime
import os

# --- متغيرات البيئة ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))  # مثال: -1001234567890
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # مثال: @AliwAlhaq_records

# --- انشاء تطبيق Pyrogram ---
app = Client(
    name="userbot",
    session_string=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

# --- حالة التسجيل ---
recording = {}
current_file = ""

# --- التحقق من المشرف ---
async def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if member.user.id == user_id:
            return True
    return False

# --- استقبال الرسائل ---
@app.on_message(filters.chat(GROUP_ID))
async def handle_messages(client, message):
    user_id = message.from_user.id

    # فقط المشرف يمكنه التعامل
    if not await is_user_admin(message.chat.id, user_id):
        return  # تجاهل رسائل الأعضاء العاديين

    text = message.text or ""
    
    # بدء التسجيل
    if text.startswith("سجل المحادثة"):
        global current_file
        name = text.replace("سجل المحادثة", "").strip()
        if name == "":
            name = "تسجيل"
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{name}.ogg"
        recording[user_id] = current_file
        await message.reply(f"✅ بدأ التسجيل: {name}")

    # إيقاف التسجيل وإرسال الملف
    elif text.startswith("أوقف التسجيل"):
        if user_id in recording:
            file_path = recording[user_id]
            # هنا يجب إضافة كود حفظ التسجيل الصوتي أو التجريبي
            # لنرسل ملف اختبار مثلاً
            test_file = "testfile.ogg"
            try:
                await client.send_audio(CHANNEL_ID, test_file, caption=f"🎙 التسجيل: {file_path}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}")
                await message.reply(f"✅ تم إرسال التسجيل للقناة: {file_path}")
            except Exception as e:
                await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")
            del recording[user_id]

# --- إرسال ملف تجريبي عند /testfile ---
@app.on_message(filters.chat(GROUP_ID) & filters.command("testfile"))
async def send_test_file(client, message):
    user_id = message.from_user.id
    if not await is_user_admin(message.chat.id, user_id):
        return
    try:
        await client.send_audio(CHANNEL_ID, "testfile.ogg", caption="🔹 اختبار الإرسال من اليوزبوت")
        await message.reply("✅ تم إرسال الملف التجريبي للقناة.")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

# --- تشغيل البوت ---
app.run()
