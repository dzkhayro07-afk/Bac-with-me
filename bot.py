import os
import logging
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

BRANCHES = {
    "تسيير_واقتصاد": {
        "label": "تسيير واقتصاد 📊",
        "subjects": ["اقتصاد", "محاسبة", "قانون", "رياضيات", "فلسفة", "تاريخ وجغرافيا", "عربية", "فرنسية", "تربية إسلامية"]
    },
    "علوم_تجريبية": {
        "label": "علوم تجريبية 🔬",
        "subjects": ["رياضيات", "فيزياء", "علوم طبيعية", "فلسفة", "عربية", "فرنسية", "تربية إسلامية"]
    },
    "رياضيات": {
        "label": "رياضيات 📐",
        "subjects": ["رياضيات", "فيزياء", "علوم طبيعية", "فلسفة", "عربية", "فرنسية", "تربية إسلامية"]
    },
    "تقني_رياضي": {
        "label": "تقني رياضي ⚙️",
        "subjects": ["رياضيات", "فيزياء", "تكنولوجيا", "فلسفة", "عربية", "فرنسية", "تربية إسلامية"]
    },
    "آداب_وفلسفة": {
        "label": "آداب وفلسفة 📚",
        "subjects": ["فلسفة", "عربية", "تاريخ وجغرافيا", "علم الاجتماع", "فرنسية", "تربية إسلامية"]
    },
    "لغات_أجنبية": {
        "label": "لغات أجنبية 🌐",
        "subjects": ["فرنسية", "إنجليزية", "إسبانية", "ألمانية", "فلسفة", "عربية", "تربية إسلامية"]
    },
}

DZEXAM_URL = "https://www.dzexams.com/ar/bac"
user_states = {}

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 ابدأ موضوعاً جديداً", callback_data="choose_branch")],
        [InlineKeyboardButton("🌐 مواضيع رسمية - DzExams", url=DZEXAM_URL)],
        [InlineKeyboardButton("ℹ️ كيف يعمل البوت؟", callback_data="help")],
    ])

def branches_keyboard():
    buttons = []
    for key, val in BRANCHES.items():
        buttons.append([InlineKeyboardButton(val["label"], callback_data=f"branch_{key}")])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def subjects_keyboard(branch_key):
    subjects = BRANCHES[branch_key]["subjects"]
    buttons = []
    for s in subjects:
        buttons.append([InlineKeyboardButton(s, callback_data=f"subject_{branch_key}_{s}")])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="choose_branch")])
    return InlineKeyboardMarkup(buttons)

def after_topic_keyboard(subject):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 تصحيح رسمي على DzExams", url=DZEXAM_URL)],
        [InlineKeyboardButton("🔄 موضوع آخر", callback_data="choose_branch")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back_main")],
    ])

