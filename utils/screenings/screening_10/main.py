import pandas as pd
import json
import base64
import time
import pymongo
from datetime import datetime
from datetime import timedelta


def inside_bar_buy(candles, periods):

    time_start = time.time()
    ('Start calc_screening')

    ('got candles in: ' + str(time.time() - time_start))

    to_dat_time = time.time()

    dat = pd.DataFrame(candles)
    dat['datetime'] = dat['datetime'].sort_values(ascending=False)
    dat = dat[:periods]

    ('to dataframe in: ' + str(time.time() - to_dat_time))

    if len(dat) < 125:
        print('Error: insufficient data')
        return False

    try:
        dat = dat.sort_values(['datetime'], ignore_index=True)
    except Exception as e:
        return 'Error on datetime, probably empty stuff'
        raise

    close = float(list(dat['close'])[-1])
    low = float(list(dat['low'])[-1])
    high = float(list(dat['high'])[-1])

    print(close, dat.high.iloc[-1])
    print(dat.high.iloc[-2], dat.high.iloc[-3])

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

    if(close > ema8
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


def entrypoint(request):
    return_data = {}

    # req_post example:
    # {"ticker": "XPTO4", "timeframe": "candle_m05", "periods": 80}

    candles_post = request.get_json(silent=True)

    if request.args and 'message' in request.args:
        print('Ta Caindo no IF')
        print(request.args.get('message'))

        return 'ERROR'

    elif candles_post and 'message' in candles_post:

        candles_post = base64.b64decode(
            candles_post['message']['data']).decode('utf-8')

        candles_post = json.loads(candles_post)

    else:
        #         print('Ta Caindo no ELSE')
        print(candles_post)

    periods = 130

    try:
        result = calc_screening(candles_post['dat'], periods)
        if(result):

            new_line = {}
            new_line['ticker'] = result['ticker']
            new_line['datetime'] = str(result['datetime'])
            new_line['type'] = 'COMPRA'
            new_line['entry_value'] = str(result['entry_value'])
            new_line['stop_loss'] = str(result['stop_loss'])
            new_line['movement'] = ''
            new_line['screening_type'] = 10
            new_line['screening_name'] = 'INSIDE BAR COMPRA'
            new_line['disruption_value'] = result['disruption_value']
            new_line['direction'] = str(result['direction'])
            new_line['take_profit'] = str(result['take_profit'])
            new_line['chart_period'] = candles_post['timeframe']
            new_line['datetime'] = result['datetime']
            new_line['valid_until'] = next_candle(
                result['datetime'], candles_post['timeframe'])['next_open']
            new_line['insert_time'] = datetime.now()
            new_line['disrupted'] = 0
            new_line['disrupted_at'] = ''
            new_line['disruption'] = 1
            try:
                client = pymongo.MongoClient(
                   os.getenv(
            'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
                    readPreference='secondaryPreferred', appname='screening_crypto')

                candles_db = client.ms_screenings_crypto['screenings_alerts_crypto']

                print(new_line)
                candles_db.insert_one(new_line)

            except Exception as e:
                print(e)
                return 'ERROR in persist', 200

    except Exception as e:
        print(str(e))
        print(str(candles_post))
        # raise
        return 'ERROR in calculation', 200

    return return_data, 200
