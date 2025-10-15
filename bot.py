import sys
import os

# أضف مجلد libs إلى sys.path ليتمكن Python من إيجاد pytgcalls و tgcalls
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

from pyrogram import Client
from pytgcalls.pytgcalls import PyTgCalls  # استيراد PyTgCalls من المسار الجديد
# من tgcalls استورد ما تحتاجه لاحقًا إذا رغبت
# from tgcalls import TgCalls

# ======= إعداد المتغيرات من بيئة Render =======
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # إذا لاحقًا تحتاجه

# ======= إنشاء جلسة Pyrogram للـ Userbot =======
app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# ======= إنشاء PyTgCalls =======
pytgcalls = PyTgCalls(app)

# ======= أوامر بسيطة للاختبار =======
@app.on_message()
async def test(client, message):
    if message.text == "/joinvc":
        await pytgcalls.join_group_call(GROUP_ID, "silence.mp3")
        await message.reply_text("تم الانضمام للمحادثة الصوتية ✅")
    elif message.text == "/leavevc":
        await pytgcalls.leave_group_call(GROUP_ID)
        await message.reply_text("تم الخروج من المحادثة الصوتية ✅")

# ======= تشغيل البوت =======
app.run()
