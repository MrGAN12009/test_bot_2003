from telebot import TeleBot
from dotenv import load_dotenv
import os


load_dotenv()

bot = TeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=["start" , "help"])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я тестовый бот для проверки работоспособности. Напиши мне что-нибудь!")

if __name__ == "__main__":
    bot.polling()