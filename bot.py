import os
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# متغير لتخزين حالة كتم الجروب
group_muted = False

# ------------------- قائمة الأوامر (للمشرفين فقط) -------------------

async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تظهر قائمة الأوامر للمشرفين فقط"""
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # التحقق إذا كان المرسل مشرف
    user_status = await context.bot.get_chat_member(chat_id, user_id)
    
    if user_status.status not in ["administrator", "creator"]:
        # الأعضاء العاديون ما يشوفون شي
        await update.message.delete()
        return
    
    # تصميم الأزرار
    keyboard = [
        [
            InlineKeyboardButton("🔇 كتم المجموعة", callback_data="mute_group"),
            InlineKeyboardButton("🔊 فك الكتم", callback_data="unmute_group")
        ],
        [
            InlineKeyboardButton("📋 قائمة المشرفين", callback_data="admins_list"),
            InlineKeyboardButton("ℹ️ معلومات البوت", callback_data="bot_info")
        ],
        [
            InlineKeyboardButton("👋 تجربة الترحيب", callback_data="test_welcome")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎛️ **لوحة تحكم المشرف** 🎛️\n\n"
        "اختر الأمر الذي تريد تنفيذه من الأزرار أدناه:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# ------------------- معالجة الضغط على الأزرار -------------------

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تتنفذ عندما يضغط المشرف على زر"""
    
    query = update.callback_query
    await query.answer()  # إشعار للمستخدم أن الزر تم الضغط عليه
    
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    # التأكد أن المستخدم مشرف
    user_status = await context.bot.get_chat_member(chat_id, user_id)
    
    if user_status.status not in ["administrator", "creator"]:
        await query.edit_message_text("⛔ هذا الأمر مسموح فقط للمشرفين!")
        return
    
    data = query.data
    
    if data == "mute_group":
        await mute_group_action(query, context)
    
    elif data == "unmute_group":
        await unmute_group_action(query, context)
    
    elif data == "admins_list":
        await show_admins_list(query, context)
    
    elif data == "bot_info":
        await bot_info_action(query, context)
    
    elif data == "test_welcome":
        await test_welcome_action(query, context)

# ------------------- تنفيذ الأوامر -------------------

async def mute_group_action(query, context):
    """تنفيذ كتم المجموعة"""
    global group_muted
    group_muted = True
    
    await query.edit_message_text(
        "🔇 **تم كتم المجموعة بالكامل!** 🔇\n\n"
        "لا أحد يستطيع الإرسال حالياً.\n"
        "لإلغاء الكتم، اضغط على زر 'فك الكتم'",
        parse_mode="HTML"
    )

async def unmute_group_action(query, context):
    """تنفيذ فك الكتم"""
    global group_muted
    group_muted = False
    
    await query.edit_message_text(
        "🔊 **تم فك كتم المجموعة!** 🔊\n\n"
        "الجميع يستطيع الإرسال الآن.\n"
        "لإعادة الكتم، اضغط على زر 'كتم المجموعة'",
        parse_mode="HTML"
    )

async def show_admins_list(query, context):
    """عرض قائمة المشرفين في المجموعة"""
    chat_id = query.message.chat.id
    
    admins = await context.bot.get_chat_administrators(chat_id)
    admins_list = []
    
    for admin in admins:
        name = admin.user.full_name
        if admin.status == "creator":
            name = f"👑 {name} (المالك)"
        else:
            name = f"👤 {name}"
        admins_list.append(name)
    
    admins_text = "\n".join(admins_list)
    
    await query.edit_message_text(
        f"👥 **قائمة المشرفين في المجموعة:**\n\n{admins_text}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")
        ]])
    )

async def bot_info_action(query, context):
    """عرض معلومات عن البوت"""
    bot_info = await context.bot.get_me()
    
    await query.edit_message_text(
        f"🤖 **معلومات البوت:**\n\n"
        f"📛 الاسم: {bot_info.first_name}\n"
        f"🔗 المعرف: @{bot_info.username}\n\n"
        f"📌 **الميزات:**\n"
        f"• الترحيب بالأعضاء الجدد مع منشن\n"
        f"• كتم الأعضاء الجدد تلقائياً\n"
        f"• كتم/فك كتم المجموعة\n"
        f"• منع الأعضاء من التواصل مع البوت\n\n"
        f"👑 فقط المشرفين يستطيعون استخدام هذه الأوامر",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")
        ]])
    )

