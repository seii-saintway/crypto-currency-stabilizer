# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/main-binance.ipynb (unless otherwise specified).

__all__ = ['TEST_RATIO', 'NOTIFY_RATE', 'BACKUP_RATE', 'MAX_USED_FIAT_MONEY_LIMIT', 'GAINABLE_UNIT_CC_SOLD_RATIO',
           'LOSSABLE_UNIT_CC_BOUGHT_RATIO', 'MIN_TRADE_FIAT_PRICE', 'MAX_TRADE_FIAT_PRICE']

# Cell
TEST_RATIO = 1

# Cell
NOTIFY_RATE = 60 * 8
BACKUP_RATE = 1

# Cell
from decimal import Decimal

MAX_USED_FIAT_MONEY_LIMIT = {
    ('CELO', 'USDT'): Decimal('Infinity'),
    ('BNB', 'USDT'): Decimal('3000'),
    ('ETH', 'USDT'): Decimal('3000'),
    ('BNB', 'ETH'): Decimal('Infinity'),
    ('OCEAN', 'USDT'): Decimal('1000'),
    ('XLM', 'USDT'): Decimal('1000'),
}
GAINABLE_UNIT_CC_SOLD_RATIO = {
    ('CELO', 'USDT'): Decimal('0.618'),
    ('BNB', 'USDT'): Decimal('0.236'),
    ('ETH', 'USDT'): Decimal('0.236'),
    ('BNB', 'ETH'): Decimal('0.618'),
    ('OCEAN', 'USDT'): Decimal('0.236'),
    ('XLM', 'USDT'): Decimal('0.236'),
}
LOSSABLE_UNIT_CC_BOUGHT_RATIO = {
    ('CELO', 'USDT'): Decimal('0.786'),
    ('BNB', 'USDT'): Decimal('0.618'),
    ('ETH', 'USDT'): Decimal('0.786'),
    ('BNB', 'ETH'): Decimal('0.618'),
    ('OCEAN', 'USDT'): Decimal('0.786'),
    ('XLM', 'USDT'): Decimal('0.786'),
}
MIN_TRADE_FIAT_PRICE = {
    ('CELO', 'USDT'): Decimal('3'),
    ('BNB', 'USDT'): Decimal('50'),
    ('ETH', 'USDT'): Decimal('150'),
    ('BNB', 'ETH'): Decimal('0'),
    ('OCEAN', 'USDT'): Decimal('0'),
    ('XLM', 'USDT'): Decimal('0'),
}
MAX_TRADE_FIAT_PRICE = {
    ('CELO', 'USDT'): Decimal('Infinity'),
    ('BNB', 'USDT'): Decimal('Infinity'),
    ('ETH', 'USDT'): Decimal('Infinity'),
    ('BNB', 'ETH'): Decimal('Infinity'),
    ('OCEAN', 'USDT'): Decimal('Infinity'),
    ('XLM', 'USDT'): Decimal('Infinity'),
}

# Internal Cell
from ccstabilizer import Binance
from ccstabilizer import secrets
from ccstabilizer import Fetcher
from ccstabilizer import Notifier
from ccstabilizer import Trader
from ccstabilizer import Status

# Internal Cell
exchange = Binance()
fetcher = Fetcher(exchange)
notifier = Notifier(channel_name='binance', name='Launcher', icon_url='https://research.binance.com/static/images/projects/bnb/logo.png')

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
    status_list.append(status)

notifier.send_slack(
    ''.join(messages), 'Power by https://jhub.name/', color
)

# Internal Cell
from ccstabilizer import BookKeeper
from ccstabilizer import Trader

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
            icon_url='https://research.binance.com/static/images/projects/bnb/logo.png'
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
        time.sleep(Trader.SAMPLE_INTERVAL / num / TEST_RATIO)

        idx = (idx + 1) % num