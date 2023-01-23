from pymongo import MongoClient
import json
import bson
import datetime
import requests

client = MongoClient('mongodb://root:QnjfRW7nl6@localhost:27017/')

candles = client.petrosa_crypto['candles_m15'].find(
    {"ticker": "ATOMUSDT"}).sort("datetime", -1).limit(2000)

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


for item in range(200, len(candles)):
    candles_json = json.dumps(candles[item-199:item], default=json_serial)
    result = requests.post(
        'http://localhost:8090/fox_trap_sell/m15', json=candles_json)
    
   
    if (result.json() == {}):
        continue
    else:
        print(item, result.json())
        # break
