import pymongo
import json
import base64
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import (
    LimitExceededBehavior,
    PublisherOptions,
    PublishFlowControl,
)
import bson
import datetime

flow_control_settings = PublishFlowControl(
    message_limit=100,  # 100 messages
    byte_limit=10 * 1024 * 1024,  # 10 MiB
    limit_exceeded_behavior=LimitExceededBehavior.BLOCK,)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    # print('obj', obj)
    # print(type(obj))
    if isinstance(obj, bson.objectid.ObjectId):
        return str(obj)

    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def entrypoint(request) -> tuple:
    '''
    Recebe request via pub/sub (push) e confere se ticker está habilitado.
    Caso esteja, envia para cada screening o payload do tipo:
    {
        "ticker":"ETHBTC",
        "timeframe": "candles_d01"
    }
    '''
    json_args = request.get_json(silent=True)

    if request.args and 'message' in request.args:
        print('Ta Caindo no IF')
        print(request.args.get('message'))

        return 'ERROR'

    elif json_args and 'message' in json_args:      # VIA PUB/SUB?
        json_args = base64.b64decode(
            json_args['message']['data']).decode('utf-8')

        json_args = json.loads(json_args)

    ### CONSTANTS ###
    print('JSON ARG: ', json_args)  # info!!!
    timeframe = json_args['timeframe']
    ticker = json_args['ticker']

    if timeframe in ["candles_m1", "candles_m5"]:
        print("Not desired timeframe!")
        return 'out a time!', 200

    ### MONGO CONN ###
    client = pymongo.MongoClient(
       os.getenv(
            'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
        readPreference='secondaryPreferred', appname='screening_crypto_actuator')

    scr_alerts = client.ms_screenings_crypto['ticker_config_crypto']

    ### RESULT BASED ON PAYLOAD ###
    this_ticker_config = list(scr_alerts.find(
        {"ticker": ticker, "time_frame": {"$regex": timeframe.split('_')[1]}},
        {'_id': 0, 'ticker': 1, "screenings": 1}))
    # print("THIS CONFIG: ", this_ticker_config)

    if len(this_ticker_config) == 0:    # HABILITADO NA TICKER CONFIG?
        print("ticker and timeframe not implemented!")
        return "ticker and timeframe not implemented!", 200

    publisher = pubsub_v1.PublisherClient(
        publisher_options=PublisherOptions(flow_control=flow_control_settings))

    candle_tf = client.petrosa_crypto[timeframe]

    results_candle_tf = candle_tf.find(
                        {'ticker': ticker, "closed_candle": True},
                             ).sort([
                                    ("datetime",
                                     pymongo.DESCENDING)]
                                    ).limit(250)

    ### PAYLOAD PARA SCREENING ###
    req = {'ticker': ticker,
           'timeframe': timeframe,
           'dat': list(results_candle_tf)
           }

    print('req', json.dumps(req, default=json_serial))
    msg = bytes(json.dumps(req, default=json_serial), "utf-8")

    # print("SCREENINGS: ", json.loads(this_ticker_config[0]['screenings']))
    permutations = 0
    for screening_type in json.loads(this_ticker_config[0]['screenings']):

        topic_path = publisher.topic_path(
            'petrosa-screenings-crypto', 'screening_'
            + str(screening_type).zfill(2))

        publisher.publish(topic_path, msg)  # PUBLISH MAN
        permutations += 1

    if permutations:
        print('Permutations: ' + str(permutations))
        return "Permutations: " + str(permutations), 200
    else:
        return 'NO DATA', 200