def generate_topic(branch_label, subject):
    prompt = f"""أنت أستاذ متخصص في إعداد مواضيع بكالوريا الجزائر.
اكتب موضوعاً كاملاً لمادة {subject} لشعبة {branch_label} على غرار مواضيع البكالوريا الجزائرية الحقيقية.
الموضوع يجب أن يحتوي على:
- جزء نظري بأسئلة متدرجة في الصعوبة
- وضعية إدماجية أو تمرين تطبيقي
- سلم التنقيط لكل سؤال (المجموع 20 نقطة)
اكتب الموضوع فقط بدون أي مقدمة أو تعليق."""
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def correct_answer(branch_label, subject, topic, student_answer, image_content=None):
    prompt = f"""أنت مصحح متخصص في بكالوريا الجزائر، شعبة {branch_label}، مادة {subject}.
الموضوع: {topic}
إجابة الطالب: {student_answer}
صحح الإجابة وأعطِ:
📊 التقييم: [X/20]
✅ ما أجاد فيه:
❌ الأخطاء والنقائص:
💡 نصائح للتحسين:
🌐 للتصحيح الرسمي: {DZEXAM_URL}"""
    if image_content:
        messages = [{"role": "user", "content": [image_content, {"type": "text", "text": prompt}]}]
    else:
        messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1500,
        messages=messages
    )
    return response.content[0].text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎓 أهلاً {user.first_name}!\n\n"
        "أنا بوت مساعدك في التحضير لبكالوريا الجزائر 🇩🇿\n\n"
        "• 📝 أولّد مواضيع لجميع الشعب والمواد\n"
        "• ✅ أصحح إجابتك (نص أو صورة)\n"
        "• 🌐 أوجهك للتصحيح الرسمي على DzExams\n\n"
        "اختر ما تريد:",
        reply_markup=main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "back_main":
        await query.edit_message_text("اختر ما تريد:", reply_markup=main_keyboard())
    elif data == "help":
        await query.edit_message_text(
            "📖 كيف يعمل البوت:\n\n"
            "1️⃣ اختر شعبتك\n"
            "2️⃣ اختر المادة\n"
            "3️⃣ يولّد البوت موضوعاً بالذكاء الاصطناعي\n"
            "4️⃣ حل الموضوع على ورقة\n"
            "5️⃣ ابعث إجابتك نصاً أو صورة\n"
            "6️⃣ البوت يصحح ويعطيك نقطة ومراجعة\n"
            "7️⃣ رابط للتصحيح الرسمي على DzExams\n\n"
            "بالتوفيق! 🎯",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]])
        )
    elif data == "choose_branch":
        await query.edit_message_text("📚 اختر شعبتك:", reply_markup=branches_keyboard())
    elif data.startswith("branch_"):
        branch_key = data.replace("branch_", "")
        branch_label = BRANCHES[branch_key]["label"]
        await query.edit_message_text(f"اخترت: {branch_label}\n\nاختر المادة:", reply_markup=subjects_keyboard(branch_key))
    elif data.startswith("subject_"):
        parts = data.split("_", 2)
        branch_key = parts[1]
        subject = parts[2]
        branch_label = BRANCHES[branch_key]["label"]
        await query.edit_message_text(f"⏳ جاري توليد موضوع {subject}...")
        try:
            topic = generate_topic(branch_label, subject)
            user_states[user_id] = {"waiting_answer": True, "subject": subject, "branch": branch_label, "topic": topic}
            await query.edit_message_text(
                f"📝 موضوع {subject} - شعبة {branch_label}\n\n{topic}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "✏️ حل الموضوع ثم أرسل إجابتك (نص أو صورة)",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 مواضيع رسمية DzExams", url=DZEXAM_URL)]])
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ حدث خطأ، حاول مرة أخرى.", reply_markup=main_keyboard())

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)
    if not state or not state.get("waiting_answer"):
        await update.message.reply_text("ابدأ أولاً باختيار موضوع 👇", reply_markup=main_keyboard())
        return
    subject = state["subject"]
    branch = state["branch"]
    topic = state["topic"]
    student_answer = ""
    image_content = None
    if update.message.photo:
        await update.message.reply_text("📸 تم استلام صورتك... جاري التصحيح ⏳")
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        import httpx, base64
        async with httpx.AsyncClient() as http_client:
            resp = await http_client.get(file.file_path)
            image_data = base64.b64encode(resp.content).decode()
        image_content = {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}}
        student_answer = update.message.caption or "الإجابة في الصورة"
    elif update.message.text:
        student_answer = update.message.text
        await update.message.reply_text("📝 تم استلام إجابتك... جاري التصحيح ⏳")
    else:
        await update.message.reply_text("⚠️ يرجى إرسال نص أو صورة.")
        return
    try:
        correction = correct_answer(branch, subject, topic, student_answer, image_content)
    except Exception as e:
        logger.error(f"Error: {e}")
        correction = "❌ حدث خطأ أثناء التصحيح، حاول مرة أخرى."
    user_states[user_id] = {"waiting_answer": False}
    await update.message.reply_text(f"📋 تصحيح موضوع {subject}\n\n{correction}", reply_markup=after_topic_keyboard(subject))

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    app.add_handler(MessageHandler(filters.PHOTO, handle_answer))
    logger.info("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
