import pandas as pd

async def json_to_df(candles_list) -> pd.DataFrame:
    
    dat = pd.DataFrame(candles_list)
    dat['datetime'] = dat['datetime'].sort_values(ascending=False)

    if len(dat) < 125:
        print('Error: insufficient data')
        raise

    dat = dat.sort_values(['datetime'], ignore_index=True)

    return dat

async def screening_output(
                           ticker, 
                           datetime, 
                           entry_value, 
                           disruption_value,
                           stop_loss,
                           take_profit,
                           direction
                           ):
    
    ret = {}
    ret['ticker'] = ticker
    ret['datetime'] = datetime
    ret['entry_value'] = entry_value
    ret['disruption_value'] = disruption_value
    ret['stop_loss'] = stop_loss
    ret['take_profit'] = take_profit
    ret['direction'] = direction

    return ret