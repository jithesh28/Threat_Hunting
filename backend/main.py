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
import re

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
DEFAULT_DASHBOARD_STATS = {
    "totals": {
        "articles_analyzed": 0,
        "hypotheses_created": 0,
        "mitre_techniques": [],
    },
    "latest_run": {
        "articles_analyzed": 0,
        "hypotheses_created": 0,
        "mitre_techniques": [],
    },
}


def ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(STORE_FILE):
        save_store(
            {
                "rss_feeds": DEFAULT_RSS_FEEDS,
                "custom_technologies": DEFAULT_CUSTOM_TECHNOLOGIES,
                "dashboard_stats": DEFAULT_DASHBOARD_STATS,
            }
        )


def load_store():
    ensure_store()

    with open(STORE_FILE, "r", encoding="utf-8") as file:
        store = json.load(file)

    changed = False

    if "rss_feeds" not in store:
        store["rss_feeds"] = DEFAULT_RSS_FEEDS
        changed = True

    if "custom_technologies" not in store:
        store["custom_technologies"] = DEFAULT_CUSTOM_TECHNOLOGIES
        changed = True

    if "dashboard_stats" not in store:
        store["dashboard_stats"] = DEFAULT_DASHBOARD_STATS
        changed = True
    elif "totals" not in store["dashboard_stats"] or "latest_run" not in store["dashboard_stats"]:
        legacy_stats = store["dashboard_stats"]
        migrated_stats = {
            "totals": {
                "articles_analyzed": int(legacy_stats.get("articles_analyzed", 0)),
                "hypotheses_created": int(legacy_stats.get("hypotheses_created", 0)),
                "mitre_techniques": legacy_stats.get("mitre_techniques", []),
            },
            "latest_run": {
                "articles_analyzed": int(legacy_stats.get("articles_analyzed", 0)),
                "hypotheses_created": int(legacy_stats.get("hypotheses_created", 0)),
                "mitre_techniques": legacy_stats.get("mitre_techniques", []),
            },
        }
        store["dashboard_stats"] = migrated_stats
        changed = True

    if changed:
        save_store(store)

    return store


