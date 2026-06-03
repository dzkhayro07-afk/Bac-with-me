import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8848085069:AAFfaUEJNerff2zXNI4DwBCjN5B-JWuDo1Y"

# دالة تجيب روابط PDF من dzexam
def get_bac_pdfs(subject, year):
    url = f"https://www.dzexam.com/{subject}-{year}-bac"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith(".pdf")]
    return links

# أمر عام: /bac subject year
async def bac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("استعمل الأمر هكذا: /bac المادة السنة\nمثال: /bac math 2023")
        return
    
    subject = context.args[0].lower()
    year = context.args[1]
    
    links = get_bac_pdfs(subject, year)
    if not links:
        await update.message.reply_text(f"ما لقيت مواضيع {subject} لسنة {year} 😕")
    else:
        for link in links:
            await update.message.reply_document(document=link)

# إعداد البوت
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("bac", bac))

app.run_polling()
