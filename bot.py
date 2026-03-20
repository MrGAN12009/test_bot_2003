from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
import logging
import sqlite3
from random import randint


logger = logging.getLogger("telebot")
logger.setLevel(logging.DEBUG)
load_dotenv()
sqlite = sqlite3.connect("users.db", check_same_thread=False)
cursor = sqlite.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, score INTEGER)")


def add_user(user_id, username):
    cursor.execute("INSERT OR IGNORE INTO users (id, username, score) VALUES (?, ?, ?)", (user_id, username, 0))
    sqlite.commit()


def add_score(user_id, score):
    cursor.execute("UPDATE users SET score = score + ? WHERE id = ?", (score, user_id))
    sqlite.commit()


def get_score(user_id):
    cursor.execute("SELECT score FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0


def get_top_users(limit=10):
    cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT ?", (limit,))
    return cursor.fetchall()


bot = TeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=["start" , "help"])
def start(message):
    add_user(message.from_user.id, message.from_user.username)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Играть", callback_data="play"))

    logger.info("Пришёл пользователь: %s", message.from_user.username)
    bot.send_message(message.chat.id, "Привет! Нажми /play, чтобы сыграть в игру и заработать очки!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "play")
def play_game(call):
    score = randint(-6, 6)
    add_score(call.from_user.id, score)
    logger.info("Пользователь %s заработал %d очков", call.from_user.username, score)
    bot.send_message(call.from_user.id, f"Ты заработал {score} очков!\nТвой текущий счёт: {get_score(call.from_user.id)}")


@bot.message_handler(commands=["top"])
def show_top(message):
    top_users = get_top_users()
    response = "Топ игроков:\n" + "\n".join([f"{i+1}. {user[0]} - {user[1]} очков" for i, user in enumerate(top_users)])
    bot.send_message(message.chat.id, response)


if __name__ == "__main__":
    bot.polling()