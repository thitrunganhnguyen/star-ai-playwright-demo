import os
import json
import re
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

Important Docker rule:
If the user asks to open http://localhost:3000, convert it to http://frontend.
The browser runs inside the Playwright MCP Server container, so localhost would point to the wrong container.

Allowed actions:
- goto
- fill
- click
- expectText
- screenshot

Return format example:
[
  {{ "action": "goto", "url": "http://frontend" }},
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

    steps = json.loads(text)
    return normalize_steps_for_docker(steps)


def normalize_steps_for_docker(steps):
    normalized_steps = []

    for step in steps:
        new_step = dict(step)

        if new_step.get("action") == "goto":
            url = new_step.get("url", "")
            if url.startswith("http://localhost:3000"):
                new_step["url"] = url.replace(
                    "http://localhost:3000",
                    "http://frontend"
                )

        normalized_steps.append(new_step)

    return normalized_steps


def fallback_test_steps(user_goal: str):
    goal_lower = user_goal.lower()

    if "login" in goal_lower or "dashboard" in goal_lower:
        return [
            {
                "action": "goto",
                "url": "http://frontend"
            },
            {
                "action": "fill",
                "selector": "#username",
                "value": "demo"
            },
            {
                "action": "fill",
                "selector": "#password",
                "value": "demo123"
            },
            {
                "action": "click",
                "selector": "#login-button"
            },
            {
                "action": "expectText",
                "selector": "body",
                "value": "Dashboard"
            },
            {
                "action": "screenshot",
                "name": extract_screenshot_name(user_goal, "fallback-login-success")
            }
        ]

    if "screenshot" in goal_lower:
        return [
            {
                "action": "goto",
                "url": "http://frontend"
            },
            {
                "action": "screenshot",
                "name": extract_screenshot_name(user_goal, "fallback-screenshot")
            }
        ]

    return [
        {
            "action": "goto",
            "url": "http://frontend"
        }
    ]


def extract_screenshot_name(user_goal: str, default_name: str):
    match = re.search(r"named\s+([a-zA-Z0-9_-]+)", user_goal)

    if match:
        return match.group(1)

    return default_name