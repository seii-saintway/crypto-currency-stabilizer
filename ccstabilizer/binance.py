# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/main-binance.ipynb (unless otherwise specified).

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
#         init_buy_jpy = status.get_max_used_fiat_money() / Decimal(math.exp(self.lossable_unit_cc_bought_ratio / (1 - self.lossable_unit_cc_bought_ratio)))
        init_buy_jpy = status.get_max_used_fiat_money() / 10
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
    ('ETH', 'USDT'): Decimal('2000'),
    ('BNB', 'USDT'): Decimal('2000'),
#     ('AUTO', 'USDT'): Decimal('1000'),
    ('CELO', 'USDT'): Decimal('2000'),
#     ('CRV', 'USDT'): Decimal('1000'),
#     ('EPS', 'USDT'): Decimal('1000'),
#     ('FIL', 'USDT'): Decimal('1000'),
#     ('HARD', 'USDT'): Decimal('1000'),
#     ('HOT', 'USDT'): Decimal('1000'),
#     ('LINK', 'USDT'): Decimal('1000'),
#     ('NMR', 'USDT'): Decimal('1000'),
#     ('PUNDIX', 'USDT'): Decimal('1000'),
#     ('OCEAN', 'USDT'): Decimal('1000'),
    ('ONE', 'USDT'): Decimal('2000'),
#     ('OXT', 'USDT'): Decimal('1000'),
    ('SC', 'USDT'): Decimal('2000'),
#     ('SKL', 'USDT'): Decimal('1000'),
#     ('STORJ', 'USDT'): Decimal('1000'),
#     ('TRX', 'USDT'): Decimal('1000'),
#     ('WIN', 'USDT'): Decimal('1000'),
#     ('XLM', 'USDT'): Decimal('1000'),
    ('XRP', 'USDT'): Decimal('2000'),
    ('BNB', 'ETH'): Decimal('Infinity'),
#     ('HOT', 'ETH'): Decimal('Infinity'),
#     ('PUNDIX', 'ETH'): Decimal('Infinity'),
#     ('SC', 'ETH'): Decimal('Infinity'),
#     ('XLM', 'ETH'): Decimal('Infinity'),
    ('XRP', 'ETH'): Decimal('Infinity'),
#     ('CRV', 'BNB'): Decimal('Infinity'),
#     ('FIL', 'BNB'): Decimal('Infinity'),
#     ('HARD', 'BNB'): Decimal('Infinity'),
#     ('HOT', 'BNB'): Decimal('Infinity'),
#     ('NMR', 'BNB'): Decimal('Infinity'),
#     ('OCEAN', 'BNB'): Decimal('Infinity'),
    ('ONE', 'BNB'): Decimal('Infinity'),
    ('SC', 'BNB'): Decimal('Infinity'),
#     ('XLM', 'BNB'): Decimal('Infinity'),
    ('XRP', 'BNB'): Decimal('Infinity'),
