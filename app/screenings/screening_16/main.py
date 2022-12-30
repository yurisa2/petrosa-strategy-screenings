import pandas as pd
import json
import base64
import time
import pymongo
from datetime import datetime
from datetime import timedelta


def next_candle(date, time_frame):

    print(date, time_frame)
    date = datetime.now()

    if(time_frame == 'candles_m1'):
        frame = 1
        time = 'm'
    elif(time_frame == 'candles_m5'):
        frame = 5
        time = 'm'
    elif(time_frame == 'candles_m15'):
        frame = 15
        time = 'm'
    elif(time_frame == 'candles_m30'):
        frame = 30
        time = 'm'
    elif(time_frame == 'candles_h1'):
        frame = 60
        time = 'm'
    elif(time_frame == 'candles_d1'):
        frame = 1
        time = 'd'
    elif(time_frame == 'candles_w1'):
        frame = 1
        time = 'w'

    if time == 'm':
        time_check = date + timedelta(minutes=frame)

    elif time == 'd':
        time_check = date + timedelta(days=frame + 1)

    elif time == 'w':
        time_check = date + timedelta(weeks=frame + 1)

    else:
        return 'Erro: Dados recebidos para calcular o póximo candle incorretos.'

    ret = {}
    ret['next_open'] = time_check

    return ret


def calc_screening(candles, periods):

    time_start = time.time()
    ('Start calc_screening')

    ('got candles in: ' + str(time.time() - time_start))

    to_dat_time = time.time()

    dat = pd.DataFrame(candles)
    dat['datetime'] = dat['datetime'].sort_values(ascending=False)
    dat = dat[:periods]

    ('to dataframe in: ' + str(time.time() - to_dat_time))

    if len(dat) < 60:
        print('Error: insufficient data')
        return False

    try:
        dat = dat.sort_values(['datetime'], ignore_index=True)
    except Exception as e:
        return 'Error on datetime, probably empty stuff'
        raise

    ema9 = dat["close"].ewm(span=9, min_periods=8, adjust=True).mean()
    dat['ema'] = ema9
    inc_ema9 = ema9.diff()

    buy_cond_1 = False in list(dat['low'][-7:-2].astype(float) > ema9[-7:-2])

    close_2 = float(dat['close'].iloc[-2])
    low = float(dat['low'].iloc[-1])
    low_2 = low = float(dat['low'].iloc[-2])
    high = float(dat['high'].iloc[-1])
    high_2 = float(dat['high'].iloc[-2])

    # print(inc_ema9)

    buy_cond_2 = (close_2 < ema9.iloc[-2]) and (low > low_2)
    buy_cond_3 = (inc_ema9.iloc[-2] < 0) and (inc_ema9.iloc[-1] > 0)

    # print(ema9[-4:], end='\n')
    # print(dat['low'][-4:])

    ret = {}
    ret['ticker'] = dat.ticker.iloc[-1]
    ret['datetime'] = dat.datetime.iloc[-1]

    if not buy_cond_1 and buy_cond_2 and buy_cond_3:
        ret['entry_value'] = high
        ret['disruption_value'] = high
        ret['stop_loss'] = low
        ret['take_profit'] = high + ((high - low) * 2)
        ret['type'] = 'COMPRA'
        ret['direction'] = 'SUPERIOR'
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

    periods = 60

    try:
        result = calc_screening(candles_post['dat'], periods)
        if(result):

            new_line = {}
            new_line['ticker'] = result['ticker']
            new_line['datetime'] = str(result['datetime'])
            new_line['type'] = str(result['type'])
            new_line['entry_value'] = str(result['entry_value'])
            new_line['stop_loss'] = str(result['stop_loss'])
            new_line['movement'] = ''
            new_line['screening_type'] = 16
            new_line['screening_name'] = 'SETUP 9.4 COMPRA'
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
