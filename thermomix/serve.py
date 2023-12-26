import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from thermomix.config import DEVICES
from thermomix.measure import MeasureException, get_measures

app = FastAPI()
logger = logging.getLogger(__name__)

app.mount("/static", StaticFiles(directory="thermomix/static"), name="static")
templates = Jinja2Templates(directory="thermomix/templates")


@app.get("/status")
async def status(request: Request):
    try:
        return get_measures(DEVICES)
    except MeasureException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "devices": DEVICES,
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=8000)  # nosec: B104 - only for development purposes
