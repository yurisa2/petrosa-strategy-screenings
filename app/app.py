from fastapi import APIRouter, Response, Request
from app.ta import screenings


router = APIRouter()


@router.get("/health")
async def health(): 
    data = 'I live'
    
    return data


@router.post("/inside_bar_buy/{timeframe}")
async def router_inside_bar_buy(request: Request, timeframe):
    content = await request.json()
        
    tempors = await screenings.inside_bar_buy(candles=content, 
                                              timeframe=timeframe)
    
    return tempors
