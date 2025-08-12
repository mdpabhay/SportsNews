# 🏏 Real-Time Cricket Tracker

The **Real-Time Cricket Tracker** is a complete web application that scrapes, stores, and displays live cricket data from [CREX](https://crex.live/fixtures/match-list).  
It is designed to automatically keep track of **upcoming fixtures**, **live matches**, and **match details** including scorecards, squads, and commentary — all from a single interface.
A FastAPI-based web app that scrapes Cricbuzz to display matches grouped by status (Live, Upcoming, Completed) with one-click scorecards in a clean, responsive UI.[1][2][3]

### Table of Contents
- About the Project
- Definitions
- UI
- Features
- Benefits
- Tech Stack and Tools
- Architecture
- How to Use
- API Reference
- Project Structure
- Best Practices and Notes
- Roadmap
- License and Acknowledgments
- Greetings

### About the Project
Cricket Scraper provides a single-page interface that fetches match listings and scorecards, normalizes statuses, and serves fast JSON endpoints for the frontend to render tabs and a slide-in scorecard drawer.[2][3][1]

### Definitions
- Live: Matches in progress, delayed, or at a break (e.g., “Live,” “Stumps,” “Innings Break”).[4][3][2]
- Upcoming: Scheduled or preview states prior to start.[3][2]
- Completed: Finished games with a result (e.g., “won by,” “tied,” “no result”).[2][4][3]


### ! Cricket Scraper UI

<p align="center">
  <img src="https://github.com/mdpabhay/Crex_Scraper/blob/main/static/Screenshot%202025-08-12%20233745.png?raw=true?raw=true" alt="App screenshot" width="1000">
</p>

#### ✨ Key Features

## 📅 Upcoming Fixtures
- Automatically scrapes the upcoming match list from the given source URL.
- Stores match IDs, descriptions, start times, and links for quick access.
- Displays all fixtures in a clean, easy-to-read list.

## 📡 Live Match Tracking
- Scrapes match pages in real-time to fetch:
  - **Match Info** (venue, toss, umpires, etc.)
  - **Playing Squads** (team lists)
  - **Scorecards**
  - **Live commentary updates**
- Continues polling until the match is finished.

## 🗄 Persistent Storage
- Uses **SQLite** as a lightweight local database.
- Automatically updates existing match data without duplicating entries.

## 🖥 User Interface
- **Index Page:** Shows all matches with status and schedule.
- **Match Details Page:** Displays detailed match info, squads, live updates, and scorecards.
- Fully responsive with clean HTML templates (`index.html` and `match.html`).

### Benefits
- Reliable Data Extraction: Browser automation handles dynamic content; HTTP fetch accelerates static HTML flows.[4][3]
- Fast Responses: Async I/O and caching keep the UI responsive and polite to the source site.[6][3]
- Easy Deployment: Minimal dependencies on the client and a modern, typed API on the server.[3][6]
- Extendable: Architecture cleanly supports features like player profiles, commentary, rankings, and PWA later.[6][3]


### 🛠 Technology Stack
- **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Scraping Engine:** [Playwright, Beautifulsoup](https://playwright.dev/python/)
- **Scheduling:** APScheduler (for periodic scraping jobs)
- **Templating:** Jinja2 (HTML rendering)
- **Frontend:** HTML, CSS, JavaScript
  
### Tech Stack and Tools
- Backend: FastAPI, Uvicorn, Pydantic for fast async APIs and typed models.[3][6]
- Scraping: Playwright for JS-rendered pages; httpx for HTTP; BeautifulSoup4 for robust parsing.[4][3]
- Frontend: Vanilla HTML/CSS/JS with tabs, cards, and a drawer; documented in GFM for GitHub rendering.[5][1][2]
- Concurrency/Caching: asyncio with a simple TTL in-memory cache for speed and courtesy.[6][3]
- Logging: Structured logs for scraper path, timing, and errors to aid maintenance.[3][6]

### Architecture
- Frontend calls /api/matches to get grouped results and renders Live/Upcoming/Completed grids; clicking a card calls /api/match/{id} to populate the scorecard drawer.[2][3]
- Backend scrapes Cricbuzz with Playwright or httpx, parses via BeautifulSoup, normalizes statuses, and caches results before returning JSON.[4][3]

```text
+-----------------------+       AJAX JSON        +---------------------------+
|   Frontend (static)   |  /api/matches, /match  |         FastAPI API       |
|  Tabs, Cards, Drawer  +----------------------->|  Cache + Scraper Orches.  |
|  Vanilla HTML/CSS/JS  |<-----------------------+  Pydantic Models          |
+-----------+-----------+                        +-------------+-------------+
            |                                                   |
            |                                                   v
            |                                    +---------------------------+
            |                                    |      Scraper Layer        |
            |                                    | Playwright (dynamic)      |
            |                                    | httpx (static)            |
            |                                    | BeautifulSoup (parsing)   |
            |                                    +---------------------------+
            v
       User’s Browser
```

References for formatting and documentation approach leverage GitHub Flavored Markdown to ensure tables, code blocks, and lists render consistently.[1][2]

## How to Use

Prerequisites
- Python 3.10+ and pip installed.
- Playwright browsers installed (Chromium).

Install
- pip install -r requirements.txt.
- playwright install chromium.

Run
- uvicorn main:app --reload and open http://127.0.0.1:8000.

Flow
- Press “Refresh Matches” to load Live/Upcoming/Completed tabs, click a match card to open the scorecard drawer, and switch tabs as needed.[2][3]

### API Reference
- GET /api/matches: Returns JSON grouped as { Live:[], Upcoming:[], Completed:[] } for display in tabs.[2][3]
- GET /api/match/{id}: Returns scorecard JSON (innings with batting and bowling tables) for the clicked match.[2][3]

These endpoints follow common REST patterns and are documented in the README using GFM for clarity and navigability.[1][2]

## Project Structure
- main.py: FastAPI app, routes, scraping orchestration, caching.[3][6]
- static/index.html: UI with tabs, cards, and scorecard drawer, using clean HTML/CSS/JS.[2][3]
- requirements.txt: Python dependencies for server and scraper setup.[6][3]

## Best Practices and Notes
- Writing: Use GitHub Flavored Markdown features (tables, fenced code, task lists) to present instructions accessibly and concisely.[5][1][2]
- Documentation: Keep README updated and skimmable; include sections for setup, usage, and API to help users get started quickly.[7][3]
- Scraping: Respect site terms, add reasonable delays and cache TTLs to reduce load; adjust selectors as source DOM evolves.[4][3]
- Accessibility: Use headings hierarchy, clear tables, and descriptive text to improve readability across devices.[8][2]

## Roadmap
- Player profiles and team rankings with supplementary endpoints and UI sections.[3][6]
- Live commentary stream and match info panels, gated behind incremental scraping refresh logic.[6][4]
- Optional Redis cache, rate limiting/backoff, and Docker deployment for scale.[3][6]

# ⚙️ Installation & Setup Guide (Cricket Scraper)

Follow these steps to set up the Cricket Scraper (FastAPI + Playwright/httpx + BeautifulSoup) on a local machine.

## 1️⃣ Clone the Repository

bash

git clone https://github.com/yourusername/cricket-scraper.git

cd cricket-scraper


## 2️⃣ Create and Activate a Virtual Environment.

bash

Windows (PowerShell)

python -m venv .venv

. .venv/Scripts/Activate.ps1

macOS/Linux

python3 -m venv .venv

source .venv/bin/activate


## 3️⃣ Install Dependencies

bash

pip install -r requirements.txt

If you don’t have a requirements.txt yet, a minimal set is:


bash

pip install fastapi uvicorn[standard] httpx==0.27.0 beautifulsoup4==4.12.3 playwright==1.* pydantic==1.* lxml


## 4️⃣ Install Playwright Browsers

bash

playwright install chromium

Notes:

Chromium is sufficient for this project, as it’s used to render JS-heavy pages when needed.

If desired, to install all browsers:

bash
playwright install


## 5️⃣ Project Files Layout

Ensure this structure (key files):

text
cricket-scraper/
├── main.py               # FastAPI app (scraper orchestration, APIs, cache)
├── static/
│   └── index.html        # Frontend UI (tabs, cards, scorecard drawer)
├── requirements.txt
└── README.md


## 6️⃣ Run the Web Server

bash

uvicorn main:app --reload

Then open:

text

http://127.0.0.1:8000


## 7️⃣ Usage Flow (Quick Test)

Click “Refresh Matches” to fetch the latest data.

Browse Live / Upcoming / Completed tabs.

Click any match card to open the scorecard drawer.

🔧 Optional Configuration Tips

If scraping is rate-limited or unstable, consider:

Increasing cache TTL in code (default ~5 minutes).

Adding small delays/backoff in requests.

Running Playwright only when JS rendering is required (already handled by fallback logic).

## ✅ Troubleshooting
Playwright not found:

Re-run: playwright install chromium

SSL or network issues:

Check firewall/VPN; retry with a stable connection.

Import errors:

Verify you’re inside the virtual environment and dependencies are installed.


## License and Acknowledgments
- Choose a license (e.g., MIT/Apache 2.0) to clarify project usage and contributions; state clearly in the repository root.
  
- Acknowledge contributors and external tools that enabled scraping, parsing, and documentation quality.


## Greetings
Thanks for checking out Cricket Scraper — built for speed, reliability, and clarity, and designed to make following cricket both delightful and developer-friendly.

