from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import asyncio

# متغيرات البيئة (سيتم وضعها في Render)
import os

SESSION_STRING = os.getenv("SESSION_STRING")
GROUP_ID = int(os.getenv("GROUP_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

app = Client("archiver_userbot", session_string=SESSION_STRING)

# قاموس مؤقت لتخزين البيانات أثناء المحادثة الخاصة
pending_audio = {}

# رصد الرسائل الصوتية في المجموعة
@app.on_message(filters.chat(GROUP_ID) & (filters.audio | filters.voice))
async def handle_audio(client: Client, message: Message):
    user = message.from_user

    # تحقق من أن المرسل مشرف
    member = await client.get_chat_member(GROUP_ID, user.id)
    if member.status not in ["administrator", "creator"]:
        return  # تجاهل غير المشرفين

    # حفظ الرسالة مؤقتًا
    pending_audio[user.id] = {
        "message": message,
        "title": message.audio.title if message.audio else None,
        "duration": message.audio.duration if message.audio else message.voice.duration,
    }

    # زر لإرسال المحادثة الخاصة للمشرف
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📩 افتح المحادثة الخاصة", url=f"https://t.me/{user.username}?start=archive")]]
    )
    await message.reply_text(
        "تم استلام المقطع الصوتي ✅\nاضغط الزر للمتابعة في المحادثة الخاصة.", 
        reply_markup=keyboard
    )

# رصد الرسائل الخاصة للمشرف بعد الضغط على الزر
@app.on_message(filters.private & filters.user(list(pending_audio.keys())))
async def private_interaction(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in pending_audio:
        return

    audio_info = pending_audio[user_id]
    state = audio_info.get("state", "ask_title")

    if state == "ask_title":
        await message.reply_text("📌 اكتب العنوان الجديد للمقطع الصوتي أو اكتب 'تخطي' للاحتفاظ بالعنوان الحالي.")
        audio_info["state"] = "waiting_title"
        return

    if state == "waiting_title":
        if message.text.lower() != "تخطي":
            audio_info["title"] = message.text
        audio_info["state"] = "ask_speaker"
        await message.reply_text("🗣️ اكتب اسم المتحدث الرئيسي في المقطع الصوتي:")
        return

    if state == "ask_speaker":
        audio_info["speaker"] = message.text
        # رفع المقطع للقناة بعد جمع البيانات
        msg = audio_info["message"]
        title = audio_info["title"] or "بدون عنوان"
        speaker = audio_info["speaker"]
        duration_min = audio_info["duration"] // 60
        group_name = (await client.get_chat(GROUP_ID)).title

        caption = f"""🎵 عنوان المقطع: {title}
🗣️ المتحدث: {speaker}
📅 التاريخ: الآن
⏱️ المدة: {duration_min} دقيقة
👥 المجموعة: {group_name}"""

        # رفع الصوت للقناة
        if msg.audio:
            await client.send_audio(CHANNEL_ID, audio=msg.audio.file_id, caption=caption)
        else:
            await client.send_voice(CHANNEL_ID, voice=msg.voice.file_id, caption=caption)

        # حذف الرسالة من المجموعة
        try:
            await msg.delete()
        except:
            pass

        await message.reply_text("✅ تم أرشفة المقطع وحذفه من المجموعة.")
        # إزالة من القاموس المؤقت
        pending_audio.pop(user_id)

@app.on_message(filters.command("start") & filters.private)
async def start_msg(client: Client, message: Message):
    await message.reply_text("مرحبًا! هذا البوت مسؤول عن أرشفة المقاطع الصوتية للمجموعة.")

print("Userbot جاهز للعمل")
app.run()
