import time
import asyncio
from google import genai
from google.genai import types

from modules.audio_utils import pcm_to_wav, audio_to_pcm16, run_async_in_thread
from modules.gemini_service import get_genai_client

async def _execute_gemini_live_call(
    api_key: str,
    model: str,
    user_text: str = None,
    user_audio_bytes: bytes = None,
    voice_name: str = "Aoede",
    thinking_level: str = None,
    system_instruction: str = None,
    target_language_code: str = None,
    timeout_sec: float = 30.0
):
    """
    Connect to Gemini Live API WebSocket, stream inputs (audio/text),
    and collect streaming 24kHz native audio + bidirectional transcriptions.
    """
    client = genai.Client(api_key=api_key)
    
    # Determine response modality: Transcribe uses TEXT, voice models use AUDIO
    is_transcribe_model = ("transcribe" in model.lower())
    response_modalities = ["TEXT"] if is_transcribe_model else ["AUDIO"]
    
    # Voice Config
    speech_config = None
    if response_modalities == ["AUDIO"] and voice_name:
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        )
        
    # Extended Thinking Config
    thinking_config = None
    if "thinking" in model.lower():
        lvl = types.ThinkingLevel.MEDIUM
        if thinking_level == "LOW":
            lvl = types.ThinkingLevel.LOW
        elif thinking_level == "HIGH":
            lvl = types.ThinkingLevel.HIGH
        thinking_config = types.ThinkingConfig(thinking_level=lvl, include_thoughts=True)
        
    # Live Translate Config
    translation_config = None
    if "translate" in model.lower() and target_language_code:
        translation_config = types.TranslationConfig(
            target_language_code=target_language_code,
            echo_target_language=True
        )
        
    sys_content = None
    if system_instruction and system_instruction.strip():
        sys_content = types.Content(parts=[types.Part.from_text(text=system_instruction.strip())])
        
    config = types.LiveConnectConfig(
        response_modalities=response_modalities,
        speech_config=speech_config,
        thinking_config=thinking_config,
        translation_config=translation_config,
        output_audio_transcription=types.AudioTranscriptionConfig() if response_modalities == ["AUDIO"] else None,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        system_instruction=sys_content
    )
    
    pcm_chunks = []
    output_transcription_text = ""
    input_transcription_text = ""
    thought_text = ""
    model_turn_text = ""
    
    async with client.aio.live.connect(model=model, config=config) as session:
        # Case 1: Audio input
        if user_audio_bytes:
            pcm_in = audio_to_pcm16(user_audio_bytes, target_sr=16000)
            if pcm_in:
                chunk_size = 3200  # 100ms chunks
                for i in range(0, len(pcm_in), chunk_size):
                    chunk = pcm_in[i:i+chunk_size]
                    await session.send_realtime_input(
                        audio=types.Blob(mime_type="audio/pcm;rate=16000", data=chunk)
                    )
                    await asyncio.sleep(0.01)
                await session.send_realtime_input(audio_stream_end=True)
            if user_text and user_text.strip():
                await session.send_realtime_input(text=user_text.strip())
        # Case 2: Text input
        elif user_text and user_text.strip():
            await session.send_client_content(
                turns=types.Content(role="user", parts=[types.Part.from_text(text=user_text.strip())]),
                turn_complete=True
            )
        else:
            return False, "Không có dữ liệu âm thanh hoặc văn bản đầu vào.", {}
            
        async def collect_stream():
            nonlocal pcm_chunks, output_transcription_text, input_transcription_text, thought_text, model_turn_text
            async for resp in session.receive():
                if resp.server_content:
                    sc = resp.server_content
                    if sc.input_transcription and sc.input_transcription.text:
                        input_transcription_text += sc.input_transcription.text + " "
                    if sc.output_transcription and sc.output_transcription.text:
                        output_transcription_text += sc.output_transcription.text
                    if sc.model_turn:
                        for part in sc.model_turn.parts:
                            if part.thought and part.text:
                                thought_text += part.text
                            elif part.text and not part.thought:
                                model_turn_text += part.text
                            if part.inline_data and part.inline_data.data:
                                pcm_chunks.append(part.inline_data.data)
                    if sc.turn_complete:
                        break
                        
        await asyncio.wait_for(collect_stream(), timeout=timeout_sec)
        
    full_pcm = b"".join(pcm_chunks)
    wav_bytes = pcm_to_wav(full_pcm, sample_rate=24000) if full_pcm else b""
    duration_sec = (len(full_pcm) / 2) / 24000 if full_pcm else 0.0
    final_text = (output_transcription_text or model_turn_text).strip()
    
    stats = {
        "audio_wav": wav_bytes,
        "duration_sec": duration_sec,
        "pcm_bytes_count": len(full_pcm),
        "chunks_count": len(pcm_chunks),
        "output_text": final_text,
        "input_text": input_transcription_text.strip(),
        "thought_text": thought_text.strip(),
        "model": model,
        "voice": voice_name
    }
    return True, "", stats

