import logging

from app import datacon


async def inside_bar_buy(candles, timeframe, periods=126):

    dat = await datacon.json_to_df(candles)


    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(list(dat['close'])[-1])
    low = float(list(dat['low'])[-1])
    high = float(list(dat['high'])[-1])

    ema8 = dat["close"].ewm(span=8, adjust=True, min_periods=7).mean()
    ema80 = dat["close"].ewm(span=80, adjust=True, min_periods=79).mean()

    ema8 = ema8.iloc[-1]
    ema80 = ema80.iloc[-1]

    last_high = dat.high.iloc[-1]
    prior_to_last_high = dat.high.iloc[-2]

    last_low = dat.low.iloc[-1]
    prior_to_last_low = dat.low.iloc[-2]

    if (close > ema8
                and close > ema80
                and last_high < prior_to_last_high
                and last_low > prior_to_last_low
            ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=high,
                                        disruption_value=high,
                                        stop_loss=low,
                                        take_profit=high +
                                        ((high - low) * 2),
                                        direction='UPPER')
    else:
        return {}


async def inside_bar_sell(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(list(dat['close'])[-1])
    low = float(list(dat['low'])[-1])
    high = float(list(dat['high'])[-1])

    ema8 = dat["close"].ewm(span=8, adjust=True, min_periods=7).mean()
    ema80 = dat["close"].ewm(span=80, adjust=True, min_periods=79).mean()

    ema8 = ema8.iloc[-1]
    ema80 = ema80.iloc[-1]

    if (close < ema8
            and float(close) < float(ema80)
            and high < float(dat.high.iloc[-2])
            and float(low) > float(dat.low.iloc[-2])
            ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=low,
                                        disruption_value=low,
                                        stop_loss=high,
                                        take_profit=low -
                                        ((high - low) * 2),
                                        direction='LOWER')
    else:
        return {}


async def continuous_stitch_buy(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(list(dat['close'])[-1])
    last_close = float(list(dat['close'])[-2])
    low = float(list(dat['low'])[-1])
    high = float(list(dat['high'])[-1])
    high2 = float(list(dat['high'])[-2])
    high3 = float(list(dat['high'])[-3])

    ema20 = dat["close"].ewm(span=20, min_periods=19, adjust=True).mean()
    ema30 = dat["close"].ewm(span=30, min_periods=29, adjust=True).mean()
    last_ema20 = ema20.iloc[-2]
    ema20_3 = ema20.iloc[-3]

    ema20 = ema20.iloc[-1]
    ema30 = ema30.iloc[-1]

    if (low <= ema20
                and close > ema20
                and ema20 > ema30
                and high2 > last_ema20
                and high3 > ema20_3
                and last_close > last_ema20
            ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=high,
                                        disruption_value=high,
                                        stop_loss=low,
                                        take_profit=high +
                                        ((high - low) * 2),
                                        direction='UPPER')
    else:
        return {}


async def continuous_stitch_sell(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    low = float(list(dat['low'])[-1])
    low2 = float(list(dat['low'])[-2])
    low3 = float(list(dat['low'])[-3])
    high = float(list(dat['high'])[-1])
    high1 = float(list(dat['high'])[-2])
    last_close = float(list(dat['close'])[-2])

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    ema20 = dat["close"].ewm(span=20, min_periods=19, adjust=True).mean()
    ema30 = dat["close"].ewm(span=30, min_periods=29, adjust=True).mean()
    last_ema20 = ema20.iloc[-2]
    ema20_3 = ema20.iloc[-3]

    ema9 = ema9.iloc[-1]
    ema20 = ema20.iloc[-1]
    ema30 = ema30.iloc[-1]

    if (low < ema20
                and high >= ema20
                and ema9 < ema20
                and high > high1
                and low2 < last_ema20
                and low3 < ema20_3
                and last_close < last_ema20
            ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=low,
                                        disruption_value=low,
                                        stop_loss=high,
                                        take_profit=low -
                                        ((high - low) * 2),
                                        direction='LOWER')
    else:
        return {}


async def setup_91_buy(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(dat['close'].iloc[-1])
    low = float(dat['low'].iloc[-1])
    high = float(dat['high'].iloc[-1])

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    ema9_last = ema9.iloc[-1]
    ema9_penultimate = ema9.iloc[-2]
    ema9_3 = ema9.iloc[-3]
    last_inclination = ema9_penultimate - ema9_3
    inclination = ema9_last - ema9_penultimate

    if (inclination > 0
            and close > ema9_last
                and last_inclination < 0
            ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=high,
                                        disruption_value=high,
                                        stop_loss=low,
                                        take_profit=high +
                                        ((high - low) * 2),
                                        direction='UPPER')
    else:
        return {}


async def setup_91_sell(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(dat['close'].iloc[-1])
    low = float(dat['low'].iloc[-1])
    high = float(dat['high'].iloc[-1])

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    ema9_last = ema9.iloc[-1]
    ema9_penultimate = ema9.iloc[-2]
    ema9_3 = ema9.iloc[-3]
    last_inclination = ema9_penultimate - ema9_3
    inclination = ema9_last - ema9_penultimate

    if (inclination < 0
        and close < ema9_last
            and last_inclination > 0
        ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=low,
                                        disruption_value=low,
                                        stop_loss=high,
                                        take_profit=low -
                                        ((high - low) * 2),
                                        direction='LOWER')
    else:
        return {}


async def setup_92_buy(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    low = float(dat['low'].iloc[-1])
    high = float(dat['high'].iloc[-1])

    close = float(dat['close'].iloc[-1])
    last_low = float(dat['low'].iloc[-2])

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    inclination = ema9.diff()

    buy_cond_1 = False in list(dat['low'][-5:].astype(float) > ema9[-5:])
    buy_cond_2 = False in list(inclination[-5:] > 0)

    if (not buy_cond_1 and not buy_cond_2
            and close < last_low
        ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=high,
                                        disruption_value=high,
                                        stop_loss=low,
                                        take_profit=high +
                                        ((high - low) * 2),
                                        direction='UPPER')
    else:
        return {}


async def setup_92_sell(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    low = float(dat['low'].iloc[-1])
    high = float(dat['high'].iloc[-1])

    close = float(dat['close'].iloc[-1])
    last_high = float(dat['high'].iloc[-2])

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    inclination = ema9.diff()

    sell_cond_1 = False in list(dat['high'][-5:].astype(float) < ema9[-5:])
    sell_cond_2 = False in list(inclination[-5:] < 0)

    if (not sell_cond_1 and not sell_cond_2
                and close > last_high
            ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=low,
                                        disruption_value=low,
                                        stop_loss=high,
                                        take_profit=low -
                                        ((high - low) * 2),
                                        direction='LOWER')
    else:
        return {}


async def setup_93_buy(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    inclination = ema9.diff()

    buy_cond_1 = False in list(dat['low'][-3:].astype(float) > ema9[-3:])
    buy_cond_2 = False in list(inclination[-5:] > 0)

    close_3 = float(dat['close'].iloc[-3])
    close_2 = float(dat['close'].iloc[-2])
    close = float(dat['close'].iloc[-1])
    low = float(dat['low'].iloc[-1])
    high = float(dat['high'].iloc[-1])

    buy_cond_3 = close_2 < close_3 and close < close_3

    if (not buy_cond_1 and buy_cond_2 and buy_cond_3
            ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=high,
                                        disruption_value=high,
                                        stop_loss=low,
                                        take_profit=high +
                                        ((high - low) * 2),
                                        direction='UPPER')
    else:
        return {}


async def setup_93_sell(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    inclination = ema9.diff()

    sell_cond_1 = False in list(dat['high'][-3:].astype(float) < ema9[-3:])
    sell_cond_2 = False in list(inclination[-5:] < 0)

    close_3 = float(dat['close'].iloc[-3])
    close_2 = float(dat['close'].iloc[-2])
    close = float(dat['close'].iloc[-1])
    low = float(dat['low'].iloc[-1])
    high = float(dat['high'].iloc[-1])

    sell_cond_3 = close_2 > close_3 and close > close_3

    if (not sell_cond_1 and sell_cond_2 and sell_cond_3
        ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=low,
                                        disruption_value=low,
                                        stop_loss=high,
                                        take_profit=low -
                                        ((high - low) * 2),
                                        direction='LOWER')
    else:
        return {}


async def setup_94_buy(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    dat['ema'] = ema9
    inc_ema9 = ema9.diff()

    buy_cond_1 = False in list(dat['low'][-7:-2].astype(float) > ema9[-7:-2])

    close_2 = float(dat['close'].iloc[-2])
    low = float(dat['low'].iloc[-1])
    low_2 = low = float(dat['low'].iloc[-2])
    high = float(dat['high'].iloc[-1])
    buy_cond_2 = (close_2 < ema9.iloc[-2]) and (low > low_2)
    buy_cond_3 = (inc_ema9.iloc[-2] < 0) and (inc_ema9.iloc[-1] > 0)

    if (not buy_cond_1 and buy_cond_2 and buy_cond_3):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=high,
                                        disruption_value=high,
                                        stop_loss=low,
                                        take_profit=high +
                                        ((high - low) * 2),
                                        direction='UPPER')
    else:
        return {}


async def setup_94_sell(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    dat['ema'] = ema9
    inc_ema9 = ema9.diff()

    sell_cond_1 = False in list(dat['high'][-7:-2].astype(float) < ema9[-7:-2])

    close_2 = float(dat['close'].iloc[-2])
    low = float(dat['low'].iloc[-1])
    high = float(dat['high'].iloc[-1])
    high_2 = float(dat['high'].iloc[-2])

    # print(inc_ema9)

    sell_cond_2 = (close_2 > ema9.iloc[-2]) and (high < high_2)
    sell_cond_3 = (inc_ema9.iloc[-2] > 0) and (inc_ema9.iloc[-1] < 0)

    if (not sell_cond_1 and sell_cond_2 and sell_cond_3
        ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=low,
                                        disruption_value=low,
                                        stop_loss=high,
                                        take_profit=low -
                                        ((high - low) * 2),
                                        direction='LOWER')
    else:
        return {}


async def fox_trap_buy(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(list(dat['close'])[-1])
    low = float(list(dat['low'])[-1])
    high = float(dat['high'].iloc[-1])
    high2 = float(dat['high'].iloc[-2])
    high3 = float(dat['high'].iloc[-3])

    ema8 = dat["close"].ewm(span=8, min_periods=7, adjust=True).mean()
    ema20 = dat["close"].ewm(span=20, min_periods=19, adjust=True).mean()
    ema80 = dat["close"].ewm(span=80, min_periods=79, adjust=True).mean()
    ema20_2 = ema20.iloc[-2]
    ema20_3 = ema20.iloc[-3]

    ema8 = ema8.iloc[-1]
    ema20 = ema20.iloc[-1]
    ema80 = ema80.iloc[-1]

    if (close > ema8
        and close > ema80
        and low < ema8
        and ema8 > ema80
        and ema8 > ema20
        and high2 > ema20_2
            and high3 > ema20_3):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=high,
                                        disruption_value=high,
                                        stop_loss=low,
                                        take_profit=high +
                                        ((high - low) * 2),
                                        direction='UPPER')
    else:
        return {}


async def fox_trap_sell(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(list(dat['close'])[-1])
    high = float(list(dat['high'])[-1])
    low = float(list(dat['low'])[-1])
    low2 = float(list(dat['low'])[-2])
    low3 = float(list(dat['low'])[-3])

    ema8 = dat["close"].ewm(span=8, min_periods=7, adjust=True).mean()
    ema80 = dat["close"].ewm(span=80, min_periods=79, adjust=True).mean()
    ema8_2 = ema8.iloc[-2]
    ema8_3 = ema8.iloc[-3]

    ema8 = ema8.iloc[-1]
    ema80 = ema80.iloc[-1]

    if (close < ema80
            and close < ema8
            and high > ema8
            and ema8 < ema80
            and low2 < ema8_2
            and low3 < ema8_3
            ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=low,
                                        disruption_value=low,
                                        stop_loss=high,
                                        take_profit=low -
                                        ((high - low) * 2),
                                        direction='LOWER')
    else:
        return {}


async def bear_trap_buy(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(list(dat['close'])[-1])
    last_close = float(list(dat['close'])[-2])
    low = float(list(dat['low'])[-1])
    high = float(list(dat['high'])[-1])
    high2 = float(list(dat['high'])[-2])
    high3 = float(list(dat['high'])[-3])

    ema8 = dat["close"].ewm(span=8, min_periods=7, adjust=True).mean()
    ema80 = dat["close"].ewm(span=80, min_periods=79, adjust=True).mean()
    last_ema80 = ema80.iloc[-2]
    ema8_2 = ema8.iloc[-2]
    ema8_3 = ema8.iloc[-3]

    ema8 = ema8.iloc[-1]
    ema80 = ema80.iloc[-1]

    if (low < ema80
        and close > ema80
        and last_close > last_ema80
        and high2 > ema8_2
            and high3 > ema8_3):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=high,
                                        disruption_value=high,
                                        stop_loss=low,
                                        take_profit=high +
                                        ((high - low) * 2),
                                        direction='UPPER')
    else:
        return {}


async def bear_trap_sell(candles, timeframe, periods=126):

    dat = candles

    dat = dat.sort_index(ascending=True)

    if len(dat) < periods:
        logging.info('Error: insufficient data')

    close = float(list(dat['close'])[-1])
    last_close = float(list(dat['close'])[-2])
    low = float(list(dat['low'])[-1])
    low2 = float(list(dat['low'])[-2])
    low3 = float(list(dat['low'])[-3])
    high = float(list(dat['high'])[-1])

    ema8 = dat["close"].ewm(span=8, min_periods=7, adjust=True).mean()
    ema80 = dat["close"].ewm(span=80, min_periods=79, adjust=True).mean()
    last_ema80 = ema80.iloc[-2]
    ema8_2 = ema8.iloc[-2]
    ema8_3 = ema8.iloc[-3]

    ema8 = ema8.iloc[-1]
    ema80 = ema80.iloc[-1]

    if (high > ema80
        and close < ema80
        and last_close < last_ema80
        and low2 < ema8_2
        and low3 < ema8_3
        ):

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                        timeframe=timeframe,
                                        pet_datetime=dat.index[-1],
                                        entry_value=low,
                                        disruption_value=low,
                                        stop_loss=high,
                                        take_profit=low -
                                        ((high - low) * 2),
                                        direction='LOWER')
    else:
        return {}
