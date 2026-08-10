"""Use Google Gemini to generate a narrative summary for each topic bucket."""

import os
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

_SYSTEM = (
    "You are an education policy analyst covering Chicago K-12 public education. "
    "Your audience is education stakeholders — advocates, administrators, parents, and policymakers. "
    "Write concise, neutral, factual summaries that highlight key themes, notable developments, "
    "and any emerging trends or tensions. Avoid jargon. Do not editorialize."
)


def summarize_topic(topic_name: str, articles: list[dict]) -> str:
    if not articles:
        return ""

    articles_text = "\n\n".join(
        f"Title: {a['title']}\n"
        f"Source: {a['source']}\n"
        f"Date: {a['published_str']}\n"
        f"Description: {a['description'][:600]}"
        for a in articles
    )

    prompt = (
        f"Below are recent news articles about **{topic_name}** in Chicago "
        f"from the past week. Write a 2-3 paragraph summary covering "
        f"the main themes and significant developments.\n\n{articles_text}"
    )

    for attempt in range(4):
        try:
            response = _client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3, system_instruction=_SYSTEM
                ),
            )
            return response.text.strip()
        except ServerError as e:
            if attempt < 3:
                wait = 15 * (2 ** attempt)  # 15s, 30s, 60s
                print(f"  [WARN] Gemini unavailable, retrying in {wait}s… ({e})")
                time.sleep(wait)
            else:
                print(f"  [ERROR] Gemini failed after 4 attempts for '{topic_name}': {e}")
                return f"Summary unavailable — Gemini API temporarily unavailable."
        except ClientError as e:
            print(f"  [ERROR] Gemini client error for '{topic_name}': {e}")
            return f"Summary unavailable — API error."
