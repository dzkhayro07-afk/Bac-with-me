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

TOPICS = {
    "اقتصاد": [
        {
            "year": 2023,
            "subject": "اقتصاد",
            "question": """موضوع البكالوريا 2023 - مادة الاقتصاد - شعبة تسيير واقتصاد

الجزء الأول: أسئلة الوضعية (12 نقطة)

السؤال الأول (6 نقاط):
1. عرّف التضخم وأذكر أسبابه الرئيسية. (2 نقطة)
2. ما الفرق بين التضخم المفرط والتضخم الزاحف؟ (2 نقطة)
3. ما هي الآثار الاقتصادية والاجتماعية للتضخم؟ (2 نقطة)

السؤال الثاني (6 نقاط):
1. عرّف مفهوم التخلف الاقتصادي. (1 نقطة)
2. اذكر ثلاثة مؤشرات للتخلف الاقتصادي. (1.5 نقطة)
3. ما هي العوامل المعيقة للتنمية الاقتصادية في الدول النامية؟ (2 نقطة)
4. ما هو دور الدولة في تحقيق التنمية الاقتصادية؟ (1.5 نقطة)

الجزء الثاني: وضعية إدماجية (8 نقاط)

النص: تواجه الجزائر تحديات اقتصادية جوهرية في ظل التقلبات الحادة لأسعار البترول، مما يستوجب التحول نحو تنويع مصادر الدخل الوطني وتحقيق التنمية المستدامة خارج إطار الريع البترولي.

1. حدد الإشكالية الاقتصادية المطروحة في النص. (1 نقطة)
2. ما المقصود بالاقتصاد الريعي؟ (1.5 نقطة)
3. ما هي بدائل النفط التي يمكن للجزائر الاعتماد عليها؟ (2.5 نقطة)
4. اقترح حلولاً لتحقيق التنمية الاقتصادية المستدامة. (3 نقاط)""",
            "correction": """التصحيح النموذجي - اقتصاد 2023

س1-1: التضخم هو الارتفاع المستمر والعام في المستوى العام للأسعار مع انخفاض القدرة الشرائية للنقود. أسبابه: زيادة الطلب الكلي، ارتفاع تكاليف الإنتاج، توسع الكتلة النقدية.

س1-2: التضخم الزاحف: ارتفاع بطيء أقل من 5%. التضخم المفرط: ارتفاع حاد يصعب السيطرة عليه أكثر من 50% شهرياً.

س1-3: الآثار الاقتصادية: إضعاف القوة الشرائية، تشويه الأسعار، تراجع الاستثمار. الاجتماعية: تدهور مستوى المعيشة، تفاقم الفقر.

س2-1: التخلف الاقتصادي: حالة يتسم فيها الاقتصاد بانخفاض مستوى الإنتاج والدخل الفردي.

س2-2: مؤشرات التخلف: انخفاض نصيب الفرد من الدخل، ارتفاع البطالة والأمية، ضعف البنية التحتية.

س2-3: العوامل المعيقة: الاستعمار وآثاره، ضعف رأس المال، الفساد الإداري.

س2-4: دور الدولة: رسم السياسات الاقتصادية، توفير البنية التحتية، تشجيع الاستثمار.

وضعية إدماجية:
1. الإشكالية: كيف تتجاوز الجزائر الاعتماد الأحادي على النفط؟
2. الاقتصاد الريعي: اقتصاد يعتمد على إيرادات الموارد الطبيعية بدلاً من الإنتاج.
3. البدائل: الفلاحة، السياحة، الصناعة التحويلية، الطاقات المتجددة.
4. الحلول: إصلاح التعليم، تحسين مناخ الاستثمار، مكافحة الفساد."""
        }
    ],
    "محاسبة": [
        {
            "year": 2023,
            "subject": "محاسبة",
            "question": """موضوع البكالوريا 2023 - مادة المحاسبة - شعبة تسيير واقتصاد

التمرين الأول (8 نقاط):
في 01/01/2023 أسست مؤسسة النور برأس مال 500,000 دج:
- حساب بنكي: 300,000 دج
- معدات: 150,000 دج
- بضاعة: 50,000 دج

العمليات:
1. 05/01: اشترت بضاعة بـ 80,000 دج، نصفها نقداً والباقي بالأجل.
2. 12/01: باعت بضاعة بـ 120,000 دج، 60,000 نقداً والباقي بالأجل.
3. 20/01: دفعت إيجار الشهر 15,000 دج نقداً.
4. 25/01: قبضت من الزبائن 30,000 دج بالبنك.
5. 28/01: سددت للموردين 20,000 دج نقداً.

المطلوب:
1. أنجز قيود اليومية. (5 نقاط)
2. افتح حسابات الأستاذ للصندوق والبنك والزبائن والموردون. (3 نقاط)

التمرين الثاني (12 نقاط):
الأرصدة في 31/12/2023:
- المبيعات: 850,000 دج
- مشتريات البضاعة: 520,000 دج
- مخزون أول المدة: 80,000 دج
- مخزون آخر المدة: 95,000 دج
- أجور الموظفين: 120,000 دج
- إيجار المحلات: 60,000 دج
- مصاريف النقل: 25,000 دج
- خسائر القيمة: 15,000 دج

المطلوب:
1. أنجز جدول حسابات النتائج. (6 نقاط)
2. احسب النتيجة الصافية. (2 نقطة)
3. قيد قفل حساب النتيجة. (4 نقاط)""",
            "correction": """التصحيح النموذجي - محاسبة 2023

قيود اليومية:
05/01: ح/المشتريات(380) 80,000 | ح/الصندوق(530) 40,000 | ح/الموردون(401) 40,000
12/01: ح/الصندوق(530) 60,000 | ح/الزبائن(411) 60,000 | ح/المبيعات(700) 120,000
20/01: ح/الإيجارات(613) 15,000 | ح/الصندوق(530) 15,000
25/01: ح/البنك(512) 30,000 | ح/الزبائن(411) 30,000
28/01: ح/الموردون(401) 20,000 | ح/الصندوق(530) 20,000

حسابات الأستاذ:
الصندوق: مدين 60,000 | دائن 75,000 | رصيد دائن 15,000
البنك: مدين 330,000 | رصيد مدين 330,000
الزبائن: مدين 60,000 | دائن 30,000 | رصيد مدين 30,000
الموردون: مدين 20,000 | دائن 40,000 | رصيد دائن 20,000

جدول النتائج:
تكلفة البضاعة = 80,000 + 520,000 - 95,000 = 505,000
مجموع الأعباء = 505,000 + 120,000 + 60,000 + 25,000 + 15,000 = 725,000
المبيعات = 850,000
النتيجة = 850,000 - 725,000 = 125,000 دج ربح"""
        }
    ],
    "قانون": [
        {
            "year": 2023,
            "subject": "قانون",
            "question": """موضوع البكالوريا 2023 - مادة القانون - شعبة تسيير واقتصاد

الجزء الأول (12 نقطة):
1. عرّف العقد وبيّن أركانه الأساسية. (3 نقاط)
2. ما الفرق بين البطلان المطلق والبطلان النسبي؟ (3 نقاط)
3. اذكر ثلاثة أنواع من الشركات التجارية مع تعريف كل منها. (4 نقاط)
4. ما هي الأوراق التجارية وأنواعها وشروط صحتها؟ (2 نقطة)

الجزء الثاني: وضعية إدماجية (8 نقاط)
أبرم كمال (19 سنة) عقدا مع سياح أجانب تحت الإكراه، حيث هددوه بالإبلاغ عنه إن رفض.

1. هل كمال أهل للتعاقد؟ (2 نقطة)
2. ما العيب الذي شاب إرادته؟ عرفه. (2 نقطة)
3. ما مصير العقد؟ (2 نقطة)
4. ما الإجراءات القانونية المتاحة لكمال؟ (2 نقطة)""",
            "correction": """التصحيح النموذجي - قانون 2023

1. العقد: اتفاق بين طرفين ينشئ التزامات. أركانه: الرضا، المحل، السبب، الأهلية.
2. البطلان المطلق: يمس النظام العام، لأي شخص التمسك به، لا يقبل الإجازة. البطلان النسبي: لحماية أحد الطرفين، قابل للإجازة.
3. الشركات: التضامن (مسؤولية شخصية كاملة)، التوصية البسيطة (متضامنون وموصون)، SARL (مسؤولية محدودة بالحصص).
4. الأوراق التجارية: الكمبيالة، السند الأذني، الشيك. شروطها: الكتابة، المبلغ، التاريخ، التوقيع.

وضعية إدماجية:
1. كمال 19 سنة = بلغ سن الرشد القانوني في الجزائر، هو أهل للتعاقد.
2. العيب: الإكراه = ضغط غير مشروع يُفقد الإرادة حريتها.
3. مصير العقد: قابل للإبطال (بطلان نسبي).
4. الإجراءات: رفع دعوى إبطال العقد، المطالبة بالتعويض، تقديم شكوى جزائية."""
        }
    ]
}

