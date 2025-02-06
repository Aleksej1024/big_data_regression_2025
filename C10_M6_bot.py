'''
import telebot
import requests

API_TOKEN = '7886805220:AAHSmidDJ6MToG28sIvodK7_HjFRZwHt-zE'
SERVER_URL = 'http://localhost:5000'  
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome! Use /upload to upload data.")

@bot.message_handler(commands=['upload'])
def upload(message):
    bot.send_message(message.chat.id, "Please send me a CSV file.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    if not message.document.file_name.endswith('.csv'):
        bot.send_message("Invalid fromat")
    # Отправка файла на сервер
    response = requests.post(f"{SERVER_URL}/upload", files={'file':downloaded_file})
    bot.send_message(message.chat.id, response.json().get("message", "Error"))

@bot.message_handler(commands=['preprocess'])
def preprocess(message):
    response = requests.post(f"{SERVER_URL}/preprocess")
    bot.send_message(message.chat.id, response.json().get("message", "Error"))

@bot.message_handler(commands=['models'])
def list_models(message):
    response = requests.get(f"{SERVER_URL}/models")
    models = response.json()
    bot.send_message(message.chat.id, "Available models: " + ", ".join(models))

@bot.message_handler(commands=['select_model'])
def select_model(message):
    model_name = message.text.split()[1]  # Предполагается, что команда будет вида /select_model model_name
    response = requests.post(f"{SERVER_URL}/select_model", json={"model_name": model_name})
    bot.send_message(message.chat.id, response.json().get("message", "Error"))

@bot.message_handler(commands=['predict'])
def predict(message):
    response = requests.post(f"{SERVER_URL}/predict")
    predictions = response.json()
    bot.send_message(message.chat.id, "Predictions: " + str(predictions))

if __name__ == '__main__':
    bot.polling(none_stop=True)

'''

import telebot
from telebot import types
import requests

# Конфигурация
API_TOKEN = '7886805220:AAHSmidDJ6MToG28sIvodK7_HjFRZwHt-zE'
SERVER_URL = 'http://localhost:5000'  

bot = telebot.TeleBot(API_TOKEN)


# Главное меню
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        "📤 Загрузить данные",
        "🔧 Предобработка",
        "📊 Список моделей",
        "🤖 Выбрать модель",
        "🔮 Предсказание"
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "Добро пожаловать! Я ваш ассистент для анализа данных.\n"
        "Выберите действие из меню ниже:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📤 Загрузить данные")
def upload_file(message):
    msg = bot.send_message(message.chat.id, "Пожалуйста, отправьте CSV файл", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, handle_document)

def handle_document(message):
    if message.document is None or not message.document.file_name.endswith('.csv'):
        bot.send_message(message.chat.id, "❌ Неверный формат файла. Отправьте CSV.", reply_markup=main_keyboard())
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Отправка файла на сервер
        response = requests.post(f"{SERVER_URL}/upload", files={'file': downloaded_file})
        if response.status_code == 200:
            bot.send_message(message.chat.id, "✅ Файл успешно загружен!", reply_markup=main_keyboard())
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при загрузке файла", reply_markup=main_keyboard())
    
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "🔧 Предобработка")
def preprocess_data(message):
    try:
        response = requests.post(f"{SERVER_URL}/preprocess")
        bot.send_message(message.chat.id, response.json().get("message", "✅ Предобработка завершена"), reply_markup=main_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📊 Список моделей")
def show_models(message):
    try:
        response = requests.get(f"{SERVER_URL}/models")
        models = response.json()
        bot.send_message(message.chat.id, f"Доступные модели:\n{', '.join(models)}", reply_markup=main_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "🤖 Выбрать модель")
def select_model_step1(message):
    msg = bot.send_message(message.chat.id, "Введите название модели:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, select_model_step2)

def select_model_step2(message):
    try:
        model_name = message.text
        response = requests.post(f"{SERVER_URL}/select_model", json={"model_name": model_name})
        bot.send_message(message.chat.id, response.json().get("message", "✅ Модель выбрана"), reply_markup=main_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "🔮 Предсказание")
def make_prediction(message):
    try:
        response = requests.post(f"{SERVER_URL}/predict")
        predictions = response.json()
        bot.send_message(message.chat.id, f"Результаты предсказаний:\n{predictions}", reply_markup=main_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", reply_markup=main_keyboard())

if __name__ == '__main__':
    bot.polling(none_stop=True)