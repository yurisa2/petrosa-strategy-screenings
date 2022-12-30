from fastapi import APIRouter, Response, Request
from app.ta import inside_bar_buy


router = APIRouter()


@router.get("/health")
async def health() -> Response: 
    data = 'I live'
    
    return data


@router.post("/inside_bar_buy")
async def router_inside_bar_buy(request: Request):
    content = await request.json()
    
    tempors = await inside_bar_buy.inside_bar_buy(candles=content)
    
    return tempors
