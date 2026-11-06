import streamlit as st

try:
    from openai import OpenAI, AuthenticationError, APIError as OpenAIAPIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def get_deepseek_client(api_key: str):
    """Create and return an OpenAI client configured for DeepSeek API."""
    if not api_key or not OPENAI_AVAILABLE:
        return None
    return OpenAI(
        api_key=api_key.strip(),
        base_url="https://api.deepseek.com"
    )

def validate_deepseek_api_key(api_key: str):
    """Validate DeepSeek API key by querying the /models endpoint."""
    if not api_key:
        return False, "Vui lòng nhập DeepSeek API Key.", []
    if not OPENAI_AVAILABLE:
        return False, "Thư viện openai chưa được cài đặt. Chạy: pip install openai", []
    
    try:
        client = get_deepseek_client(api_key)
        models_resp = client.models.list()
        deepseek_models = []
        for m in getattr(models_resp, "data", []):
            m_id = getattr(m, "id", "")
            deepseek_models.append({
                "id": m_id,
                "display_name": m_id,
                "description": "DeepSeek Official Model"
            })
        if not deepseek_models:
            deepseek_models = [
                {"id": "deepseek-chat", "display_name": "deepseek-chat (V3)", "description": "Mô hình đa năng, tốc độ cao, giá siêu rẻ"},
                {"id": "deepseek-reasoner", "display_name": "deepseek-reasoner (R1)", "description": "Mô hình suy luận logic chuyên sâu với Chain of Thought"}
            ]
        return True, "DeepSeek API Key hợp lệ! Đã kết nối thành công tới DeepSeek API.", deepseek_models
    except AuthenticationError:
        return False, "DeepSeek API Key không hợp lệ hoặc đã hết hạn (401 Unauthorized). Hãy kiểm tra lại tại platform.deepseek.com.", []
    except Exception as e:
        return False, f"Lỗi kết nối DeepSeek: {str(e)}", []

