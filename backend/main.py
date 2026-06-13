from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import feedparser
import requests
import os
import json
import uuid

try:
    import trafilatura
except ImportError:
    trafilatura = None

app = FastAPI(title="Threat Hunting Hypothesis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

DATA_DIR = "/app/data"
STORE_FILE = os.path.join(DATA_DIR, "app_store.json")

DEFAULT_RSS_FEEDS = [
    {
        "id": "default-cisa-advisories",
        "name": "CISA Cybersecurity Advisories",
        "url": "https://www.cisa.gov/news-events/cybersecurity-advisories.xml",
        "category": "Government Advisory",
        "enabled": True,
    },
    {
        "id": "default-bleepingcomputer",
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "category": "Security News",
        "enabled": True,
    },
    {
        "id": "default-rapid7",
        "name": "Rapid7 Blog",
        "url": "https://blog.rapid7.com/rss/",
        "category": "Threat Research",
        "enabled": True,
    },
]

DEFAULT_CUSTOM_TECHNOLOGIES = []


def ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(STORE_FILE):
        save_store(
            {
                "rss_feeds": DEFAULT_RSS_FEEDS,
                "custom_technologies": DEFAULT_CUSTOM_TECHNOLOGIES,
            }
        )


def load_store():
    ensure_store()

    with open(STORE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_store(data):
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(STORE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


class RSSFeed(BaseModel):
    id: Optional[str] = None
    name: str
    url: str
    category: Optional[str] = "Custom"
    enabled: Optional[bool] = True


class RSSFeedCreate(BaseModel):
    name: str
    url: str
    category: Optional[str] = "Custom"
    enabled: Optional[bool] = True


class TechnologyCreate(BaseModel):
    name: str
    group: Optional[str] = "Custom"


class HypothesisRequest(BaseModel):
    sector: Optional[str] = ""
    geo_location: Optional[str] = ""
    technology_stack: Optional[List[str]] = []
    threat_date: Optional[str] = "any"
    date_from: Optional[str] = ""
    date_to: Optional[str] = ""


class ArticleHypothesisRequest(BaseModel):
    url: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/settings")
def get_settings():
    store = load_store()

    return {
        "rss_feeds": store.get("rss_feeds", []),
        "custom_technologies": store.get("custom_technologies", []),
    }


@app.post("/api/rss/feeds")
def add_rss_feed(feed: RSSFeedCreate):
    store = load_store()

    new_feed = {
        "id": str(uuid.uuid4()),
        "name": feed.name.strip(),
        "url": feed.url.strip(),
        "category": feed.category.strip() if feed.category else "Custom",
        "enabled": feed.enabled,
    }

    store["rss_feeds"].append(new_feed)
    save_store(store)

    return {
        "status": "success",
        "feed": new_feed,
        "rss_feeds": store["rss_feeds"],
    }


@app.put("/api/rss/feeds/{feed_id}/toggle")
def toggle_rss_feed(feed_id: str):
    store = load_store()

    for feed in store["rss_feeds"]:
        if feed["id"] == feed_id:
            feed["enabled"] = not feed.get("enabled", True)
            save_store(store)

            return {
                "status": "success",
                "feed": feed,
                "rss_feeds": store["rss_feeds"],
            }

    return {"status": "failed", "message": "RSS feed not found"}


@app.delete("/api/rss/feeds/{feed_id}")
def delete_rss_feed(feed_id: str):
    store = load_store()

    before_count = len(store["rss_feeds"])
    store["rss_feeds"] = [
        feed for feed in store["rss_feeds"] if feed["id"] != feed_id
    ]

    if len(store["rss_feeds"]) == before_count:
        return {"status": "failed", "message": "RSS feed not found"}

    save_store(store)

    return {
        "status": "success",
        "rss_feeds": store["rss_feeds"],
    }


@app.post("/api/rss/test")
def test_rss(feed: RSSFeed):
    headers = {
        "User-Agent": "Mozilla/5.0 ThreatHuntingRSSBot/1.0"
    }

    try:
        response = requests.get(feed.url, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as error:
        return {
            "status": "failed",
            "message": f"Unable to fetch RSS feed: {str(error)}",
        }

    parsed = feedparser.parse(response.content)

    if parsed.bozo or len(parsed.entries) == 0:
        return {
            "status": "failed",
            "message": "URL is reachable, but it does not appear to be a valid RSS/Atom feed.",
        }

    entries = []

    for item in parsed.entries[:5]:
        entries.append(
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "published": item.get("published", item.get("updated", "")),
            }
        )

    return {
        "status": "success",
        "feed_title": parsed.feed.get("title", feed.name),
        "total_sample_items": len(entries),
        "sample_items": entries,
    }


@app.post("/api/technologies")
def add_custom_technology(technology: TechnologyCreate):
    store = load_store()

    name = technology.name.strip()
    group = technology.group.strip() if technology.group else "Custom"

    if not name:
        return {"status": "failed", "message": "Technology name is required"}

    existing = [
        tech for tech in store["custom_technologies"]
        if tech["name"].lower() == name.lower()
    ]

    if existing:
        return {
            "status": "failed",
            "message": "Technology already exists",
        }

    new_technology = {
        "id": str(uuid.uuid4()),
        "name": name,
        "group": group,
    }

    store["custom_technologies"].append(new_technology)
    save_store(store)

    return {
        "status": "success",
        "technology": new_technology,
        "custom_technologies": store["custom_technologies"],
    }


@app.delete("/api/technologies/{technology_id}")
def delete_custom_technology(technology_id: str):
    store = load_store()

    before_count = len(store["custom_technologies"])
    store["custom_technologies"] = [
        tech for tech in store["custom_technologies"]
        if tech["id"] != technology_id
    ]

    if len(store["custom_technologies"]) == before_count:
        return {"status": "failed", "message": "Technology not found"}

    save_store(store)

    return {
        "status": "success",
        "custom_technologies": store["custom_technologies"],
    }


def parse_article_date(item):
    published = item.get("published") or item.get("updated")

    if not published:
        return None

    try:
        return parsedate_to_datetime(published).date()
    except Exception:
        return None


def article_matches_date(item, threat_date: str, date_from: str = "", date_to: str = ""):
    if threat_date == "any":
        return True

    article_date = parse_article_date(item)

    if not article_date:
        return False

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    if threat_date == "today":
        return article_date == today

    if threat_date == "yesterday":
        return article_date == yesterday

    if threat_date == "custom":
        try:
            start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            end_date = datetime.strptime(date_to, "%Y-%m-%d").date()
            return start_date <= article_date <= end_date
        except Exception:
            return False

    return True


def collect_rss_articles(feeds: List[dict], threat_date: str, date_from: str = "", date_to: str = ""):
    articles = []

    headers = {
        "User-Agent": "Mozilla/5.0 ThreatHuntingRSSBot/1.0"
    }

    for feed in feeds:
        if not feed.get("enabled", True):
            continue

        try:
            response = requests.get(feed["url"], headers=headers, timeout=20)
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
        except Exception:
            continue

        for item in parsed.entries[:20]:
            if not article_matches_date(item, threat_date, date_from, date_to):
                continue

            articles.append(
                {
                    "feed": feed.get("name", ""),
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "link": item.get("link", ""),
                    "published": item.get("published", item.get("updated", "")),
                }
            )

    return articles[:6]


def extract_article_text(url: str, fallback_summary: str = ""):
    if not trafilatura or not url:
        return fallback_summary

    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return fallback_summary

        extracted = trafilatura.extract(downloaded)
        return extracted or fallback_summary
    except Exception:
        return fallback_summary


def extract_single_article(url: str):
    if not trafilatura:
        return {
            "error": "Article extraction is unavailable. Install trafilatura and rebuild the backend."
        }

    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return {"error": "Unable to fetch the article URL."}

        metadata = trafilatura.extract_metadata(downloaded)
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
        )

        if not text or len(text.strip()) < 200:
            return {"error": "Unable to extract enough article content from this URL."}

        return {
            "title": metadata.title if metadata and metadata.title else "Single Article",
            "author": metadata.author if metadata and metadata.author else "",
            "published": metadata.date if metadata and metadata.date else "",
            "url": url,
            "text": text.strip(),
        }
    except Exception as error:
        return {"error": f"Article extraction failed: {str(error)}"}


def call_ollama(prompt: str):
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=600,
    )

    response.raise_for_status()
    return response.json().get("response", "")


def build_hypothesis_prompt(context: str, article_text: str):
    return f"""
You are a senior cyber threat hunting analyst.

Create a professional threat hunting hypothesis report.

Organization context:
{context}

Threat intelligence articles:
{article_text}

Return the report in this structure:

1. Executive Summary
2. Main Threat Hunting Hypothesis
3. Supporting Threat Articles
4. MITRE ATT&CK Mapping
5. Hunting Steps
6. Detection Queries
   - Microsoft Sentinel KQL
   - Splunk SPL
   - Sigma Rule
7. Required Log Sources
8. Confidence Rating
9. Analyst Notes

Rules:
- Do not invent source URLs.
- Use only the given article context.
- If evidence is weak, say confidence is Low.
- Make it useful for SOC analysts.
"""


@app.post("/api/hypothesis/generate")
def generate_hypothesis(request: HypothesisRequest):
    has_sector = bool(request.sector and request.sector.strip())
    has_geo = bool(request.geo_location and request.geo_location.strip())
    has_tech = bool(request.technology_stack and len(request.technology_stack) > 0)
    has_date = bool(request.threat_date and request.threat_date != "any")

    if not any([has_sector, has_geo, has_tech, has_date]):
        return {
            "error": "Select at least one option: industry, geo location, technology stack, or date."
        }

    store = load_store()
    feeds = store.get("rss_feeds", [])

    articles = collect_rss_articles(
        feeds,
        request.threat_date or "any",
        request.date_from or "",
        request.date_to or "",
    )

    if not articles:
        return {
            "error": "No RSS articles found for the selected filter. Try Any Date or add more feeds.",
            "articles": [],
        }

    article_text = "\n\n".join(
        [
            (
                f"Title: {a['title']}\n"
                f"Source: {a['feed']}\n"
                f"Published: {a['published']}\n"
                f"URL: {a['link']}\n"
                f"Summary: {extract_article_text(a['link'], a['summary'])[:2500]}"
            )
            for a in articles
        ]
    )

    context = f"""
Sector: {request.sector or "Not provided"}
Geo location: {request.geo_location or "Not provided"}
Technology stack: {", ".join(request.technology_stack or []) or "Not provided"}
Threat article date filter: {request.threat_date}
Custom date from: {request.date_from or "Not provided"}
Custom date to: {request.date_to or "Not provided"}
"""
    prompt = build_hypothesis_prompt(context, article_text)

    result = call_ollama(prompt)

    return {
        "report": result,
        "articles": articles,
    }


@app.post("/api/hypothesis/article")
def generate_article_hypothesis(request: ArticleHypothesisRequest):
    article_url = request.url.strip()

    if not article_url.startswith(("http://", "https://")):
        return {"error": "Enter a valid article URL starting with http:// or https://."}

    article = extract_single_article(article_url)

    if article.get("error"):
        return {"error": article["error"], "articles": []}

    article_text = (
        f"Title: {article['title']}\n"
        f"Source: Single Article URL\n"
        f"Published: {article['published'] or 'Not provided'}\n"
        f"Author: {article['author'] or 'Not provided'}\n"
        f"URL: {article['url']}\n"
        f"Content: {article['text'][:8000]}"
    )
    context = """
Sector: Not provided
Geo location: Not provided
Technology stack: Not provided
Threat article date filter: Single article URL
"""
    prompt = build_hypothesis_prompt(context, article_text)
    result = call_ollama(prompt)

    return {
        "report": result,
        "articles": [
            {
                "feed": "Single Article URL",
                "title": article["title"],
                "summary": article["text"][:500],
                "link": article["url"],
                "published": article["published"],
            }
        ],
    }


