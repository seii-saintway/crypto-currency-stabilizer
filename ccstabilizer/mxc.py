# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/main-mxc.ipynb (unless otherwise specified).

__all__ = ['TEST_RATIO', 'NOTIFY_RATE', 'BACKUP_RATE', 'FIAT_SYMBOLS', 'MAX_USED_FIAT_MONEY_LIMIT',
           'GAINABLE_UNIT_CC_SOLD_RATIO', 'LOSSABLE_UNIT_CC_BOUGHT_RATIO', 'MIN_TRADE_FIAT_PRICE',
           'MAX_TRADE_FIAT_PRICE']

# Cell
TEST_RATIO = 1

# Cell
NOTIFY_RATE = 60 * 8
BACKUP_RATE = 1

# Cell
from decimal import Decimal

FIAT_SYMBOLS = {
    'AR': 'USDT',
    'B20': 'USDT',
    'BDP': 'USDT',
    'HOPR': 'USDT',
    'OCEAN': 'USDT',
    'VELO': 'USDT',
    'ZYRO': 'USDT',
}
MAX_USED_FIAT_MONEY_LIMIT = {
    'AR': Decimal('1000'),
    'B20': Decimal('1000'),
    'BDP': Decimal('1000'),
    'HOPR': Decimal('1000'),
    'OCEAN': Decimal('1000'),
    'VELO': Decimal('1000'),
    'ZYRO': Decimal('1000'),
}
GAINABLE_UNIT_CC_SOLD_RATIO = {
    'AR': Decimal('0.236'),
    'B20': Decimal('0.236'),
    'BDP': Decimal('0.236'),
    'HOPR': Decimal('0.236'),
    'OCEAN': Decimal('0.236'),
    'VELO': Decimal('0.236'),
    'ZYRO': Decimal('0.236'),
}
LOSSABLE_UNIT_CC_BOUGHT_RATIO = {
    'AR': Decimal('0.618'),
    'B20': Decimal('0.786'),
    'BDP': Decimal('0.618'),
    'HOPR': Decimal('0.618'),
    'OCEAN': Decimal('0.786'),
    'VELO': Decimal('0.618'),
    'ZYRO': Decimal('0.786'),
}
MIN_TRADE_FIAT_PRICE = {
    'AR': Decimal('0'),
    'B20': Decimal('0'),
    'BDP': Decimal('0'),
    'HOPR': Decimal('0'),
    'OCEAN': Decimal('0'),
    'VELO': Decimal('0'),
    'ZYRO': Decimal('0'),
}
MAX_TRADE_FIAT_PRICE = {
    'AR': Decimal('Infinity'),
    'B20': Decimal('Infinity'),
    'BDP': Decimal('Infinity'),
    'HOPR': Decimal('Infinity'),
    'OCEAN': Decimal('Infinity'),
    'VELO': Decimal('Infinity'),
    'ZYRO': Decimal('Infinity'),
}

# Internal Cell
from ccstabilizer import Fetcher
from ccstabilizer import Notifier
from ccstabilizer import Trader
from ccstabilizer import Status

# Internal Cell
fetcher = Fetcher()
notifier = Notifier('Launcher')

# notifier.send_slack(
#     f'{CRYPTO_SYMBOL}-{FIAT_SYMBOL} Detecting started\n', 'Power by https://jhub.name/', 'good'
# )

crypto_infos = {}
for crypto_symbol in FIAT_SYMBOLS:
    fiat_symbol = FIAT_SYMBOLS[crypto_symbol]

    symbol_in_mxc = f'{crypto_symbol}_{fiat_symbol}'
    crypto_info = fetcher.get_trading_spec(symbol_in_mxc)
    if crypto_info.get('symbol', '') == symbol_in_mxc and crypto_info.get('limited', False) == True:
        crypto_infos[crypto_symbol] = crypto_info
        notifier.send_slack(
            f'{crypto_symbol}-{fiat_symbol} detected\n', 'Power by https://jhub.name/', 'good'
        )

status_list = []
for crypto_symbol in crypto_infos:
    fiat_symbol = FIAT_SYMBOLS[crypto_symbol]
    max_used_fiat_money_limit = MAX_USED_FIAT_MONEY_LIMIT[crypto_symbol]
    crypto_info = crypto_infos[crypto_symbol]
    status = Status(
        robot_name = f'{crypto_symbol} Robot',
        crypto_symbol = crypto_symbol,
        fiat_symbol = fiat_symbol,
        max_used_fiat_money_limit = max_used_fiat_money_limit,
        **crypto_info
    )
    status.read()
    status_list.append(status)

trader_list = []
notifier_list = []
for status in status_list:
    trader = Trader(
        status = status,
        gainable_unit_cc_sold_ratio = GAINABLE_UNIT_CC_SOLD_RATIO[status.crypto_symbol],
        lossable_unit_cc_bought_ratio = LOSSABLE_UNIT_CC_BOUGHT_RATIO[status.crypto_symbol],
        min_trade_fiat_price = MIN_TRADE_FIAT_PRICE[status.crypto_symbol],
        max_trade_fiat_price = MAX_TRADE_FIAT_PRICE[status.crypto_symbol]
    )
    trader_list.append(trader)
    notifier = Notifier(status.crypto_symbol)
    notifier.send_slack(
        f'{status.robot_name} launched\n' f'{status.get_robot_title()}', 'Power by https://jhub.name/', 'good'
    )
    notifier_list.append(notifier)

# Internal Cell
from ccstabilizer import BookKeeper
from ccstabilizer import Trader

# Internal Cell
import time


with BookKeeper(status_list) as bookkeeper:

    idx = 0
    num = len(status_list)

    while __name__ == '__main__':

        status = status_list[idx]
        trader = trader_list[idx]
        notifier = notifier_list[idx]

        cooling_interval, trade_type, unit_amount = trader.check_and_trade()

        bookkeeper.fsh.write(f'{status}\n')

        new_status_list = bookkeeper.estimate_status()

        messages = []
        for i, new_status in enumerate(new_status_list):
            if new_status is not status_list[i]:

                status_list[i].update(new_status)

                bookkeeper.fth.write(f'{status_list[i]}\n')
                status_list[i].write()

                messages.append(f'{status_list[i].last_transaction} => {status_list[i].get_robot_title()}')
                messages.append(f'{status_list[i]} => Support level is {trader.min_unit_cc_trade_fiat_money} {status_list[i].fiat_symbol}.')

#         if status.bought_unit_amount == 0:
#             messages.append(f'{status.robot_name} terminated\n' f'{status.get_robot_title()}')
#             del status_list[idx], trader_list[idx], notifier_list[idx]
#             num = len(status_list)

#         if status.total_gained_fiat_money < -Trader.MAX_LOST_JPY:
#             messages.append(f'{status.robot_name} terminated\n' f'{status.get_robot_title()}')
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