"""
Docs View Module: Tab 6 - Documentation, Model Specs & API Guides.
Covers Google Gemini API, Gemini Live API, and DeepSeek API.
"""
import streamlit as st


def render_docs_tab() -> None:
    """
    Renders Tab 6: Comprehensive documentation, model comparison tables,
    and SDK implementation guidelines for Gemini and DeepSeek.
    """
    st.subheader("📚 Hướng dẫn Sử dụng & Quản lý AI API Key (Gemini & DeepSeek)")
    
    provider_doc_tab_gemini, provider_doc_tab_deepseek = st.tabs(["✨ Google Gemini API", "🐋 DeepSeek API"])
    
    with provider_doc_tab_gemini:
        col_d1, col_d2 = st.columns([1, 1], gap="large")
        
        with col_d1:
            st.markdown("""
            ### 🔑 Cách lấy Gemini API Key miễn phí (3 Bước)
            
            1. **Truy cập Google AI Studio**:
               - Mở liên kết: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
               - Đăng nhập bằng tài khoản Google.
            
            2. **Tạo API Key**:
               - Nhấn nút **"Create API key"**.
               - Chọn dự án Google Cloud hoặc tạo tự động dự án mới.
            
            3. **Lưu và Sử dụng**:
               - Sao chép chuỗi khóa API (bắt đầu bằng `AIzaSy...`).
               - Dán vào ô **Gemini API Key** ở Sidebar ứng dụng này và nhấn **"Lưu vào .env"**.
            
            ---
            ### 🛡️ Nguyên tắc Bảo mật API Key
            - **Không bao giờ commit file `.env` lên GitHub/GitLab public**. File `.gitignore` của dự án này đã tự động loại trừ `.env`.
            - Khi triển khai lên server hoặc Streamlit Cloud, hãy sử dụng **Secrets Management** (`st.secrets` hoặc biến môi trường hệ thống).
            """)

        with col_d2:
            st.markdown("""
            ### ⚡ Code Python Mẫu (Google GenAI SDK)
            """)
            sample_code_gemini = """from google import genai
from google.genai import types

# 1. Khởi tạo Client với API Key
client = genai.Client(api_key="AIzaSy...")

# 2. Gọi Model đơn giản
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Xin chào! Bạn có thể làm được gì?"
)
print(response.text)

# 3. Phản hồi Streaming (Thời gian thực)
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Kể một câu chuyện ngắn về robot AI."
):
    print(chunk.text, end="")
"""
            st.code(sample_code_gemini, language="python")
            
            st.markdown("""
            ### 📊 Bảng so sánh các Model Gemini phổ biến
            | Model | Ưu điểm chính | Token Context | Khuyên dùng cho |
            | :--- | :--- | :--- | :--- |
            | **gemini-3.6-flash** | Thế hệ mới nhất, tốc độ cực cao | 1M tokens | Chatbot, OCR văn bản, tác vụ thời gian thực |
            | **gemini-3.5-flash** | Cực nhanh, đa phương thức, chi phí thấp | 1M tokens | Web apps, đa phương thức hình ảnh & tài liệu |
            | **gemini-3.1-pro** | Suy luận phức tạp, giải toán & coding sâu | 2M tokens | Phân tích tài liệu lớn, refactor mã nguồn |

            ---
            ### 🎙️ Danh mục Model Gemini Live API (Thời gian thực & Giọng nói)
            | Model Live API | Chức năng chính | Output Modality | Điểm nổi bật |
            | :--- | :--- | :---: | :--- |
            | **`gemini-2.5-flash-native-audio-latest`** | Native Audio Dialog | `AUDIO` | Giọng nói tự nhiên nguyên bản 24kHz, độ trễ cực thấp |
            | **`gemini-3.1-flash-live-preview`** | Gemini 3 Flash Live | `AUDIO` | Tốc độ phản hồi hai chiều siêu nhanh |
            | **`gemini-3.5-live-translate-preview`** | Live Audio Translate | `AUDIO` | Dịch thuật giọng nói tức thì đa ngôn ngữ |
            | **`gemini-3.5-transcribe-live`** | Realtime Transcribe STT | `TEXT` | Bóc tách âm thanh sang chữ thời gian thực qua WebSocket |
            | **`gemini-3.8-live`** | Gemini 3.8 Live | `AUDIO` | Thế hệ mới nhất, tổng hợp thoại mượt mà |
            | **`gemini-3.8-live-extended-thinking`** | Live Extended Thinking | `AUDIO` | Suy luận sâu đa bước (Chain-of-Thought) kết hợp Live Voice |
            """)

        # Interactive Model List
        if st.session_state.available_models:
            st.markdown("---")
            st.markdown("### 📋 Danh sách các Model Gemini khả dụng trên API Key của bạn:")
            with st.expander(f"Xem tất cả {len(st.session_state.available_models)} model được API Key hỗ trợ", expanded=False):
                for m in st.session_state.available_models:
                    st.markdown(f"**`{m['id']}`** — *{m['display_name']}*")
                    if m['description']:
                        st.caption(m['description'])
                    st.caption(f"Input Token Limit: `{m['input_token_limit']}` | Output Token Limit: `{m['output_token_limit']}`")
                    st.write("")

    with provider_doc_tab_deepseek:
        col_ds_d1, col_ds_d2 = st.columns([1, 1], gap="large")
        
        with col_ds_d1:
            st.markdown("""
            ### 🔑 Cách lấy DeepSeek API Key (3 Bước)
            
            1. **Truy cập DeepSeek Platform**:
               - Mở liên kết: [https://platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)
               - Đăng ký tài khoản (hỗ trợ Google/Email/GitHub) và nhận ngay credit dùng thử miễn phí.
            
            2. **Tạo API Key**:
               - Chọn mục **API Keys** ở menu bên trái.
               - Nhấn **"Create new API key"**, đặt tên gợi nhớ và bấm Tạo.
            
            3. **Lưu và Sử dụng**:
               - Sao chép chuỗi khóa (bắt đầu bằng `sk-...`).
               - Dán vào ô **DeepSeek API Key** ở tab DeepSeek trong Sidebar và nhấn **"Lưu vào .env"**.
            
            ---
            ### 🌐 Tài liệu & Giao thức Tương thích
            - **Tài liệu chính thức:** [https://api-docs.deepseek.com/](https://api-docs.deepseek.com/)
            - **Bảng giá chi tiết:** [https://api-docs.deepseek.com/quick_start/pricing](https://api-docs.deepseek.com/quick_start/pricing)
            - **Endpoint tương thích OpenAI:** `https://api.deepseek.com`
            - **Quy định giờ Peak / Off-Peak (Giờ quốc tế UTC):**
              - **Peak Hours:** 01:00 – 04:00 và 06:00 – 10:00 UTC (Thứ 2 đến Thứ 6).
              - **Off-Peak Hours:** Toàn bộ các khung giờ còn lại (và cuối tuần) — **Giảm 50% chi phí!**
            """)

        with col_ds_d2:
            st.markdown("""
            ### ⚡ Code Python Mẫu (Sử dụng OpenAI SDK)
            """)
            sample_code_deepseek = """from openai import OpenAI

# 1. Khởi tạo Client tương thích DeepSeek
client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"
)

# 2. Gọi Model deepseek-flash (Rẻ nhất, hỗ trợ cả Vision & Thinking)
response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": "Bạn là trợ lý AI hữu ích."},
        {"role": "user", "content": "Tóm tắt ưu điểm của DeepSeek Flash."}
    ],
    stream=False
)
print(response.choices[0].message.content)

# 3. Phản hồi Streaming kèm Chain-of-Thought (Thinking Mode)
stream = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role": "user", "content": "Giải bài toán logic hóc búa..."}],
    stream=True
)

for chunk in stream:
    delta = chunk.choices[0].delta
    # Suy luận (Thinking Process)
    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
        print(f"[Thinking]: {delta.reasoning_content}", end="")
    # Nội dung câu trả lời
    if hasattr(delta, 'content') and delta.content:
        print(delta.content, end="")
"""
            st.code(sample_code_deepseek, language="python")
            
            st.markdown("""
            ### 📊 Bảng Model Details Chính Thức (Tài Liệu DeepSeek)
            | THÔNG SỐ | `deepseek-flash` (RẺ NHẤT) | `deepseek-v4-pro` |
            | :--- | :--- | :--- |
            | **Phiên bản (Model Version)** | **DeepSeek-V4.1-Flash-1017** | DeepSeek-V4-Pro-0813 |
            | **Thị giác (Vision OCR)** | **✓ Có hỗ trợ** | Không hỗ trợ |
            | **Thinking Mode (CoT)** | **✓ Hỗ trợ cả 2 chế độ** | **✓ Hỗ trợ cả 2 chế độ** |
            | **Context Length** | 1M tokens | 1M tokens |
            | **Max Output** | 384K tokens | 384K tokens |
            | **Cache Hit (Off-Peak)** | **$0.003 / 1M** ($0.006 Peak) | $0.022 / 1M ($0.044 Peak) |
            | **Cache Miss (Off-Peak)** | **$0.15 / 1M** ($0.30 Peak) | $0.66 / 1M ($1.32 Peak) |
            | **Output Tokens (Off-Peak)** | **$0.60 / 1M** ($1.20 Peak) | $1.98 / 1M ($3.96 Peak) |
            | **Concurrency Limit** | 2,500 kết nối đồng thời | 500 kết nối đồng thời |
            
            💡 *Ghi chú: `deepseek-chat` (V3) và `deepseek-reasoner` (R1) là các định danh thế hệ trước được DeepSeek duy trì làm alias tương thích ngược.*
            """)

