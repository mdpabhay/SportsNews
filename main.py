# main.py
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import database

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("web")

app = FastAPI(title="Cricket Tracker")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup():
    database.init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    matches = database.get_all_matches()
    return templates.TemplateResponse("index.html", {"request": request, "matches": matches})

@app.get("/match/{match_id}", response_class=HTMLResponse)
def match_page(request: Request, match_id: str):
    match = database.get_match_details(match_id)
    if not match:
        return HTMLResponse(content=f"<h1>Match {match_id} not found</h1>", status_code=404)
    return templates.TemplateResponse("match.html", {"request": request, "match": match})

@app.get("/api/matches")
def api_matches():
    return JSONResponse(database.get_all_matches())

@app.get("/api/matches/{match_id}")
def api_match(match_id: str):
    m = database.get_match_details(match_id)
    if not m:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse(m)

@app.get("/api/matches/{match_id}/live")
def api_live(match_id: str):
    m = database.get_match_details(match_id)
    if not m:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse({"live_data": m.get("live_data"), "scorecard": m.get("scorecard"), "status": m.get("status")})
