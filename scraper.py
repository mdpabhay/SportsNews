# scraper.py
import logging, time
from typing import List, Dict, Optional
from urllib.parse import urljoin
from dateutil import parser as date_parser
from playwright.sync_api import Page

log = logging.getLogger("scraper")

def _parse_dt_maybe(text: Optional[str]):
    if not text:
        return None
    try:
        dt = date_parser.parse(text, fuzzy=True)
        return dt
    except Exception:
        return None

def _text_from_html(html: Optional[str]):
    if not html:
        return None
    import re
    return " ".join(re.sub(r"<[^>]+>", "", html).split())

def scrape_fixture_list(page: Page, base_url: str) -> List[Dict]:
    log.info("scraper: loading fixtures page: %s", base_url)
    page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(1.0)  # allow JS rendering
    # Try several approaches to find match links
    anchors = []
    try:
        anchors = page.query_selector_all("a[href*='/match/']")
    except Exception:
        try:
            anchors = page.query_selector_all("a")
        except Exception:
            anchors = []

    results = []
    seen = set()
    for a in anchors:
        try:
            href = a.get_attribute("href") or ""
            if "/match/" not in href:
                continue
            url = href if href.startswith("http") else urljoin(page.url, href)
            if url in seen:
                continue
            text = (a.inner_text() or "").strip()
            # try to find nearby time element
            start_text = None
            try:
                parent = a.evaluate_handle("el => el.closest('div, li, section, article')")
                if parent:
                    el = parent.as_element().query_selector("time, .time, .start-time, .date")
                    if el:
                        start_text = (el.inner_text() or "").strip()
            except Exception:
                start_text = None
            if not start_text:
                start_text = text
            dt = _parse_dt_maybe(start_text)
            match_id = a.get_attribute("data-match-id") or url.rstrip("/").split("/")[-1]
            item = {
                "match_id": match_id,
                "series_name": None,
                "match_description": text,
                "start_time": dt.isoformat() if dt else None,
                "status": "upcoming",
                "match_url": url
            }
            seen.add(url)
            results.append(item)
        except Exception:
            log.exception("Error parsing anchor")
    log.info("scraper: found %d matches", len(results))
    return results

def _click_tab_and_get_html(page: Page, names):
    for name in names:
        try:
            btn = page.query_selector(f"button:has-text('{name}')") or page.query_selector(f"text=\"{name}\"")
            if btn:
                try:
                    btn.click()
                    time.sleep(0.5)
                except Exception:
                    pass
                panel = page.query_selector("[role='tabpanel']") or page.query_selector(".tab-content") or page.query_selector(".content")
                if panel:
                    return panel.inner_html()
        except Exception:
            continue
    return None

def scrape_match_page(page: Page, match_url: str) -> Dict:
    log.info("scraper: loading match page %s", match_url)
    page.goto(match_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(0.8)

    match_info_html = _click_tab_and_get_html(page, ["Match info", "Info", "Match Details", "Match Info"])
    squads_html = _click_tab_and_get_html(page, ["Squads", "Playing XI", "Squad"])
    scorecard_html = _click_tab_and_get_html(page, ["Scorecard", "Score Card", "Score"])
    live_html = _click_tab_and_get_html(page, ["Live", "Live Score", "Live Commentary", "Live Feed"])

    match_info = {"raw": match_info_html, "text": _text_from_html(match_info_html)}
    squads = {"raw": squads_html, "text": _text_from_html(squads_html)}
    scorecard = {"raw": scorecard_html, "text": _text_from_html(scorecard_html)}
    live_data = {"raw": live_html, "text": _text_from_html(live_html)}

    # basic finished detection
    status_text = (match_info["text"] or "") + " " + (live_data["text"] or "")
    finished_keywords = ["won by", "match over", "match finished", "stumps", "completed", "result"]
    is_finished = any(kw.lower() in status_text.lower() for kw in finished_keywords)

    return {
        "match_info": match_info,
        "squads": squads,
        "scorecard": scorecard,
        "live_data": live_data,
        "is_finished": is_finished
    }

