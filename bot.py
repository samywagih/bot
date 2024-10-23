import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, PollHandler, ContextTypes, filters
import logging
from collections import defaultdict

# إعداد تسجيل البيانات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# استخدم API الخاص بك من OpenAI
openai.api_key = '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'

class TelegramQuizBot:
    def __init__(self, token: str):
        self.token = token
        self.users_data = defaultdict(lambda: {
            'questions': [],
            'stats': {
                'total_quizzes': 0,
                'total_questions': 0,
                'correct_answers': 0,
                'average_score': 0.0,
                'quiz_history': []
            }
        })

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        welcome_message = (
            f"👋 مرحباً {user.first_name}!\n\n"
            "🤖 أنا بوت الاختبارات الذكي المطور. يمكنني:\n"
            "📝 فهم الأسئلة بتنسيقات متعددة باستخدام الذكاء الاصطناعي\n"
            "✨ دعم اللغتين العربية والإنجليزية\n"
            "📊 تحليل وتتبع تقدمك\n\n"
            "🔍 فقط أرسل أسئلتك بأي تنسيق مريح لك!"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("➕ إضافة أسئلة", callback_data='add_questions'),
                InlineKeyboardButton("📝 بدء اختبار", callback_data='start_quiz')
            ],
            [
                InlineKeyboardButton("📊 إحصائياتي", callback_data='my_stats'),
                InlineKeyboardButton("ℹ️ المساعدة", callback_data='help')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        user_id = update.effective_user.id
        
        # إرسال النص إلى نموذج GPT-4 لتحليل الأسئلة
        questions = self.analyze_text_with_ai(text)
        
        if questions:
            await update.message.reply_text(f"✅ تم إضافة {len(questions)} سؤال بنجاح!")
            
            # قم بإنشاء استفتاء لكل سؤال
            for question in questions:
                await self.create_poll(update, context, question)
        else:
            await update.message.reply_text("❌ لم أتمكن من تحليل الأسئلة. حاول إرسال صيغة مختلفة.")
    
    def analyze_text_with_ai(self, text: str):
        """تحليل النص باستخدام GPT"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "أنت مساعد ذكي لتحليل الأسئلة وتحويلها إلى أسئلة متعددة الخيارات أو صح/خطأ."},
                    {"role": "user", "content": f"حلل النص التالي واستخرج الأسئلة والخيارات والإجابة الصحيحة:\n{text}"}
                ]
            )
            
            ai_response = response['choices'][0]['message']['content']
            
            # هنا يمكنك معالجة الرد وإعادة هيكلته بالطريقة التي تناسب البوت
            questions = self.parse_ai_response(ai_response)
            
            return questions
        except Exception as e:
            logger.error(f"خطأ في تحليل النص باستخدام الذكاء الاصطناعي: {e}")
            return []

    def parse_ai_response(self, ai_response: str):
        """تحليل الرد من الذكاء الاصطناعي وإعادة بناء الأسئلة"""
        # هنا يجب أن تقوم بتحليل النص الذي أُعيد من الـ AI
        # مثال على ما قد يتم إرجاعه:
        # [{"question": "ما هو عاصمة فرنسا؟", "options": ["باريس", "لندن", "روما", "مدريد"], "correct_answer": "باريس"}]
        
        # افترض أن الرد سيكون بصيغة JSON أو قائمة
        # هذه عينة تجريبية:
        return [
            {
                "question": "ما هي عاصمة فرنسا؟",
                "options": ["باريس", "لندن", "روما", "مدريد"],
                "correct_answer": "باريس"
            },
            {
                "question": "صح أم خطأ: الأرض مسطحة.",
                "options": ["صح", "خطأ"],
                "correct_answer": "خطأ"
            }
        ]

    async def create_poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE, question_data):
        """إنشاء استفتاء بناءً على السؤال"""
        try:
            await context.bot.send_poll(
                chat_id=update.effective_chat.id,
                question=question_data['question'],
                options=question_data['options'],
                type=Poll.QUIZ,
                correct_option_id=question_data['options'].index(question_data['correct_answer']),
                is_anonymous=False
            )
        except Exception as e:
            logger.error(f"خطأ في إنشاء الاستفتاء: {e}")

    async def handle_poll_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تعامل مع إجابات المستخدم على الاستفتاء"""
        poll_answer = update.poll_answer
        user = update.effective_user
        selected_option = poll_answer.option_ids[0]
        # هنا يمكنك التعامل مع إجابة المستخدم وتحديث النتائج أو الإحصائيات الخاصة به

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == 'add_questions':
            await query.edit_message_text("✏️ أرسل الأسئلة التي تريد إضافتها.")
        elif query.data == 'start_quiz':
            await query.edit_message_text("🔍 سيتم البدء في اختبار قريبًا.")
        elif query.data == 'my_stats':
            await query.edit_message_text("📊 عرض الإحصائيات قريبًا.")
        elif query.data == 'help':
            await query.edit_message_text("ℹ️ تعليمات المساعدة قريبًا.")

async def main():
    token = '7630895452:AAEwYasU3wa1cRNybWBcHeBQ0-VPIvgLJHM'
    bot = TelegramQuizBot(token)
    
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(CallbackQueryHandler(bot.handle_callback))
    application.add_handler(PollHandler(bot.handle_poll_answer))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
