from pymongo import MongoClient
import json
import bson
import datetime

client = MongoClient('mongodb://root:QnjfRW7nl6@localhost:27017/')

candles = client.petrosa_crypto['candles_h1'].find({"ticker": "BTCUSDT"}).limit(200)

candles = list(candles)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    # print('obj', obj)
    # print(type(obj))
    if isinstance(obj, bson.objectid.ObjectId):
        return str(obj)

    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


candles = json.dumps(candles, default=json_serial)

print(candles)
