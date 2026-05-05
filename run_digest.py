"""
Main entry point.

Usage:
  python run_digest.py              # fetch last 14 days, summarize, email, save digest
  python run_digest.py --no-email   # skip email (useful for local testing)
  python run_digest.py --days 7     # override lookback window
"""

import argparse
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fetch_news import fetch_articles, categorize_articles
from summarize import summarize_topic
from send_email import render_html, render_plain, send_digest


DIGESTS_DIR = Path(__file__).parent / "digests"


def build_date_range(days_back: int) -> str:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days_back)
    return f"{start.strftime('%b %d')} – {end.strftime('%b %d, %Y')}"


def save_markdown(date_range: str, sections: list[dict]) -> Path:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = DIGESTS_DIR / f"{today}.md"
    DIGESTS_DIR.mkdir(exist_ok=True)

    lines = [
        f"# Chicago Education Digest",
        f"_{date_range}_",
        "",
        "> Covering: K-12 Education & Schools · Board of Education & Governance",
        "",
    ]

    for section in sections:
        if not section["articles"]:
            lines += [f"## {section['topic']}", "", "_No articles matched this period._", ""]
            continue

        lines += [f"## {section['topic']}", "", section["summary"], "", "### Articles", ""]
        for a in section["articles"]:
            lines.append(f"- [{a['title']}]({a['url']}) — {a['source']}, {a['published_str']}")
        lines += [""]

    path.write_text("\n".join(lines))
    print(f"Digest saved → {path}")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-email", action="store_true", help="Skip sending email")
    parser.add_argument("--days", type=int, default=14, help="Lookback window in days")
    args = parser.parse_args()

    print(f"Fetching articles from the last {args.days} days…")
    articles = fetch_articles(days_back=args.days)
    print(f"  {len(articles)} articles retrieved")

    categorized = categorize_articles(articles)
    total_matched = sum(len(v) for v in categorized.values())
    print(f"  {total_matched} articles matched topic filters")

    date_range = build_date_range(args.days)
    sections = []

    for topic_name, topic_articles in categorized.items():
        print(f'Summarizing "{topic_name}" ({len(topic_articles)} articles)…')
        summary = summarize_topic(topic_name, topic_articles)
        if not summary and not topic_articles:
            summary = "No articles matched this topic in the current period."
        sections.append({"topic": topic_name, "summary": summary, "articles": topic_articles})

    digest_path = save_markdown(date_range, sections)

    if not args.no_email:
        print("Sending email…")
        subject = f"Chicago Education Digest — {date_range}"
        send_digest(
            subject=subject,
            html_body=render_html(date_range, sections),
            plain_body=render_plain(date_range, sections),
        )
    else:
        print("Skipping email (--no-email flag set)")

    print("Done.")
    return str(digest_path)


if __name__ == "__main__":
    main()
