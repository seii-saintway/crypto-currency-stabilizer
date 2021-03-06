# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/main-huobi.ipynb (unless otherwise specified).

__all__ = ['TEST_RATIO', 'NOTIFY_RATE', 'BACKUP_RATE', 'Trader', 'MAX_USED_FIAT_MONEY_LIMIT',
           'GAINABLE_UNIT_CC_SOLD_RATIO', 'LOSSABLE_UNIT_CC_BOUGHT_RATIO', 'MIN_TRADE_FIAT_PRICE',
           'MAX_TRADE_FIAT_PRICE', 'ICON_URL']

# Cell
TEST_RATIO = 1

# Cell
NOTIFY_RATE = 60 * 8
BACKUP_RATE = 1

# Cell
import math
from ccstabilizer import Trader as TraderBase


class Trader(TraderBase):

    def check_and_trade(self):
        status = self.status

        min_trade_fiat_money_limit = self.exchange.get_trading_specification(
            status.crypto_symbol, status.fiat_symbol
        ).get('min_trade_fiat_money_limit', 1)

        status.update(self.get_price())

        please_sell_unit_amount = 0

        if (status.sample_number % type(self).TRADE_RATE == 0 or status.sold_unit_amount == 0) and status.fiat_price_is_higher_than_average():
            please_sell_unit_amount = min(
                math.ceil(min_trade_fiat_money_limit / status.now_sell_fiat_price_without_fee / status.trade_unit),
                math.floor(status.bought_unit_amount)
            )
            cooling_interval = type(self).HAPPY_COOLING_INTERVAL

        if status.sold_unit_amount > 0 and status.now_sell_fiat_price > status.sold_average_fiat_price:
            trade_unit_amount = min(self.get_sell_unit_amount(), math.floor(status.bought_unit_amount))
            if trade_unit_amount > 0:
                please_sell_unit_amount = trade_unit_amount
                cooling_interval = type(self).HAPPY_COOLING_INTERVAL

        gained_fiat_money = status.estimate_gained_fiat_money(status.bought_unit_amount)
        if gained_fiat_money is not None and gained_fiat_money > type(self).MAX_GAIN_JPY:
            please_sell_unit_amount = math.floor(status.bought_unit_amount)
            cooling_interval = type(self).HAPPY_COOLING_INTERVAL

        if gained_fiat_money is not None and gained_fiat_money < -type(self).MAX_LOSS_JPY:
            please_sell_unit_amount = math.floor(status.bought_unit_amount)
            cooling_interval = type(self).SAD_COOLING_INTERVAL

        if status.bought_average_fiat_price is not None and status.now_sell_fiat_price < status.bought_average_fiat_price - type(self).LOSSABLE_UNIT_CC_SELL_JPY and status.get_usage() > 90/100:
            please_sell_unit_amount = math.floor(status.bought_unit_amount)
            cooling_interval = type(self).SAD_COOLING_INTERVAL

#         if status.bought_unit_amount > 0 and status.now_sell_fiat_price < self.min_unit_cc_trade_fiat_money:
#             please_sell_unit_amount = status.bought_unit_amount
#             cooling_interval = type(self).SAD_COOLING_INTERVAL

        if self.exchange.trade_fiat_money_is_larger_than_limit(
            status.crypto_symbol,
            status.fiat_symbol,
            status.trade_unit * please_sell_unit_amount,
            status.now_sell_fiat_price_without_fee
        ):
            self.sell(please_sell_unit_amount)
            status.sample_number = 0
            return cooling_interval, 'sell', please_sell_unit_amount

        please_buy_unit_amount = 0

        # TODO: self-adaptive by trend analysis
