import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
BOT_USERNAME = os.environ.get("BOT_USERNAME")  # اسم اليوزربوت بدون @

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# -----------------------------
# متغيرات مؤقتة
# -----------------------------
current_title = ""
current_file = ""

# -----------------------------
# دوال مساعدة
# -----------------------------
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

async def is_user_admin(chat_id, user_id):
    """يتأكد أن المرسل مشرف"""
    try:
        async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.user.id == user_id:
                return True
        return False
    except Exception as e:
        print("Error checking admin:", e)
        return False


# -----------------------------
# التعامل مع المقاطع الصوتية في المجموعة
# -----------------------------
@app.on_message(filters.chat(GROUP_ID) & (filters.audio | filters.voice))
async def handle_group_audio(client, message):
    """يتفاعل مع الصوت أو المقاطع الصوتية من المشرفين فقط"""
    user_id = message.from_user.id
    is_admin = await is_user_admin(GROUP_ID, user_id)
    if not is_admin:
        return

    # حفظ بيانات المقطع مؤقتاً
    global current_file, current_title
    current_title = message.audio.title if message.audio and message.audio.title else "تسجيل بدون عنوان"
    current_file = "test_audio.ogg"  # ملف تجريبي، لاحقاً نبدله بالفعلي

    # رد يحتوي الزر
    await message.reply_text(
        "تم استلام المقطع الصوتي ✅\nاضغط الزر للمتابعة في المحادثة الخاصة.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📥 المتابعة في الخاص",
                        url=f"https://t.me/{BOT_USERNAME}?start=archive"
                    )
                ]
            ]
        ),
    )


# -----------------------------
# أوامر الخاص
# -----------------------------
@app.on_message(filters.private & filters.command("start"))
async def handle_private_start(client, message):
    """يبدأ الأرشفة عندما يضغط المشرف على الزر"""
    if len(message.command) > 1 and message.command[1] == "archive":
        await message.reply_text("🎧 تم فتح جلسة الأرشفة.\nجاري تجهيز التسجيل...")
        test_file = "test_audio.ogg"

        if not os.path.exists(test_file):
            await message.reply_text("❌ لم يتم العثور على الملف الصوتي التجريبي (test_audio.ogg).")
            return

        try:
            caption = (
                f"🎙 التسجيل: {current_title}\n"
                f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"👤 المشرف: {message.from_user.first_name}\n"
                f"👥 المجموعة: {GROUP_ID}"
            )
            await app.send_audio(CHANNEL_ID, audio=test_file, caption=caption)
            await message.reply_text("✅ تمت الأرشفة بنجاح، تم إرسال الملف إلى القناة.")
        except Exception as e:
            await message.reply_text(f"❌ حدث خطأ أثناء الإرسال:\n{e}")
    else:
        await message.reply_text("👋 أهلاً! استخدم الزر من المجموعة لبدء الأرشفة.")


# -----------------------------
# Flask لتشغيل Render
# -----------------------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🚀 Starting userbot...")
    threading.Thread(target=run_flask).start()
    app.run()
