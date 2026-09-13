import sys
import uvicorn
from aws_xray_sdk.core import xray_recorder
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, food, food_log, user, ai

app = FastAPI(title="Calorie Tracker API")

xray_recorder.configure(service='calorie-tracker-backend-service')

@app.middleware("http")
async def xray_middleware(request: Request, call_next):
    segment_name = f"{request.method} {request.url.path}"
    segment = xray_recorder.begin_segment(segment_name)
    try:
        response = await call_next(request)
        segment.put_http_meta("response", {"status": response.status_code})
        return response
    except Exception as e:
        segment.add_exception(e, sys.exc_info()[2])
        raise
    finally:
        xray_recorder.end_segment()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://localhost",
                   "http://16.192.69.83",
                   "calorie-tracker-load-balancer-1589280626.eu-north-1.elb.amazonaws.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(food.router)
app.include_router(food_log.router)
app.include_router(user.router)
app.include_router(ai.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)