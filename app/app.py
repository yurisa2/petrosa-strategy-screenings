from fastapi import APIRouter, Request, Response

from app.ta import screenings

router = APIRouter()


@router.get("/healthz")
async def health() -> Response:
    return Response(200)


@router.post("/{strategy}/{timeframe}")
async def router_inside_bar_buy(request: Request, strategy, timeframe):
    content = await request.json()
    func = getattr(screenings, strategy)
    result = await func(candles=content, timeframe=timeframe)
    
    return result
