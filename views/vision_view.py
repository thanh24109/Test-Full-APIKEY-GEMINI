"""
Vision View Module: Tab 3 - Multimodal Vision Analysis (Gemini & DeepSeek).
"""
import time
from typing import Dict, Any
import streamlit as st
from PIL import Image
from google.genai import errors

from modules.gemini_service import get_genai_client
from modules.deepseek_service import get_deepseek_client
from modules.doc_parsers import pil_image_to_base64_jpeg


def render_vision_tab(config: Dict[str, Any]) -> None:
    """
    Renders Tab 3: Multimodal Vision tab for analyzing images, OCR,
    chart analysis, and scene understanding with Gemini and DeepSeek.
    """
    active_key = config.get("active_key", "")
    active_deepseek_key = config.get("active_deepseek_key", "")
    selected_model = config.get("selected_model", "gemini-3.5-flash")
    selected_deepseek_model = config.get("selected_deepseek_model", "deepseek-flash")
    temperature = config.get("temperature", 0.7)
    top_p = config.get("top_p", 0.95)
    max_tokens = config.get("max_tokens", 2048)
    client_config = config.get("client_config")

    col_vt1, col_vt2 = st.columns([2.5, 1.5])
    with col_vt1:
        st.subheader("🖼️ Phân tích Hình ảnh Đa phương thức (Multimodal Vision)")
        st.markdown(
            "Tải lên hình ảnh và đặt bất kỳ câu hỏi nào. Mô hình AI sẽ phân tích chi tiết, "
            "nhận diện vật thể, quét văn bản (OCR), hoặc suy luận nội dung."
        )
    with col_vt2:
        vision_engine_choice = st.radio(
            "Chọn Vision AI Provider:",
            ["✨ Google Gemini", "🐋 DeepSeek AI"],
            horizontal=True,
            key="vision_provider_selector"
        )
    
    col_v1, col_v2 = st.columns([1, 1], gap="large")
    
    with col_v1:
        uploaded_image = st.file_uploader(
            "Tải lên ảnh cần phân tích (PNG, JPG, JPEG, WEBP):",
            type=["png", "jpg", "jpeg", "webp"],
            help="Hỗ trợ tối đa 25MB"
        )
        
        pil_image = None
        if uploaded_image:
            pil_image = Image.open(uploaded_image)
            st.image(pil_image, caption=f"📸 {uploaded_image.name}", use_container_width=True)
            
            st.markdown("##### 🎯 Tác vụ gợi ý nhanh cho ảnh:")
            preset_map = {
                "Tùy chỉnh": "Hãy mô tả chi tiết những gì bạn nhìn thấy trong bức ảnh này.",
                "📝 Trích xuất toàn bộ văn bản (OCR) có trong ảnh": "Hãy đọc và trích xuất toàn bộ văn bản (OCR) có trong hình ảnh này một cách đầy đủ, chính xác nhất. Giữ nguyên tiếng Việt có dấu, toàn bộ câu chữ, các mục, đề mục, bảng biểu và dấu xuống dòng.",
                "🔍 Mô tả chi tiết toàn bộ nội dung bức ảnh này": "Hãy mô tả chi tiết, đầy đủ toàn bộ nội dung, bố cục, các thành phần chính và ý nghĩa của bức ảnh này.",
                "📊 Phân tích cấu trúc dữ liệu / biểu đồ / sơ đồ này": "Hãy phân tích chi tiết dữ liệu, biểu đồ, các con số và rút ra nhận xét quan trọng từ hình ảnh này.",
                "💡 Đánh giá thiết kế UI/UX và đề xuất điểm cải thiện": "Hãy phân tích thiết kế giao diện UI/UX trong hình ảnh này và đưa ra nhận xét, đề xuất cải thiện."
            }
            preset_options = list(preset_map.keys())
            selected_preset = st.radio("Chọn câu lệnh mẫu:", preset_options, index=1 if len(preset_options) > 1 else 0)
        else:
            st.info("👈 Hãy tải lên một hình ảnh ở khung bên trái để bắt đầu.")
            selected_preset = "Tùy chỉnh"
            preset_map = {"Tùy chỉnh": "Hãy mô tả chi tiết những gì bạn nhìn thấy trong bức ảnh này."}

    with col_v2:
        default_prompt = preset_map.get(selected_preset, "Hãy đọc và trích xuất toàn bộ văn bản (OCR) có trong ảnh.")
            
        vision_prompt = st.text_area(
            "Câu hỏi hoặc yêu cầu phân tích ảnh:",
            value=default_prompt,
            height=120
        )
        
        analyze_btn = st.button("🚀 Bắt đầu Phân tích Hình ảnh", type="primary", use_container_width=True)
        
        output_box = st.container()
        
        if analyze_btn:
            is_deepseek_vision = "DeepSeek" in vision_engine_choice
            
            if is_deepseek_vision and not active_deepseek_key:
                st.error("⚠️ Vui lòng nhập DeepSeek API Key ở Sidebar!")
            elif not is_deepseek_vision and not active_key:
                st.error("⚠️ Vui lòng nhập Gemini API Key ở Sidebar!")
            elif not pil_image:
                st.warning("⚠️ Vui lòng chọn hoặc tải lên một hình ảnh trước!")
            elif not vision_prompt.strip():
                st.warning("⚠️ Vui lòng nhập yêu cầu phân tích!")
            else:
                if is_deepseek_vision:
                    # DeepSeek Multimodal Vision
                    with st.spinner(f"🐋 DeepSeek ({selected_deepseek_model}) đang phân tích hình ảnh..."):
                        start_time = time.time()
                        full_vision_resp = ""
                        full_reasoning_resp = ""
                        
                        reasoning_placeholder = None
                        if selected_deepseek_model in ["deepseek-reasoner", "deepseek-flash", "deepseek-v4-pro"]:
                            with output_box.expander("🧠 Quá trình suy luận (DeepSeek Thinking Mode...)", expanded=True):
                                reasoning_placeholder = st.empty()
                        result_placeholder = output_box.empty()
                        
                        try:
                            client = get_deepseek_client(active_deepseek_key)
                            b64_img = pil_image_to_base64_jpeg(pil_image, quality=85, max_dim=1500)
                            
                            messages = [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": vision_prompt},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                                    ]
                                }
                            ]
                            
                            stream_kwargs = {
                                "model": selected_deepseek_model,
                                "messages": messages,
                                "stream": True
                            }
                            if selected_deepseek_model != "deepseek-reasoner":
                                stream_kwargs["temperature"] = temperature
                                stream_kwargs["top_p"] = top_p
                                stream_kwargs["max_tokens"] = max_tokens
                            else:
                                stream_kwargs["max_tokens"] = max_tokens
                                
                            stream = client.chat.completions.create(**stream_kwargs)
                            for chunk in stream:
                                if not chunk.choices:
                                    continue
                                delta = chunk.choices[0].delta
                                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                                    full_reasoning_resp += delta.reasoning_content
                                    if reasoning_placeholder:
                                        reasoning_placeholder.markdown(full_reasoning_resp + " ▌")
                                if hasattr(delta, "content") and delta.content:
                                    full_vision_resp += delta.content
                                    result_placeholder.markdown(full_vision_resp + " ▌")
                                    
                            if reasoning_placeholder and full_reasoning_resp:
                                reasoning_placeholder.markdown(full_reasoning_resp)
                            result_placeholder.markdown(full_vision_resp)
                            
                            elapsed = time.time() - start_time
                            st.session_state.last_vision_result = full_vision_resp
                            st.session_state.last_vision_time = elapsed
                            st.session_state.last_actual_model = selected_deepseek_model
                            st.success(f"✅ Hoàn thành phân tích hình ảnh bằng DeepSeek AI trong **{elapsed:.2f}s**!")
                            st.caption(f"⏱️ Thời gian: **{elapsed:.2f}s** | Model: `{selected_deepseek_model}` (DeepSeek AI)")
                            
                            st.download_button(
                                "📥 Tải kết quả OCR (.txt)",
                                data=full_vision_resp,
                                file_name="deepseek_ocr_result.txt",
                                mime="text/plain",
                                key="download_deepseek_ocr_btn"
                            )
                        except Exception as e:
                            st.error(f"❌ Lỗi DeepSeek Vision: {str(e)}")
                else:
                    # Google Gemini Vision
                    with st.spinner("✨ Gemini đang phân tích hình ảnh..."):
                        result_placeholder = output_box.empty()
                        start_time = time.time()
                        full_vision_resp = ""
                        finish_reason = None
                        actual_model_version = None
                        
                        try:
                            client = get_genai_client(active_key)
                            
                            # Step 1: Streaming
                            try:
                                response_stream = client.models.generate_content_stream(
                                    model=selected_model,
                                    contents=[pil_image, vision_prompt],
                                    config=client_config
                                )
                                for chunk in response_stream:
                                    chunk_text = ""
                                    try:
                                        if chunk.text:
                                            chunk_text = chunk.text
                                    except Exception:
                                        pass
                                    
                                    if not chunk_text and hasattr(chunk, "candidates") and chunk.candidates:
                                        c = chunk.candidates[0]
                                        if hasattr(c, "finish_reason") and c.finish_reason:
                                            finish_reason = c.finish_reason
                                        if hasattr(c, "content") and c.content and hasattr(c.content, "parts"):
                                            for p in c.content.parts:
                                                p_text = getattr(p, "text", "")
                                                if p_text:
                                                    chunk_text += p_text
                                    
                                    if getattr(chunk, "model_version", None):
                                        actual_model_version = chunk.model_version
                                    if chunk_text:
                                        full_vision_resp += chunk_text
                                        result_placeholder.markdown(full_vision_resp + " ▌")
                            except Exception:
                                pass
                            
                            # Step 2: Fallback to non-streaming if stream yielded no text
                            if not full_vision_resp.strip():
                                direct_resp = client.models.generate_content(
                                    model=selected_model,
                                    contents=[pil_image, vision_prompt],
                                    config=client_config
                                )
                                if direct_resp.text:
                                    full_vision_resp = direct_resp.text
                                if getattr(direct_resp, "model_version", None):
                                    actual_model_version = direct_resp.model_version
                                if hasattr(direct_resp, "candidates") and direct_resp.candidates:
                                    finish_reason = direct_resp.candidates[0].finish_reason
                            
                            elapsed = time.time() - start_time
                            
                            # Step 3: Render and persist output
                            if full_vision_resp.strip():
                                result_placeholder.markdown(full_vision_resp)
                                st.session_state.last_vision_result = full_vision_resp
                                st.session_state.last_vision_time = elapsed
                                st.session_state.last_actual_model = actual_model_version or selected_model
                                
                                info_msg = f"⏱️ Thời gian: **{elapsed:.2f}s** | Model chỉ định: `{selected_model}`"
                                if actual_model_version and actual_model_version != selected_model:
                                    info_msg += f" | ⚡ Model thực tế (Google Rerouted): `{actual_model_version}`"
                                st.success("✅ Hoàn thành phân tích!")
                                st.caption(info_msg)
                                
                                st.download_button(
                                    "📥 Tải kết quả OCR (.txt)",
                                    data=full_vision_resp,
                                    file_name="ocr_result.txt",
                                    mime="text/plain",
                                    key="download_ocr_btn"
                                )
                            else:
                                st.error(f"⚠️ Không nhận được phản hồi văn bản từ Gemini (Lý do: `{finish_reason}`).")
                                st.info("💡 **Gợi ý khắc phục:**\n"
                                        "- Tăng thanh trượt **Max Output Tokens** ở Sidebar lên 4096 hoặc 8192.\n"
                                        "- Chuyển sang model **`gemini-3.5-flash-lite`** hoặc **`gemini-3.8-flash`**.\n"
                                        "- Bấm lại nút **'🚀 Bắt đầu Phân tích Hình ảnh'**.")
                                
                        except errors.APIError as e:
                            st.error(f"❌ Lỗi Gemini API ({e.code}): {e.message}")
                        except Exception as e:
                            st.error(f"❌ Lỗi: {str(e)}")
                        
        elif st.session_state.get("last_vision_result"):
            output_box.markdown("##### 📄 Kết quả phân tích gần nhất:")
            output_box.markdown(st.session_state.last_vision_result)
            if st.session_state.get("last_vision_time"):
                output_box.caption(f"⏱️ Thời gian phản hồi: {st.session_state.last_vision_time:.2f}s")
            st.download_button(
                "📥 Tải kết quả OCR (.txt)",
                data=st.session_state.last_vision_result,
                file_name="ocr_result.txt",
                mime="text/plain",
                key="download_cached_ocr_btn"
            )
