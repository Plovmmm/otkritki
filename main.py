from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import json
import base64
from io import BytesIO
import logging
from datetime import datetime

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Логируем входящее сообщение
        logger.info(f"Получены данные от пользователя: {update.effective_user.id}")
        
        data = json.loads(update.message.web_app_data.data)
        image_data = data.get('image')
        user_id = data.get('userId')
        username = data.get('username', 'неизвестно')
        date = data.get('date', datetime.now().isoformat())
        
        if not image_data:
            await update.message.reply_text("⚠️ Не получены данные изображения")
            return
            
        try:
            # Декодируем изображение
            img_bytes = base64.b64decode(image_data.split(',')[1])
        except Exception as e:
            logger.error(f"Ошибка декодирования изображения: {e}")
            await update.message.reply_text("⚠️ Ошибка обработки изображения")
            return
            
        # Логируем успешное декодирование
        logger.info(f"Изображение успешно декодировано, размер: {len(img_bytes)} байт")
        
        # Отправляем админу (ваш ID: 1323961884)
        try:
            await context.bot.send_photo(
                chat_id=1323961884,
                photo=BytesIO(img_bytes),
                caption=(
                    f"🎨 Новое граффити\n"
                    f"👤 Пользователь: {user_id}\n"
                    f"📛 Имя: @{username}\n"
                    f"📅 Дата: {date}"
                )
            )
            logger.info("Изображение успешно отправлено администратору")
            await update.message.reply_text("✅ Граффити успешно отправлено администратору!")
        except Exception as e:
            logger.error(f"Ошибка отправки фото админу: {e}")
            await update.message.reply_text("⚠️ Не удалось отправить граффити администратору")
            
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при обработке граффити")

def main():
    # Инициализация бота
    application = Application.builder().token("8185739343:AAH1jagUB9l0gnNW9Klyg4nRgsKZHHNCI8c").build()
    
    # Обработчик данных из веб-приложения
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
