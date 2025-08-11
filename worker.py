# worker.py
import os, time, logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright
import database
from scraper import scrape_fixture_list, scrape_match_page
from dotenv import load_dotenv

load_dotenv()
TARGET_FIXTURES_URL = os.getenv("TARGET_FIXTURES_URL", "https://crex.live/fixtures/match-list")
MONITOR_INTERVAL_MINUTES = int(os.getenv("MONITOR_INTERVAL_MINUTES", "2"))
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "20"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("worker")

scheduler = BackgroundScheduler()

def schedule_live_poll(match_id: str, match_url: str, browser, poll_seconds: int = POLL_INTERVAL_SECONDS):
    job_id = f"live_poll_{match_id}"
    if scheduler.get_job(job_id):
        return
    def poll_job():
        log.info("Polling live for %s", match_id)
        page = browser.new_page()
        try:
            details = scrape_match_page(page, match_url)
            payload = {
                "match_id": match_id,
                "status": "Live" if not details.get("is_finished") else "Finished",
                "match_url": match_url,
                "match_info": details.get("match_info"),
                "squads": details.get("squads"),
                "scorecard": details.get("scorecard"),
                "live_data": details.get("live_data"),
                "raw_html": {"details_snapshot": details}
            }
            database.upsert_match(payload)
            if details.get("is_finished"):
                try:
                    scheduler.remove_job(job_id)
                except Exception:
                    pass
        except Exception:
            log.exception("Error polling live")
        finally:
            try:
                page.close()
            except Exception:
                pass
    scheduler.add_job(poll_job, 'interval', seconds=poll_seconds, id=job_id, misfire_grace_time=30)
    log.info("Scheduled live poll for %s every %ds", match_id, poll_seconds)

def schedule_match_start(match):
    match_id = match["match_id"]
    job_id = f"start_{match_id}"
    if scheduler.get_job(job_id):
        return
    run_date = None
    if match.get("start_time"):
        try:
            run_date = datetime.fromisoformat(match["start_time"])
        except Exception:
            run_date = datetime.utcnow() + timedelta(seconds=10)
    else:
        run_date = datetime.utcnow() + timedelta(seconds=10)

    def start_job():
        log.info("Start job running for %s", match_id)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                try:
                    details = scrape_match_page(page, match["match_url"])
                    payload = {
                        "match_id": match_id,
                        "status": "Live" if not details.get("is_finished") else "Finished",
                        "match_url": match["match_url"],
                        "match_info": details.get("match_info"),
                        "squads": details.get("squads"),
                        "scorecard": details.get("scorecard"),
                        "live_data": details.get("live_data"),
                        "raw_html": {"details_snapshot": details}
                    }
                    database.upsert_match(payload)
                finally:
                    try:
                        page.close()
                    except Exception:
                        pass
            finally:
                try:
                    browser.close()
                except Exception:
                    pass
    scheduler.add_job(start_job, 'date', run_date=run_date, id=job_id, misfire_grace_time=30)
    log.info("Scheduled start job for %s at %s", match_id, run_date.isoformat())

def monitor_fixtures(browser):
    log.info("monitor: visiting fixtures")
    page = browser.new_page()
    try:
        matches = scrape_fixture_list(page, TARGET_FIXTURES_URL)
        log.info("monitor: found %d matches", len(matches))
        for m in matches:
            database.upsert_match(m)
            schedule_match_start(m)
    except Exception:
        log.exception("Error during monitor")
    finally:
        try:
            page.close()
        except Exception:
            pass

def main_loop():
    database.init_db()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            monitor_fixtures(browser)
            scheduler.add_job(lambda: monitor_fixtures(browser), 'interval', minutes=MONITOR_INTERVAL_MINUTES, id="monitor", replace_existing=True)
            scheduler.start()

            # ensure live polls for matches marked Live
            def ensure_live_polls():
                matches = database.get_all_matches()
                for mm in matches:
                    if mm.get("status") == "Live":
                        m_id = mm.get("match_id")
                        job_id = f"live_poll_{m_id}"
                        if not scheduler.get_job(job_id):
                            schedule_live_poll(m_id, mm.get("match_url"), browser, POLL_INTERVAL_SECONDS)
            scheduler.add_job(ensure_live_polls, 'interval', seconds=30, id="ensure_live_polls", replace_existing=True)

            log.info("Worker started. CTRL+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Worker shutting down...")
        finally:
            try:
                scheduler.shutdown(wait=False)
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass

if __name__ == "__main__":
    main_loop()
