import io
import wave
import asyncio
import concurrent.futures

try:
    import pydub
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

def pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
    """Convert raw 16-bit PCM bytes from Gemini Live API into a standard WAV audio file."""
    if not pcm_bytes:
        return b""
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return wav_io.getvalue()

def audio_to_pcm16(audio_bytes: bytes, target_sr: int = 16000) -> bytes:
    """Convert input audio (WAV, MP3, M4A, OGG) to 16-bit 16kHz mono PCM for Gemini Live API."""
    if not audio_bytes:
        return b""
    if PYDUB_AVAILABLE:
        try:
            seg = pydub.AudioSegment.from_file(io.BytesIO(audio_bytes))
            seg = seg.set_frame_rate(target_sr).set_channels(1).set_sample_width(2)
            return seg.raw_data
        except Exception:
            pass
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            return wf.readframes(wf.getnframes())
    except Exception:
        return b""

def run_async_in_thread(coro_fn, *args, **kwargs):
    """Safely execute an asynchronous coroutine in an isolated thread with a fresh event loop."""
    def runner():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coro_fn(*args, **kwargs))
        finally:
            new_loop.close()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(runner).result()

