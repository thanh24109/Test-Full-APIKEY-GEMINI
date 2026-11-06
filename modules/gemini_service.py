import streamlit as st

try:
    from google import genai
    from google.genai import types, errors
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

def get_genai_client(api_key: str):
    """Create and return a Google GenAI Client instance."""
    if not api_key or not GENAI_AVAILABLE:
        return None
    return genai.Client(api_key=api_key)

def validate_gemini_api_key(api_key: str):
    """Validate API key by querying client.models.list()."""
    if not api_key:
        return False, "Vui lòng nhập API Key.", []
    if not GENAI_AVAILABLE:
        return False, "Thư viện google-genai chưa được cài đặt. Chạy: pip install google-genai", []
    
    try:
        client = get_genai_client(api_key)
        models_pager = client.models.list()
        gemini_models = []
        for m in models_pager:
            name = m.name or ""
            clean_name = name.replace("models/", "")
            if "gemini" in clean_name.lower():
                gemini_models.append({
                    "id": clean_name,
                    "display_name": getattr(m, "display_name", clean_name),
                    "description": getattr(m, "description", ""),
                    "input_token_limit": getattr(m, "input_token_limit", "N/A"),
                    "output_token_limit": getattr(m, "output_token_limit", "N/A")
                })
        return True, "API Key hợp lệ! Đã kết nối thành công tới Gemini API.", gemini_models
    except errors.APIError as e:
        error_msg = f"Lỗi API ({e.code}): {e.message}"
        if "API_KEY_INVALID" in str(e) or e.code == 400:
            error_msg = "API Key không hợp lệ. Vui lòng kiểm tra lại trên Google AI Studio."
        return False, error_msg, []
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", []

def get_default_safety_settings():
    """Default safety settings to avoid false positives on legitimate documents."""
    if not GENAI_AVAILABLE:
        return None
    return [
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    ]
