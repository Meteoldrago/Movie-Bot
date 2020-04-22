from back import get_deets , get_url
import os
from threading import Timer
from flask import Flask,request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time


TOKEN = 'Bot Token'
bot = telebot.TeleBot(TOKEN)
chat_id = 0
global text
message_id = 0
server = Flask(__name__)
def gen_markup(word,rp):
    markup = InlineKeyboardMarkup()
    text = get_deets(word,-1,rp)
    markup.row_width = 1
    if text == False:
        markup.add(InlineKeyboardButton("No Movies Found", callback_data=999))
    else:
        for i in range(0,len(text)):
            markup.add(InlineKeyboardButton(text[i], callback_data=i+1))
    return markup

def new_markup():
    return InlineKeyboardMarkup()

def feedback_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("YES", callback_data=9999))
    markup.add(InlineKeyboardButton("NO", callback_data=99999))
    return markup


def close_markup():
    global chat_id, message_id
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text= "Session terminated due to inactivity",reply_markup=new_markup())
        message_id = 0

end_chat = None

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

@bot.message_handler(commands=['example'])
def example(message):
    global word, chat_id, message_id, end_chat
    chat_id = message.chat.id
    name = message.chat.first_name
    message_id = bot.send_message(chat_id=chat_id,text="Hello "+ name + "\n" + "For example if you type 'avengers' ").message_id
    time.sleep(2)
    message_id_1 = bot.send_message(chat_id=chat_id, text="Select the movies from the list", reply_markup=gen_markup("avengers", 1)).message_id
    message_id_2 = bot.send_message(chat_id=chat_id,text="you will have [  60  ] seconds to select the movie from the list").message_id
    time.sleep(2)
    message_id_3 = bot.send_message(chat_id=chat_id,text="For example you select the First option 'The Avengers--2012--movie'").message_id
    time.sleep(2)
    message_id_4 = bot.send_message(chat_id=chat_id, text=get_deets("avengers", "2012", 2), reply_markup=new_markup()).message_id
    time.sleep(10)
    bot.delete_message(chat_id=chat_id, message_id=message_id_4)
    bot.delete_message(chat_id=chat_id, message_id=message_id_1)
    bot.delete_message(chat_id=chat_id, message_id=message_id_2)
    bot.delete_message(chat_id=chat_id, message_id=message_id_3)
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Are you satisfied with the example",reply_markup=feedback_markup())
    end_chat = Timer(5.0, close_markup)
    end_chat.start()

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    global word, chat_id, message_id,end_chat
    word = message.text
    chat_id = message.chat.id
    end_chat = Timer(60.0, close_markup)
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id,text="Thanks for using our bot" ,reply_markup=new_markup())
    message_id = bot.send_message(chat_id, text="Select the movies from the list", reply_markup=gen_markup(word,1)).message_id
    end_chat.start()

@bot.callback_query_handler(func=lambda call: True)
def call_handler(call):
    global word, chat_id, message_id, end_chat
    answer = None
    result=[]
    end_chat.cancel()
    parameter = call.data
    if (int(parameter) != 999 and int(parameter) != 99999 and int(parameter) != 9999):
        text = get_deets(word,-1,1)
        result = text[int(parameter)-1].split("--")
        answer = get_deets(result[0],result[1],2)
        bot.answer_callback_query(call.id, "Fetching Information about " + result[0])
        time.sleep(2)
        bot.send_message(chat_id, answer)
        end_chat = Timer(120.0, close_markup)
        end_chat.start()
    elif(int(parameter) == 999):
        for i in range (0,5):
            bot.answer_callback_query(call.id, "MOVIE NOT FOUND")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Movie Not Found", reply_markup=new_markup())
        end_chat = Timer(120.0, close_markup)
        end_chat.start()
    elif(int(parameter) == 9999):
        bot.send_message(chat_id=chat_id,
                              text="Thank you \n We hope that now you know how to use our bot.\n Click here for help -----> /help",reply_markup=new_markup())
        end_chat = Timer(5.0, close_markup)
        end_chat.start()
    elif(int(parameter) == 99999):
        bot.send_message(chat_id=chat_id,text="\n Click here to see the example again-----> /example ",reply_markup=new_markup())
        end_chat = Timer(5.0, close_markup)
        end_chat.start()


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "working", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='your heroku app link' + TOKEN)
    return "!!!!!!!",200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