#         init_buy_jpy = min_trade_fiat_money_limit * 5
        init_buy_jpy = status.get_max_used_fiat_money() / Decimal(math.exp(self.lossable_unit_cc_bought_ratio / (1 - self.lossable_unit_cc_bought_ratio)))
        status.init_buy_jpy = init_buy_jpy
        # self.exchange.has_enough_unused_fiat_money(init_buy_jpy, status.unused_fiat_money) !! status.unused_fiat_money
        if status.used_fiat_money < min_trade_fiat_money_limit and self.exchange.has_enough_unused_fiat_money(init_buy_jpy, status.unused_fiat_money) and self.has_buyable_fiat_price():
            buy_fiat_money = max(init_buy_jpy - status.used_fiat_money, min_trade_fiat_money_limit)
            please_buy_unit_amount = math.ceil(buy_fiat_money / status.now_buy_fiat_price / status.trade_unit)

        if status.used_fiat_money < init_buy_jpy and status.fiat_price_is_lower_than_average() and self.exchange.has_enough_unused_fiat_money(init_buy_jpy - status.used_fiat_money, status.unused_fiat_money) and self.has_buyable_fiat_price():
            buy_fiat_money = max(init_buy_jpy - status.used_fiat_money, min_trade_fiat_money_limit)
            please_buy_unit_amount = math.ceil(buy_fiat_money / status.now_buy_fiat_price / status.trade_unit)

        if status.used_fiat_money >= init_buy_jpy and status.fiat_price_is_lower_than_average():
            trade_unit_amount = self.get_buy_unit_amount()
            while trade_unit_amount > 0 and not self.exchange.has_enough_unused_fiat_money(status.now_buy_fiat_price * status.trade_unit * trade_unit_amount, status.unused_fiat_money):
                trade_unit_amount >>= 1
            if trade_unit_amount > 0:
                please_buy_unit_amount = trade_unit_amount

        # print(f'{status.crypto_symbol}-{status.fiat_symbol}: please_buy_fiat_money={status.now_buy_fiat_price_without_fee * status.trade_unit * please_buy_unit_amount}\n')
        if self.exchange.trade_fiat_money_is_larger_than_limit(
            status.crypto_symbol,
            status.fiat_symbol,
            status.trade_unit * please_buy_unit_amount,
            status.now_buy_fiat_price_without_fee
        ):
            self.buy(please_buy_unit_amount)
            status.sample_number = 0
            return type(self).SAMPLE_INTERVAL, 'buy', please_buy_unit_amount

        return type(self).SAMPLE_INTERVAL, 'wait', 0


Trader.SAMPLE_INTERVAL = 60

# Cell
from decimal import Decimal