async def test_welcome_action(query, context):
    """تجربة رسالة الترحيب"""
    user = query.from_user
    
    await query.edit_message_text(
        f"🎉 **هذه رسالة ترحيب تجريبية** 🎉\n\n"
        f"{user.mention_html()}\n\n"
        f"✨ هذا شكل الترحيب الذي سيراه العضو الجديد\n"
        f"📌 سيتم كتم العضو تلقائياً بعد الترحيب",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")
        ]])
    )

async def back_to_menu(query, context):
    """العودة إلى القائمة الرئيسية"""
    keyboard = [
        [
            InlineKeyboardButton("🔇 كتم المجموعة", callback_data="mute_group"),
            InlineKeyboardButton("🔊 فك الكتم", callback_data="unmute_group")
        ],
        [
            InlineKeyboardButton("📋 قائمة المشرفين", callback_data="admins_list"),
            InlineKeyboardButton("ℹ️ معلومات البوت", callback_data="bot_info")
        ],
        [
            InlineKeyboardButton("👋 تجربة الترحيب", callback_data="test_welcome")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎛️ **لوحة تحكم المشرف** 🎛️\n\n"
        "اختر الأمر الذي تريد تنفيذه من الأزرار أدناه:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# ------------------- الترحيب بالأعضاء الجدد -------------------

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for new_member in update.message.new_chat_members:
        # رسالة ترحيب مع منشن للعضو الجديد
        welcome_text = (
            f"🎉 **أهلاً وسهلاً بك يا عزيزي** 🎉\n\n"
            f"{new_member.mention_html()}\n\n"
            f"✨ نورتنا في جروب مملكة دارين✨\n"
            f"📌 ملاحظة: تم كتم صوتك تلقائياً لحين إشعار آخر"
        )
        
        await update.message.reply_text(welcome_text, parse_mode="HTML")
        
        # كتم العضو الجديد
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_audios=False,
            can_send_documents=False,
            can_send_photos=False,
            can_send_videos=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=new_member.id,
            permissions=permissions
        )

# ------------------- منع الأعضاء من التواصل مع البوت -------------------

async def block_non_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يمنع الأعضاء العاديين من استخدام البوت"""
    
    if update.effective_chat.type == "private":
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    user_status = await context.bot.get_chat_member(chat_id, user_id)
    
    # إذا كان عضو عادي
    if user_status.status not in ["administrator", "creator"]:
        # حذف رسالته إذا حاول يكلم البوت
        if update.message.text and (update.message.text.startswith('/') or update.message.text.startswith('@')):
            await update.message.delete()

# ------------------- حذف رسائل الأعضاء المقيدين -------------------

async def block_restricted_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return
    
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    
    if member.status == "restricted" and not member.can_send_messages:
        try:
            await update.message.delete()
        except:
            pass

# ------------------- أمر /start للمشرف فقط -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "🤖 **مرحباً! أنا بوت إدارة المجموعات**\n\n"
            "لتفعيل البوت في مجموعتك:\n"
            "1. أضفني إلى مجموعتك\n"
            "2. ارفعني مشرف\n"
            "3. اكتب الأمر /panel أو @bot_username"
        )
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    user_status = await context.bot.get_chat_member(chat_id, user_id)
    
    if user_status.status not in ["administrator", "creator"]:
        await update.message.delete()
        return
    
    await show_commands(update, context)

# ------------------- تشغيل البوت -------------------

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", show_commands))  # /panel يظهر القائمة
    
    # معالج الأزرار التفاعلية
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # الترحيب بالأعضاء الجدد
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # منع الأعضاء العاديين
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, block_non_admin))
    app.add_handler(MessageHandler(filters.COMMAND, block_non_admin))
    
    # حذف رسائل المقيدين
    app.add_handler(MessageHandler(filters.TEXT, block_restricted_messages))
    
    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == '__main__':
    main()