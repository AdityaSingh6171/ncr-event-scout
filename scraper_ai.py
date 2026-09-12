import os
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import List
import streamlit as st
from google import genai
from google.genai import types

# Use Streamlit Secrets on cloud; fallback to environment variable locally
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
client = genai.Client(api_key=api_key)

class EventItem(BaseModel):
    title: str = Field(description="Name or title of the event")
    category: str = Field(description="Genre: Music, Comedy, Art, Food, Heritage, Tech")
    venue: str = Field(description="Specific auditorium, ground, or area")
    region: str = Field(description="South Delhi, Central Delhi, Dwarka, Gurugram, Noida")
    schedule: str = Field(description="Date and time string")
    price: str = Field(description="Ticket starting price or 'Free Entry'")
    summary: str = Field(description="Crisp 1-2 sentence AI summary of what to expect")

class EventResponse(BaseModel):
    events: List[EventItem]

def fetch_and_summarize(url: str = "https://allevents.in/delhi") -> List[dict]:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        page_text = soup.get_text(separator=" ", strip=True)[:10000]
    except Exception:
        page_text = "Delhi NCR Cultural events, music concerts at Yashobhoomi, food festivals in Okhla, and heritage walks at Sunder Nursery."

    prompt = f"""
    You are an event scout for Delhi NCR. Extract upcoming events from this text into structured JSON.
    Content:
    {page_text}
    """

    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EventResponse,
            temperature=0.2
        )
    )
    return EventResponse.model_validate_json(res.text).events