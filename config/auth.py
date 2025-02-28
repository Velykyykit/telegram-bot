import os
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class AuthManager:
    def __init__(self, sheet_id, credentials_file):
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file

        if not self.sheet_id:
            raise ValueError("❌ SHEET_ID не знайдено! Перевірте змінні Railway.")
        if not self.credentials_file:
            raise ValueError("❌ CREDENTIALS_FILE не знайдено! Перевірте змінні Railway.")

        # Використовуємо абсолютний шлях, щоб знайти файл у кореневій папці
        CREDENTIALS_PATH = os.path.join("/app", self.credentials_file)

        # Виводимо шлях до файлу в логах (щоб перевірити)
        print(f"DEBUG: Використовується CREDENTIALS_FILE: {CREDENTIALS_PATH}")

        # Перевіряємо, чи існує файл
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(f"❌ Файл облікових даних не знайдено: {CREDENTIALS_PATH}")

        # Авторизація в Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
        self.client = gspread.authorize(self.creds)

        # Відкриваємо аркуш "contact"
        self.sheet = self.client.open_by_key(self.sheet_id).worksheet("contact")

    def clean_phone_number(self, phone):
        """Видаляє всі пробіли, дужки, тире та інші зайві символи з номера телефону."""
        phone = re.sub(r"[^\d+]", "", phone)  # Видаляємо все, крім цифр та знака "+"
        if not phone.startswith("+"):
            phone = f"+{phone}"  # Додаємо "+" на початок, якщо його немає
        return phone

    def check_user_in_database(self, phone_number):
        """
        Перевіряє, чи є номер телефону у базі Google Sheets.
        Повертає лише ім'я користувача, якщо знайдено.
        """
        phone_number = self.clean_phone_number(phone_number)
        phone_numbers = [self.clean_phone_number(num) for num in self.sheet.col_values(2)]  # Отримуємо всі значення з другого стовпця

        if phone_number in phone_numbers:
            row_index = phone_numbers.index(phone_number) + 1
            found_data = self.sheet.row_values(row_index)  # Отримуємо весь рядок

            # Отримуємо ім'я користувача з 3-го стовпця (змінюй індекс за потреби)
            user_name = found_data[2] if len(found_data) > 2 else "Невідомий користувач"

            return user_name  # Повертаємо лише ім'я

        return None  # Якщо номер не знайдено
