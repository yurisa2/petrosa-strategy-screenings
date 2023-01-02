import datetime

import pandas as pd


async def json_to_df(candles_list) -> pd.DataFrame:
    
    dat = pd.DataFrame(candles_list)
    dat['datetime'] = dat['datetime'].sort_values(ascending=False)

    dat = dat.sort_values(['datetime'], ignore_index=True)

    return dat

async def screening_output(
                           ticker,
                           timeframe,
                           pet_datetime, 
                           entry_value, 
                           disruption_value,
                           stop_loss,
                           take_profit,
                           direction
                           ):
    
    if(timeframe == 'm15'):
        minutes = 15
    elif(timeframe == 'm30'):
        minutes = 30
    elif(timeframe == 'h1'):
        minutes = 60
    else:
        raise
    
    
    valid_until = datetime.datetime.fromisoformat(pet_datetime) + datetime.timedelta(minutes=minutes)
    
    ret = {}
    ret['ticker'] = ticker
    ret['datetime'] = pet_datetime
    ret['entry_value'] = entry_value
    ret['disruption_value'] = disruption_value
    ret['stop_loss'] = stop_loss
    ret['take_profit'] = take_profit
    ret['direction'] = direction
    ret['timeframe'] = timeframe
    ret['valid_until'] = valid_until

    return ret