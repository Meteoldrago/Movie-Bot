from back import get_deets
import os
from flask import Flask,request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = 'token'
bot = telebot.TeleBot(TOKEN)
chat_id = 0
global text
message_id = 0
server = Flask(__name__)
def gen_markup(word,rp):
    markup = InlineKeyboardMarkup()
    text = get_deets(word,-1,rp)
    markup.row_width = 1
    for i in range(0,len(text)):
        markup.add(InlineKeyboardButton(text[i], callback_data=i+1))
    return markup

def new_markup():
    return InlineKeyboardMarkup()

@bot.message_handler(commands=['start'])
def start(message):
    chatid = message.chat.id
    name = message.chat.first_name
    text = 'Hi ' + str(name) + ', How are you ?! 😊 Welcome to TV BOT 😍🔥'
    bot.send_message(chatid, text)


@bot.message_handler(commands=['help'])
def help_text(message):
    chatid = message.chat.id
    text = 'Just Type the movie [OR] series name and then the select your choice from list(based on the entered text) to get info about the same'
    bot.send_message(chatid, text)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    global word, chat_id, message_id
    word = message.text
    chat_id = message.chat.id
    message_id = bot.send_message(chat_id, text="Select the movies from the list", reply_markup=gen_markup(word,1)).message_id


@bot.callback_query_handler(func=lambda call: True)
def call_handler(call):
    answer = ""
    result=[]
    rp = 1
    parameter = call.data
    text = get_deets(word,-1,1)
    result = text[int(parameter)-1].split("--")
    answer = get_deets(result[0],result[1],2)
    #bot.edit_message_reply_markup(chat_id=chat_id,message_id=message_id)
    bot.send_message(chat_id, answer)

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='your heroku app link' + TOKEN)
    return "!",200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
