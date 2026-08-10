"""Send the weekly digest via Gmail using an App Password."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# One accent color per topic — cycles if there are more topics than colors
_TOPIC_COLORS = [
    "#1a3a5c",  # navy
    "#2e7d32",  # green
    "#b71c1c",  # red
    "#e65100",  # orange
    "#4527a0",  # purple
    "#00695c",  # teal
    "#1565c0",  # blue
    "#558b2f",  # olive
    "#6a1b9a",  # violet
    "#0277bd",  # light blue
]


def send_digest(subject: str, html_body: str, plain_body: str) -> None:
    sender = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Chicago Education Digest <{sender}>"
    msg["To"] = recipient

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Email sent to {recipient}")


# ── HTML rendering ────────────────────────────────────────────────────────────

def render_html(date_range: str, sections: list[dict]) -> str:
    active = [s for s in sections if s["articles"]]
    if not active:
        return _empty_html(date_range)

    topic_count = len(active)
    total_articles = sum(len(s["articles"]) for s in active)

    # Table of contents
    toc_items = ""
    for i, section in enumerate(active):
        color = _TOPIC_COLORS[i % len(_TOPIC_COLORS)]
        toc_items += (
            f'<a href="#topic-{i}" style="display:inline-block;margin:4px 6px 4px 0;'
            f'padding:4px 12px;background:{color};color:#fff;border-radius:20px;'
            f'font-size:0.78em;text-decoration:none;font-family:Arial,sans-serif;">'
            f'{section["topic"]}</a>'
        )

    # Topic sections
    topic_blocks = ""
    for i, section in enumerate(active):
        color = _TOPIC_COLORS[i % len(_TOPIC_COLORS)]
        count = len(section["articles"])
        summary_html = section["summary"].replace("\n\n", "</p><p>").replace("\n", " ")

        article_rows = ""
        for a in section["articles"]:
            article_rows += (
                f'<tr>'
                f'<td style="padding:8px 0;border-bottom:1px solid #f0f0f0;vertical-align:top">'
                f'<a href="{a["url"]}" style="color:{color};font-weight:600;'
                f'text-decoration:none;font-size:0.9em;line-height:1.4;">{a["title"]}</a>'
                f'<div style="margin-top:3px;">'
                f'<span style="display:inline-block;background:#f0f0f0;color:#555;'
                f'font-size:0.72em;padding:1px 7px;border-radius:10px;'
                f'font-family:Arial,sans-serif;">{a["source"]}</span>'
                f'<span style="color:#aaa;font-size:0.75em;margin-left:6px;">{a["published_str"]}</span>'
                f'</div>'
                f'</td>'
                f'</tr>'
            )

        topic_blocks += f"""
        <div id="topic-{i}" style="margin-bottom:2.5em;">
          <div style="border-left:4px solid {color};padding-left:14px;margin-bottom:1em;">
            <h2 style="margin:0 0 2px;font-size:1.05em;color:{color};font-family:Arial,sans-serif;">
              {section["topic"]}
            </h2>
            <span style="font-size:0.75em;color:#888;font-family:Arial,sans-serif;">
              {count} article{"s" if count != 1 else ""}
            </span>
          </div>
          <div style="color:#333;line-height:1.7;font-size:0.92em;margin-bottom:1.2em;">
            <p style="margin:0 0 0.8em;">{summary_html}</p>
          </div>
          <table style="width:100%;border-collapse:collapse;">
            {article_rows}
          </table>
        </div>
        """

    topic_labels = " &middot; ".join(s["topic"] for s in active)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Georgia,serif;">
  <div style="max-width:660px;margin:24px auto;background:#fff;border-radius:6px;
              overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:#1a3a5c;padding:24px 28px 20px;">
      <div style="font-size:0.7em;color:#7fb3d3;letter-spacing:2px;
                  text-transform:uppercase;font-family:Arial,sans-serif;margin-bottom:6px;">
        Chicago Education
      </div>
      <h1 style="margin:0;font-size:1.5em;color:#fff;letter-spacing:-0.3px;">
        Weekly Digest
      </h1>
      <p style="margin:6px 0 0;font-size:0.83em;color:#a8c8e8;font-family:Arial,sans-serif;">
        {date_range}
      </p>
    </div>

    <!-- Stats bar -->
    <div style="background:#f0f4f8;padding:10px 28px;border-bottom:1px solid #dde3ea;
                font-family:Arial,sans-serif;font-size:0.78em;color:#555;">
      <strong style="color:#1a3a5c;">{total_articles}</strong> articles across
      <strong style="color:#1a3a5c;">{topic_count}</strong> topics
    </div>

    <!-- Table of contents -->
    <div style="padding:16px 28px 8px;background:#fff;border-bottom:1px solid #eee;">
      <div style="font-size:0.72em;color:#999;font-family:Arial,sans-serif;
                  text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">
        This week
      </div>
      {toc_items}
    </div>

    <!-- Body -->
    <div style="padding:24px 28px;">
      {topic_blocks}
    </div>

    <!-- Footer -->
    <div style="background:#f8f8f8;border-top:1px solid #eee;padding:16px 28px;
                font-size:0.72em;color:#999;font-family:Arial,sans-serif;line-height:1.6;">
      Auto-generated weekly by chicago-education digest.<br>
      Sources: Chalkbeat Chicago, Chicago Tribune, Crain's Chicago Business, CPS, ISBE, Google News.
    </div>

  </div>
</body>
</html>"""


def _empty_html(date_range: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:660px;margin:24px auto;padding:24px;">
  <h1 style="color:#1a3a5c;">Chicago Education Digest</h1>
  <p style="color:#555;">{date_range}</p>
  <p>No articles matched this week's filters. Check back next week.</p>
</body></html>"""


# ── Plain-text rendering ──────────────────────────────────────────────────────

def render_plain(date_range: str, sections: list[dict]) -> str:
    lines = [
        "CHICAGO EDUCATION DIGEST",
        date_range,
        "=" * 60,
        "",
    ]
    for section in sections:
        if not section["articles"]:
            continue
        lines += [
            section["topic"].upper(),
            "-" * len(section["topic"]),
            "",
            section["summary"],
            "",
            "Articles:",
        ]
        for a in section["articles"]:
            lines.append(f"  • {a['title']} ({a['source']}, {a['published_str']})")
            lines.append(f"    {a['url']}")
        lines += ["", ""]
    return "\n".join(lines)
