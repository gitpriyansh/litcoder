from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from config import Config

URL = "https://leetcode.com/graphql"
QUERY = """
query recent($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title titleSlug timestamp
  }
}"""

def fetch_recent_accepted(username, limit=20):
    """Unofficial endpoint: returns only the latest ~20 accepted submissions
    and may break anytime. Manual logging is the fallback."""
    r = requests.post(
        URL,
        json={"query": QUERY, "variables": {"username": username, "limit": limit}},
        headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
        timeout=10,
    )
    r.raise_for_status()
    items = (r.json().get("data") or {}).get("recentAcSubmissionList") or []
    tz = ZoneInfo(Config.TIMEZONE)
    return [
        {"slug": i["titleSlug"], "title": i["title"],
         "date": datetime.fromtimestamp(int(i["timestamp"]), tz).date()}
        for i in items
    ]

DIFF_QUERY = """
query q($slug: String!) { question(titleSlug: $slug) { difficulty } }"""

def fetch_difficulty(slug):
    """Returns 'Easy' / 'Medium' / 'Hard'. Falls back to Medium if lookup fails."""
    try:
        r = requests.post(
            URL,
            json={"query": DIFF_QUERY, "variables": {"slug": slug}},
            headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
            timeout=10,
        )
        r.raise_for_status()
        d = ((r.json().get("data") or {}).get("question") or {}).get("difficulty")
        return d if d in Config.POINTS else "Medium"
    except Exception:
        return "Medium"
