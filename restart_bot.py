import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')
REPO = "mo7amad20/my-telegram-bot"

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التحقق من أن المستخدم مشرف
    if update.effective_chat.type != "private":
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        user_status = await context.bot.get_chat_member(chat_id, user_id)
        
        if user_status.status not in ["administrator", "creator"]:
            await update.message.delete()
            return
    
    # إرسال طلب تشغيل workflow
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/bot.yml/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = '{"ref":"main"}'
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 204:
        await update.message.reply_text("✅ جاري إعادة تشغيل البوت... انتظر دقيقة ثم جرب /panel")
    else:
        await update.message.reply_text(f"❌ خطأ: {response.status_code}")

def main():
    if not BOT_TOKEN:
        print("❌ خطأ: BOT_TOKEN غير موجود")
        return
    if not GITHUB_TOKEN:
        print("❌ خطأ: GH_TOKEN غير موجود")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("restart", restart))
    
    print("✅ بوت إعادة التشغيل شغال...")
    app.run_polling()

if __name__ == '__main__':
    main()