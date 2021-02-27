# -*- coding: utf-8 -*-

import logging
import coloredlogs
from threading import Timer
import sys
import telegram
from telegram import ParseMode
import numpy as np
import talib as ta
from trading_client import TradingClient
from binance.client import Client
from datetime import datetime
from collections import deque

nslow = 26
nfast = 12
nema = 9
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
    macd, signal, hist = ta.MACD(prices, fastperiod=nfast, slowperiod=nslow, signalperiod=nema)
    rsi = ta.RSI(prices, timeperiod=14)

    return macd, signal, hist, rsi


def sign(n):
    return '+' if np.sign(n) == 1 else '-'


def sign_pattern(numbers, n):
    return ''.join([sign(x) for x in numbers[-n:]])


def signal_line_crossover_event(hist):
    pattern = sign_pattern(hist, 4)
    if pattern == '--++':
        return 'bullish'
    elif pattern == '++--':
        return 'bearish'
    else:
        return None


def zero_line_crossover_event():
    pass


def divergence_event():
    pass


def overbought():
    pass


def oversold():
    pass


def report():
    Timer(int(frame * 60), report).start()
    macd, signal, hist, rsi = updated_statistics()
    # logging.info('MACD: %0.8f\tSignal: %.8f\tHistogram: %.8f\tRSI: %.8f' % (macd[-1], signal[-1], hist[-1], rsi[-1]))
    slce = signal_line_crossover_event(hist)
    if slce:
        dt = datetime.now().strftime('%b %d %Y %H:%M:%S')
        caption = '<b>%s/%s market is %s!</b>\nDate|Time:\t%s\nMACD:\t%.8f\nSignal:\t%.8f\nHistogram:\t%.8f\nRSI:\t%.8f' % (
            trade_currency, base_currency, slce.capitalize(), dt, macd[-1], signal[-1], hist[-1], rsi[-1])
        # logging.info(caption)
        with open('images/' + slce + '.jpg', 'rb') as photo:
            telegram_bot.send_photo(chat_id='-1001236167919', photo=photo, caption=caption, parse_mode=ParseMode.HTML)


def main():
    coloredlogs.install()
    coloredlogs.install(fmt='%(asctime)s %(message)s')
    logging.info('Bot trading just started')
    report()


if __name__ == '__main__':
    main()
