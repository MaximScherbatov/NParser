import httpx
import asyncio
import logging
from collections import deque
from telethon import TelegramClient

from telegram_parser import telegram_parser
from rss_parser import rss_parser

from utils import create_logger, get_history, send_error_message
from config import api_id, api_hash, kgh_chat_id, bot_token, rss_channels, telegram_channels, key_words
from NLP_Model import tag_prediction

import warnings
warnings.filterwarnings('ignore')
###########################

def check_pattern_func(text):
    words = text.lower().split()
    tag = tag_prediction(text)
    print(tag)
    if tag=='Происшествия':
        for word in words:
            if ('моск' in word) and (len(word) < 11):
                return True
    elif tag in ['Город','Общество','Квартира','Москва']:
        for word in words:
            for key in key_words:
                if key in word:
                    return True
    return False

###########################
# Если у парсеров много ошибок или появляются повторные новости
# 50 первых символов от поста - это ключ для поиска повторных постов
n_test_chars = 50

# Количество уже опубликованных постов, чтобы их не повторять
amount_messages = 50

# Очередь уже опубликованных постов
posted_q = deque(maxlen=amount_messages)

# +/- интервал между запросами у rss и кастомного парсеров в секундах
timeout = 2

###########################

logger = create_logger('kgh')
logger.info('Start...')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

tele_logger = create_logger('telethon', level=logging.ERROR)

bot = TelegramClient('bot', api_id, api_hash, base_logger=tele_logger, loop=loop)
bot.start(bot_token=bot_token)


async def send_message_func(text):
    '''Отправляет посты в канал через бот'''
    await bot.send_message(entity=kgh_chat_id, parse_mode='html', link_preview=False, message=text)
    logger.info(text)

# Телеграм парсер
client = telegram_parser('kgh', api_id, api_hash, telegram_channels, posted_q,
                         n_test_chars, check_pattern_func, send_message_func,
                         tele_logger, loop)


# Список из уже опубликованных постов, чтобы их не дублировать
history = loop.run_until_complete(get_history(client, kgh_chat_id, n_test_chars, amount_messages))

posted_q.extend(history)

httpx_client = httpx.AsyncClient()

# Добавляй в текущий event_loop rss парсеры
for source, rss_link in rss_channels.items():
    print('>>>', source, rss_link)
    # https://docs.python-guide.org/writing/gotchas/#late-binding-closures
    async def wrapper(source, rss_link):
        try:
            await rss_parser(httpx_client, source, rss_link, posted_q,
                             n_test_chars, timeout, check_pattern_func,
                             send_message_func, logger)
        except Exception as e:
            message = f'&#9888; ERROR: {source} parser is down! \n{e}'
            await send_error_message(message, bot_token, kgh_chat_id, logger)

    loop.create_task(wrapper(source, rss_link))


try:
    # Запускает все парсеры
    client.run_until_disconnected()

except Exception as e:
    message = f'&#9888; ERROR: telegram parser (all parsers) is down! \n{e}'
    loop.run_until_complete(send_error_message(message, bot_token, kgh_chat_id, logger))
finally:
    loop.run_until_complete(httpx_client.aclose())
    loop.close()