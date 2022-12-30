from datetime import datetime
from datetime import timedelta
import pytz
import pymongo
import base64
import json
from google.cloud import pubsub_v1


TZ = 'UTC'

conn = None


def update_found(alert_ids, collection, time_now):

    try:

        client_update = pymongo.MongoClient(
           os.getenv(
            'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
            readPreference='secondaryPreferred', appname='screening_crypto')

        scr_alerts = client_update.ms_screenings_crypto['screenings_alerts_crypto']

        result = scr_alerts.update_many(
            {"_id": {"$in": alert_ids}}, {"$set":
                                          {"disrupted": 1,
                                           "disrupted_at": time_now}
                                          })
        print(result.raw_result)

        msg = bytes(json.dumps(alert_ids, default=str), "utf-8")

        publisher = pubsub_v1.PublisherClient()

        topic_path = publisher.topic_path(
                    'petrosa-screenings-crypto',
                    'publish_results')
        print('publish_results')
        print(msg)
        publisher.publish(topic_path, msg)

    except Exception as e:
        raise
    pass


def entrypoint(request):
    '''
    TRIGGED FROM CLOUD SCHEDULER
    '''

    json_args = request.get_json(silent=True)  # if Needed, probably not
    # print(json_args)

    time_now = datetime.now()  # - timedelta(hours=3)
    print('time_now: ' + str(time_now))

    # print(time_last_m1_candle)
    client = pymongo.MongoClient(
                   os.getenv(
            'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'))

    # candles_m1 = client.petrosa_crypto['candles_m1']
    # last_time= list(candles_m1.find().sort("datetime", -1).limit(1))[0]['datetime']
    # print(last_time)

    last_prices = client.petrosa_crypto['last_prices']

    ticker_list = last_prices.find({}, {'_id': 0, 'price': 1, 'ticker': 1})

    buffer_data = {}
    for ticker in ticker_list:
        buffer_data[ticker['ticker']] = {}
        buffer_data[ticker['ticker']]['ticker'] = ticker['ticker']
        buffer_data[ticker['ticker']]['price'] = ticker['price']

    scr_alerts = client.ms_screenings_crypto['screenings_alerts_crypto']
    pre_disruptions = scr_alerts.find({
                             "disrupted": 0,
                             "disruption": 1,
                             "valid_until": {"$gt": time_now}},
                            {"_id": 1,
                             "disruption_value": 1,
                             "direction": 1,
                             "ticker": 1}
                            )

    disrupted = []
    for line in pre_disruptions:

        ticker = line['ticker']
        dsr_value = line['disruption_value']
        dir_value = line['direction']
        # print(buffer_data.keys())

        if(ticker not in buffer_data):
            # print('Could not find the ticker')
            # print(ticker)
            continue

        # UP
        if(buffer_data[ticker]['ticker'] == ticker
                and dir_value == 'SUPERIOR'
                and dsr_value < float(buffer_data[ticker]['price'])):
            print(line)
            print('ROMPEU SUPERIOR')

            print(buffer_data[ticker])

            disrupted.append(line["_id"])

        # DOWN
        if(buffer_data[ticker]['ticker'] == ticker
                and dir_value == 'INFERIOR'
                and dsr_value > float(buffer_data[ticker]['price'])):
            print(line)
            print('ROMPEU INFERIOR')

            print(buffer_data[ticker])

            disrupted.append(line["_id"])

    try:
        if(len(disrupted) > 0):
            update_found(disrupted, scr_alerts, time_now)
    except Exception as e:
        print(e)
        return 'Error in mongo', 500

    return 'OK', 200