def save_store(data):
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(STORE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def extract_mitre_techniques(report: str):
    return sorted(set(re.findall(r"\bT\d{4}(?:\.\d{3})?\b", report or "")))


def count_report_hypotheses(report: str, fallback_count: int = 1):
    title_count = len(re.findall(r"hypothesis title\s*:", report or "", re.IGNORECASE))

    if title_count:
        return title_count

    numbered_count = len(
        re.findall(
            r"(?im)^\s*(?:hypothesis\s*)?\d+[\).\s-]+.+",
            report or "",
        )
    )

    if numbered_count:
        return min(numbered_count, fallback_count)

    return fallback_count


def update_dashboard_stats(articles_analyzed: int, hypotheses_created: int, report: str):
    store = load_store()
    stats = store.get("dashboard_stats", DEFAULT_DASHBOARD_STATS.copy())
    totals = stats.get("totals", DEFAULT_DASHBOARD_STATS["totals"].copy())
    latest_run = {
        "articles_analyzed": articles_analyzed,
        "hypotheses_created": hypotheses_created,
        "mitre_techniques": extract_mitre_techniques(report),
    }

    total_mitre_techniques = set(totals.get("mitre_techniques", []))
    total_mitre_techniques.update(latest_run["mitre_techniques"])

    stats = {
        "totals": {
            "articles_analyzed": int(totals.get("articles_analyzed", 0)) + articles_analyzed,
            "hypotheses_created": int(totals.get("hypotheses_created", 0)) + hypotheses_created,
            "mitre_techniques": sorted(total_mitre_techniques),
        },
        "latest_run": latest_run,
    }

    store["dashboard_stats"] = stats
    save_store(store)

    return stats


def build_dashboard_response():
    store = load_store()
    stats = store.get("dashboard_stats", DEFAULT_DASHBOARD_STATS)
    totals = stats.get("totals", DEFAULT_DASHBOARD_STATS["totals"])
    latest_run = stats.get("latest_run", DEFAULT_DASHBOARD_STATS["latest_run"])

    return {
        "rss_sources": len(store.get("rss_feeds", [])),
        "totals": {
            "articles_analyzed": int(totals.get("articles_analyzed", 0)),
            "hypotheses_created": int(totals.get("hypotheses_created", 0)),
            "mitre_techniques": len(totals.get("mitre_techniques", [])),
        },
        "latest_run": {
            "articles_analyzed": int(latest_run.get("articles_analyzed", 0)),
            "hypotheses_created": int(latest_run.get("hypotheses_created", 0)),
            "mitre_techniques": len(latest_run.get("mitre_techniques", [])),
        },
    }


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
    hypothesis_count: Optional[int] = 5


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


@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    return build_dashboard_response()


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

    return articles[:20]


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


def clamp_hypothesis_count(value: Optional[int]):
    try:
        return max(1, min(int(value or 1), 10))
    except Exception:
        return 1


def article_is_referenced(article: dict, report: str):
    report_text = report.lower()
    link = article.get("link", "").strip().lower()
    title = article.get("title", "").strip().lower()

    if link and link in report_text:
        return True

    if title and title in report_text:
        return True

    title_words = [
        word
        for word in title.replace("-", " ").split()
        if len(word) >= 5
    ]

    if len(title_words) < 3:
        return False

    matches = sum(1 for word in title_words if word in report_text)
    return matches >= min(4, len(title_words))


def filter_referenced_articles(articles: List[dict], report: str):
    return [article for article in articles if article_is_referenced(article, report)]


def build_hypothesis_prompt(context: str, article_text: str, hypothesis_count: int = 1):
    count = clamp_hypothesis_count(hypothesis_count)

    return f"""
You are a senior cyber threat hunting analyst.

Create {count} distinct professional threat hunting hypotheses.

Organization context:
{context}

Threat intelligence articles:
{article_text}

Return the report in this structure:

1. Executive Summary
2. Hypotheses
   For each hypothesis from 1 to {count}, include:
   - Hypothesis Title
   - Main Threat Hunting Hypothesis
   - Supporting Threat Articles with exact source URL
   - MITRE ATT&CK Mapping
   - Hunting Steps
   - Detection Queries
     - Microsoft Sentinel KQL
     - Splunk SPL
     - Sigma Rule
   - Required Log Sources
   - Confidence Rating
   - Analyst Notes

Rules:
- Do not invent source URLs.
- Use only the given article context.
- Cite a source URL only when it directly supports that specific hypothesis.
- Do not include unrelated supporting articles.
- Make each hypothesis different in behavior, technique, detection angle, or affected technology.
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

    hypothesis_count = clamp_hypothesis_count(request.hypothesis_count)
    selected_articles = articles[:max(6, min(len(articles), hypothesis_count * 3))]

    article_text = "\n\n".join(
        [
            (
                f"Title: {a['title']}\n"
                f"Source: {a['feed']}\n"
                f"Published: {a['published']}\n"
                f"URL: {a['link']}\n"
                f"Summary: {extract_article_text(a['link'], a['summary'])[:2500]}"
            )
            for a in selected_articles
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
    prompt = build_hypothesis_prompt(context, article_text, hypothesis_count)

    result = call_ollama(prompt)
    referenced_articles = filter_referenced_articles(selected_articles, result)
    created_count = count_report_hypotheses(result, hypothesis_count)
    update_dashboard_stats(len(selected_articles), created_count, result)

    return {
        "report": result,
        "articles": referenced_articles,
        "dashboard_stats": build_dashboard_response(),
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
    prompt = build_hypothesis_prompt(context, article_text, 1)
    result = call_ollama(prompt)
    update_dashboard_stats(1, count_report_hypotheses(result, 1), result)

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
        "dashboard_stats": build_dashboard_response(),
    }


