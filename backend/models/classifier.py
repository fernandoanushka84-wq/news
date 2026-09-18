import ollama
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

CATEGORIES = [
    "Visa & Immigration",
    "Safety & Security",
    "Attractions & Destinations",
    "Events & Festivals",
    "Transportation",
    "Weather & Natural Disasters",
    "Health & Medical",
    "Hotels & Accommodation",
    "Food & Cuisine",
    "Shopping & Markets",
    "Culture & Heritage",
    "Adventure & Activities",
    "Economy & Tourism Statistics",
    "Sustainability & Eco-Tourism",
    "Crisis & Emergency Updates",
    "Other"
]

SYSTEM_PROMPT = """You are a news classifier specialized in Thailand tourism.
Your task is to decide if a news article is related to Thailand tourism and assign the most suitable category.

Categories:
- Visa & Immigration
- Safety & Security
- Attractions & Destinations
- Events & Festivals
- Transportation
- Weather & Natural Disasters
- Health & Medical
- Hotels & Accommodation
- Food & Cuisine
- Shopping & Markets
- Culture & Heritage
- Adventure & Activities
- Economy & Tourism Statistics
- Sustainability & Eco-Tourism
- Crisis & Emergency Updates
- Other

Rules:
1. Only mark is_tourism = true if the article is clearly about tourism, travel, visitors, hotels, attractions, visas for tourists, safety for travellers, festivals that attract tourists, or tourism economy in Thailand.
2. Ignore pure politics, pure crime (unless tourist related), pure business unrelated to tourism, sports (unless tourism event), etc.
3. Respond ONLY in valid JSON format with keys: is_tourism (boolean), category (string), confidence (float 0-1), reason (short string).
"""


def classify_article(title: str, summary: str = "", content: str = "") -> dict:
    """
    Classify a news article using local Ollama model.
    Returns dict with is_tourism, category, confidence, reason.
    """
    text = f"Title: {title}\n\nSummary: {summary}\n\nContent: {content[:1500]}"

    user_prompt = f"""Analyze this news article and classify it.

{text}

Respond only with JSON:
{{
  "is_tourism": true or false,
  "category": "one of the categories",
  "confidence": 0.0 to 1.0,
  "reason": "brief explanation"
}}
"""

    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.1}
        )

        raw = response["message"]["content"].strip()

        json_match = re.search(r"\{[\s\S]*\}", raw)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {
                "is_tourism": False,
                "category": "Other",
                "confidence": 0.0,
                "reason": "Failed to parse model response"
            }

        if result.get("category") not in CATEGORIES:
            result["category"] = "Other"

        return result

    except Exception as e:
        return {
            "is_tourism": False,
            "category": "Other",
            "confidence": 0.0,
            "reason": f"Error: {str(e)}"
        }


def check_ollama_status() -> str:
    """Check if Ollama is reachable."""
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        client.list()
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"
