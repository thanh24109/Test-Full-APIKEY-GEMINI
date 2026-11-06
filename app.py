"""
Gemini & DeepSeek API Explorer
A modular Streamlit application for interacting with Google Gemini (including Live API)
and DeepSeek AI models.
"""
import streamlit as st

from modules.ui_styles import apply_custom_css
from views.sidebar_view import render_sidebar
from views.chat_view import render_chat_tab
from views.live_api_view import render_live_api_tab
from views.vision_view import render_vision_tab
from views.doc_extract_view import render_doc_extract_tab
from views.prompt_lab_view import render_prompt_lab_tab
from views.docs_view import render_docs_tab


def init_session_state() -> None:
    """Initializes all Streamlit session state variables with default values."""
    default_states = {
        "chat_messages": [],
        "starter_prompt": None,
        "available_models": [],
        "api_key_valid": None,
        "last_tested_key": None,
        "deepseek_api_key_valid": None,
        "last_tested_deepseek_key": None,
        "available_deepseek_models": [],
        "live_dialog_history": [],
        "last_live_audio_response": None,
        "last_live_transcript": "",
        "last_live_thought": "",
        "last_live_stats": {},
        "last_stt_result": "",
        "last_stt_stats": {},
        "last_translate_audio": None,
        "last_translate_text": "",
        "last_vision_result": None,
        "last_vision_time": None,
        "last_actual_model": None,
        "last_local_doc_result": None,
        "last_local_doc_time": None,
        "last_local_doc_stats": {},
        "last_local_doc_filename": "",
        "last_markitdown_result": None,
        "last_markitdown_time": None,
        "last_markitdown_stats": {},
        "last_markitdown_filename": "",
        "last_markitdown_bytes": None,
        "last_docling_result": None,
        "last_docling_time": None,
        "last_docling_stats": {},
        "last_docling_filename": "",
        "last_deepseek_doc_result": None,
        "last_deepseek_doc_reasoning": None,
        "last_deepseek_doc_time": None,
        "last_deepseek_doc_model": "deepseek-flash",
        "last_deepseek_doc_filename": "",
        "last_deepseek_doc_stats": {},
        "last_doc_result": None,
        "last_doc_time": None,
        "last_doc_model": None,
        "last_doc_filename": "",
        "md_sample_selected": None,
        "docling_sample_selected": None,
        "deepseek_sample_selected": None,
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_hero_header() -> None:
    """Renders the top banner and hero section."""
    st.markdown(
        """
        <div class="hero-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h1 style="margin: 0; font-size: 2.2rem;">
                        <span class="gemini-gradient-text">Gemini API Explorer</span> ✨
                    </h1>
                    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 1.05rem;">
                        Ứng dụng trải nghiệm và kiểm thử Google Gemini API Key: Trò chuyện Streaming, Gemini Live API (Voice & Audio), Thị giác Đa phương thức và Trích xuất Tài liệu.
                    </p>
                </div>
                <div>
                    <a href="https://aistudio.google.com/app/apikey" target="_blank" style="text-decoration: none;">
                        <button style="
                            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                            color: white;
                            border: none;
                            padding: 10px 18px;
                            border-radius: 8px;
                            font-weight: 600;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.4);
                        ">
                            🔑 Lấy API Key miễn phí ↗
                        </button>
                    </a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Main application orchestrator."""
    st.set_page_config(
        page_title="Gemini & DeepSeek AI Explorer",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 1. Apply global custom CSS
    apply_custom_css()

    # 2. Initialize application state
    init_session_state()

    # 3. Render sidebar controls and retrieve configuration
    config = render_sidebar()

    # 4. Render main hero header
    render_hero_header()

    # 5. Welcome notice if no API keys are provided
    if not config["active_key"] and not config["active_deepseek_key"]:
        st.info(
            "👋 **Chào bạn!** Ứng dụng hỗ trợ cả **Google Gemini API** và **DeepSeek API**. "
            "Hãy nhập API Key ở thanh bên trái (Sidebar) để bắt đầu trải nghiệm!\n\n"
            "- Lấy Gemini API Key miễn phí: [Google AI Studio](https://aistudio.google.com/app/apikey)\n"
            "- Lấy DeepSeek API Key: [DeepSeek Platform](https://platform.deepseek.com/api_keys)",
            icon="👉",
        )

    # 6. Render main feature tabs
    tab_chat, tab_live_api, tab_vision, tab_docs_extract, tab_tools, tab_docs = st.tabs([
        "💬 Trò chuyện Chatbot",
        "🎙️ Gemini Live API (Voice & Audio)",
        "🖼️ Thị giác Đa phương thức (Vision)",
        "📄 Trích xuất Tài liệu (PDF & DOCX)",
        "⚡ Prompt Lab & Tác vụ mẫu",
        "📚 Thông tin Models & Tài liệu",
    ])

    with tab_chat:
        render_chat_tab(config)

    with tab_live_api:
        render_live_api_tab(config["active_key"])

    with tab_vision:
        render_vision_tab(config)

    with tab_docs_extract:
        render_doc_extract_tab(config)

    with tab_tools:
        render_prompt_lab_tab(config)

    with tab_docs:
        render_docs_tab()


if __name__ == "__main__":
    main()