MAX_USED_FIAT_MONEY_LIMIT = {
    ('AR', 'USDT'): Decimal('1500'),
    ('ETH', 'USDT'): Decimal('Infinity'),
    ('FLOW', 'USDT'): Decimal('1000'),
    ('HT', 'USDT'): Decimal('Infinity'),
    ('VIDY', 'USDT'): Decimal('1000'),
    ('XLM', 'USDT'): Decimal('1000'),
    ('XRP', 'USDT'): Decimal('Infinity'),
    ('AR', 'ETH'): Decimal('Infinity'),
    ('FLOW', 'ETH'): Decimal('Infinity'),
    ('XLM', 'ETH'): Decimal('Infinity'),
    ('VIDY', 'HT'): Decimal('Infinity'),
    ('XRP', 'HT'): Decimal('Infinity'),
}
GAINABLE_UNIT_CC_SOLD_RATIO = {
    ('AR', 'USDT'): Decimal('0.146'),
    ('ETH', 'USDT'): Decimal('0.146'),
    ('FLOW', 'USDT'): Decimal('0.146'),
    ('HT', 'USDT'): Decimal('0.236'),
    ('VIDY', 'USDT'): Decimal('0.146'),
    ('XLM', 'USDT'): Decimal('0.146'),
    ('XRP', 'USDT'): Decimal('0.236'),
    ('AR', 'ETH'): Decimal('0.146'),
    ('FLOW', 'ETH'): Decimal('0.146'),
    ('XLM', 'ETH'): Decimal('0.146'),
    ('VIDY', 'HT'): Decimal('0.146'),
    ('XRP', 'HT'): Decimal('0.146'),
}
LOSSABLE_UNIT_CC_BOUGHT_RATIO = {
    ('AR', 'USDT'): Decimal('0.618'),
    ('ETH', 'USDT'): Decimal('0.618'),
    ('FLOW', 'USDT'): Decimal('0.786'),
    ('HT', 'USDT'): Decimal('0.618'),
    ('VIDY', 'USDT'): Decimal('0.786'),
    ('XLM', 'USDT'): Decimal('0.786'),
    ('XRP', 'USDT'): Decimal('0.786'),
    ('AR', 'ETH'): Decimal('0.618'),
    ('FLOW', 'ETH'): Decimal('0.618'),
    ('XLM', 'ETH'): Decimal('0.618'),
    ('VIDY', 'HT'): Decimal('0.382'),
    ('XRP', 'HT'): Decimal('0.382'),
}
MIN_TRADE_FIAT_PRICE = {
    ('AR', 'USDT'): Decimal('0'),
    ('ETH', 'USDT'): Decimal('1950'),
    ('FLOW', 'USDT'): Decimal('0'),
    ('HT', 'USDT'): Decimal('0'),
    ('VIDY', 'USDT'): Decimal('0'),
    ('XLM', 'USDT'): Decimal('0'),
    ('XRP', 'USDT'): Decimal('0'),
    ('AR', 'ETH'): Decimal('0'),
    ('FLOW', 'ETH'): Decimal('0'),
    ('XLM', 'ETH'): Decimal('0'),
    ('VIDY', 'HT'): Decimal('0'),
    ('XRP', 'HT'): Decimal('0'),
}
MAX_TRADE_FIAT_PRICE = {
    ('AR', 'USDT'): Decimal('Infinity'),
    ('ETH', 'USDT'): Decimal('Infinity'),
    ('FLOW', 'USDT'): Decimal('Infinity'),
    ('HT', 'USDT'): Decimal('Infinity'),
    ('VIDY', 'USDT'): Decimal('Infinity'),
    ('XLM', 'USDT'): Decimal('Infinity'),
    ('XRP', 'USDT'): Decimal('Infinity'),
    ('AR', 'ETH'): Decimal('Infinity'),
    ('FLOW', 'ETH'): Decimal('Infinity'),
    ('XLM', 'ETH'): Decimal('Infinity'),
    ('VIDY', 'HT'): Decimal('Infinity'),
    ('XRP', 'HT'): Decimal('Infinity'),
}
ICON_URL = {
    'AR': 'https://cryptologos.cc/logos/arweave-ar-logo.png',
    'ETH': 'https://cryptologos.cc/logos/ethereum-eth-logo.png',
    'FLOW': 'https://cryptologos.cc/logos/flow-flow-logo.png',
    'HT': 'https://cryptologos.cc/logos/huobi-token-ht-logo.png',
    'VIDY': 'https://cryptologos.cc/logos/huobi-token-ht-logo.png',
    'XLM': 'https://cryptologos.cc/logos/stellar-xlm-logo.png',
    'XRP': 'https://cryptologos.cc/logos/xrp-xrp-logo.png',
}

# Internal Cell
from ccstabilizer import Huobi
from ccstabilizer import secrets
from ccstabilizer import Fetcher
from ccstabilizer import Notifier
from ccstabilizer import Status

# Internal Cell
Status.robot_name_prefix = 'HB-'
exchange = Huobi()
fetcher = Fetcher(exchange)
notifier = Notifier(channel_name='huobi', name='Launcher')

messages = []
color = 'good'
status_list = []
for crypto_symbol, fiat_symbol in MAX_USED_FIAT_MONEY_LIMIT:
    trading_spec = fetcher.get_trading_spec(crypto_symbol, fiat_symbol)
    if not trading_spec.get('liquid', False):
        messages.append(f'{crypto_symbol}-{fiat_symbol} detection failed\n')
        color = 'danger'
        continue
    messages.append(f'{crypto_symbol}-{fiat_symbol} detected\n')
    if 'min_trade_unit' not in trading_spec:
        raise Exception("'min_trade_unit' not in trading_spec")
    min_trade_unit = trading_spec.get('min_trade_unit', 1)
    max_used_fiat_money_limit = MAX_USED_FIAT_MONEY_LIMIT[(crypto_symbol, fiat_symbol)]
    status = Status(
        robot_name = f'{crypto_symbol}-{fiat_symbol} Robot',
        crypto_symbol = crypto_symbol,
        fiat_symbol = fiat_symbol,
        trade_unit = min_trade_unit,
        max_used_fiat_money_limit = max_used_fiat_money_limit,
    )
    status.read()