#     ('WIN', 'TRX'): Decimal('Infinity'),
}
GAINABLE_UNIT_CC_SOLD_RATIO = {
    ('ETH', 'USDT'): Decimal('0.146'),
    ('BNB', 'USDT'): Decimal('0.146'),
#     ('AUTO', 'USDT'): Decimal('0.0557'),
    ('CELO', 'USDT'): Decimal('0.618'),
#     ('CRV', 'USDT'): Decimal('0.146'),
#     ('EPS', 'USDT'): Decimal('0.0031'),
#     ('FIL', 'USDT'): Decimal('0.146'),
#     ('HARD', 'USDT'): Decimal('0.146'),
#     ('HOT', 'USDT'): Decimal('0.146'),
#     ('LINK', 'USDT'): Decimal('0.09'),
#     ('NMR', 'USDT'): Decimal('0.146'),
#     ('PUNDIX', 'USDT'): Decimal('0.146'),
#     ('OCEAN', 'USDT'): Decimal('0.146'),
    ('ONE', 'USDT'): Decimal('0.146'),
#     ('OXT', 'USDT'): Decimal('0.146'),
    ('SC', 'USDT'): Decimal('0.146'),
#     ('SKL', 'USDT'): Decimal('0.146'),
#     ('STORJ', 'USDT'): Decimal('0.146'),
#     ('TRX', 'USDT'): Decimal('0.146'),
#     ('WIN', 'USDT'): Decimal('0.382'),
#     ('XLM', 'USDT'): Decimal('0.146'),
    ('XRP', 'USDT'): Decimal('0.146'),
    ('BNB', 'ETH'): Decimal('0.146'),
#     ('HOT', 'ETH'): Decimal('0.146'),
#     ('PUNDIX', 'ETH'): Decimal('0.146'),
#     ('SC', 'ETH'): Decimal('0.146'),
#     ('XLM', 'ETH'): Decimal('0.146'),
    ('XRP', 'ETH'): Decimal('0.146'),
#     ('CRV', 'BNB'): Decimal('0.146'),
#     ('FIL', 'BNB'): Decimal('0.146'),
#     ('HARD', 'BNB'): Decimal('0.146'),
#     ('HOT', 'BNB'): Decimal('0.146'),
#     ('NMR', 'BNB'): Decimal('0.146'),
#     ('OCEAN', 'BNB'): Decimal('0.146'),
    ('ONE', 'BNB'): Decimal('0.146'),
    ('SC', 'BNB'): Decimal('0.146'),
#     ('XLM', 'BNB'): Decimal('0.146'),
    ('XRP', 'BNB'): Decimal('0.146'),
#     ('WIN', 'TRX'): Decimal('0.146'),
}
LOSSABLE_UNIT_CC_BOUGHT_RATIO = {
    ('ETH', 'USDT'): Decimal('0.618'),
    ('BNB', 'USDT'): Decimal('0.618'),
#     ('AUTO', 'USDT'): Decimal('0.618'),
    ('CELO', 'USDT'): Decimal('0.618'),
#     ('CRV', 'USDT'): Decimal('0.618'),
#     ('EPS', 'USDT'): Decimal('0.618'),
#     ('FIL', 'USDT'): Decimal('0.618'),
#     ('HARD', 'USDT'): Decimal('0.618'),
#     ('HOT', 'USDT'): Decimal('0.618'),
#     ('LINK', 'USDT'): Decimal('0.618'),
#     ('NMR', 'USDT'): Decimal('0.618'),
#     ('PUNDIX', 'USDT'): Decimal('0.618'),
#     ('OCEAN', 'USDT'): Decimal('0.618'),
    ('ONE', 'USDT'): Decimal('0.618'),
#     ('OXT', 'USDT'): Decimal('0.618'),
    ('SC', 'USDT'): Decimal('0.618'),
#     ('SKL', 'USDT'): Decimal('0.618'),
#     ('STORJ', 'USDT'): Decimal('0.618'),
#     ('TRX', 'USDT'): Decimal('0.618'),
#     ('WIN', 'USDT'): Decimal('0.618'),
#     ('XLM', 'USDT'): Decimal('0.618'),
    ('XRP', 'USDT'): Decimal('0.618'),
    ('BNB', 'ETH'): Decimal('0.382'),
#     ('HOT', 'ETH'): Decimal('0.382'),
#     ('PUNDIX', 'ETH'): Decimal('0.382'),
#     ('SC', 'ETH'): Decimal('0.382'),
#     ('XLM', 'ETH'): Decimal('0.382'),
    ('XRP', 'ETH'): Decimal('0.382'),
#     ('CRV', 'BNB'): Decimal('0.236'),
#     ('FIL', 'BNB'): Decimal('0.236'),
#     ('HARD', 'BNB'): Decimal('0.236'),
#     ('HOT', 'BNB'): Decimal('0.236'),
#     ('NMR', 'BNB'): Decimal('0.236'),
#     ('OCEAN', 'BNB'): Decimal('0.236'),
    ('ONE', 'BNB'): Decimal('0.236'),
    ('SC', 'BNB'): Decimal('0.236'),
#     ('XLM', 'BNB'): Decimal('0.236'),
    ('XRP', 'BNB'): Decimal('0.236'),
#     ('WIN', 'TRX'): Decimal('0.146'),
}
# => MA(99)
MIN_TRADE_FIAT_PRICE = {
    ('ETH', 'USDT'): Decimal('1380'),
    ('BNB', 'USDT'): Decimal('210'),
#     ('AUTO', 'USDT'): Decimal('0'),
    ('CELO', 'USDT'): Decimal('3'),
#     ('CRV', 'USDT'): Decimal('0'),
#     ('EPS', 'USDT'): Decimal('0'),
#     ('FIL', 'USDT'): Decimal('0'),
#     ('HARD', 'USDT'): Decimal('0'),
#     ('HOT', 'USDT'): Decimal('0'),
#     ('LINK', 'USDT'): Decimal('0'),
#     ('NMR', 'USDT'): Decimal('0'),
#     ('PUNDIX', 'USDT'): Decimal('0'),
#     ('OCEAN', 'USDT'): Decimal('0'),
    ('ONE', 'USDT'): Decimal('0.045'),
#     ('OXT', 'USDT'): Decimal('0'),
    ('SC', 'USDT'): Decimal('0.017'),
#     ('SKL', 'USDT'): Decimal('0'),
#     ('STORJ', 'USDT'): Decimal('0'),
#     ('TRX', 'USDT'): Decimal('0'),
#     ('WIN', 'USDT'): Decimal('0'),
#     ('XLM', 'USDT'): Decimal('0'),
    ('XRP', 'USDT'): Decimal('0.55'),
    ('BNB', 'ETH'): Decimal('0'),
#     ('HOT', 'ETH'): Decimal('0'),
#     ('PUNDIX', 'ETH'): Decimal('0'),
#     ('SC', 'ETH'): Decimal('0'),
#     ('XLM', 'ETH'): Decimal('0'),
    ('XRP', 'ETH'): Decimal('0'),
#     ('CRV', 'BNB'): Decimal('0'),
#     ('FIL', 'BNB'): Decimal('0'),
#     ('HARD', 'BNB'): Decimal('0'),
#     ('HOT', 'BNB'): Decimal('0'),
#     ('NMR', 'BNB'): Decimal('0'),
#     ('OCEAN', 'BNB'): Decimal('0'),
    ('ONE', 'BNB'): Decimal('0'),
    ('SC', 'BNB'): Decimal('0'),
#     ('XLM', 'BNB'): Decimal('0'),
    ('XRP', 'BNB'): Decimal('0'),
#     ('WIN', 'TRX'): Decimal('0'),
}
MAX_TRADE_FIAT_PRICE = {
    ('ETH', 'USDT'): Decimal('Infinity'),
    ('BNB', 'USDT'): Decimal('Infinity'),
#     ('AUTO', 'USDT'): Decimal('Infinity'),
    ('CELO', 'USDT'): Decimal('Infinity'),
#     ('CRV', 'USDT'): Decimal('Infinity'),
#     ('EPS', 'USDT'): Decimal('Infinity'),
#     ('FIL', 'USDT'): Decimal('Infinity'),
#     ('HARD', 'USDT'): Decimal('Infinity'),
#     ('HOT', 'USDT'): Decimal('Infinity'),
#     ('LINK', 'USDT'): Decimal('Infinity'),
#     ('NMR', 'USDT'): Decimal('Infinity'),
#     ('PUNDIX', 'USDT'): Decimal('Infinity'),
#     ('OCEAN', 'USDT'): Decimal('Infinity'),
    ('ONE', 'USDT'): Decimal('Infinity'),
#     ('OXT', 'USDT'): Decimal('Infinity'),
    ('SC', 'USDT'): Decimal('Infinity'),
#     ('SKL', 'USDT'): Decimal('Infinity'),
#     ('STORJ', 'USDT'): Decimal('Infinity'),
#     ('TRX', 'USDT'): Decimal('Infinity'),
#     ('WIN', 'USDT'): Decimal('Infinity'),
#     ('XLM', 'USDT'): Decimal('Infinity'),
    ('XRP', 'USDT'): Decimal('Infinity'),
    ('BNB', 'ETH'): Decimal('Infinity'),
#     ('HOT', 'ETH'): Decimal('Infinity'),
#     ('PUNDIX', 'ETH'): Decimal('Infinity'),
#     ('SC', 'ETH'): Decimal('Infinity'),
#     ('XLM', 'ETH'): Decimal('Infinity'),
    ('XRP', 'ETH'): Decimal('Infinity'),
#     ('CRV', 'BNB'): Decimal('Infinity'),
#     ('FIL', 'BNB'): Decimal('Infinity'),
#     ('HARD', 'BNB'): Decimal('Infinity'),
#     ('HOT', 'BNB'): Decimal('Infinity'),
#     ('NMR', 'BNB'): Decimal('Infinity'),
#     ('OCEAN', 'BNB'): Decimal('Infinity'),
    ('ONE', 'BNB'): Decimal('Infinity'),
    ('SC', 'BNB'): Decimal('Infinity'),
#     ('XLM', 'BNB'): Decimal('Infinity'),
    ('XRP', 'BNB'): Decimal('Infinity'),
#     ('WIN', 'TRX'): Decimal('Infinity'),
}
ICON_URL = {
    'AUTO': 'https://research.binance.com/static/images/projects/bnb/logo.png',
    'BNB': 'https://cryptologos.cc/logos/binance-coin-bnb-logo.png',
    'CELO': 'https://cryptologos.cc/logos/celo-celo-logo.png',
    'CRV': 'https://cryptologos.cc/logos/curve-dao-token-crv-logo.png',
    'EPS': 'https://research.binance.com/static/images/projects/bnb/logo.png',
    'ETH': 'https://cryptologos.cc/logos/ethereum-eth-logo.png',
    'FIL': 'https://cryptologos.cc/logos/filecoin-fil-logo.png',
    'HARD': 'https://research.binance.com/static/images/projects/bnb/logo.png',
    'HOT': 'https://cryptologos.cc/logos/holo-hot-logo.png',
    'LINK': 'https://cryptologos.cc/logos/chainlink-link-logo.png',
    'NMR': 'https://cryptologos.cc/logos/numeraire-nmr-logo.png',
    'OCEAN': 'https://cryptologos.cc/logos/ocean-protocol-ocean-logo.png',
    'ONE': 'https://cryptologos.cc/logos/harmony-one-logo.png',
    'OXT': 'https://cryptologos.cc/logos/orchid-oxt-logo.png',
    'PUNDIX': 'https://cryptologos.cc/logos/pundi-x-npxs-logo.png',
    'SC': 'https://cryptologos.cc/logos/siacoin-sc-logo.png',
    'SKL': 'https://research.binance.com/static/images/projects/bnb/logo.png',
    'STORJ': 'https://cryptologos.cc/logos/storj-storj-logo.png',
    'TRX': 'https://cryptologos.cc/logos/tron-trx-logo.png',
    'WIN': 'https://research.binance.com/static/images/projects/bnb/logo.png',
    'XLM': 'https://cryptologos.cc/logos/stellar-xlm-logo.png',
    'XRP': 'https://cryptologos.cc/logos/xrp-xrp-logo.png',
}

# Internal Cell
from ccstabilizer import Binance
from ccstabilizer import secrets
from ccstabilizer import Fetcher
from ccstabilizer import Notifier
from ccstabilizer import Status

# Internal Cell
Status.robot_name_prefix = 'BN-'
exchange = Binance()
fetcher = Fetcher(exchange)
notifier = Notifier(channel_name='binance', name='Launcher')

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
    # TODO: eliminate trade_unit specifications/logic
#     status.trade_unit = min_trade_unit
    status.max_used_fiat_money_limit = max_used_fiat_money_limit
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
            channel_name='binance',
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

        if status.bought_unit_amount == 0:
            messages.append(f'{status.get_robot_title()} terminated')
            del status_list[idx], trader_list[idx], notifier_list[idx]
            num = len(status_list)

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