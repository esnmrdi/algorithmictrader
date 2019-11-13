from binance.client import Client
import logging


class TradingClient:

    def __init__(self, base_currency, trade_currency, key, secret):
        self.base_currency = base_currency
        self.trade_currency = trade_currency
        self.client = Client(key, secret)
        self.symbol = trade_currency + base_currency

    def get_historical_klines(self, interval, start_ts):
        return self.client.get_historical_klines(symbol=self.symbol, interval=interval, start_str=start_ts)

    def get_recent_trades(self):
        return self.client.get_recent_trades(symbol=self.symbol, limit=500)

    def get_order_book(self):
        return self.client.get_order_book(symbol=self.symbol, limit=1000)

    def get_order_book_ticker(self):
        return self.client.get_orderbook_ticker(symbol=self.symbol)

    def get_base_balance(self):
        return self.client.get_asset_balance(asset=self.base_currency)

    def get_trading_balance(self):
        return self.client.get_asset_balance(asset=self.trade_currency)

    @staticmethod
    def asset_balance_to_float(balance):
        return float(balance['free']) + float(balance['locked'])

    def get_all_trading_balance(self):
        trading_balance = self.get_trading_balance()
        return self.asset_balance_to_float(trading_balance)

    @staticmethod
    def trading_balance_available(trading_balance):
        return trading_balance > 1

    def get_balances(self):
        return self.client.get_account()['balances']

    def get_open_orders(self):
        return self.client.get_open_orders(symbol=self.symbol)

    def cancel_all_orders(self):
        open_orders = self.get_open_orders()
        for order in open_orders:
            self.client.cancel_order(symbol=self.symbol, orderId=order['orderId'])

    # GTC(Good-Til-Canceled) orders are effective until they are executed or canceled.
    # IOC(Immediate or Cancel) orders fills all or part of an order immediately and cancels the remaining part of the
    # order.
    def buy(self, quantity, price):
        price = '.8f' % price
        logging.info('Buying %d for %s', quantity, price)
        self.client.order_limit_buy(symbol=self.symbol, timeInForce=Client.TIME_IN_FORCE_GTC, quantity=quantity,
                                    price=price)

    def sell(self, quantity, price):
        price = '.8f' % price
        logging.info('Selling %d for %s', quantity, price)
        self.client.order_limit_sell(symbol=self.symbol, timeInForce=Client.TIME_IN_FORCE_GTC, quantity=quantity,
                                     price=price)

    def sell_market(self, quantity):
        if quantity > 0:
            logging.info('Selling to MARKET with quantity ' + str(quantity))
            self.client.order_market_sell(symbol=self.symbol, quantity=quantity)
        else:
            logging.info('Not executing - 0 quantity sell')

    def get_order(self, order_id):
        return self.client.get_order(symbol=self.symbol, orderId=order_id)

    def last_price(self):
        return float(self.client.get_symbol_ticker(symbol=self.symbol)['price'])

    def cancel_order(self, order_id):
        logging.info('Cancelling order ' + order_id)
        self.client.cancel_order(symbol=self.symbol, orderId=order_id)

    def panic_sell(self, last_known_amount, last_known_price):
        logging.error('!!! PANIC SELL !!!')
        logging.warn('Probably selling %.8f for %.8f', last_known_amount, last_known_price)
        self.cancel_all_orders()
        self.sell_market(float(self.get_trading_balance()['free']))
