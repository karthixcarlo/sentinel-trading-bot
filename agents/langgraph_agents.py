# -*- coding: utf-8 -*-
"""
Shared LLM instance for Project Sentinel.

Provides a single ChatGoogleGenerativeAI (Gemini 2.5 Flash) instance
used by the Copilot, stock analyzer, and other backend AI endpoints.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Support both GOOGLE_API_KEY and GEMINI_API_KEY
_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
    google_api_key=_api_key,
)
