"""Use Google Gemini to generate a narrative summary for each topic bucket."""

import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "You are an education policy analyst covering Chicago K-12 public education. "
        "Your audience is education stakeholders — advocates, administrators, parents, and policymakers. "
        "Write concise, neutral, factual summaries that highlight key themes, notable developments, "
        "and any emerging trends or tensions. Avoid jargon. Do not editorialize."
    ),
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
        f"from the past two weeks. Write a 2-3 paragraph summary covering "
        f"the main themes and significant developments.\n\n{articles_text}"
    )

    response = _model.generate_content(prompt)
    return response.text.strip()