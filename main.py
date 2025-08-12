import asyncio
import sys
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uvicorn
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import logging
import re
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fix for Windows asyncio issue
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI()

# Mount static files (ensure 'static/index.html' exists)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Pydantic Models ---
class Player(BaseModel):
    name: str
    details: str

class BattingScore(BaseModel):
    player: str
    dismissal: str
    runs: str
    balls: str
    fours: str
    sixes: str
    strike_rate: str

class BowlingScore(BaseModel):
    player: str
    overs: str
    maidens: str
    runs: str
    wickets: str
    economy: str

class Innings(BaseModel):
    team: str
    score: str
    batting: List[BattingScore]
    bowling: List[BowlingScore]

class Scorecard(BaseModel):
    innings: Dict[str, Innings]

class Match(BaseModel):
    id: str
    title: str
    status: str
    teams: List[str]
    venue: str
    date: str
    format: str
    result: Optional[str] = None
    current_score: Optional[str] = None
    match_url: Optional[str] = None

class MatchDetails(BaseModel):
    squads: Optional[Dict[str, List[Player]]] = None
    scorecard: Optional[Scorecard] = None
    info: Optional[Dict[str, str]] = None

class CricketScraper:
    def __init__(self):
        self.base_url = "https://www.cricbuzz.com/cricket-match/live-scores"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }

    async def _get_page_content(self, url: str) -> str:
        logger.info(f"Attempting to scrape content from {url} using Playwright")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=self.headers['User-Agent'])
                page = await context.new_page()
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                # Wait for a generic container used on live-scores pages
                await page.wait_for_selector('div[class*="cb-mtch-lst"], div#page-wrapper', timeout=20000)
                html = await page.content()
                await browser.close()
                return html
        except Exception as e:
            logger.error(f"Playwright scraping failed for {url}: {str(e)}")
            logger.info(f"Falling back to httpx for {url}")
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text

    def _normalize_status(self, text: str) -> str:
        t = text.lower()
        # Based on Cricbuzz status DOM classes and texts for live/upcoming/completed[8][9][11]
        if any(k in t for k in ["live", "stumps", "innings break", "rain", "delayed"]):
            return "Live"
        if any(k in t for k in ["upcoming", "starts", "scheduled", "preview"]):
            return "Upcoming"
        if any(k in t for k in ["won by", "match tied", "no result", "complete", "result"]):
            return "Completed"
        return "Upcoming"

    def parse_matches(self, html: str) -> List[Match]:
        soup = BeautifulSoup(html, 'html.parser')
        matches: List[Match] = []

        # Cricbuzz live scores page groups matches into lists[8][9][11]
        match_containers = soup.select('div[class*="cb-mtch-lst"]')
        logger.info(f"Found {len(match_containers)} match containers")

        # Each container may have multiple match cards; handle both container-level and card-level
        cards = soup.select('div.cb-mtch-lst div.cb-mtch-lst-rt, div.cb-mtch-lst li, div.cb-mtch-lst div.cb-lv-main')
        if not cards:
            # Fallback: try a broader selector
            cards = soup.select('a[href*="/live-cricket-scorecard/"], a[href*="/live-cricket-scores/"]')

        # Another robust approach: each match block often contains header with link to match[8]
        blocks = soup.select('div.cb-mtch-lst div.cb-mtch-lst-rt, div.cb-lv-main, div.cb-series-matches')
        if not blocks:
            blocks = match_containers

        used = set()

        def extract_from_block(block):
            try:
                # Title link
                title_el = block.select_one('a[href*="/live-cricket-scores/"]')
                if not title_el:
                    title_el = block.select_one('a.cb-lv-scr-mtch-hdr')
                if not title_el:
                    title_el = block.find('a', href=re.compile(r'/live-cricket-scores/'))
                if not title_el:
                    return None

                match_url = "https://www.cricbuzz.com" + title_el['href']
                if match_url in used:
                    return None
                used.add(match_url)

                raw_title = title_el.get('title') or title_el.get_text(strip=True)
                raw_title = raw_title.strip() if raw_title else "Match"

                # Teams
                team_els = block.select('div.cb-hmscg-tm-nm, span.cb-hmscg-tm-nm')
                teams = [el.get_text(strip=True) for el in team_els if el.get_text(strip=True)]
                if len(teams) < 2:
                    # Try to infer from title "A vs B"
                    parts = re.split(r'\s+vs\s+|\s+v\s+', raw_title, flags=re.I)
                    if len(parts) >= 2:
                        teams = [parts[0].strip(), parts[1].split(',')[0].strip()]
                if len(teams) < 2:
                    teams = ["Team A", "Team B"]

                # Status text from known classes[8][9][11]
                status_el = block.select_one('div.cb-text-live, div.cb-text-complete, div.cb-text-upcoming, div.cb-lv-scrs-col')
                status_text = status_el.get_text(strip=True) if status_el else ""
                status = self._normalize_status(status_text or raw_title)

                # Venue (best effort from title "... at Venue, City")[8][9]
                venue_match = re.search(r'\bat\s([^|,]+)', raw_title, flags=re.I)
                venue = venue_match.group(1).strip() if venue_match else "Unknown Venue"

                # Date string (Cricbuzz shows short date near each card)[8][9][11]
                date_el = block.select_one('span.cb-mat-date, div.cb-col-33 span, div.cb-col-50 span')
                date_str = date_el.get_text(strip=True) if date_el else datetime.now().strftime("%Y-%m-%d")

                # Format
                fmt_match = re.search(r'(Test|ODI|T20I|T20|First Class|List A)', raw_title, re.I)
                match_format = fmt_match.group(1).upper() if fmt_match else "T20"

                # Current score if present
                score_els = block.select('div.cb-hmscg-tm-scr, div.cb-lv-scrs-col')
                current_score = " | ".join([s.get_text(strip=True) for s in score_els if s.get_text(strip=True)]) or None

                # Result if completed
                result = None
                if status == "Completed":
                    comp_el = block.select_one('div.cb-text-complete')
                    if comp_el:
                        result = comp_el.get_text(strip=True)

                match = Match(
                    id=str(uuid.uuid4()),
                    title=f"{teams[0]} vs {teams[1]}",
                    status=status,
                    teams=teams,
                    venue=venue,
                    date=date_str,
                    format=match_format,
                    result=result,
                    current_score=current_score,
                    match_url=match_url
                )
                return match
            except Exception as e:
                logger.error(f"Error extracting match from block: {e}")
                return None

        for block in soup.select('div.cb-mtch-lst div, li'):
            m = extract_from_block(block)
            if m:
                matches.append(m)

        # As a fallback, scan anchor links to matches if list is too small
        if len(matches) < 3:
            for a in soup.select('a[href*="/live-cricket-scores/"]'):
                try:
                    match_url = "https://www.cricbuzz.com" + a['href']
                    if match_url in used:
                        continue
                    raw_title = a.get('title') or a.get_text(strip=True)
                    if not raw_title:
                        continue
                    parts = re.split(r'\s+vs\s+|\s+v\s+', raw_title, flags=re.I)
                    teams = [p.strip() for p in parts[:2]] if len(parts) >= 2 else ["Team A", "Team B"]
                    status = "Upcoming"
                    match = Match(
                        id=str(uuid.uuid4()),
                        title=f"{teams[0]} vs {teams[1]}",
                        status=status,
                        teams=teams,
                        venue="Unknown Venue",
                        date=datetime.now().strftime("%Y-%m-%d"),
                        format="T20",
                        result=None,
                        current_score=None,
                        match_url=match_url
                    )
                    matches.append(match)
                    used.add(match_url)
                except Exception:
                    continue

        logger.info(f"Parsed {len(matches)} matches.")
        return matches

    async def scrape_match_details(self, match_url: str, status: str) -> MatchDetails:
        logger.info(f"Scraping details from {match_url} for a '{status}' match.")
        # Build scorecard URL based on Cricbuzz pattern[13]
        # e.g., https://www.cricbuzz.com/live-cricket-scorecard/<match-id>/<slug>
        if "/live-cricket-scorecard/" in match_url:
            scorecard_url = match_url
        else:
            scorecard_url = match_url.replace("/live-cricket-scores/", "/live-cricket-scorecard/")

        try:
            html = await self._get_page_content(scorecard_url)
            scorecard = self._parse_scorecard(html)
            return MatchDetails(scorecard=scorecard)
        except Exception as e:
            logger.error(f"Error scraping match details from {match_url}: {str(e)}")
            return MatchDetails()

    def _parse_scorecard(self, html: str) -> Scorecard:
        soup = BeautifulSoup(html, 'html.parser')
        innings_data: Dict[str, Innings] = {}

        # Innings sections typically have ids like "innings_1", "innings_2"[10]
        innings_divs = soup.select('div[id^="innings_"], div[id^="inning_"]')
        idx = 0
        for innings_div in innings_divs:
            # Header contains "Team Name Innings" and score at right[10]
            header = innings_div.select_one('div.cb-scrd-hdr-rw')
            if not header:
                # Try a broader selection inside the innings block
                header = innings_div.find('div', class_=re.compile(r'cb-scrd-hdr-rw'))
            if not header:
                continue

            team_name_el = header.find('span')
            team_name = team_name_el.get_text(strip=True) if team_name_el else "Innings"
            team_name = re.sub(r'\s*Innings.*', '', team_name).strip()

            score_el = header.select_one('span.pull-right')
            score = score_el.get_text(strip=True) if score_el else ""

            batting_scores: List[BattingScore] = []
            # Batting table rows[10]
            batting_rows = innings_div.select('div.cb-col.cb-col-100.cb-ltst-wgt-hdr > div.cb-col.cb-col-100.cb-scrd-itms')
            for row in batting_rows:
                cols = row.select('div.cb-col')
                # Batting rows usually have >=7 columns; filter extras and header rows
                if len(cols) < 7:
                    continue
                name = cols[0].get_text(strip=True)
                dismissal = cols[1].get_text(strip=True)
                runs = cols[2].get_text(strip=True)
                balls = cols[3].get_text(strip=True)
                fours = cols[4].get_text(strip=True)
                sixes = cols[5].get_text(strip=True)
                sr = cols[6].get_text(strip=True)
                # Skip summary/footer rows that often have non-player text
                if name.lower() in ["extras", "total", "did not bat", "fall of wickets"]:
                    continue
                batting_scores.append(BattingScore(
                    player=name, dismissal=dismissal, runs=runs, balls=balls, fours=fours, sixes=sixes, strike_rate=sr
                ))

            bowling_scores: List[BowlingScore] = []
            # Bowling table rows[10]
            bowling_rows = innings_div.select('div.cb-col.cb-col-100.cb-ltst-wgt-hdr.cb-bow-wgt > div.cb-col.cb-col-100.cb-scrd-itms')
            for row in bowling_rows:
                cols = row.select('div.cb-col')
                if len(cols) < 6:
                    continue
                name = cols[0].get_text(strip=True)
                overs = cols[1].get_text(strip=True)
                maidens = cols[2].get_text(strip=True)
                runs = cols[3].get_text(strip=True)
                wickets = cols[4].get_text(strip=True)
                econ = cols[5].get_text(strip=True)
                bowling_scores.append(BowlingScore(
                    player=name, overs=overs, maidens=maidens, runs=runs, wickets=wickets, economy=econ
                ))

            idx += 1
            innings_data[f"innings_{idx}"] = Innings(
                team=team_name, score=score, batting=batting_scores, bowling=bowling_scores
            )

        logger.info(f"Parsed scorecard with {len(innings_data)} innings.")
        return Scorecard(innings=innings_data)

