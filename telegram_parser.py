from collections import deque
from telethon import TelegramClient, events
from config import api_id, api_hash


def telegram_parser(session, api_id, api_hash, telegram_channels, posted_q,
                    n_test_chars=50, check_pattern_func=None,
                    send_message_func=None, logger=None, loop=None):
    '''Телеграм парсер'''
    telegram_channels_links = list(telegram_channels.values())
    client = TelegramClient(session, api_id, api_hash, base_logger=logger, loop=loop)
    client.start()

    @client.on(events.NewMessage(chats=telegram_channels_links))
    async def handler(event):
        '''Забирает посты из телеграмм каналов и посылает их в наш канал'''
        if event.raw_text == '':
            return

        news_text = ' '.join(event.raw_text.split('\n')[:2])

        if not (check_pattern_func is None):
            if not check_pattern_func(news_text):
                return

        head = news_text[:n_test_chars].strip()

        if head in posted_q:
            return

        source = telegram_channels[event.message.peer_id.channel_id]

        link = f'{source}/{event.message.id}'

        channel = '@' + source.split('/')[-1]

        post = f'<b>{channel}</b>\n{link}\n{news_text}'

        if send_message_func is None:
            print(post, '\n')
        else:
            await send_message_func(post)

        posted_q.appendleft(head)

    return client


if __name__ == "__main__":
    telegram_channels = {
        1354034423: 'https://t.me/rusmsk',
        1003313758: 'https://t.me/moscowmap',
        1597228121: 'https://t.me/DGONews',
        1387151456: 'https://t.me/kgh_moscow',
        1393945742: 'https://t.me/moslentaru',
        1135758880: 'https://t.me/mchs_moscow_operational',
        1588259750: 'https://t.me/testchanel021122',
        1117628569: 'https://t.me/breakingmash',
        1064785472: 'https://t.me/mosrutop',
        1643894529: 'https://t.me/mchsmsk',
        1497406484: 'https://t.me/vmoskva',
        1135115323: 'https://t.me/moscownewsagency'
    }

    # Очередь из уже опубликованных постов, чтобы их не дублировать
    posted_q = deque(maxlen=25)
    client = telegram_parser('kgh', api_id, api_hash, telegram_channels, posted_q)
    client.run_until_disconnected()