user_states = {}

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📝 ابدأ موضوعاً جديداً", callback_data="new_topic")],
        [InlineKeyboardButton("ℹ️ كيف يعمل البوت؟", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def subject_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 اقتصاد", callback_data="subject_اقتصاد")],
        [InlineKeyboardButton("🧾 محاسبة", callback_data="subject_محاسبة")],
        [InlineKeyboardButton("⚖️ قانون", callback_data="subject_قانون")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎓 أهلاً {user.first_name}!\n\n"
        "أنا بوت مساعدك في التحضير لبكالوريا تسيير واقتصاد 🇩🇿\n\n"
        "أستطيع:\n"
        "• إعطاءك مواضيع باكالوريا حقيقية\n"
        "• تصحيح إجابتك (نص أو صورة)\n"
        "• تقييمك مقارنةً بالتصحيح النموذجي\n\n"
        "اختر ما تريد:",
        reply_markup=main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "new_topic":
        await query.edit_message_text("📚 اختر المادة:", reply_markup=subject_keyboard())

    elif data == "help":
        await query.edit_message_text(
            "كيف يعمل البوت:\n\n"
            "1 - اختر مادة\n"
            "2 - سيعطيك البوت موضوع باكالوريا\n"
            "3 - حل الموضوع على ورقة\n"
            "4 - ابعث إجابتك نصاً أو صورة\n"
            "5 - البوت يصحح ويعطيك نقطة ومراجعة\n\n"
            "بالتوفيق في البكالوريا!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]])
        )

    elif data == "back_main":
        await query.edit_message_text("اختر ما تريد:", reply_markup=main_keyboard())

    elif data.startswith("subject_"):
        subject = data.replace("subject_", "")
        topic = TOPICS[subject][0]
        user_states[user_id] = {"waiting_answer": True, "subject": subject, "topic": topic}
        await query.edit_message_text(
            f"موضوع {subject} - بكالوريا {topic['year']}\n"
            f"شعبة: تسيير واقتصاد\n\n"
            f"{topic['question']}\n\n"
            "حل الموضوع ثم أرسل إجابتك هنا (نص أو صورة)"
        )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)

    if not state or not state.get("waiting_answer"):
        await update.message.reply_text("ابدأ أولاً باختيار موضوع 👇", reply_markup=main_keyboard())
        return

    topic = state["topic"]
    subject = state["subject"]
    student_answer = ""
    image_content = None

    if update.message.photo:
        await update.message.reply_text("تم استلام صورتك... جاري التصحيح ⏳")
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
        await update.message.reply_text("تم استلام إجابتك... جاري التصحيح ⏳")
    else:
        await update.message.reply_text("يرجى إرسال نص أو صورة.")
        return

    correction_prompt = f"""أنت مصحح متخصص في بكالوريا الجزائر، شعبة تسيير واقتصاد، مادة {subject}.

الموضوع: {topic['question']}

التصحيح النموذجي: {topic['correction']}

إجابة الطالب: {student_answer}

قيّم الإجابة وأعطِ:
1. نقطة من 20
2. ما أجاد فيه الطالب
3. الأخطاء والنقائص
4. ملاحظات للتحسين"""

    try:
        if image_content:
            messages = [{"role": "user", "content": [image_content, {"type": "text", "text": correction_prompt}]}]
        else:
            messages = [{"role": "user", "content": correction_prompt}]

        response = client.messages.create(model="claude-opus-4-20250514", max_tokens=1500, messages=messages)
        correction = response.content[0].text
    except Exception as e:
        logger.error(f"Error: {e}")
        correction = "حدث خطأ أثناء التصحيح، حاول مرة أخرى."

    user_states[user_id] = {"waiting_answer": False}
    await update.message.reply_text(
        f"تصحيح موضوع {subject}\n\n{correction}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("موضوع آخر", callback_data="new_topic")],
            [InlineKeyboardButton("القائمة الرئيسية", callback_data="back_main")]
        ])
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    app.add_handler(MessageHandler(filters.PHOTO, handle_answer))
    logger.info("البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
