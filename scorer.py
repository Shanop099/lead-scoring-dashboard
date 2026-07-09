import os
import json

from groq import Groq
from dotenv import load_dotenv

from prompt import SYSTEM_PROMPT

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def score_lead(lead: dict):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(lead, indent=2)
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)

    except Exception:

        result = {
            "score": 0,
            "priority": "Unknown",
            "reason": [
                "Failed to parse LLM response."
            ],
            "next_action": "Retry"
        }

    return result


def score_all(leads):

    scored = []

    for lead in leads:

        result = score_lead(lead)

        scored.append({
            **lead,
            **result
        })

    return scored