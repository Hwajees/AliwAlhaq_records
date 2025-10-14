import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram.enums import ChatMembersFilter

# ==========================
# المتغيرات
# ==========================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")  # سلسلة الجلسة لليوزربوت

GROUP_ID = int(os.environ.get("GROUP_ID"))  # معرف المجموعة
CHANNEL_ID = os.environ.get("CHANNEL_ID")   # اسم القناة بدون @ مثال: AliwAlhaq_records

# ==========================
# إعداد اليوزربوت
# ==========================
app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# ==========================
# خادم وهمي لإرضاء Render
# ==========================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Userbot is running!")

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ==========================
# متغيرات تسجيل
# ==========================
is_recording = False
recording_name = ""

# ==========================
# تحقق من المشرف
# ==========================
sync def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

# ==========================
# معالجة الرسائل
# ==========================
@app.on_message(filters.group & filters.text)
async def handle_messages(client: Client, message: Message):
    global is_recording, recording_name

    user_id = message.from_user.id
    text = message.text.strip()

    # تحقق من المشرف
    if not await is_user_admin(message.chat.id, user_id):
        # تجاهل الأعضاء العاديين تماما
        return

    # أوامر التسجيل
    if text.startswith("سجل المحادثة"):
        recording_name = text.replace("سجل المحادثة", "").strip()
        if recording_name == "":
            recording_name = "تسجيل_بدون_اسم"
        is_recording = True
        await message.reply_text(f"✅ بدأ التسجيل: {recording_name}")
        return

    if text == "أوقف التسجيل":
        if not is_recording:
            await message.reply_text("❌ لم يتم بدء التسجيل مسبقاً.")
            return
        is_recording = False

        # بناء اسم الملف
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        file_name = f"{date_str}_{recording_name}.ogg"

        # إرسال ملف اختباري للقناة
        test_file = "test_audio.ogg"  # يجب وضع الملف في نفس مجلد المشروع
        try:
            await app.send_audio(CHANNEL_ID, test_file,
                                 caption=f"🎙 التسجيل: {recording_name}\n📅 التاريخ: {date_str}\n👥 المجموعة: {message.chat.id}")
            await message.reply_text(f"✅ تم إرسال التسجيل للقناة: {recording_name}")
        except Exception as e:
            await message.reply_text(f"❌ حدث خطأ أثناء إرسال الملف: {e}")
        return

# ==========================
# تشغيل اليوزربوت
# ==========================
app.run()

