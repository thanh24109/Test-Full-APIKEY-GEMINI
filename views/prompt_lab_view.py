"""
Prompt Lab View Module: Tab 5 - Prompt Lab & Task Templates.
Includes Summarization, Translation, Code Generator, Structured JSON, and Freeform prompt.
"""
from typing import Dict, Any
import streamlit as st
from google.genai import errors

from modules.gemini_service import get_genai_client


def render_prompt_lab_tab(config: Dict[str, Any]) -> None:
    """
    Renders Tab 5: Prompt Lab & specialized task templates for Gemini.
    """
    active_key = config.get("active_key", "")
    selected_model = config.get("selected_model", "gemini-3.5-flash")
    client_config = config.get("client_config")

    st.subheader("⚡ Prompt Lab: Thử nghiệm Các Tác vụ Phổ biến")
    st.markdown("Chọn tác vụ chuyên biệt để kiểm thử khả năng xử lý ngôn ngữ và sinh nội dung có cấu trúc của Gemini.")
    
    task_type = st.selectbox(
        "Chọn loại tác vụ:",
        [
            "📝 Tóm tắt Văn bản Chuyên sâu (Summarization)",
            "🌐 Dịch thuật Đa ngôn ngữ (Translation)",
            "💻 Lập trình & Phân tích Code (Code Generator / Debugger)",
            "📊 Trích xuất Dữ liệu JSON có cấu trúc (Structured JSON Extraction)",
            "🧪 Tự do Thử nghiệm (Freeform Prompt)"
        ]
    )
    
    col_t1, col_t2 = st.columns([1, 1], gap="large")
    
    with col_t1:
        if "Tóm tắt" in task_type:
            input_text = st.text_area(
                "Đoạn văn bản cần tóm tắt:",
                height=250,
                value="Google Gemini là thế hệ mô hình ngôn ngữ lớn (LLM) và đa phương thức tiên tiến nhất của Google. Được phát triển từ đầu để có khả năng hiểu và kết hợp liền mạch nhiều loại thông tin khác nhau bao gồm văn bản, hình ảnh, âm thanh, video và mã nguồn. Gemini có các phiên bản như Ultra, Pro và Flash, trong đó Gemini 2.5 Flash được tối ưu hóa cho tốc độ phản hồi cực nhanh với chi phí thấp và khả năng suy luận vượt trội. Gemini API cung cấp cho lập trình viên khả năng tích hợp trí tuệ nhân tạo mạnh mẽ vào các ứng dụng một cách dễ dàng và bảo mật."
            )
            prompt_instruction = "Hãy tóm tắt đoạn văn bản trên thành 3 ý chính dạng gạch đầu dòng, kèm theo 1 câu kết luận ngắn gọn."
            
        elif "Dịch thuật" in task_type:
            target_lang = st.selectbox("Ngôn ngữ đích:", ["Tiếng Anh (English)", "Tiếng Nhật (日本語)", "Tiếng Hàn (한국어)", "Tiếng Pháp (Français)", "Tiếng Đức (Deutsch)", "Tiếng Trung (中文)"])
            input_text = st.text_area(
                "Đoạn văn cần dịch:",
                height=200,
                value="Xin chào, chúng tôi rất vui mừng được giới thiệu ứng dụng demo kết nối Google Gemini API. Hãy thoải mái trải nghiệm các tính năng thông minh!"
            )
            prompt_instruction = f"Hãy dịch đoạn văn bản sau sang {target_lang}. Giữ đúng ngữ điệu tự nhiên, chuyên nghiệp và chuẩn xác ngữ pháp."
            
        elif "Lập trình" in task_type:
            prog_lang = st.selectbox("Ngôn ngữ lập trình:", ["Python", "JavaScript / TypeScript", "SQL", "Go", "C# / .NET"])
            input_text = st.text_area(
                "Mô tả thuật toán / chức năng cần viết:",
                height=200,
                value="Viết hàm kiểm tra một chuỗi có phải là Palindrome (chuỗi đối xứng) hay không, bỏ qua khoảng trắng và không phân biệt chữ hoa thường. Kèm theo unit test."
            )
            prompt_instruction = f"Hãy viết mã nguồn hoàn chỉnh bằng ngôn ngữ {prog_lang} cho yêu cầu trên, có chú thích giải thích rõ ràng và các test case mẫu."
            
        elif "JSON" in task_type:
            input_text = st.text_area(
                "Dữ liệu văn bản tự do:",
                height=200,
                value="Nguyễn Văn A, 28 tuổi, kỹ sư phần mềm tại Hà Nội, kỹ năng: Python, PyTorch, Docker, email: vana@example.com. Trần Thị B, 25 tuổi, chuyên viên thiết kế UI/UX tại TP.HCM, kỹ năng: Figma, CSS, Design System, email: thib@example.com."
            )
            prompt_instruction = "Trích xuất thông tin trên thành một mảng đối tượng JSON hợp lệ chuẩn, bao gồm các trường: name, age, job_title, city, skills (mảng chuỗi), email. Chỉ trả về đúng cú pháp JSON hợp lệ, không giải thích thêm."
            
        else: # Freeform
            input_text = st.text_area("Nội dung prompt của bạn:", height=250, placeholder="Nhập bất kỳ câu lệnh nào...")
            prompt_instruction = ""

        run_task_btn = st.button("🚀 Thực thi Tác vụ", type="primary", use_container_width=True)

    with col_t2:
        st.markdown("##### 📤 Kết quả Đầu ra:")
        output_placeholder = st.empty()
        
        if run_task_btn:
            if not active_key:
                st.error("⚠️ Vui lòng nhập Gemini API Key ở Sidebar!")
            elif not input_text.strip():
                st.warning("⚠️ Vui lòng nhập nội dung đầu vào!")
            else:
                final_content = f"{prompt_instruction}\n\nNội dung:\n{input_text}" if prompt_instruction else input_text
                
                with st.spinner("Đang xử lý qua Gemini..."):
                    try:
                        client = get_genai_client(active_key)
                        
                        response_stream = client.models.generate_content_stream(
                            model=selected_model,
                            contents=final_content,
                            config=client_config
                        )
                        
                        accumulated = ""
                        for chunk in response_stream:
                            accumulated += getattr(chunk, "text", "") or ""
                            output_placeholder.markdown(accumulated + " ▌")
                        
                        output_placeholder.markdown(accumulated)
                        
                    except errors.APIError as e:
                        st.error(f"❌ Lỗi API ({e.code}): {e.message}")
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
