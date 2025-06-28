import os
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes
)
import base64
from io import BytesIO
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMIN_CHAT_ID = 1323961884  # Ваш chat_id

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"Получены данные от: {update.effective_user.id}")
        
        # Парсим данные из WebApp
        data = json.loads(update.message.web_app_data.data)
        image_base64 = data.get('image')
        user_id = data.get('userId', 'anonymous')
        
        if not image_base64:
            await update.message.reply_text("❌ Не получены данные изображения")
            return
            
        try:
            # Декодируем изображение
            image_bytes = base64.b64decode(image_base64)
            img_file = BytesIO(image_bytes)
            img_file.name = f"graffiti_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        except Exception as e:
            logger.error(f"Ошибка декодирования: {str(e)}")
            await update.message.reply_text("❌ Ошибка обработки изображения")
            return
            
        # Отправляем администратору
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=img_file,
                caption=(
                    f"🖌 Новое граффити\n"
                    f"👤 ID: {user_id}\n"
                    f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                    f"#граффити"
                ),
                parse_mode='Markdown'
            )
            logger.info(f"Изображение отправлено администратору {ADMIN_CHAT_ID}")
            await update.message.reply_text("✅ Ваше граффити успешно отправлено!")
        except Exception as e:
            logger.error(f"Ошибка отправки админу: {str(e)}")
            await update.message.reply_text("❌ Ошибка при отправке. Попробуйте позже.")
            
    except Exception as e:
        logger.error(f"Общая ошибка: {str(e)}")
        await update.message.reply_text("⚠️ Произошла непредвиденная ошибка")

def main():
    # Инициализация бота
    application = Application.builder() \
        .token("8185739343:AAH1jagUB9l0gnNW9Klyg4nRgsKZHHNCI8c") \
        .build()
    
    # Обработчик данных из WebApp
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
