from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import json
import base64
from io import BytesIO

async def handle_web_app_data(update: Update, context):
    try:
        data = json.loads(update.message.web_app_data.data)
        image_data = data.get('image')
        user_id = update.effective_user.id
        
        if image_data:
            # Декодируем изображение
            img_bytes = base64.b64decode(image_data.split(',')[1])
            
            # Отправляем админу (ваш ID: 1323961884)
            await context.bot.send_photo(
                chat_id=1323961884,
                photo=BytesIO(img_bytes),
                caption=f"Новая открытка от пользователя: {user_id}"
            )
            
            await update.message.reply_text("✅ Открытка отправлена администратору!")
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при обработке открытки")

# Инициализация бота
app = Application.builder().token("8185739343:AAH1jagUB9l0gnNW9Klyg4nRgsKZHHNCI8c").build()
app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
app.run_polling()
