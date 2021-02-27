# -*- coding: utf-8 -*-

import logging
import coloredlogs
from threading import Timer
import sys
import telegram
from telegram import ParseMode
import numpy as np
from trading_client import TradingClient
from binance.client import Client
from datetime import datetime
from collections import deque

trade_currency = sys.argv[1]
base_currency = sys.argv[2]
frame = int(sys.argv[3])
history_window = int(sys.argv[4])
binance_key = 'lRAn2l36Qfvv9e9yDlIDWK9dpEfKRKrVbbBO8ynHcHd5eA0voNBbGBcrW4n3zlZ5'
binance_secret = 'bwd309D5pzgUioC9rxlJKpvAg5qwFU9zIkCLop9knRVki8nu3i3Ba88Z7K9xzV6p'
client = TradingClient(base_currency, trade_currency, binance_key, binance_secret)
telegram_bot = telegram.Bot(token='599534060:AAFPzCZkojZNje8rjapHRZdYm-EaLsT-EH4')
close_prices = deque(maxlen=history_window)


def updated_statistics():
    start_ts = (int(datetime.now().strftime('%s')) - history_window * 60) * 1000
    klines = client.get_historical_klines(Client.KLINE_INTERVAL_3MINUTE, start_ts)
    prices = np.array([float(kline[4]) for kline in klines])
    return prices


def report():
    Timer(int(frame * 60), report).start()
    prices = updated_statistics()
    logging.info('Price: %d' % prices[-1])
    dt = datetime.now().strftime('%b %d %Y - %H:%M:%S')
    text = '<b>%s/%s</b>\nDate-Time:\t%s\nPrice:\t%d' % (trade_currency, base_currency, dt, prices[-1])
    telegram_bot.send_message(chat_id='-1001236167919', text=text, parse_mode=ParseMode.HTML)


def main():
    coloredlogs.install()
    coloredlogs.install(fmt='%(asctime)s %(message)s')
    logging.info('Price-notifier bot just started')
    report()


if __name__ == '__main__':
    main()
