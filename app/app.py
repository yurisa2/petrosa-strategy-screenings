from fastapi import APIRouter, Request, Response

from app.ta import screenings

router = APIRouter()


@router.get("/health")
async def health() -> Response:
    return Response(200)


@router.post("/inside_bar_buy/{timeframe}")
async def router_inside_bar_buy(request: Request, timeframe):
    content = await request.json()
        
    tempors = await screenings.inside_bar_buy(candles=content, 
                                              timeframe=timeframe)
    
    return tempors