#     status.trade_unit = min_trade_unit
#     status.max_used_fiat_money_limit = max_used_fiat_money_limit
    status_list.append(status)

# notifier.send_slack(
#     ''.join(messages), 'Power by https://jhub.name/', color
# )

# Internal Cell
from ccstabilizer import BookKeeper

# Internal Cell
import time


with BookKeeper(exchange, status_list) as bookkeeper:

    trader_list = []
    notifier_list = []
    messages = []
    for status in status_list:
        trader = Trader(
            exchange = exchange,
            status = status,
            gainable_unit_cc_sold_ratio = GAINABLE_UNIT_CC_SOLD_RATIO[(status.crypto_symbol, status.fiat_symbol)],
            lossable_unit_cc_bought_ratio = LOSSABLE_UNIT_CC_BOUGHT_RATIO[(status.crypto_symbol, status.fiat_symbol)],
            min_trade_fiat_price = MIN_TRADE_FIAT_PRICE[(status.crypto_symbol, status.fiat_symbol)],
            max_trade_fiat_price = MAX_TRADE_FIAT_PRICE[(status.crypto_symbol, status.fiat_symbol)]
        )
        trader_list.append(trader)
        notifier_list.append(Notifier(
            channel_name='huobi',
            name=f'{status.crypto_symbol}-{status.fiat_symbol}',
            icon_url=ICON_URL.get(status.crypto_symbol, 'https://jupyter.org/assets/apple-touch-icon.png')
        ))
        messages.append(f'{status.get_robot_title()} launched')

    notifier.send_slack(
        '\n'.join(messages), 'Power by https://jhub.name/', 'good'
    )

    idx = 0
    num = len(status_list)

    while __name__ == '__main__':

        status = status_list[idx]
        trader = trader_list[idx]
        notifier = notifier_list[idx]

        cooling_interval, trade_type, unit_amount = trader.check_and_trade()

        status.write()
        bookkeeper.fsh.write(f'{status}\n')

        time.sleep(Trader.SAMPLE_INTERVAL / num / 2 / TEST_RATIO)

        new_status_list = bookkeeper.estimate_status_list()

        messages = []
        for i, new_status in enumerate(new_status_list):
            if new_status is not status_list[i]:

                status_list[i].update(new_status)

                bookkeeper.fth.write(f'{status_list[i]}\n')
                status_list[i].write()

                messages.append(f'{status_list[i].last_transaction} => {status_list[i].get_robot_title()}')
                messages.append(f'{status_list[i]} => Support level is {trader_list[i].min_unit_cc_trade_fiat_money} {status_list[i].fiat_symbol}.\n')

#         if status.bought_unit_amount == 0:
#             messages.append(f'{status.get_robot_title()} terminated')
#             del status_list[idx], trader_list[idx], notifier_list[idx]
#             num = len(status_list)

#         if status.total_gained_fiat_money < -Trader.MAX_LOST_JPY:
#             messages.append(f'{status.get_robot_title()} terminated')
#             del status_list[idx], trader_list[idx], notifier_list[idx]
#             num = len(status_list)

        if messages == []:

            if status.sample_number % Trader.TRADE_RATE == 0:
                bookkeeper.fth.write(f'{status}\n')

            if status.sample_number % BACKUP_RATE == 0:
                status.write()

            if status.sample_number % NOTIFY_RATE == 0:
                messages.append(f'{status} => Support level is {trader.min_unit_cc_trade_fiat_money} {status.fiat_symbol}.')

        if messages:
            notifier.send_slack(
                '\n'.join(messages), 'Power by https://jhub.name/', 'good' if status.get_total_gain_fiat_money() >= 0 else 'danger'
            )

#         if num == 0:
#             break

        status.sample_number += 1
        time.sleep(Trader.SAMPLE_INTERVAL / num / 2 / TEST_RATIO)

        idx = (idx + 1) % num