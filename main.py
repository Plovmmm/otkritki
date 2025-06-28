import os
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

ADMIN_CHAT_ID = 1323961884  # Ваш ID

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Получаем данные от пользователя
        user = update.effective_user
        data = update.message.web_app_data.data
        json_data = json.loads(data)
        
        logger.info(f"Получены данные от: {user.id if user else 'anonymous'}")
        
        # Проверяем наличие изображения
        if not json_data.get('image'):
            await update.message.reply_text("❌ Не получены данные изображения")
            return
            
        try:
            # Декодируем изображение
            image_bytes = base64.b64decode(json_data['image'])
            img_file = BytesIO(image_bytes)
            img_file.name = f"graffiti_{json_data.get('userId', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # Формируем подпись
            caption = (
                f"🖌 Новое граффити\n"
                f"👤 От: @{json_data.get('username', 'unknown')} (ID: {json_data.get('userId', 'unknown')})\n"
                f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            )
            
            if json_data.get('isAdmin'):
                caption += "⚠️ Отправлено администратором себе\n"
            
            # Отправляем администратору
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=img_file,
                caption=caption,
                parse_mode='Markdown'
            )
            
            # Отправляем подтверждение пользователю
            if str(user.id) != str(ADMIN_CHAT_ID):
                await update.message.reply_text("✅ Ваше граффити отправлено администратору!")
            else:
                await update.message.reply_text("✅ Вы отправили граффити себе (как администратору)")
                
            logger.info(f"Изображение отправлено в чат {ADMIN_CHAT_ID}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки изображения: {str(e)}")
            await update.message.reply_text("❌ Ошибка при обработке изображения")
            
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
