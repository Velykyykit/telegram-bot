import telebot
import os
from menu.keyboards import get_phone_keyboard  # Імпортуємо клавіатуру
from config.auth import check_user_in_database  # Імпортуємо функцію перевірки номера

# Отримуємо токен з змінної середовища
TOKEN = os.getenv("TOKEN")  
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Запит на надання номера телефону для аутентифікації після команди /start."""
    markup = get_phone_keyboard()  # Використовуємо тільки одну кнопку

    bot.send_message(
        message.chat.id,
        "Поділіться номером для аутентифікації:",  
        reply_markup=markup  
    )

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    """Обробляє отримання номера телефону від користувача та перевіряє його в базі даних."""
    if message.contact:
        phone_number = message.contact.phone_number

        # Перевірка номера в базі даних
        user_name = check_user_in_database(phone_number)

        if user_name:
            bot.send_message(
                message.chat.id,
                f"✅ Вітаю, *{user_name}*! Ви успішно ідентифіковані. 🎉"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Ваш номер не знайдено у базі. Зверніться до адміністратора."
            )

# Запуск бота
if __name__ == "__main__":
    print("Бот запущено. Очікування повідомлень...")
    bot.polling(none_stop=True)
