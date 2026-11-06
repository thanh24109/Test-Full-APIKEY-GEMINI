"""
Live API View Module: Tab 2 - Gemini Live API (Voice & Realtime Audio Studio).
Includes Speech-to-Speech, Realtime STT, Live Translation, and Multi-turn Dialog.
Each mode features its own dedicated model selection dropdown and status indicators.
"""
import time
from typing import Dict, Any
import streamlit as st

from modules.live_api_service import call_gemini_live, transcribe_audio_multimodal


def render_live_api_tab(active_key: str) -> None:
    """
    Renders Tab 2: Gemini Live API Studio supporting bidirectional voice streaming,
    speech recognition (STT), speech translation, and multi-turn live dialogs.
    Every mode contains its own dedicated Model Selector and configuration controls.
    """
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <h3 style="margin: 0; display: inline-flex; align-items: center; gap: 10px;">
                    🎙️ Gemini Live API — Voice & Realtime Audio Studio
                </h3>
            </div>
            <div>
                <span class="live-badge"><span class="live-pulse-dot"></span> LIVE WEBSOCKET</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="voice-studio-card">
            <b>✨ Trải nghiệm thế hệ mô hình Gemini Live API mới nhất từ Google:</b><br>
            • Kết nối phiên làm việc hai chiều độ trễ cực thấp (Bidirectional WebSocket Streaming).<br>
            • Tiếp nhận âm thanh trực tiếp (Microphone / File), nhận diện giọng nói (STT), suy luận tư duy sâu (Extended Thinking CoT).<br>
            • Tạo phản hồi bằng giọng nói tự nhiên nguyên bản (Native PCM 24kHz Studio Quality) kèm văn bản phiên âm hai chiều đồng bộ.
        </div>
        """,
        unsafe_allow_html=True
    )

    if not active_key:
        st.warning("⚠️ **Vui lòng nhập Google Gemini API Key tại thanh bên trái (Sidebar) để kích hoạt tính năng Gemini Live API!**")

    # 1. Global Studio Controls: Prebuilt Voice & System Instruction
    col_live_v, col_live_meta = st.columns([1.5, 2.5], gap="large")
    
    with col_live_v:
        voice_options = [
            ("Aoede", "Aoede (Nữ - Trong trẻo, tự nhiên - Khuyên dùng)"),
            ("Kore", "Kore (Nữ - Dịu dàng, truyền cảm)"),
            ("Zephyr", "Zephyr (Nữ - Tươi sáng, vui tươi)"),
            ("Leda", "Leda (Nữ - Ấm áp, trò chuyện thân mật)"),
            ("Callirrhoe", "Callirrhoe (Nữ - Thư thái, nhẹ nhàng)"),
            ("Autonoe", "Autonoe (Nữ - Rõ ràng, hoạt bát)"),
            ("Puck", "Puck (Nam - Năng động, tự nhiên)"),
            ("Charon", "Charon (Nam - Trầm ấm, chuyên nghiệp)"),
            ("Fenrir", "Fenrir (Nam - Dứt khoát, mạnh mẽ)"),
            ("Orus", "Orus (Nam - Đĩnh đạc, đanh thép)"),
            ("Enceladus", "Enceladus (Nam - Trầm sâu, truyền cảm)"),
            ("custom", "Tùy chọn khác (Nhập tên giọng trong 30 giọng Google)...")
        ]
        selected_voice_tuple = st.selectbox(
            "🎙️ Giọng đọc AI toàn cục (Prebuilt Voice):",
            options=voice_options,
            format_func=lambda x: x[1],
            index=0,
            key="live_voice_selectbox",
            help="Danh mục Google Gemini Prebuilt Voices tổng hợp âm thanh tự nhiên chuẩn Studio 24kHz"
        )
        if selected_voice_tuple[0] == "custom":
            custom_voice_input = st.text_input(
                "Nhập tên giọng đọc Google (VD: Despina, Achernar, Sadachbia, Gacrux...):",
                value="Zephyr",
                key="custom_voice_name_input"
            ).strip()
            selected_voice_name = custom_voice_input if custom_voice_input else "Aoede"
        else:
            selected_voice_name = selected_voice_tuple[0]

    with col_live_meta:
        st.markdown(
            """
            <div style="margin-top: 18px;">
                <span class="metric-chip">⚡ Giao thức: WebSocket 2 chiều</span>
                <span class="metric-chip">🔊 Âm thanh: PCM 24kHz Studio</span>
                <span class="metric-chip">🎯 4 Chế độ Kiểm thử Độc lập</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.expander("🛠️ Cấu hình Chỉ dẫn Hệ thống (System Instruction) cho Live Voice", expanded=False):
        live_sys_prompt = st.text_area(
            "Hướng dẫn phong cách cho AI:",
            value="Bạn là trợ lý AI tiếng Việt thân thiện, phát âm rõ ràng, giao tiếp tự nhiên và giải thích súc tích, ngắn gọn.",
            key="live_system_instruction_input",
            height=70
        )

    st.markdown("---")

    # 2. Main Feature Mode Selector (4 Functional Modes)
    live_sub_mode = st.radio(
        "🎯 Chọn Chức năng Kiểm thử Live API:",
        [
            "🗣️ Chế độ 1: Hội thoại Giọng nói Trực tiếp (Speech-to-Speech & Voice Chat)",
            "📝 Chế độ 2: Chuyển Giọng nói thành Văn bản Realtime (Realtime STT / Transcribe Live)",
            "🌐 Chế độ 3: Dịch thuật Giọng nói Tức thì (Live Audio Translate)",
            "📞 Chế độ 4: Phiên Hội thoại AI Thời gian thực (Multi-turn Live Dialog Session)"
        ],
        horizontal=True,
        key="live_api_submode_radio"
    )

    # ========================================================
    # CHẾ ĐỘ 1: HỘI THOẠI GIỌNG NÓI TRỰC TIẾP
    # ========================================================
    if "Chế độ 1" in live_sub_mode:
        # Dedicated Model Selector for Mode 1
        col_c1_mod, col_c1_opt = st.columns([1.8, 1.2], gap="medium")
        with col_c1_mod:
            c1_model_options = [
                "gemini-2.5-flash-native-audio-latest — 🗣️ Native Audio Dialog (Khuyên dùng - 24kHz Studio)",
                "gemini-3.1-flash-live-preview — ⚡ Gemini 3 Flash Live (Tốc độ cao)",
                "gemini-3.8-live — 🚀 Gemini 3.8 Live (Thế hệ mới nhất)",
                "gemini-3.8-live-extended-thinking — 🧠 Gemini 3.8 Extended Thinking (Suy luận CoT)"
            ]
            selected_c1_opt = st.selectbox(
                "🤖 Chọn Model cho Chế độ 1 (Voice & Audio):",
                options=c1_model_options,
                index=0,
                key="c1_model_select",
                help="Chọn mô hình Live API để hội thoại trực tiếp bằng giọng nói 2 chiều"
            )
            c1_model_id = selected_c1_opt.split(" — ")[0].strip()

        with col_c1_opt:
            c1_thinking_level = "MEDIUM"
            if "extended-thinking" in c1_model_id:
                c1_thinking_level = st.select_slider(
                    "🧠 Mức độ Suy luận (Thinking Level):",
                    options=["LOW", "MEDIUM", "HIGH"],
                    value="MEDIUM",
                    key="c1_thinking_level",
                    help="AI sẽ suy luận logic trước khi phát âm thanh trả lời"
                )
            else:
                st.markdown(
                    f'<div style="margin-top: 26px;">'
                    f'<span class="metric-chip">Model: <b>{c1_model_id}</b></span>'
                    f'<span class="metric-chip">Đầu ra: <b>AUDIO 24kHz</b></span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

        col_c1_in, col_c1_out = st.columns([1, 1], gap="large")
        
        with col_c1_in:
            st.markdown("##### 📥 Đầu vào Âm thanh hoặc Văn bản:")
            input_method = st.radio(
                "Chọn hình thức tương tác:",
                ["🎙️ Nói qua Microphone", "📁 Tải lên tệp âm thanh", "✍️ Nhập câu hỏi văn bản"],
                horizontal=True,
                key="ch1_input_method"
            )
            
            c1_audio_bytes = None
            c1_text_prompt = ""
            
            if "Microphone" in input_method:
                st.caption("💡 Bấm vào nút Micro bên dưới, nói câu hỏi của bạn và bấm dừng để gửi:")
                mic_recorded = st.audio_input("Ghi âm giọng nói trực tiếp:", key="ch1_mic_input")
                if mic_recorded:
                    c1_audio_bytes = mic_recorded.getvalue()
                    st.caption(f"🎤 Đã thu âm: **{len(c1_audio_bytes)/1024:.1f} KB** ({mic_recorded.type})")
                    
                c1_extra_text = st.text_input("Ghi chú/câu hỏi bổ sung kèm theo âm thanh (tùy chọn):", key="ch1_extra_mic_text")
                if c1_extra_text.strip():
                    c1_text_prompt = c1_extra_text.strip()
                    
            elif "Tải lên" in input_method:
                uploaded_audio = st.file_uploader(
                    "Tải lên tệp âm thanh (WAV, MP3, M4A, OGG):",
                    type=["wav", "mp3", "m4a", "ogg"],
                    key="ch1_file_audio_upload"
                )
                if uploaded_audio:
                    c1_audio_bytes = uploaded_audio.getvalue()
                    st.audio(c1_audio_bytes, format=uploaded_audio.type)
                c1_file_prompt = st.text_input("Câu hỏi cần AI trả lời về tệp âm thanh này:", value="Hãy lắng nghe và phản hồi lại nội dung trong đoạn âm thanh này.", key="ch1_file_prompt")
                c1_text_prompt = c1_file_prompt
                
            else:
                c1_text_input = st.text_area(
                    "Nhập câu hỏi để nghe Gemini phản hồi bằng giọng nói:",
                    value="Xin chào bạn! Bạn có thể giới thiệu về khả năng xử lý giọng nói Live API của mình không?",
                    height=100,
                    key="ch1_text_area_input"
                )
                c1_text_prompt = c1_text_input
                
            # Quick Starters for Live Voice
            st.caption("💡 Gợi ý câu hỏi nhanh:")
            col_qs1, col_qs2 = st.columns(2)
            with col_qs1:
                if st.button("⛅ Thời tiết hôm nay thế nào?", key="btn_qs_weather", use_container_width=True):
                    c1_text_prompt = "Hãy đóng vai một trợ lý thời tiết và dự báo thời tiết một ngày đẹp trời bằng giọng nói ấm áp."
            with col_qs2:
                if st.button("🤖 Giới thiệu bản thân", key="btn_qs_intro", use_container_width=True):
                    c1_text_prompt = "Hãy giới thiệu về bản thân bạn, các mô hình Gemini Live API và ưu điểm của việc nói chuyện trực tiếp qua âm thanh."

            run_c1_btn = st.button(f"🚀 Gửi tới {c1_model_id} (Bắt đầu Hội thoại Live)", type="primary", use_container_width=True, key="btn_run_ch1")

        with col_c1_out:
            st.markdown("##### 📤 Phản hồi Giọng nói & Phiên âm:")
            c1_out_box = st.container()
            
            if run_c1_btn:
                if not active_key:
                    st.error("❌ Vui lòng nhập Gemini API Key ở Sidebar để tiếp tục.")
                elif not c1_audio_bytes and not c1_text_prompt.strip():
                    st.warning("⚠️ Vui lòng ghi âm giọng nói hoặc nhập câu hỏi trước khi gửi.")
                else:
                    with st.spinner(f"Đang kết nối WebSocket tới `{c1_model_id}` và truyền luồng âm thanh..."):
                        t_call_start = time.time()
                        success, err, stats = call_gemini_live(
                            api_key=active_key,
                            model=c1_model_id,
                            user_text=c1_text_prompt if c1_text_prompt.strip() else None,
                            user_audio_bytes=c1_audio_bytes,
                            voice_name=selected_voice_name,
                            thinking_level=c1_thinking_level,
                            system_instruction=live_sys_prompt
                        )
                        call_elapsed = time.time() - t_call_start
                        
                        if success:
                            stats["model"] = c1_model_id
                            st.session_state.last_live_audio_response = stats.get("audio_wav")
                            st.session_state.last_live_transcript = stats.get("output_text", "")
                            st.session_state.last_live_thought = stats.get("thought_text", "")
                            st.session_state.last_live_stats = stats
                            
                            st.success(f"✅ Đã nhận phản hồi từ **{c1_model_id}** trong **{call_elapsed:.2f} giây**!")
                            
                            dur = stats.get("duration_sec", 0.0)
                            chunks = stats.get("chunks_count", 0)
                            st.markdown(
                                f'<span class="metric-chip">⚡ Độ trễ: {call_elapsed:.2f}s</span>'
                                f'<span class="metric-chip">⏱️ Thời lượng audio: {dur:.2f}s</span>'
                                f'<span class="metric-chip">🎙️ Giọng: {selected_voice_name}</span>'
                                f'<span class="metric-chip">🤖 Model: {c1_model_id}</span>'
                                f'<span class="metric-chip">📦 Gói âm thanh: {chunks} chunks</span>',
                                unsafe_allow_html=True
                            )
                            
                            wav_data = stats.get("audio_wav")
                            if wav_data:
                                st.markdown("##### 🔊 Nghe phản hồi giọng nói của Gemini:")
                                st.audio(wav_data, format="audio/wav", autoplay=True)
                                
                                st.download_button(
                                    "📥 Tải tệp giọng nói phản hồi (.wav)",
                                    data=wav_data,
                                    file_name=f"gemini_live_{c1_model_id}.wav",
                                    mime="audio/wav",
                                    key="btn_dl_live_wav"
                                )
                                
                            if stats.get("input_text"):
                                st.markdown(
                                    f"""
                                    <div class="dialog-turn-user">
                                        <b>👤 Lời nói của bạn (Transcribed STT):</b><br>
                                        <span style="color: #e2e8f0;">{stats.get("input_text")}</span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                            if stats.get("output_text"):
                                st.markdown(
                                    f"""
                                    <div class="dialog-turn-ai">
                                        <b>🤖 Gemini nói:</b><br>
                                        <span style="color: #38bdf8; font-size: 1.05rem;">{stats.get("output_text")}</span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                            if stats.get("thought_text"):
                                with st.expander("🧠 Xem Quá trình Suy nghĩ Nội tâm của AI (Extended Thinking / CoT)", expanded=True):
                                    st.markdown(f"```text\n{stats.get('thought_text')}\n```")
                        else:
                            st.error(f"❌ {err}")
                            if "1007" in err or "modality" in err.lower():
                                st.info("💡 Lưu ý: Với tác vụ nhận diện văn bản STT thuần túy, hãy chuyển sang **Chế độ 2** (Chuyển giọng nói sang văn bản).")
                                
            elif st.session_state.get("last_live_audio_response"):
                wav_cached = st.session_state.get("last_live_audio_response")
                stats_cached = st.session_state.get("last_live_stats", {})
                
                c1_out_box.caption(f"⏱️ Phiên gần nhất | Model: `{stats_cached.get('model', c1_model_id)}` | Giọng: `{stats_cached.get('voice', selected_voice_name)}`")
                if wav_cached:
                    c1_out_box.audio(wav_cached, format="audio/wav")
                    c1_out_box.download_button(
                        "📥 Tải tệp giọng nói gần nhất (.wav)",
                        data=wav_cached,
                        file_name="gemini_live_response.wav",
                        mime="audio/wav",
                        key="btn_dl_live_wav_cached"
                    )
                if stats_cached.get("output_text"):
                    c1_out_box.markdown(
                        f"""
                        <div class="dialog-turn-ai">
                            <b>🤖 Gemini nói:</b><br>
                            <span style="color: #38bdf8;">{stats_cached.get("output_text")}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                c1_out_box.info("Phản hồi giọng nói và văn bản phiên âm của Gemini Live API sẽ hiển thị tại đây sau khi bạn gửi.")

    # ========================================================
    # CHẾ ĐỘ 2: CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN (REALTIME STT)
    # ========================================================
    elif "Chế độ 2" in live_sub_mode:
        # Dedicated Model Selector for Mode 2
        col_c2_mod, col_c2_opt = st.columns([1.8, 1.2], gap="medium")
        with col_c2_mod:
            c2_model_options = [
                "gemini-3.5-transcribe-live — ⚡ Live WebSocket STT (Chuyên dụng thời gian thực)",
                "gemini-3.5-flash — ✨ Multimodal Audio Flash (Bóc tách chi tiết & Định dạng)",
                "gemini-3.6-flash — 🚀 Gemini 3.6 Flash (Multimodal Audio thế hệ mới)",
                "gemini-3.1-flash-lite — 🪶 Gemini 3.1 Flash Lite (Siêu nhẹ, tốc độ cao)"
            ]
            selected_c2_opt = st.selectbox(
                "🤖 Chọn Model cho Chế độ 2 (Realtime STT):",
                options=c2_model_options,
                index=0,
                key="c2_model_select",
                help="Chọn mô hình nhận diện giọng nói và bóc tách thành văn bản (Speech-to-Text)"
            )
            c2_model_id = selected_c2_opt.split(" — ")[0].strip()

        with col_c2_opt:
            engine_label = "⚡ WebSocket Streaming" if "transcribe-live" in c2_model_id else "✨ Multimodal Audio API"
            st.markdown(
                f'<div style="margin-top: 26px;">'
                f'<span class="metric-chip">Model: <b>{c2_model_id}</b></span>'
                f'<span class="metric-chip">Cơ chế: <b>{engine_label}</b></span>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

        col_stt1, col_stt2 = st.columns([1, 1], gap="large")
        
        with col_stt1:
            st.markdown("##### 🎙️ Đầu vào Âm thanh cần Chuyển thành Văn bản:")
            stt_input_choice = st.radio(
                "Nguồn âm thanh:",
                ["🎙️ Ghi âm trực tiếp qua Micro", "📁 Tải lên tệp âm thanh (WAV, MP3, M4A, OGG)"],
                horizontal=True,
                key="stt_input_choice"
            )
            
            stt_audio_bytes = None
            stt_mime = "audio/wav"
            
            if "Micro" in stt_input_choice:
                st.caption("💡 Bấm vào nút Micro bên dưới, nói nội dung cần bóc tách văn bản:")
                stt_mic = st.audio_input("Ghi âm lời nói:", key="stt_mic_recorder")
                if stt_mic:
                    stt_audio_bytes = stt_mic.getvalue()
                    st.caption(f"🎤 Đã thu âm: **{len(stt_audio_bytes)/1024:.1f} KB**")
            else:
                stt_file = st.file_uploader(
                    "Tải lên tệp âm thanh bài giảng, cuộc họp, phỏng vấn:",
                    type=["wav", "mp3", "m4a", "ogg"],
                    key="stt_file_uploader"
                )
                if stt_file:
                    stt_audio_bytes = stt_file.getvalue()
                    stt_mime = stt_file.type or "audio/wav"
                    st.audio(stt_audio_bytes, format=stt_mime)
                    
            stt_format_style = st.radio(
                "Phong cách định dạng đầu ra:",
                ["📝 Verbatim (Nguyên văn từng từ có dấu)", "📋 Summary & Structured (Tóm tắt ý chính và chia mục)"],
                index=0,
                key="stt_format_style_radio"
            )
            
            run_stt_btn = st.button(f"📝 Bắt đầu Bóc tách STT với {c2_model_id}", type="primary", use_container_width=True, key="btn_run_stt")

        with col_stt2:
            st.markdown("##### 📄 Kết quả Văn bản Bóc tách (Speech-to-Text):")
            stt_out_box = st.container()
            
            if run_stt_btn:
                if not active_key:
                    st.error("❌ Vui lòng nhập Gemini API Key ở Sidebar để tiếp tục.")
                elif not stt_audio_bytes:
                    st.warning("⚠️ Vui lòng ghi âm qua Micro hoặc tải lên một tệp âm thanh.")
                else:
                    with st.spinner(f"Đang xử lý nhận diện giọng nói qua `{c2_model_id}`..."):
                        t0 = time.time()
                        if "transcribe-live" in c2_model_id:
                            success, err, stats = call_gemini_live(
                                api_key=active_key,
                                model=c2_model_id,
                                user_audio_bytes=stt_audio_bytes,
                                system_instruction="Transcribe speech accurately in Vietnamese with proper punctuation and capitalization."
                            )
                            elapsed = time.time() - t0
                            if success:
                                text_result = stats.get("output_text") or stats.get("input_text") or ""
                                if not text_result.strip():
                                    _, text_result, _ = transcribe_audio_multimodal(
                                        api_key=active_key,
                                        audio_bytes=stt_audio_bytes,
                                        mime_type=stt_mime,
                                        model="gemini-3.5-flash",
                                        prompt_mode="summary" if "Summary" in stt_format_style else "verbatim"
                                    )
                            else:
                                success, text_result, _ = transcribe_audio_multimodal(
                                    api_key=active_key,
                                    audio_bytes=stt_audio_bytes,
                                    mime_type=stt_mime,
                                    model="gemini-3.5-flash",
                                    prompt_mode="summary" if "Summary" in stt_format_style else "verbatim"
                                )
                                err = ""
                        else:
                            success, text_result, stats = transcribe_audio_multimodal(
                                api_key=active_key,
                                audio_bytes=stt_audio_bytes,
                                mime_type=stt_mime,
                                model=c2_model_id,
                                prompt_mode="summary" if "Summary" in stt_format_style else "verbatim"
                            )
                            elapsed = time.time() - t0
                            
                        if success and text_result:
                            st.session_state.last_stt_result = text_result
                            w_cnt = len(text_result.split())
                            c_cnt = len(text_result)
                            st.session_state.last_stt_stats = {"words": w_cnt, "chars": c_cnt, "time": elapsed, "model": c2_model_id}
                            
                            st.success(f"✅ Bóc tách giọng nói thành công bằng **{c2_model_id}** trong **{elapsed:.2f} giây**!")
                            st.markdown(
                                f'<span class="metric-chip">⚡ Thời gian: {elapsed:.2f}s</span>'
                                f'<span class="metric-chip">🤖 Model: {c2_model_id}</span>'
                                f'<span class="metric-chip">📝 Từ: {w_cnt:,}</span>'
                                f'<span class="metric-chip">🔤 Ký tự: {c_cnt:,}</span>',
                                unsafe_allow_html=True
                            )
                            
                            st.text_area("Văn bản bóc tách:", value=text_result, height=260, key="stt_result_textarea")
                            
                            col_dl_t1, col_dl_t2 = st.columns(2)
                            with col_dl_t1:
                                st.download_button(
                                    "📥 Tải tệp văn bản (.txt)",
                                    data=text_result,
                                    file_name=f"transcription_{c2_model_id}.txt",
                                    mime="text/plain",
                                    key="btn_dl_stt_txt"
                                )
                            with col_dl_t2:
                                st.download_button(
                                    "📥 Tải tệp Markdown (.md)",
                                    data=f"# Bản ghi lời nói (Speech-to-Text - {c2_model_id})\n\n{text_result}",
                                    file_name=f"transcription_{c2_model_id}.md",
                                    mime="text/markdown",
                                    key="btn_dl_stt_md"
                                )
                        else:
                            st.error(f"❌ {err or 'Không nhận diện được nội dung âm thanh hoặc tệp bị rỗng.'}")
            elif st.session_state.get("last_stt_result"):
                cached_stt = st.session_state.get("last_stt_result")
                cached_stt_stats = st.session_state.get("last_stt_stats", {})
                stt_out_box.caption(f"⏱️ Lần chạy gần nhất: {cached_stt_stats.get('time', 0):.2f}s | Model: `{cached_stt_stats.get('model', c2_model_id)}` | Từ: {cached_stt_stats.get('words', 0)}")
                stt_out_box.text_area("Văn bản bóc tách gần nhất:", value=cached_stt, height=240, key="stt_cached_textarea")
                stt_out_box.download_button(
                    "📥 Tải tệp văn bản (.txt)",
                    data=cached_stt,
                    file_name="gemini_transcription.txt",
                    mime="text/plain",
                    key="btn_dl_cached_stt_txt"
                )
            else:
                stt_out_box.info("Văn bản sau khi nhận diện giọng nói sẽ hiển thị tại đây.")

    # ========================================================
    # CHẾ ĐỘ 3: DỊCH THUẬT GIỌNG NÓI TỨC THÌ (LIVE TRANSLATE)
    # ========================================================
    elif "Chế độ 3" in live_sub_mode:
        # Dedicated Model Selector for Mode 3
        col_c3_mod, col_c3_opt = st.columns([1.8, 1.2], gap="medium")
        with col_c3_mod:
            c3_model_options = [
                "gemini-3.5-live-translate-preview — 🌐 Live Translate Preview (Chuyên dụng dịch thoại trực tiếp)",
                "gemini-2.5-flash-native-audio-latest — 🗣️ Native Audio Dialog + Prompt dịch thuật",
                "gemini-3.1-flash-live-preview — ⚡ Gemini 3 Flash Live + Prompt dịch thuật",
                "gemini-3.8-live — 🚀 Gemini 3.8 Live + Prompt dịch thuật"
            ]
            selected_c3_opt = st.selectbox(
                "🤖 Chọn Model cho Chế độ 3 (Live Audio Translate):",
                options=c3_model_options,
                index=0,
                key="c3_model_select",
                help="Chọn mô hình dịch thuật giọng nói thời gian thực"
            )
            c3_model_id = selected_c3_opt.split(" — ")[0].strip()

        with col_c3_opt:
            st.markdown(
                f'<div style="margin-top: 26px;">'
                f'<span class="metric-chip">Model: <b>{c3_model_id}</b></span>'
                f'<span class="metric-chip">Chức năng: <b>Dịch giọng nói trực tiếp</b></span>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

        col_tr1, col_tr2 = st.columns([1, 1], gap="large")
        
        with col_tr1:
            st.markdown("##### 🌐 Cấu hình Dịch thuật Giọng nói:")
            
            col_lg1, col_lg2 = st.columns(2)
            with col_lg1:
                st.selectbox(
                    "Ngôn ngữ nguồn (Nói):",
                    ["🇻🇳 Tiếng Việt", "🇬🇧 Tiếng Anh (English)", "🇯🇵 Tiếng Nhật", "🇰🇷 Tiếng Hàn", "🇨🇳 Tiếng Trung"],
                    index=0,
                    key="tr_src_lang_select"
                )
            with col_lg2:
                tr_tgt_lang_dict = {
                    "en": "🇬🇧 Tiếng Anh (English)",
                    "vi": "🇻🇳 Tiếng Việt (Vietnamese)",
                    "ja": "🇯🇵 Tiếng Nhật (Japanese)",
                    "ko": "🇰🇷 Tiếng Hàn (Korean)",
                    "zh": "🇨🇳 Tiếng Trung (Chinese)",
                    "fr": "🇫🇷 Tiếng Pháp (French)",
                    "de": "🇩🇪 Tiếng Đức (German)"
                }
                tr_tgt_code = st.selectbox(
                    "Ngôn ngữ đích (Dịch sang & Phát âm):",
                    options=list(tr_tgt_lang_dict.keys()),
                    format_func=lambda k: tr_tgt_lang_dict[k],
                    index=0,
                    key="tr_tgt_code_select"
                )
                
            tr_input_mode = st.radio("Cách thức nhập:", ["🎙️ Nói qua Micro", "✍️ Nhập câu cần dịch"], horizontal=True, key="tr_input_mode_radio")
            
            tr_audio_bytes = None
            tr_text_input = ""
            
            if "Micro" in tr_input_mode:
                st.caption("💡 Bấm nút Micro và nói câu cần dịch:")
                tr_mic = st.audio_input("Nói để dịch tức thì:", key="tr_mic_input")
                if tr_mic:
                    tr_audio_bytes = tr_mic.getvalue()
            else:
                tr_text_input = st.text_area(
                    "Nhập câu tiếng Việt hoặc tiếng Anh cần dịch:",
                    value="Xin chào, rất vui được gặp bạn! Tôi đang thử nghiệm tính năng dịch thuật giọng nói thời gian thực.",
                    height=90,
                    key="tr_text_input_area"
                )
                
            run_trans_btn = st.button(f"🌐 Dịch & Phát Giọng nói với {c3_model_id}", type="primary", use_container_width=True, key="btn_run_trans")

        with col_tr2:
            st.markdown("##### 🔊 Bản dịch & Phát âm Giọng nói Chuẩn:")
            tr_out_box = st.container()
            
            if run_trans_btn:
                if not active_key:
                    st.error("❌ Vui lòng nhập Gemini API Key ở Sidebar để tiếp tục.")
                elif not tr_audio_bytes and not tr_text_input.strip():
                    st.warning("⚠️ Vui lòng ghi âm hoặc nhập câu cần dịch.")
                else:
                    tgt_name = tr_tgt_lang_dict.get(tr_tgt_code, tr_tgt_code)
                    sys_trans_prompt = (
                        f"You are a professional realtime voice translator. "
                        f"Translate the user's speech or text directly into {tgt_name}. "
                        f"Respond with the spoken translation in natural, fluent pronunciation. "
                        f"Do not add commentary, just translate accurately."
                    )
                    
                    with st.spinner(f"Đang dịch và tổng hợp giọng nói sang {tgt_name} bằng `{c3_model_id}`..."):
                        t0 = time.time()
                        success, err, stats = call_gemini_live(
                            api_key=active_key,
                            model=c3_model_id,
                            user_text=tr_text_input if tr_text_input.strip() else None,
                            user_audio_bytes=tr_audio_bytes,
                            voice_name=selected_voice_name,
                            system_instruction=sys_trans_prompt,
                            target_language_code=tr_tgt_code
                        )
                        elapsed = time.time() - t0
                        
                        if success:
                            stats["model"] = c3_model_id
                            st.session_state.last_translate_audio = stats.get("audio_wav")
                            st.session_state.last_translate_text = stats.get("output_text", "")
                            
                            st.success(f"✅ Dịch thành công sang **{tgt_name}** bằng **{c3_model_id}** trong **{elapsed:.2f} giây**!")
                            st.markdown(
                                f'<span class="metric-chip">⚡ Thời gian: {elapsed:.2f}s</span>'
                                f'<span class="metric-chip">🤖 Model: {c3_model_id}</span>'
                                f'<span class="metric-chip">🎯 Ngôn ngữ đích: {tgt_name}</span>',
                                unsafe_allow_html=True
                            )
                            
                            wav_tr = stats.get("audio_wav")
                            if wav_tr:
                                st.markdown("##### 🔊 Nghe câu dịch phát âm bản ngữ:")
                                st.audio(wav_tr, format="audio/wav", autoplay=True)
                                st.download_button(
                                    "📥 Tải tệp âm thanh bản dịch (.wav)",
                                    data=wav_tr,
                                    file_name=f"translated_{c3_model_id}_{tr_tgt_code}.wav",
                                    mime="audio/wav",
                                    key="btn_dl_tr_wav"
                                )
                                
                            if stats.get("input_text"):
                                st.markdown(f"**👤 Bản gốc đã nói:** `{stats.get('input_text')}`")
                            st.markdown(
                                f"""
                                <div class="dialog-turn-ai">
                                    <b>🌐 Bản dịch ({tgt_name}):</b><br>
                                    <span style="color: #38bdf8; font-size: 1.15rem; font-weight: 600;">{stats.get("output_text")}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.error(f"❌ {err}")
            elif st.session_state.get("last_translate_audio"):
                wav_cached = st.session_state.get("last_translate_audio")
                text_cached = st.session_state.get("last_translate_text", "")
                tr_out_box.caption(f"⏱️ Phiên gần nhất | Model: `{c3_model_id}`")
                tr_out_box.audio(wav_cached, format="audio/wav")
                if text_cached:
                    tr_out_box.markdown(
                        f"""
                        <div class="dialog-turn-ai">
                            <b>🌐 Bản dịch gần nhất:</b><br>
                            <span style="color: #38bdf8; font-size: 1.1rem;">{text_cached}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                tr_out_box.info("Bản dịch âm thanh và văn bản sẽ xuất hiện tại đây sau khi bạn bấm Dịch.")

    # ========================================================
    # CHẾ ĐỘ 4: PHIÊN HỘI THOẠI AI THỜI GIAN THỰC (MULTI-TURN)
    # ========================================================
    else:
        # Dedicated Model Selector for Mode 4
        col_c4_mod, col_c4_opt = st.columns([1.8, 1.2], gap="medium")
        with col_c4_mod:
            c4_model_options = [
                "gemini-3.8-live-extended-thinking — 🧠 Gemini 3.8 Extended Thinking (Suy luận sâu CoT từng lượt - Khuyên dùng)",
                "gemini-2.5-flash-native-audio-latest — 🗣️ Native Audio Dialog (Đàm thoại liên tục tự nhiên)",
                "gemini-3.1-flash-live-preview — ⚡ Gemini 3 Flash Live (Phản hồi siêu tốc)",
                "gemini-3.8-live — 🚀 Gemini 3.8 Live (Thế hệ mới nhất)"
            ]
            selected_c4_opt = st.selectbox(
                "🤖 Chọn Model cho Chế độ 4 (Multi-turn Live Dialog):",
                options=c4_model_options,
                index=0,
                key="c4_model_select",
                help="Chọn mô hình duy trì phiên hội thoại thoại liên tục nhiều lượt"
            )
            c4_model_id = selected_c4_opt.split(" — ")[0].strip()

        with col_c4_opt:
            c4_thinking_level = "MEDIUM"
            if "extended-thinking" in c4_model_id:
                c4_thinking_level = st.select_slider(
                    "🧠 Mức độ Suy luận (Thinking Level):",
                    options=["LOW", "MEDIUM", "HIGH"],
                    value="MEDIUM",
                    key="c4_thinking_level",
                    help="AI sẽ suy nghĩ đa bước (Chain-of-Thought) cho từng lượt thoại"
                )
            else:
                st.markdown(
                    f'<div style="margin-top: 26px;">'
                    f'<span class="metric-chip">Model: <b>{c4_model_id}</b></span>'
                    f'<span class="metric-chip">Chế độ: <b>Đàm thoại Đa lượt</b></span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

        st.markdown("##### 📞 Phiên Hội thoại Thoại Đa lượt (Multi-turn Live Dialog):")
        st.caption("Trò chuyện liên tục với Gemini như một cuộc gọi thoại trực tiếp. Mỗi câu trả lời của AI sẽ phát âm thanh và hiển thị phiên âm.")
        
        dialog_history = st.session_state.live_dialog_history
        if dialog_history:
            for idx, turn in enumerate(dialog_history):
                role = turn.get("role")
                if role == "user":
                    st.markdown(
                        f"""
                        <div class="dialog-turn-user">
                            <b>👤 Bạn:</b> {turn.get("text", "")}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if turn.get("audio"):
                        st.audio(turn.get("audio"), format="audio/wav")
                else:
                    turn_model_label = turn.get("model", c4_model_id)
                    st.markdown(
                        f"""
                        <div class="dialog-turn-ai">
                            <b>🤖 Gemini ({turn_model_label} — {turn.get("voice", selected_voice_name)}):</b><br>
                            <span style="color: #38bdf8; font-size: 1.05rem;">{turn.get("text", "")}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if turn.get("audio"):
                        st.audio(turn.get("audio"), format="audio/wav")
                    if turn.get("thought"):
                        with st.expander(f"🧠 Tư duy lượt {idx // 2 + 1} ({turn_model_label})", expanded=False):
                            st.text(turn.get("thought"))
        else:
            st.info("Chưa có lượt hội thoại nào trong phiên này. Hãy bắt đầu nói chuyện với Gemini ở khung bên dưới!")

        col_nt1, col_nt2 = st.columns([3, 1], gap="medium")
        with col_nt1:
            nt_input_type = st.radio("Cách thức phản hồi:", ["🎙️ Nói qua Micro", "✍️ Nhập văn bản"], horizontal=True, key="nt_input_type_radio")
            nt_audio = None
            nt_text = ""
            if "Micro" in nt_input_type:
                nt_mic_val = st.audio_input("Nói lượt tiếp theo:", key="nt_mic_recorder")
                if nt_mic_val:
                    nt_audio = nt_mic_val.getvalue()
            else:
                nt_text = st.text_input("Nhập tin nhắn tiếp theo:", key="nt_text_input_field", placeholder="Ví dụ: Bạn có thể giải thích chi tiết hơn được không?")
                
        with col_nt2:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            send_nt_btn = st.button(f"💬 Gửi tới {c4_model_id}", type="primary", use_container_width=True, key="btn_send_next_turn")
            clear_nt_btn = st.button("🧹 Xóa lịch sử phiên", use_container_width=True, key="btn_clear_live_dialog")
            
        if clear_nt_btn:
            st.session_state.live_dialog_history = []
            st.success("Đã làm mới phiên hội thoại thoại!")
            st.rerun()
            
        if send_nt_btn:
            if not active_key:
                st.error("❌ Vui lòng nhập Gemini API Key ở Sidebar để tiếp tục.")
            elif not nt_audio and not nt_text.strip():
                st.warning("⚠️ Vui lòng nói qua Micro hoặc nhập tin nhắn trước khi gửi.")
            else:
                with st.spinner(f"Gemini ({c4_model_id}) đang lắng nghe và phản hồi bằng giọng nói ({selected_voice_name})..."):
                    context_prompt = live_sys_prompt + "\n\nĐây là phiên hội thoại thoại tiếp nối. Hãy trả lời tự nhiên, thân thiện và súc tích."
                    if dialog_history:
                        history_summary = "Lịch sử trò chuyện trước đó:\n"
                        for h in dialog_history[-4:]:
                            history_summary += f"{'Người dùng' if h['role']=='user' else 'Gemini'}: {h.get('text', '')}\n"
                        context_prompt += "\n" + history_summary
                        
                    success, err, stats = call_gemini_live(
                        api_key=active_key,
                        model=c4_model_id,
                        user_text=nt_text if nt_text.strip() else None,
                        user_audio_bytes=nt_audio,
                        voice_name=selected_voice_name,
                        thinking_level=c4_thinking_level,
                        system_instruction=context_prompt
                    )
                    
                    if success:
                        user_spoken_label = stats.get("input_text") or nt_text or "Tin nhắn thoại"
                        st.session_state.live_dialog_history.append({
                            "role": "user",
                            "text": user_spoken_label,
                            "audio": nt_audio
                        })
                        st.session_state.live_dialog_history.append({
                            "role": "model",
                            "text": stats.get("output_text", ""),
                            "audio": stats.get("audio_wav"),
                            "thought": stats.get("thought_text", ""),
                            "voice": selected_voice_name,
                            "model": c4_model_id
                        })
                        st.rerun()
                    else:
                        st.error(f"❌ {err}")
