"""
Chat View Module: Tab 1 - Interactive Chatbot with Gemini & DeepSeek streaming.
"""
import time
from typing import Dict, Any
import streamlit as st
from google.genai import types, errors

from modules.gemini_service import get_genai_client
from modules.deepseek_service import get_deepseek_client

try:
    from openai import AuthenticationError
except ImportError:
    class AuthenticationError(Exception):
        pass


def render_chat_tab(config: Dict[str, Any]) -> None:
    """
    Renders Tab 1: Chatbot conversation interface supporting both
    Google Gemini and DeepSeek AI with live streaming responses.
    """
    active_key = config.get("active_key", "")
    active_deepseek_key = config.get("active_deepseek_key", "")
    selected_model = config.get("selected_model", "gemini-3.5-flash")
    selected_deepseek_model = config.get("selected_deepseek_model", "deepseek-flash")
    temperature = config.get("temperature", 0.7)
    top_p = config.get("top_p", 0.95)
    max_tokens = config.get("max_tokens", 2048)
    system_instruction = config.get("system_instruction", "")
    client_config = config.get("client_config")

    col_c1, col_c2 = st.columns([2.5, 1.5])
    with col_c1:
        st.subheader("💬 Hội thoại tương tác với AI (Streaming)")
    with col_c2:
        chat_provider_choice = st.radio(
            "Chọn AI Provider:",
            ["✨ Google Gemini", "🐋 DeepSeek AI"],
            horizontal=True,
            key="chat_provider_selector"
        )
    
    current_model_label = selected_model if "Gemini" in chat_provider_choice else selected_deepseek_model
    st.markdown(
        f'<div style="text-align: right; margin-bottom: 10px;">'
        f'<span class="metric-chip">Provider: {"Google Gemini" if "Gemini" in chat_provider_choice else "DeepSeek AI"}</span>'
        f'<span class="metric-chip">Model: {current_model_label}</span>'
        f'<span class="metric-chip">Tin nhắn: {len(st.session_state.chat_messages)}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Prompt Starters (Quick Suggestion Buttons)
    if not st.session_state.chat_messages:
        st.markdown("##### 💡 Gợi ý câu hỏi bắt đầu nhanh:")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        starters = [
            ("✨ Giới thiệu Gemini", "Hãy giới thiệu ngắn gọn về các dòng mô hình Google Gemini 2.5 và ưu điểm nổi bật của chúng."),
            ("🐍 Code Python API", "Viết một đoạn code Python mẫu sử dụng thư viện google-genai để gọi model gemini-2.5-flash."),
            ("🚀 Kế hoạch học AI", "Lập kế hoạch lộ trình 3 tháng để từ người mới bắt đầu trở thành AI Application Developer."),
            ("📝 Viết email công việc", "Soạn giúp tôi một email xin nghỉ phép 2 ngày đi việc gia đình thật lịch sự và chuyên nghiệp.")
        ]
        
        cols = [col_s1, col_s2, col_s3, col_s4]
        for idx, (title, prompt_text) in enumerate(starters):
            with cols[idx]:
                if st.button(title, key=f"starter_{idx}", use_container_width=True):
                    st.session_state.starter_prompt = prompt_text
                    st.rerun()

    # Render previous messages
    for msg in st.session_state.chat_messages:
        role = msg["role"]
        provider = msg.get("provider", "gemini")
        avatar = "👤" if role == "user" else ("🐋" if provider == "deepseek" else "✨")
        with st.chat_message(role, avatar=avatar):
            if "reasoning" in msg and msg["reasoning"]:
                with st.expander("🧠 Suy luận DeepSeek-R1 (Chain of Thought)", expanded=False):
                    st.markdown(msg["reasoning"])
            st.markdown(msg["content"])
            if "time" in msg and msg["time"]:
                caption_text = f"⏱️ Thời gian phản hồi: {msg['time']:.2f}s"
                if "model" in msg and msg["model"]:
                    caption_text += f" | Model: `{msg['model']}`"
                st.caption(caption_text)

    # Chat Input logic
    chat_prompt = st.chat_input("Nhập câu hỏi hoặc yêu cầu của bạn...")
    
    # Check if a prompt was triggered by a starter button
    if st.session_state.starter_prompt:
        chat_prompt = st.session_state.starter_prompt
        st.session_state.starter_prompt = None

    if chat_prompt:
        is_deepseek_mode = "DeepSeek" in chat_provider_choice
        
        if is_deepseek_mode and not active_deepseek_key:
            st.error("⚠️ Vui lòng nhập DeepSeek API Key ở Sidebar trước khi trò chuyện!")
        elif not is_deepseek_mode and not active_key:
            st.error("⚠️ Vui lòng nhập Gemini API Key ở Sidebar trước khi trò chuyện!")
        else:
            # Append user message
            st.session_state.chat_messages.append({"role": "user", "content": chat_prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(chat_prompt)

            if is_deepseek_mode:
                # DeepSeek streaming response
                with st.chat_message("assistant", avatar="🐋"):
                    start_time = time.time()
                    full_response = ""
                    full_reasoning = ""
                    
                    reasoning_placeholder = None
                    if selected_deepseek_model in ["deepseek-reasoner", "deepseek-flash", "deepseek-v4-pro"]:
                        with st.expander("🧠 Quá trình suy luận (DeepSeek Thinking Mode...)", expanded=True):
                            reasoning_placeholder = st.empty()
                    
                    response_placeholder = st.empty()
                    
                    try:
                        client = get_deepseek_client(active_deepseek_key)
                        
                        ds_messages = []
                        if system_instruction.strip() and selected_deepseek_model != "deepseek-reasoner":
                            ds_messages.append({"role": "system", "content": system_instruction.strip()})
                            
                        for m in st.session_state.chat_messages:
                            m_role = m["role"]
                            if m_role in ["user", "assistant"]:
                                ds_messages.append({"role": m_role, "content": m["content"]})
                        
                        stream_params = {
                            "model": selected_deepseek_model,
                            "messages": ds_messages,
                            "stream": True,
                        }
                        if selected_deepseek_model != "deepseek-reasoner":
                            stream_params["temperature"] = temperature
                            stream_params["top_p"] = top_p
                            stream_params["max_tokens"] = max_tokens
                        else:
                            stream_params["max_tokens"] = max_tokens
                            
                        stream = client.chat.completions.create(**stream_params)
                        
                        for chunk in stream:
                            if not chunk.choices:
                                continue
                            choice = chunk.choices[0]
                            delta = choice.delta
                            
                            # Handle R1 reasoning_content
                            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                                full_reasoning += delta.reasoning_content
                                if reasoning_placeholder:
                                    reasoning_placeholder.markdown(full_reasoning + " ▌")
                                    
                            # Handle standard content
                            if hasattr(delta, "content") and delta.content:
                                full_response += delta.content
                                response_placeholder.markdown(full_response + " ▌")
                        
                        if reasoning_placeholder and full_reasoning:
                            reasoning_placeholder.markdown(full_reasoning)
                        response_placeholder.markdown(full_response)
                        
                        elapsed_time = time.time() - start_time
                        st.caption(f"⏱️ Phản hồi trong {elapsed_time:.2f}s | Model: `{selected_deepseek_model}` (DeepSeek AI)")
                        
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": full_response,
                            "reasoning": full_reasoning if full_reasoning else None,
                            "provider": "deepseek",
                            "model": selected_deepseek_model,
                            "time": elapsed_time
                        })
                    except AuthenticationError:
                        err = "❌ **Lỗi DeepSeek (401 Unauthorized)**: API Key không hợp lệ. Vui lòng kiểm tra lại tại platform.deepseek.com"
                        response_placeholder.markdown(err)
                        st.session_state.chat_messages.append({"role": "assistant", "content": err, "provider": "deepseek", "time": 0})
                    except Exception as e:
                        err = f"❌ **Lỗi DeepSeek API**: {str(e)}"
                        response_placeholder.markdown(err)
                        st.session_state.chat_messages.append({"role": "assistant", "content": err, "provider": "deepseek", "time": 0})
            else:
                # Generate Gemini response with streaming
                with st.chat_message("assistant", avatar="✨"):
                    response_placeholder = st.empty()
                    full_response = ""
                    start_time = time.time()

                    try:
                        client = get_genai_client(active_key)
                        
                        # Convert history to google.genai Content objects
                        history_contents = []
                        for m in st.session_state.chat_messages[:-1]:  # exclude the last user message
                            role = "user" if m["role"] == "user" else "model"
                            history_contents.append(
                                types.Content(
                                    role=role,
                                    parts=[types.Part.from_text(text=m["content"])]
                                )
                            )
                        
                        # Create chat session with history and send message stream
                        chat = client.chats.create(
                            model=selected_model,
                            config=client_config,
                            history=history_contents
                        )
                        
                        stream = chat.send_message_stream(chat_prompt)
                        
                        for chunk in stream:
                            chunk_text = getattr(chunk, "text", "") or ""
                            full_response += chunk_text
                            response_placeholder.markdown(full_response + " ▌")
                        
                        response_placeholder.markdown(full_response)
                        elapsed_time = time.time() - start_time
                        st.caption(f"⏱️ Phản hồi trong {elapsed_time:.2f}s | Model: `{selected_model}` (Google Gemini)")
                        
                        # Save assistant response to state
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": full_response,
                            "provider": "gemini",
                            "model": selected_model,
                            "time": elapsed_time
                        })

                    except errors.APIError as e:
                        error_msg = f"❌ **Lỗi Gemini API ({e.code})**: {e.message}"
                        response_placeholder.markdown(error_msg)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "provider": "gemini",
                            "time": 0
                        })
                    except Exception as e:
                        error_msg = f"❌ **Lỗi xảy ra**: {str(e)}"
                        response_placeholder.markdown(error_msg)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "provider": "gemini",
                            "time": 0
                        })
