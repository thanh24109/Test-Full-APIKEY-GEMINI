"""
Environment and Secrets Utilities Module.
Handles loading and saving API keys from .env file and environment variables.
"""
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Resolve project root .env path accurately regardless of working directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"

# Initial load on module import
load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)


def _read_key_from_file(key_name: str) -> str:
    """Fallback reader directly parsing the .env file in case os.environ is desynced."""
    if not ENV_FILE_PATH.exists():
        return ""
    try:
        with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == key_name:
                        return v.strip().strip("'").strip('"')
    except Exception:
        pass
    return ""


def get_env_api_key() -> str:
    """Retrieve Gemini API key from environment variable or .env file."""
    load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)
    val = os.getenv("GEMINI_API_KEY", "").strip()
    if not val:
        val = _read_key_from_file("GEMINI_API_KEY")
        if val:
            os.environ["GEMINI_API_KEY"] = val
    return val


def get_env_deepseek_key() -> str:
    """Retrieve DeepSeek API key from environment variable or .env file."""
    load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)
    val = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not val:
        val = _read_key_from_file("DEEPSEEK_API_KEY")
        if val:
            os.environ["DEEPSEEK_API_KEY"] = val
    return val


def save_both_keys_to_env(gemini_key: str = None, deepseek_key: str = None) -> bool:
    """Save both Gemini and DeepSeek API keys to .env file preserving existing values."""
    try:
        g_key = (gemini_key if gemini_key is not None else get_env_api_key()).strip()
        d_key = (deepseek_key if deepseek_key is not None else get_env_deepseek_key()).strip()
        
        lines = [
            "# AI API Configurations",
            f"GEMINI_API_KEY={g_key}",
            f"DEEPSEEK_API_KEY={d_key}",
            ""
        ]
        with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        os.environ["GEMINI_API_KEY"] = g_key
        os.environ["DEEPSEEK_API_KEY"] = d_key
        load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)
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
