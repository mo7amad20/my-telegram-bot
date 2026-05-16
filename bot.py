import os
import logging
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# تشغيل التسجيل للأخطاء
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# قراءة التوكن من متغيرات البيئة (GitHub Secrets)
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# متغير لحالة كتم المجموعة
group_muted = False

# ------------------- أوامر البوت -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /start - يظهر لوحة التحكم للمشرفين فقط"""
    
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "🤖 **مرحباً! أنا بوت إدارة المجموعات**\n\n"
            "لتفعيل البوت في مجموعتك:\n"
            "1. أضفني إلى مجموعتك\n"
            "2. ارفعني مشرف\n"
            "3. اكتب /panel\n\n"
            "👑 فقط المشرفين يستطيعون استخدام أوامري"
        )
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    try:
        user_status = await context.bot.get_chat_member(chat_id, user_id)
        if user_status.status not in ["administrator", "creator"]:
            await update.message.delete()
            return
    except Exception as e:
        logging.error(f"خطأ: {e}")
        return
    
    await show_panel(update, context)

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /panel - يعرض لوحة التحكم"""
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if update.effective_chat.type == "private":
        await update.message.reply_text("هذا الأمر يعمل فقط في المجموعات")
        return
    
    try:
        user_status = await context.bot.get_chat_member(chat_id, user_id)
        if user_status.status not in ["administrator", "creator"]:
            await update.message.delete()
            return
    except Exception as e:
        logging.error(f"خطأ: {e}")
        return
    
    await show_panel(update, context)

async def show_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض لوحة التحكم بالأزرار"""
    
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
        "🎛️ **لوحة تحكم المشرف** 🎛️\n\nاختر الأمر الذي تريد تنفيذه:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# ------------------- معالجة الأزرار -------------------

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنفيذ عند الضغط على زر"""
    
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    try:
        user_status = await context.bot.get_chat_member(chat_id, user_id)
        if user_status.status not in ["administrator", "creator"]:
            await query.edit_message_text("⛔ هذا الأمر للمشرفين فقط!")
            return
    except:
        await query.edit_message_text("⛔ لا يمكن التحقق من صلاحياتك")
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
    elif data == "back_to_menu":
        await back_to_menu(query, context)

async def mute_group_action(query, context):
    """كتم المجموعة"""
    global group_muted
    group_muted = True
    await query.edit_message_text(
        "🔇 **تم كتم المجموعة بالكامل!**\n\nلا أحد يستطيع الإرسال حالياً.",
        parse_mode="HTML"
    )

async def unmute_group_action(query, context):
    """فك كتم المجموعة"""
    global group_muted
    group_muted = False
    await query.edit_message_text(
        "🔊 **تم فك كتم المجموعة!**\n\nالجميع يستطيع الإرسال الآن.",
        parse_mode="HTML"
    )

async def show_admins_list(query, context):
    """عرض قائمة المشرفين"""
    chat_id = query.message.chat.id
    
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        admin_list = []
        
        for admin in admins:
            name = admin.user.full_name
            if admin.status == "creator":
                name = f"👑 {name} (المالك)"
            else:
                name = f"👤 {name}"
            admin_list.append(name)
        
        text = "👥 **قائمة المشرفين:**\n\n" + "\n".join(admin_list)
        await query.edit_message_text(text, parse_mode="HTML")
    except Exception as e:
        await query.edit_message_text(f"خطأ: {e}")

async def bot_info_action(query, context):
    """معلومات البوت"""
    bot_info = await context.bot.get_me()
    await query.edit_message_text(
        f"🤖 **معلومات البوت:**\n\n"
        f"📛 الاسم: {bot_info.first_name}\n"
        f"🔗 المعرف: @{bot_info.username}\n\n"
        f"📌 **الميزات:**\n"
        f"• الترحيب بالأعضاء الجدد مع منشن\n"
        f"• كتم الأعضاء الجدد تلقائياً\n"
        f"• كتم وفك كتم المجموعة\n"
        f"• منع الأعضاء من التواصل مع البوت\n\n"
        f"👑 فقط المشرفين يستطيعون استخدام هذه الأوامر",
        parse_mode="HTML"
    )

async def test_welcome_action(query, context):
    """تجربة الترحيب"""
    user = query.from_user
    await query.edit_message_text(
        f"🎉 **هذه رسالة ترحيب تجريبية** 🎉\n\n"
        f"{user.mention_html()}\n\n"
        f"✨ هذا شكل الترحيب الذي سيراه العضو الجديد",
        parse_mode="HTML"
    )

async def back_to_menu(query, context):
    """العودة للقائمة الرئيسية"""
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
        "🎛️ **لوحة تحكم المشرف** 🎛️\n\nاختر الأمر الذي تريد تنفيذه:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# ------------------- الترحيب بالأعضاء الجدد -------------------

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الترحيب بالأعضاء الجدد وكتمهم"""
    
    for new_member in update.message.new_chat_members:
        welcome_text = (
            f"🎉 **أهلاً وسهلاً بك** 🎉\n\n"
            f"{new_member.mention_html()}\n\n"
            f"✨ نورتنا في جروب مملكة دارين✨\n"
            f"📌 تم كتم صوتك تلقائياً"
        )
        
        await update.message.reply_text(welcome_text, parse_mode="HTML")
        
        # كتم العضو الجديد
        permissions = ChatPermissions(can_send_messages=False)
        
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=new_member.id,
            permissions=permissions
        )

# ------------------- منع الأعضاء العاديين -------------------

async def block_non_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منع الأعضاء العاديين من استخدام البوت"""
    
    if update.effective_chat.type == "private":
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    try:
        user_status = await context.bot.get_chat_member(chat_id, user_id)
        
        if user_status.status not in ["administrator", "creator"]:
            if update.message.text and update.message.text.startswith('/'):
                await update.message.delete()
    except:
        pass

# ------------------- تشغيل البوت -------------------

def main():
    if not BOT_TOKEN:
        print("❌ خطأ: لم يتم العثور على التوكن!")
        print("تأكد من وجود BOT_TOKEN في متغيرات البيئة")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel_command))
    
    # الأزرار
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # الترحيب
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # منع الأعضاء العاديين
    app.add_handler(MessageHandler(filters.COMMAND, block_non_admin))
    
    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == '__main__':
    main()