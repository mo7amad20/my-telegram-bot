import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# راح نجيب التوكن من متغيرات البيئة
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('مرحباً! أنا بوتك شغال على GitHub 🚀')

# أمر /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('الأوامر المتاحة:\n/start - بدء المحادثة\n/help - المساعدة')

# تشغيل البوت
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == '__main__':
    main()
