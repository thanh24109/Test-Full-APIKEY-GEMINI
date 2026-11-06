import os
from pathlib import Path
import streamlit as st

ENV_FILE_PATH = Path(".env")

def get_env_api_key() -> str:
    """Retrieve Gemini API key from environment variable or .env file."""
    return os.getenv("GEMINI_API_KEY", "").strip()

def get_env_deepseek_key() -> str:
    """Retrieve DeepSeek API key from environment variable or .env file."""
    return os.getenv("DEEPSEEK_API_KEY", "").strip()

def save_both_keys_to_env(gemini_key: str = None, deepseek_key: str = None) -> bool:
    """Save both Gemini and DeepSeek API keys to .env file preserving existing values."""
    try:
        g_key = gemini_key if gemini_key is not None else get_env_api_key()
        d_key = deepseek_key if deepseek_key is not None else get_env_deepseek_key()
        
        lines = [
            "# AI API Configurations",
            f"GEMINI_API_KEY={g_key.strip()}",
            f"DEEPSEEK_API_KEY={d_key.strip()}",
            ""
        ]
        with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        os.environ["GEMINI_API_KEY"] = g_key.strip()
        os.environ["DEEPSEEK_API_KEY"] = d_key.strip()
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu vào file .env: {e}")
        return False

def save_api_key_to_env(key: str) -> bool:
    """Save Gemini API key to .env file."""
    return save_both_keys_to_env(gemini_key=key)

def save_deepseek_key_to_env(key: str) -> bool:
    """Save DeepSeek API key to .env file."""
    return save_both_keys_to_env(deepseek_key=key)
