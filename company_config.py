"""
Cloud-friendly configuration for a generalist app.

Secrets are loaded from environment variables or Streamlit secrets:
- OPENAI_API_KEY
- GOOGLE_API_KEY
- GOOGLE_CX
"""

import os
import streamlit as st


def get_api_key(key_name: str):
    """Fetch API keys from env first, then from Streamlit secrets."""
    env_val = os.getenv(key_name)
    if env_val:
        return env_val
    try:
        if key_name == "OPENAI_API_KEY":
            return st.secrets["openai"]["api_key"]
        if key_name == "GOOGLE_API_KEY":
            return st.secrets["google"]["api_key"]
        if key_name == "GOOGLE_CX":
            return st.secrets["google"]["cx"]
    except Exception:
        pass
    return None


# Secrets (loaded at runtime)
openai_api_key = get_api_key("OPENAI_API_KEY")
google_api_key = get_api_key("GOOGLE_API_KEY")
google_cx = get_api_key("GOOGLE_CX")
