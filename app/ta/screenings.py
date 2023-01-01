from utils import datacon


async def inside_bar_buy(candles, timeframe, periods = 126):

    dat = await datacon.json_to_df(candles)

    if len(dat) < periods:
        print('Error: insufficient data')
        raise

    dat = dat.sort_values(['datetime'], ignore_index=True)

    close = float(list(dat['close'])[-1])
    low = float(list(dat['low'])[-1])
    high = float(list(dat['high'])[-1])

    ema8 = dat["close"].ewm(span=8, adjust=True, min_periods=7).mean()
    ema80 = dat["close"].ewm(span=80, adjust=True, min_periods=79).mean()

    ema8 = ema8.iloc[-1]
    ema80 = ema80.iloc[-1]

    if (close > ema8
        and close > ema80
        and dat.high.iloc[-1] < dat.high.iloc[-2]
        and dat.low.iloc[-1] > dat.low.iloc[-2]
        ):
        print('ema8: ' + str(ema8))
        print('ema80: ' + str(ema80))

        return await datacon.screening_output(ticker=dat.ticker.iloc[-1],
                                              timeframe=timeframe,
                                              datetime=dat.datetime.iloc[-1],
                                              entry_value=high,
                                              disruption_value=high,
                                              stop_loss=low,
                                              take_profit=high + ((high - low) * 2),
                                              direction='UPPER')
    else:
        return {}
