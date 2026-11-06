"""
Sidebar View Module: Renders API key configurations and model hyperparameters.
"""
from typing import Dict, Any, Optional
import streamlit as st
from google.genai import types

from modules.env_utils import (
    get_env_api_key,
    get_env_deepseek_key,
    save_api_key_to_env,
    save_deepseek_key_to_env,
)
from modules.gemini_service import (
    GENAI_AVAILABLE,
    validate_gemini_api_key,
    get_default_safety_settings,
)
from modules.deepseek_service import validate_deepseek_api_key


def render_sidebar() -> Dict[str, Any]:
    """
    Renders the sidebar controls for Gemini and DeepSeek providers,
    along with global hyperparameter sliders.

    Returns:
        dict containing:
            - active_key: Active Gemini API Key
            - active_deepseek_key: Active DeepSeek API Key
            - selected_model: Selected Gemini model ID
            - selected_deepseek_model: Selected DeepSeek model ID
            - temperature: Generation temperature
            - top_p: Nucleus sampling parameter
            - max_tokens: Max output tokens
            - system_instruction: Global system instruction string
            - client_config: types.GenerateContentConfig instance for Gemini
    """
    with st.sidebar:
        st.markdown("### ⚙️ Cấu hình API Key & Providers")

        sidebar_tab_gemini, sidebar_tab_deepseek = st.tabs(["✨ Google Gemini", "🐋 DeepSeek AI"])

        # ----------------------------------------------------
        # 1. Google Gemini Sidebar Tab
        # ----------------------------------------------------
        with sidebar_tab_gemini:
            saved_key = get_env_api_key()
            api_key_input = st.text_input(
                "🔑 Gemini API Key",
                value=saved_key,
                type="password",
                placeholder="AIzaSy...",
                help="Lấy API Key miễn phí từ Google AI Studio (https://aistudio.google.com/app/apikey)",
            ).strip()

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                test_key_clicked = st.button("🔍 Kiểm tra Key", use_container_width=True, key="btn_test_gemini")
            with col_btn2:
                save_key_clicked = st.button("💾 Lưu vào .env", use_container_width=True, key="btn_save_gemini")

            if save_key_clicked:
                if api_key_input:
                    if save_api_key_to_env(api_key_input):
                        st.success("✅ Đã lưu Gemini Key vào `.env`!")
                else:
                    st.warning("⚠️ Hãy nhập Gemini Key trước khi lưu.")

            if test_key_clicked:
                with st.spinner("Đang xác thực Gemini API Key..."):
                    is_valid, msg, models = validate_gemini_api_key(api_key_input)
                    st.session_state.api_key_valid = is_valid
                    st.session_state.last_tested_key = api_key_input
                    if is_valid:
                        st.session_state.available_models = models
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
            elif api_key_input and st.session_state.api_key_valid is None:
                is_valid, msg, models = validate_gemini_api_key(api_key_input)
                st.session_state.api_key_valid = is_valid
                st.session_state.last_tested_key = api_key_input
                if is_valid:
                    st.session_state.available_models = models

            if api_key_input:
                if st.session_state.api_key_valid is True and st.session_state.last_tested_key == api_key_input:
                    st.markdown('<div class="status-badge-ok">🟢 Gemini: Hợp lệ & Sẵn sàng</div>', unsafe_allow_html=True)
                elif st.session_state.api_key_valid is False and st.session_state.last_tested_key == api_key_input:
                    st.markdown('<div class="status-badge-warn">🔴 Gemini: Không hợp lệ</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-badge-warn">🟡 Gemini: Chưa kiểm tra</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-badge-warn">⚪ Chưa có Gemini Key</div>', unsafe_allow_html=True)

            st.markdown(
                '<div style="font-size:0.8rem; margin:6px 0 10px 0;"><a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#818cf8; text-decoration:none;">🔑 Lấy Gemini Key miễn phí ↗</a></div>',
                unsafe_allow_html=True,
            )

            st.markdown("##### 🧠 Mô hình Gemini:")
            default_models = [
                "gemini-3.6-flash",
                "gemini-3.1-flash-lite",
                "gemini-3.5-flash",
                "gemini-3.5-flash-lite",
                "gemini-3.8-flash",
                "gemini-3.1-pro-preview",
                "gemini-flash-latest",
            ]
            if st.session_state.available_models:
                fetched_ids = [m["id"] for m in st.session_state.available_models]
                model_options = [m for m in default_models if m in fetched_ids] + [m for m in fetched_ids if m not in default_models]
                if not model_options:
                    model_options = default_models
            else:
                model_options = default_models
            model_options.append("Tùy chỉnh (Nhập tên model)...")

            selected_option = st.selectbox(
                "Chọn model Gemini:",
                options=model_options,
                index=0,
                key="sel_gemini_model_box",
            )
            if selected_option == "Tùy chỉnh (Nhập tên model)...":
                selected_model = st.text_input("Tên model tùy chỉnh:", value="gemini-3.5-flash", key="custom_gemini_name")
            else:
                selected_model = selected_option

        # ----------------------------------------------------
        # 2. DeepSeek AI Sidebar Tab
        # ----------------------------------------------------
        with sidebar_tab_deepseek:
            saved_ds_key = get_env_deepseek_key()
            deepseek_key_input = st.text_input(
                "🐋 DeepSeek API Key",
                value=saved_ds_key,
                type="password",
                placeholder="sk-...",
                help="Lấy API Key tại DeepSeek Platform: https://platform.deepseek.com/api_keys",
            ).strip()

            col_ds1, col_ds2 = st.columns([1, 1])
            with col_ds1:
                test_ds_clicked = st.button("🔍 Kiểm tra Key", use_container_width=True, key="btn_test_deepseek")
            with col_ds2:
                save_ds_clicked = st.button("💾 Lưu vào .env", use_container_width=True, key="btn_save_deepseek")

            if save_ds_clicked:
                if deepseek_key_input:
                    if save_deepseek_key_to_env(deepseek_key_input):
                        st.success("✅ Đã lưu DeepSeek Key vào `.env`!")
                else:
                    st.warning("⚠️ Hãy nhập DeepSeek Key trước khi lưu.")

            if test_ds_clicked:
                with st.spinner("Đang xác thực DeepSeek API Key..."):
                    ds_valid, ds_msg, ds_models = validate_deepseek_api_key(deepseek_key_input)
                    st.session_state.deepseek_api_key_valid = ds_valid
                    st.session_state.last_tested_deepseek_key = deepseek_key_input
                    if ds_valid:
                        st.session_state.available_deepseek_models = ds_models
                        st.success(f"✅ {ds_msg}")
                    else:
                        st.error(f"❌ {ds_msg}")
            elif deepseek_key_input and st.session_state.deepseek_api_key_valid is None:
                ds_valid, ds_msg, ds_models = validate_deepseek_api_key(deepseek_key_input)
                st.session_state.deepseek_api_key_valid = ds_valid
                st.session_state.last_tested_deepseek_key = deepseek_key_input
                if ds_valid:
                    st.session_state.available_deepseek_models = ds_models

            if deepseek_key_input:
                if st.session_state.deepseek_api_key_valid is True and st.session_state.last_tested_deepseek_key == deepseek_key_input:
                    st.markdown('<div class="status-badge-ok">🟢 DeepSeek: Hợp lệ & Sẵn sàng</div>', unsafe_allow_html=True)
                elif st.session_state.deepseek_api_key_valid is False and st.session_state.last_tested_deepseek_key == deepseek_key_input:
                    st.markdown('<div class="status-badge-warn">🔴 DeepSeek: Không hợp lệ</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-badge-warn">🟡 DeepSeek: Chưa kiểm tra</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-badge-warn">⚪ Chưa có DeepSeek Key</div>', unsafe_allow_html=True)

            st.markdown(
                '<div style="font-size:0.8rem; margin:6px 0 10px 0;"><a href="https://platform.deepseek.com/api_keys" target="_blank" style="color:#38bdf8; text-decoration:none;">🔑 Lấy DeepSeek API Key ↗</a></div>',
                unsafe_allow_html=True,
            )

            st.markdown("##### 🐋 Mô hình DeepSeek:")
            ds_models_list = [
                "deepseek-flash — 💰 RẺ NHẤT & 🖼️ VISION ($0.003 - $0.15 / 1M)",
                "deepseek-v4-pro — 🚀 Flagship ($0.66 - $1.32 / 1M)",
                "deepseek-chat (V3 Legacy Alias) — ⚡ Tương thích ngược",
                "deepseek-reasoner (R1 Legacy Alias) — 🧠 Suy luận sâu CoT",
                "Tùy chỉnh (Nhập tên model)...",
            ]
            selected_ds_opt = st.selectbox(
                "Chọn model DeepSeek:",
                options=ds_models_list,
                index=0,
                key="sel_deepseek_model_box",
                help="Theo tài liệu DeepSeek Pricing chính thức: deepseek-flash là model RẺ NHẤT ($0.15/1M input, $0.003 nếu cache hit) và là model DUY NHẤT hỗ trợ Vision.",
            )
            if selected_ds_opt.startswith("deepseek-flash"):
                selected_deepseek_model = "deepseek-flash"
            elif selected_ds_opt.startswith("deepseek-v4-pro"):
                selected_deepseek_model = "deepseek-v4-pro"
            elif selected_ds_opt.startswith("deepseek-chat"):
                selected_deepseek_model = "deepseek-chat"
            elif selected_ds_opt.startswith("deepseek-reasoner"):
                selected_deepseek_model = "deepseek-reasoner"
            elif selected_ds_opt == "Tùy chỉnh (Nhập tên model)...":
                selected_deepseek_model = st.text_input("Tên model tùy chỉnh:", value="deepseek-flash", key="custom_deepseek_name")
            else:
                selected_deepseek_model = selected_ds_opt.split(" ")[0]

            if selected_deepseek_model == "deepseek-flash":
                st.caption("💵 **Giá rẻ nhất & Vision:** Cache Hit **$0.003 - $0.006**/1M | Input **$0.15 - $0.30**/1M | Output **$0.60 - $1.20**/1M.")
            elif selected_deepseek_model == "deepseek-v4-pro":
                st.caption("🚀 **Pro Flagship:** Cache Hit **$0.022 - $0.044**/1M | Input **$0.66 - $1.32**/1M | Output **$1.98 - $3.96**/1M (Không hỗ trợ Vision).")
            elif selected_deepseek_model == "deepseek-chat":
                st.caption("⚡ **Legacy V3 Alias:** Input **$0.14**/1M tokens ($0.014 nếu Cache Hit) | Output **$0.28**/1M tokens.")
            elif selected_deepseek_model == "deepseek-reasoner":
                st.caption("🧠 **Legacy R1 Alias:** Input **$0.55**/1M tokens | Output **$2.19**/1M tokens (kèm CoT Thinking).")

        st.markdown("---")

        # ----------------------------------------------------
        # 3. Generation Hyperparameters
        # ----------------------------------------------------
        st.markdown("### 🎛️ Tham số sinh nội dung")
        temperature = st.slider(
            "Nhiệt độ (Temperature)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.05,
            help="0.0: Logic, nhất quán, sự thật | 1.0+: Sáng tạo, phong phú",
        )

        top_p = st.slider(
            "Top-P (Nucleus Sampling)",
            min_value=0.0,
            max_value=1.0,
            value=0.95,
            step=0.05,
            help="Giới hạn phân phối xác suất các token được chọn",
        )

        max_tokens = st.slider(
            "Max Output Tokens",
            min_value=128,
            max_value=8192,
            value=2048,
            step=128,
            help="Độ dài tối đa của phản hồi trả về",
        )

        system_instruction = st.text_area(
            "System Instruction (Chỉ dẫn hệ thống)",
            value="Bạn là một trợ lý trí tuệ nhân tạo chuyên nghiệp, nhiệt tình và luôn trả lời bằng tiếng Việt rõ ràng, mạch lạc.",
            help="Định hình vai trò và nguyên tắc phản hồi của Gemini",
        )

        st.markdown("---")
        if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

        st.markdown(
            """
            <div style="font-size: 0.8rem; color: #94a3b8; text-align: center; margin-top: 20px;">
                Google GenAI SDK v2.33+<br>
                Made with ❤️ in Streamlit
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Resolve active keys
    active_key = api_key_input or get_env_api_key()
    active_deepseek_key = deepseek_key_input or get_env_deepseek_key()

    safety_settings = get_default_safety_settings() if GENAI_AVAILABLE else None

    client_config = types.GenerateContentConfig(
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_tokens,
        safety_settings=safety_settings,
        system_instruction=system_instruction.strip() if system_instruction.strip() else None,
    ) if GENAI_AVAILABLE else None

    return {
        "active_key": active_key,
        "active_deepseek_key": active_deepseek_key,
        "selected_model": selected_model,
        "selected_deepseek_model": selected_deepseek_model,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "system_instruction": system_instruction,
        "client_config": client_config,
    }
