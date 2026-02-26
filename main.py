from fastapi import FastAPI
from datetime import datetime
import pytz

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello my first ai app!!"}

@app.get("/time")
def get_current_time():
    """Return the current time in JST (Japan Standard Time)"""
    jst = pytz.timezone('Asia/Tokyo')
    current_time = datetime.now(jst)
    return {
        "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "JST",
        "timestamp": current_time.timestamp()
    }

@app.get("/time/{timezone}")
def get_time_in_timezone(timezone: str):
    """Return the current time in the specified timezone"""
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": timezone,
            "timestamp": current_time.timestamp()
        }
    except pytz.exceptions.UnknownTimeZoneError:
        return {"error": f"Unknown timezone: {timezone}"}