scraper = CricketScraper()
matches_cache: List[Match] = []
cache_time: Optional[datetime] = None
match_url_map: Dict[str, str] = {}
match_status_map: Dict[str, str] = {}

async def get_cached_matches() -> List[Match]:
    global matches_cache, cache_time, match_url_map, match_status_map
    if (not matches_cache) or (cache_time is None) or ((datetime.now() - cache_time).total_seconds() > 300):
        logger.info("Cache empty or expired. Scraping new matches.")
        html = await scraper._get_page_content(scraper.base_url)
        matches_cache = scraper.parse_matches(html)
        cache_time = datetime.now()
        # Map ids to URLs and statuses for later detail fetches
        match_url_map = {m.id: m.match_url for m in matches_cache if m.match_url}
        match_status_map = {m.id: m.status for m in matches_cache}
    else:
        logger.info("Returning matches from cache.")
    return matches_cache

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error("index.html not found in static directory")
        return HTMLResponse(content="<h2>index.html not found. Please create this file in the 'static' directory.</h2>")
    except Exception as e:
        logger.error(f"Error serving homepage: {str(e)}")
        return HTMLResponse(content=f"<h2>Error: {str(e)}</h2>")

# -------- API Endpoints for Frontend --------

@app.get("/api/matches")
async def api_matches():
    matches = await get_cached_matches()
    # Return grouped by status for easier client rendering[8][9][11]
    grouped = {"Live": [], "Upcoming": [], "Completed": []}
    for m in matches:
        grouped.setdefault(m.status, [])
        grouped[m.status].append(m.dict())
    return JSONResponse(grouped)

@app.get("/api/match/{match_id}")
async def api_match_details(match_id: str):
    await get_cached_matches()  # ensure maps are fresh
    match_url = match_url_map.get(match_id)
    status = match_status_map.get(match_id, "Upcoming")
    if not match_url:
        raise HTTPException(status_code=404, detail="Match not found")
    details = await scraper.scrape_match_details(match_url, status)
    if not details.scorecard and not details.squads:
        raise HTTPException(status_code=500, detail="Unable to fetch match details")
    return JSONResponse(details.dict())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
