@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    # تأكد أن الرسالة من نفس المجموعة المطلوبة
    if str(message.chat.id) != str(GROUP_ID):
        return

    # لا تتعامل إلا مع الأوامر الخاصة بنا
    if not message.text.startswith(("سجل المحادثة", "أوقف التسجيل")):
        return  # تجاهل أي رسالة أخرى

    # --- التحقق من المرسل ---
    if not message.from_user:
        # أحياناً يكون المرسل مشرف مجهول أو عبر قناة
        try:
            member = await app.get_chat_member(message.chat.id, message.sender_chat.id)
            if member.status not in ("creator", "administrator"):
                await message.reply("❌ لا يمكن التحقق من هويتك — استخدم الأمر من حسابك الشخصي.")
                return
        except Exception:
            await message.reply("❌ لا يمكن التحقق من هويتك — أرسل الأمر من حسابك الشخصي.")
            return
    else:
        # تحقق من كونه مشرف أو مالك
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
