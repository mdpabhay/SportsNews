# 🏏 Real-Time Cricket Tracker

The **Real-Time Cricket Tracker** is a complete web application that scrapes, stores, and displays live cricket data from [CREX](https://crex.live/fixtures/match-list).  
It is designed to automatically keep track of **upcoming fixtures**, **live matches**, and **match details** including scorecards, squads, and commentary — all from a single interface.

## ✨ Key Features
- **Live Match Tracking** – Automatically fetches and updates match scores, squads, and live commentary.
- **Upcoming Fixtures** – Lists all upcoming matches with schedule details.
- **Match Details Page** – Shows squads, scorecards, match info, and live updates.
- **REST API** – Fetch matches and details in JSON format.
- **Auto Scheduling** – Uses APScheduler to refresh match data periodically.
- **Persistent Storage** – Saves all scraped data in a local SQLite database.

---

## 📂 Project Structure


This project is ideal for:
- Developers learning **FastAPI** and **web scraping**.
- Cricket enthusiasts who want a **self-hosted live score tracker**.
- Students building **data scraping + web app** projects for academic or portfolio purposes.

---

## ✨ Key Features

### 📅 Upcoming Fixtures
- Automatically scrapes the upcoming match list from the given source URL.
- Stores match IDs, descriptions, start times, and links for quick access.
- Displays all fixtures in a clean, easy-to-read list.

### 📡 Live Match Tracking
- Scrapes match pages in real-time to fetch:
  - **Match Info** (venue, toss, umpires, etc.)
  - **Playing Squads** (team lists)
  - **Scorecards**
  - **Live commentary updates**
- Continues polling until the match is finished.

### 🗄 Persistent Storage
- Uses **SQLite** as a lightweight local database.
- Automatically updates existing match data without duplicating entries.

### 🖥 User Interface
- **Index Page:** Shows all matches with status and schedule.
- **Match Details Page:** Displays detailed match info, squads, live updates, and scorecards.
- Fully responsive with clean HTML templates (`index.html` and `match.html`).

### 🔌 API Endpoints
- `/api/matches` – Get all matches as JSON.
- `/api/matches/{match_id}` – Get full match details.
- `/api/matches/{match_id}/live` – Get live score and commentary.

---

## 📂 Project Structure


---

## 🛠 Technology Stack

- **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Scraping Engine:** [Playwright](https://playwright.dev/python/) (headless browser automation)
- **Database:** SQLite (lightweight and file-based)
- **Scheduling:** APScheduler (for periodic scraping jobs)
- **Templating:** Jinja2 (HTML rendering)
- **Frontend:** HTML, CSS, JavaScript

---

## ⚙️ Installation & Setup Guide

Follow these steps to set up the Real-Time Cricket Tracker on your local machine.

### 1️⃣ Clone the Repository
git clone https://github.com/yourusername/cricket-tracker.git
cd cricket-tracker

###2️⃣ Install Dependencies
Make sure Python 3.9+ is installed.
pip install -r requirements.txt

###3️⃣ Install Playwright Browsers
playwright install
This will install Chromium.
For all browsers (Chromium, Firefox, WebKit), use:
playwright install 

###4️⃣ Configure Environment
Create a .env :
env
TARGET_FIXTURES_URL=https://crex.live/fixtures/match-list
MONITOR_INTERVAL_MINUTES=2
POLL_INTERVAL_SECONDS=20
DATABASE_FILE=cricket_data.db

Explanation:
TARGET_FIXTURES_URL → Source page for fixtures
MONITOR_INTERVAL_MINUTES → How often to refresh fixtures
POLL_INTERVAL_SECONDS → How often to fetch live data
DATABASE_FILE → Path for SQLite database file

###5️⃣ Start the Background Scraper
bash
Copy
Edit
python worker.py
Keep this terminal open 

###6️⃣ Start the Web Server
Open a new terminal and run:
uvicorn main:app --reload

---

## 🎉 Final Words

The **Real-Time Cricket Tracker** is more than just a project — it’s a fusion of **technology and passion for cricket**.  
Whether you’re using it to **follow your favorite matches**, **learn cutting-edge web scraping**, or **showcase your coding skills**,  
this project offers a fun, real-world, and hands-on experience.  

⚡ Now it’s your turn — **clone it, run it, hack it, and make it your own!**  
Let’s bring cricket to the code and make every ball count! 🏏🔥

