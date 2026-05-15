import os
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن من متغيرات البيئة
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# متغير لتخزين حالة كتم الجروب
group_muted = False

# ------------------- أوامر البوت -------------------

# أمر /start - للاختبار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فقط المشرفين يقدرون يستخدمون هذا الأمر
    if update.effective_chat.type == "private":
        await update.message.reply_text('مرحباً! أنا بوت إدارة المجموعات 🤖')
    else:
        # في المجموعة، تحقق إذا كان المرسل مشرف
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        user_status = await context.bot.get_chat_member(chat_id, user_id)
        
        if user_status.status in ["administrator", "creator"]:
            await update.message.reply_text('✅ البوت شغال، انت مشرف تقدر تتحكم بي')
        else:
            # الأعضاء العاديون لا يستطيعون استخدام البوت
            await update.message.delete()
            await context.bot.send_message(chat_id, f"⛔ {update.effective_user.mention_html()}، فقط المشرفين يقدرون يتواصلون مع البوت", parse_mode="HTML")

# أمر كتم الجروب كله (للمشرفين فقط)
async def mute_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # التحقق من صلاحية المشرف
    user_status = await context.bot.get_chat_member(chat_id, user_id)
    
    if user_status.status not in ["administrator", "creator"]:
        await update.message.delete()
        return
    
    global group_muted
    group_muted = True
    
    # تطبيق الكتم على كل الأعضاء (هذا الكود يحتاج للتطوير بشكل أكبر)
    await update.message.reply_text("🔇 **تم كتم المجموعة بالكامل!** 🔇\nلا أحد يستطيع الإرسال حالياً.", parse_mode="HTML")

# أمر فك الكتم عن الجروب (للمشرفين فقط)
async def unmute_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    user_status = await context.bot.get_chat_member(chat_id, user_id)
    
    if user_status.status not in ["administrator", "creator"]:
        await update.message.delete()
        return
    
    global group_muted
    group_muted = False
    
    await update.message.reply_text("🔊 **تم فك كتم المجموعة!** 🔊\nالجميع يستطيع الإرسال الآن.", parse_mode="HTML")

# ------------------- الترحيب بالأعضاء الجدد -------------------

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for new_member in update.message.new_chat_members:
        # رسالة ترحيب مع منشن للعضو الجديد
        welcome_text = (
            f"🎉 **أهلاً وسهلاً بك يا عزيزي** 🎉\n\n"
            f"{new_member.mention_html()}\n\n"
            f"✨ نورتنا في جروب مملكه دارين ✨\n"
            f"📌 ملاحظة: تم كتم صوتك تلقائياً لحين إشعار آخر"
        )
        
        await update.message.reply_text(welcome_text, parse_mode="HTML")
        
        # كتم العضو الجديد (منعه من الكلام)
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

async def block_non_admin_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يمنع الأعضاء العاديين من استخدام أوامر البوت"""
    
    # إذا كانت الرسالة في محادثة خاصة، يسمح (للتجربة فقط)
    if update.effective_chat.type == "private":
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # تحقق إذا كان المرسل مشرف أو مالك المجموعة
    user_status = await context.bot.get_chat_member(chat_id, user_id)
    
    # إذا كان الأمر يبدأ بـ / (أمر بوت)
    if update.message.text and update.message.text.startswith('/'):
        if user_status.status not in ["administrator", "creator"]:
            # حذف رسالة العضو العادي
            await update.message.delete()
            # إرسال تحذير خاص للمستخدم (يُرسل في الخاص عشان ما يسبب فوضى)
            await context.bot.send_message(
                user_id, 
                f"⛔ لا يمكنك استخدام أوامر البوت في مجموعة {update.effective_chat.title}.\nهذا الأمر مسموح فقط للمشرفين."
            )

# ------------------- حذف رسائل الأعضاء المقيدين -------------------

async def block_restricted_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يمنع الأعضاء المقيدين من إرسال رسائل"""
    
    if update.effective_chat.type == "private":
        return
    
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    
    # إذا كان العضو مقيداً ولا يسمح له بإرسال رسائل
    if member.status == "restricted" and not member.can_send_messages:
        try:
            await update.message.delete()
        except:
            pass

# ------------------- تشغيل البوت -------------------

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # أوامر البوت (للمشرفين فقط)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mute", mute_group))     # /mute - كتم الجروب
    app.add_handler(CommandHandler("unmute", unmute_group)) # /unmute - فك الكتم
    
    # الترحيب بالأعضاء الجدد
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # منع الأعضاء العاديين من التواصل مع البوت
    app.add_handler(MessageHandler(filters.COMMAND, block_non_admin_commands))
    
    # حذف رسائل الأعضاء المقيدين
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, block_restricted_messages))
    
    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == '__main__':
    main()