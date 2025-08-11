# 🏏 Real-Time Cricket Tracker

![Index Page Preview](assets/index_preview.png)

A **Real-Time Cricket Data Tracker** built with **FastAPI**, **Playwright**, and **SQLite**.  
It scrapes live cricket fixtures and match details from [CREX](https://crex.live/fixtures/match-list), stores them in a database, and displays them in a web interface.

---

## 🚀 Features
- **Live Match Tracking** – Automatically fetches and updates match scores, squads, and live commentary.
- **Upcoming Fixtures** – Lists all upcoming matches with schedule details.
- **Match Details Page** – Shows squads, scorecards, match info, and live updates.
- **REST API** – Fetch matches and details in JSON format.
- **Auto Scheduling** – Uses APScheduler to refresh match data periodically.

---

## 📂 Project Structure
.
├── main.py # FastAPI app for frontend & API
├── worker.py # Background scraper & scheduler
├── scraper.py # Web scraping logic (Playwright)
├── database.py # SQLite database management
├── templates/ # HTML templates (index.html, match.html)
├── static/ # CSS, JS, and static files
├── cricket_data.db # SQLite database (auto-created)
├── requirements.txt # Python dependencies
├── .env # Environment variables
└── README.md # Project documentation

yaml
Copy
Edit

---

## 🛠 Tech Stack
- **Backend:** FastAPI
- **Scraping:** Playwright (headless browser)
- **Database:** SQLite
- **Scheduling:** APScheduler
- **Templating:** Jinja2
- **Frontend:** HTML, CSS, JS

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/cricket-tracker.git
cd cricket-tracker
2️⃣ Install Dependencies
Make sure you have Python 3.9+ installed.

bash
Copy
Edit
pip install -r requirements.txt
Also install Playwright browsers:

bash
Copy
Edit
playwright install
3️⃣ Configure Environment
Create a .env file (already included in this repo) with:

env
Copy
Edit
TARGET_FIXTURES_URL=https://crex.live/fixtures/match-list
MONITOR_INTERVAL_MINUTES=2
POLL_INTERVAL_SECONDS=20
DATABASE_FILE=cricket_data.db
4️⃣ Run the Scraper Worker
This script continuously monitors and updates match data.

bash
Copy
Edit
python worker.py
5️⃣ Run the Web App
In a separate terminal:

bash
Copy
Edit
uvicorn main:app --reload
The app will be available at:
🔗 http://127.0.0.1:8000/

🌐 API Endpoints
Method	Endpoint	Description
GET	/api/matches	List all matches
GET	/api/matches/{match_id}	Get details for a specific match
GET	/api/matches/{match_id}/live	Get live score & updates

📸 Screenshots
Index Page

Match Details Page

📜 License
This project is licensed under the MIT License – feel free to modify and use.

🤝 Contributing
Pull requests are welcome! For major changes, open an issue first to discuss your ideas.

🙌 Acknowledgements
Data source: CREX

Built with ❤️ using FastAPI and Playwright

yaml
Copy
Edit

---

If you don’t yet have the screenshots, you can open `index.html` and `match.html` in your browser, take a screenshot, save them as `index_preview.png` and `match_preview.png` inside an `assets/` folder in your repo, and the README will display them.  

Do you want me to also **embed actual HTML previews instead of static images** so that the README looks interactive? That would make it even more appealing on GitHub.








Ask ChatGPT
