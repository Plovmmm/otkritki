import os
import json
import logging
from telegram import Update, Bot
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes
)
import base64
from io import BytesIO
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8185739343:AAH1jagUB9l0gnNW9Klyg4nRgsKZHHNCI8c"

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных из WebApp"""
    try:
        user = update.effective_user
        logger.info(f"Получено граффити от: {user.id if user else 'аноним'}")

        # Парсим данные
        data = json.loads(update.message.web_app_data.data)
        image_base64 = data.get('image')
        
        if not image_base64:
            await update.message.reply_text("❌ Не получилось загрузить изображение")
            return

        # Декодируем изображение
        try:
            image_bytes = base64.b64decode(image_base64)
            img_file = BytesIO(image_bytes)
            img_file.name = f"graffiti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        except Exception as e:
            logger.error(f"Ошибка декодирования: {str(e)}")
            await update.message.reply_text("❌ Ошибка обработки изображения")
            return

        # Отправляем обратно в тот же чат
        try:
            await update.message.reply_photo(
                photo=img_file,
                caption="🎨 Ваше граффити:",
                parse_mode='Markdown'
            )
            logger.info(f"Граффити отправлено в чат {update.message.chat.id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки: {str(e)}")
            await update.message.reply_text("❌ Не удалось отправить граффити")

    except Exception as e:
        logger.error(f"Общая ошибка: {str(e)}")
        await update.message.reply_text("⚠️ Произошла непредвиденная ошибка")

def main():
    # Инициализация бота
    application = Application.builder() \
        .token(BOT_TOKEN) \
        .build()
    
    # Обработчик данных из WebApp
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
