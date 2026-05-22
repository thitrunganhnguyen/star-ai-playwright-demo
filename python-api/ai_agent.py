import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()


def generate_test_steps(user_goal: str):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing in .env")

    prompt = f"""
You are a test automation assistant.
Return ONLY valid JSON.
Generate safe Playwright test steps.

Allowed actions:
- goto
- fill
- click
- expectText
- screenshot

Return format example:
[
  {{ "action": "goto", "url": "http://localhost:3000" }},
  {{ "action": "fill", "selector": "#username", "value": "demo" }},
  {{ "action": "fill", "selector": "#password", "value": "demo123" }},
  {{ "action": "click", "selector": "#login-button" }},
  {{ "action": "expectText", "selector": "body", "value": "Dashboard" }},
  {{ "action": "screenshot", "name": "login-success" }}
]

Do not return markdown.
Do not return explanation.

User goal:
{user_goal}
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={api_key}"
    )

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1
            }
        },
        timeout=60
    )

    if not response.ok:
        raise RuntimeError(
            f"Gemini API error {response.status_code}: {response.text}"
        )

    data = response.json()

    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    if not text:
        raise RuntimeError("Gemini returned empty response")

    return json.loads(text)