def call_gemini_live(
    api_key: str,
    model: str,
    user_text: str = None,
    user_audio_bytes: bytes = None,
    voice_name: str = "Aoede",
    thinking_level: str = None,
    system_instruction: str = None,
    target_language_code: str = None,
    timeout_sec: float = 35.0
):
    """Synchronous wrapper to execute Gemini Live API call cleanly."""
    if not api_key:
        return False, "Vui lòng nhập và kiểm tra Gemini API Key ở Sidebar.", {}
    try:
        t0 = time.time()
        success, err, stats = run_async_in_thread(
            _execute_gemini_live_call,
            api_key=api_key,
            model=model,
            user_text=user_text,
            user_audio_bytes=user_audio_bytes,
            voice_name=voice_name,
            thinking_level=thinking_level,
            system_instruction=system_instruction,
            target_language_code=target_language_code,
            timeout_sec=timeout_sec
        )
        elapsed = time.time() - t0
        stats["elapsed_time"] = elapsed
        return success, err, stats
    except Exception as e:
        return False, f"Lỗi Gemini Live API: {str(e)}", {}

def transcribe_audio_multimodal(
    api_key: str,
    audio_bytes: bytes,
    mime_type: str = "audio/wav",
    model: str = "gemini-3.5-flash",
    prompt_mode: str = "verbatim"
):
    """Bóc tách âm thanh sang văn bản toàn diện bằng Gemini Multimodal Audio."""
    if not api_key:
        return False, "Vui lòng nhập Gemini API Key ở Sidebar.", {}
    try:
        t0 = time.time()
        client = get_genai_client(api_key)
        if prompt_mode == "summary":
            prompt = (
                "Hãy lắng nghe kỹ toàn bộ file âm thanh và thực hiện 2 nhiệm vụ:\n"
                "1. 📝 TÓM TẮT ĐIỀU HÀNH: Tóm lược các ý chính, kết luận, số liệu và hành động quan trọng nhất.\n"
                "2. 📄 BẢN GHI ĐẦY ĐỦ: Bóc tách lại nội dung chi tiết theo từng người nói hoặc từng phân đoạn chính."
            )
        else:
            prompt = (
                "Hãy chuyển đổi toàn bộ lời nói trong file âm thanh này thành văn bản chính xác 100% (Verbatim Speech-to-Text).\n"
                "- Giữ nguyên tiếng Việt có dấu chuẩn xác.\n"
                "- Ngắt câu, chia đoạn văn bản rõ ràng, hợp lý theo ngữ cảnh.\n"
                "- Nếu có nhiều người nói, hãy phân tách rõ từng người nói (ví dụ: Người 1:, Người 2:)."
            )
            
        part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        resp = client.models.generate_content(
            model=model,
            contents=[part, prompt]
        )
        elapsed = time.time() - t0
        text_out = resp.text.strip()
        stats = {
            "total_words": len(text_out.split()),
            "total_chars": len(text_out),
            "elapsed_time": elapsed,
            "model_used": model
        }
        return True, text_out, stats
    except Exception as e:
        return False, f"Lỗi bóc tách âm thanh: {str(e)}", {}
