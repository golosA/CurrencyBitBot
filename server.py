# https://www.digitalocean.com/community/tutorials/docker-explained-how-to-containerize-python-web-applications
import sys
import time
import re
import threading
import random
import telepot
from pprint import pprint
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
from telepot.loop import MessageLoop
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup as Soup
import requests

delta_time = 15
cache = {}
urls = {
    'SNM/BTC': 'https://yobit.net/en/trade/SNM/BTC',
    'BTC/USD': 'https://yobit.net/ru/trade/BTC/USD'
}
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='SNM/BTC', callback_data='callback_snm_btc')],
])

def get_last_price(token, token2):
    resultToken = token + '/' + token2
    if resultToken in cache:
        (value, value_time) = cache[resultToken]
        cur_time = int(time.time())
        if cur_time - value_time <= delta_time:
            return value
    url = urls[resultToken]
    content = requests.get(url).text
    soup = Soup(content, 'html.parser')
    lastPrice  =  soup.select('#label_last')
    if len(lastPrice) != 0:
        lastStr = lastPrice[0].text
        cache[resultToken] = (lastStr, int(time.time()))
        return lastStr
    else:
        return None

def get_cource_msg(token1, token2):
    lastPrice = get_last_price(token1, token2)
    msg = None
    if lastPrice is None:
        msg = 'Some trouble'
    else:
        msg = 'Last Price: 1 ' + token1 + ' = ' + lastPrice + ' ' + token2
        if token2 != 'USD':
            token2Usd = get_last_price(token2, 'USD')
            msg = msg + ' = $' + str(float(token2Usd) * float(lastPrice))
    return msg

def on_chat_message(msg):
    print(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)
    user_id = msg['from']['id']
    bot.sendMessage(user_id, 'try use button', reply_markup=keyboard)

def callback_snm_btc(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    user_id = msg['from']['id']
    print('Callback Query:', query_id, from_id, query_data)
    token1 = 'SNM'
    token2 = 'BTC'
    msg = get_cource_msg(token1, token2)
    bot.sendMessage(user_id, msg, reply_markup=keyboard)
    bot.answerCallbackQuery(query_id)

def on_inline_query(msg):
    print('empty')

def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)

TOKEN = sys.argv[1]  # get token from command-line
bot = telepot.Bot(TOKEN)

MessageLoop(bot, {
    'chat': on_chat_message,
    'callback_query': callback_snm_btc
}).run_as_thread()
print('Listening ...')
# Keep the program running.
while 1:
    time.sleep(10)
