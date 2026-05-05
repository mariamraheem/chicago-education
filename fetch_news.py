"""Fetch articles from RSS feeds and categorize them by topic."""

import time
import feedparser
import yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path


def _load_yaml(filename: str) -> dict:
    with open(Path(__file__).parent / filename) as f:
        return yaml.safe_load(f)


def _parse_published(entry) -> datetime | None:
    raw = entry.get("published_parsed") or entry.get("updated_parsed")
    if raw is None:
        return None
    return datetime(*raw[:6], tzinfo=timezone.utc)


def fetch_articles(days_back: int = 14) -> list[dict]:
    sources = _load_yaml("sources.yaml")["sources"]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    articles = []

    for source in sources:
        if not source.get("active") or not source.get("url"):
            continue
        try:
            feed = feedparser.parse(source["url"])
        except Exception as exc:
            print(f"[WARN] Could not fetch {source['name']}: {exc}")
            continue

        if feed.bozo and not feed.entries:
            print(f"[WARN] Feed parse issue for {source['name']}: {feed.bozo_exception}")
            continue

        for entry in feed.entries:
            pub_dt = _parse_published(entry)
            if pub_dt and pub_dt < cutoff:
                continue

            articles.append({
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "description": _strip_html(entry.get("summary", "")),
                "published": pub_dt,
                "published_str": pub_dt.strftime("%b %d, %Y") if pub_dt else "Date unknown",
                "source": source["name"],
            })

    return articles


def categorize_articles(articles: list[dict]) -> dict[str, list[dict]]:
    topics = _load_yaml("filters.yaml")["topics"]
    categorized: dict[str, list[dict]] = {t["name"]: [] for t in topics}
    seen: dict[str, set[str]] = {t["name"]: set() for t in topics}

    for article in articles:
        haystack = (article["title"] + " " + article["description"]).lower()
        for topic in topics:
            if any(kw.lower() in haystack for kw in topic["keywords"]):
                url = article["url"]
                if url not in seen[topic["name"]]:
                    categorized[topic["name"]].append(article)
                    seen[topic["name"]].add(url)

    return categorized


def _strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text).strip()