import os
import json

import streamlit as st
from groq import Groq
from dotenv import load_dotenv

from prompt import SYSTEM_PROMPT

# -----------------------------
# Load API Key
# -----------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# Streamlit Cloud Secrets
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        st.error(
            "❌ GROQ_API_KEY not found.\n\n"
            "Local: create a .env file.\n"
            "Streamlit Cloud: add GROQ_API_KEY under App Settings → Secrets."
        )
        st.stop()

client = Groq(api_key=api_key)


# -----------------------------
# Score Single Lead
# -----------------------------

def score_lead(lead: dict):
    try:
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

        return json.loads(content)

    except json.JSONDecodeError:
        return {
            "score": 0,
            "priority": "Unknown",
            "reason": [
                "Groq returned an invalid JSON response."
            ],
            "next_action": "Retry",
        }

    except Exception as e:
        st.error(f"❌ Groq API Error:\n\n{e}")

        return {
            "score": 0,
            "priority": "Unknown",
            "reason": [
                str(e)
            ],
            "next_action": "Check API configuration",
        }


# -----------------------------
# Score All Leads
# -----------------------------

def score_all(leads):
    scored = []

    for lead in leads:
        scored.append({
            **lead,
            **score_lead(lead)
        })

    return scored