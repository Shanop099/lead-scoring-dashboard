import os
import json

import streamlit as st
from groq import Groq
from dotenv import load_dotenv

from prompt import SYSTEM_PROMPT

# Load local .env (works on your computer)
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

# If deployed on Streamlit Cloud, use Secrets
if not api_key:
    api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)


def score_lead(lead: dict):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(lead, indent=2),
            },
        ],
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {
            "score": 0,
            "priority": "Unknown",
            "reason": ["Failed to parse LLM response."],
            "next_action": "Retry",
        }

    return result


def score_all(leads):

    return [
        {
            **lead,
            **score_lead(lead),
        }
        for lead in leads
    ]