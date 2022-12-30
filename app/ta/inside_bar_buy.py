import time
import pandas as pd
import logging


async def inside_bar_buy(candles, periods = 126):

    dat = pd.DataFrame(candles)
    dat['datetime'] = dat['datetime'].sort_values(ascending=False)
    dat = dat[:periods]

    if len(dat) < 125:
        print('Error: insufficient data')
        raise

    try:
        dat = dat.sort_values(['datetime'], ignore_index=True)
    except Exception as e:
        return 'Error on datetime, probably empty stuff'
        raise

    close = float(list(dat['close'])[-1])
    low = float(list(dat['low'])[-1])
    high = float(list(dat['high'])[-1])

    ema8 = dat["close"].ewm(span=8, adjust=True, min_periods=7).mean()
    ema80 = dat["close"].ewm(span=80, adjust=True, min_periods=79).mean()

    ema8 = ema8.iloc[-1]
    ema80 = ema80.iloc[-1]

    ret = {}
    ret['ticker'] = dat.ticker.iloc[-1]
    ret['datetime'] = dat.datetime.iloc[-1]
    ret['entry_value'] = high
    ret['disruption_value'] = high
    ret['stop_loss'] = low
    ret['take_profit'] = high + ((high - low) * 2)
    ret['direction'] = 'SUPERIOR'

    if (close > ema8
        and close > ema80
        and dat.high.iloc[-1] < dat.high.iloc[-2]
        and dat.low.iloc[-1] > dat.low.iloc[-2]
        ):
        print(ret)
        print('ema8: ' + str(ema8))
        print('ema80: ' + str(ema80))

        return ret
    else:
        return False
