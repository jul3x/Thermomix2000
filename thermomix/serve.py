import logging
import subprocess  # nosec: B404

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

WATCHDOG_SERVICE = "ac_watchdog.service"
WATCHDOG_LOG_LINES = 1000


def get_service_logs(service, lines):
    try:
        result = subprocess.run(  # nosec: B603, B607
            ["journalctl", "-u", service, "-n", str(lines),
             "--no-pager", "-o", "short-iso"],
            capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as e:
        logger.error("Failed to read logs of %s: %s", service, e)
        return f"Error: {e}"
    return result.stdout or result.stderr


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
        "watchdog_service": WATCHDOG_SERVICE,
        "watchdog_logs": get_service_logs(WATCHDOG_SERVICE,
                                          WATCHDOG_LOG_LINES),
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=8000)  # nosec: B104 - only for development purposes
