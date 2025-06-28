import os
import json
import logging
from telegram import Update
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
    try:
        user = update.effective_user
        data = json.loads(update.message.web_app_data.data)
        
        # Декодируем изображение
        image_bytes = base64.b64decode(data['image'])
        img_file = BytesIO(image_bytes)
        img_file.name = f"graffiti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        # Отправляем обратно в чат
        await update.message.reply_photo(
            photo=img_file,
            caption="🎨 Ваше граффити сохранено!",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await update.message.reply_text("⚠️ Ошибка при обработке граффити")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    application.run_polling()

if __name__ == "__main__":
    main()