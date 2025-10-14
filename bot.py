import os
from pyrogram import Client

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH"))
SESSION_STRING = os.environ.get("SESSION_STRING")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# -----------------------------
# إرسال ملف صوتي للقناة مباشرة
# -----------------------------
async def main():
    await app.start()
    await app.send_message(CHANNEL_ID, "🔹 اختبار الإرسال من اليوزبوت")
    await app.send_audio(CHANNEL_ID, "test_audio.ogg", caption="🔹 اختبار إرسال ملف صوتي")
    await app.stop()
    print("تم إرسال الرسالة والملف بنجاح ✅")

app.run(main())
