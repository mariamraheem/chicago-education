# Chicago Education Digest

A biweekly automated newsletter covering K-12 education and school governance news in Chicago. Articles are pulled from RSS feeds, categorized by topic, summarized using Google Gemini, and delivered to your inbox via Gmail.

## What it does

- Fetches articles from Chalkbeat Chicago, Chicago Tribune, Crain's Chicago Business, CPS, and ISBE
- Filters articles by topic (K-12 schools, board of education & governance)
- Summarizes each topic using Google Gemini
- Emails a formatted digest on the 1st and 15th of every month
- Saves each digest as a Markdown file in `digests/`

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/mariamraheem/chicago-education.git
cd chicago-education
pip install -r requirements.txt
```

### 2. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|---|---|
| `GEMINI_API_KEY` | From Google AI Studio |
| `GMAIL_USER` | Your Gmail address (e.g. `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | 16-char App Password — see below |
| `RECIPIENT_EMAIL` | Where to deliver the digest (can be same as `GMAIL_USER`) |

### 3. Get a Gmail App Password

1. Go to myaccount.google.com/security
2. Enable **2-Step Verification** if not already on
3. Search for **"App passwords"** and create one (name it anything, e.g. "chicago digest")
4. Copy the 16-character code — that's your `GMAIL_APP_PASSWORD`

Your real Gmail password is never stored or used.

## Running locally

```bash
# Fetch, summarize, and email
python run_digest.py

# Skip email (for testing)
python run_digest.py --no-email

# Override the lookback window
python run_digest.py --days 7 --no-email
```

## Customizing

- **`sources.yaml`** — add or disable RSS feeds
- **`filters.yaml`** — add keywords to topic buckets or create new topics

## Schedule

Runs automatically on the **1st and 15th of every month at 9 AM CT** via GitHub Actions.
You can also trigger it manually: **Actions tab → Biweekly Chicago Education Digest → Run workflow**.
```
Then scroll down and click **Commit changes**.
