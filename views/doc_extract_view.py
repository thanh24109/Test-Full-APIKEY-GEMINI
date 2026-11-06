"""
Document Extraction View Module: Tab 4 - Document Intelligence (PDF & DOCX).
Supports 5 extraction modes:
1. Local Parser (pypdf & python-docx - Fast, 0 Quota)
2. Microsoft MarkItDown (Markdown layout)
3. Docling AI (IBM Research)
4. DeepSeek Multimodal VLM (OCR Scan & Table Extraction)
5. Google Gemini AI (Multimodal VLM)
"""
import os
import io
import time
from pathlib import Path
from typing import Dict, Any
import streamlit as st
from PIL import Image
from google.genai import types, errors

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None

try:
    from openai import AuthenticationError
except ImportError:
    class AuthenticationError(Exception):
        pass

from modules.doc_parsers import (
    extract_docx_content,
    get_pdf_metadata,
    pil_image_to_base64_jpeg,
    render_pdf_to_vlm_images,
    extract_pdf_full_local,
    extract_docx_full_local,
    extract_with_markitdown,
    extract_with_docling,
    MARKITDOWN_AVAILABLE,
    DOCLING_AVAILABLE,
    PDFIUM_AVAILABLE,
)
from modules.gemini_service import get_genai_client
from modules.deepseek_service import get_deepseek_client


def render_doc_extract_tab(config: Dict[str, Any]) -> None:
    """
    Renders Tab 4: Comprehensive document extraction & analysis across 5 modes.
    """
    active_key = config.get("active_key", "")
    active_deepseek_key = config.get("active_deepseek_key", "")
    selected_model = config.get("selected_model", "gemini-3.5-flash")
    selected_deepseek_model = config.get("selected_deepseek_model", "deepseek-flash")
    temperature = config.get("temperature", 0.7)
    top_p = config.get("top_p", 0.95)
    max_tokens = config.get("max_tokens", 2048)
    client_config = config.get("client_config")

    st.subheader("📄 Trích xuất & Phân tích Tài liệu (PDF & Microsoft Word .docx)")
    
    # Mode selector at top
    col_mode_sel, col_mode_info = st.columns([1.7, 1.3], gap="medium")
    with col_mode_sel:
        extraction_mode = st.radio(
            "🛠️ Chọn phương thức trích xuất:",
            [
                "⚡ Chế độ 1: Trích xuất thông thường (Local Parser - Miễn phí, Tức thì, Không tốn Quota)",
                "📑 Chế độ 2: Microsoft MarkItDown (Thư viện chuẩn của Microsoft - Chuyển sang Markdown)",
                "🦆 Chế độ 3: Docling (Thư viện chuẩn của IBM - Chuyển sang Markdown)",
                "🐋 Chế độ 4: DeepSeek AI (Multimodal VLM - OCR Scan, Bảng biểu, Tóm tắt & Q&A)",
                "✨ Chế độ 5: Google Gemini AI (Multimodal VLM - OCR Scan, Bảng biểu, Tóm tắt & Q&A)"
            ],
            index=2,
            horizontal=False
        )
    with col_mode_info:
        if "thông thường" in extraction_mode:
            st.info(
                "⚡ **Đặc điểm Trích xuất Thông thường:**\n"
                "- Chạy 100% offline trên máy (engine `pypdf` & `python-docx`).\n"
                "- **Tốc độ:** ~0.02 giây (tức thì), không cần internet.\n"
                "- **Chi phí:** Miễn phí 100%, **không dùng API Key, không tốn Quota**.\n"
                "- Tự động bóc tách đoạn văn và **dựng lại Bảng biểu sang Markdown**."
            )
        elif "MarkItDown" in extraction_mode:
            st.info(
                "📑 **Đặc điểm Microsoft MarkItDown:**\n"
                "- Thư viện mã nguồn mở chuyên dụng từ Microsoft ([GitHub: microsoft/markitdown](https://github.com/microsoft/markitdown)).\n"
                "- **Đầu ra:** Định dạng **Markdown chuẩn** (`.md`), bảo toàn cấu trúc Header (`#`, `##`), danh sách & Bảng biểu (`|---|---|`).\n"
                "- **Định dạng hỗ trợ:** PDF, DOCX, PPTX, XLSX, HTML...\n"
                "- **Ưu điểm:** Chạy 100% offline, **0 Quota, 0 API Key, tốc độ cao, an toàn dữ liệu**.\n"
                "- ⚠️ **Lưu ý PDF:** Trích xuất văn bản số trực tiếp. Với **tài liệu scan từ giấy hoặc ảnh chụp** (không có text layer), vui lòng chọn **Chế độ 4 (DeepSeek AI)** hoặc **Chế độ 5 (Gemini AI)** để OCR thị giác."
            )
        elif "Docling" in extraction_mode:
            st.info(
                "🦆 **Đặc điểm Docling (DS4SD / IBM Research):**\n"
                "- Thư viện chuẩn mã nguồn mở từ IBM Research ([GitHub: docling-project/docling](https://github.com/docling-project/docling)).\n"
                "- **Đầu ra:** Định dạng **Markdown chuẩn** (`.md`), phân tích bố cục AI chuyên sâu, bảo toàn cấu trúc Header (`#`, `##`), thứ tự đọc đa cột (Reading Order) & Bảng biểu (`|---|---|`).\n"
                "- **Định dạng hỗ trợ:** PDF, DOCX, PPTX, XLSX, HTML, hình ảnh...\n"
                "- **Ưu điểm:** Chạy 100% offline với mô hình AI cục bộ, **0 Quota, 0 API Key, an toàn dữ liệu**."
            )
        elif "DeepSeek" in extraction_mode:
            st.info(
                "🐋 **Đặc điểm DeepSeek AI Multimodal VLM:**\n"
                "- **Quét quang học (OCR Scan) trực quan:** Render từng trang PDF sang ảnh độ phân giải cao và truyền trực tiếp vào mô hình VLM của DeepSeek để đọc mọi văn bản scan, hóa đơn, biểu mẫu, chữ viết tay và con dấu (tương tự Gemini AI).\n"
                "- **Bóc tách Bảng biểu & Số liệu:** Chuyển đổi bảng biểu thị giác thành cú pháp Markdown chuẩn (`|---|---|`).\n"
                "- **Hỗ trợ các model hàng đầu:**\n"
                "  • **`deepseek-flash`:** Chi phí rẻ nhất ($0.15/1M), hỗ trợ Multimodal Vision OCR.\n"
                "  • **`deepseek-chat` (V3):** Phản hồi siêu nhanh, bóc tách văn bản cực sạch.\n"
                "  • **`deepseek-reasoner` (R1):** Suy luận logic sâu với **Chain-of-Thought (CoT)**, thẩm định tính chặt chẽ của hợp đồng và phát hiện rủi ro.\n"
                "- **Định dạng nhận diện:** PDF (quét scan trang), Hình ảnh (PNG, JPG, WEBP), Word (.docx)."
            )
        else:
            st.info(
                "✨ **Đặc điểm Trích xuất bằng Gemini AI:**\n"
                "- Sử dụng mô hình Google Gemini Multimodal VLM.\n"
                "- **Thế mạnh:** Đọc được file scan/ảnh chụp (OCR nâng cao), hiểu sâu ngữ cảnh, trích xuất bảng biểu phức tạp, tóm tắt điều hành và hỏi đáp trực tiếp theo tài liệu."
            )

    st.markdown("---")

    # ========================================================
    # CHẾ ĐỘ 1: TRÍCH XUẤT THÔNG THƯỜNG (LOCAL PARSER)
    # ========================================================
    if "thông thường" in extraction_mode:
        col_loc1, col_loc2 = st.columns([1, 1], gap="large")
        
        with col_loc1:
            uploaded_loc = st.file_uploader(
                "Chọn tệp PDF hoặc Word (.docx) để trích xuất thường:",
                type=["pdf", "docx"],
                key="uploader_loc_mode",
                help="Engine nội bộ pypdf & python-docx, hỗ trợ tối đa 50MB"
            )
            
            if uploaded_loc:
                loc_bytes = uploaded_loc.getvalue()
                loc_name = uploaded_loc.name
                loc_type = "pdf" if loc_name.lower().endswith(".pdf") else "docx"
                file_size_kb = len(loc_bytes) / 1024
                
                st.markdown(
                    f"""
                    <div class="feature-card">
                        <b>📁 Tệp:</b> <code>{loc_name}</code><br>
                        <b>📦 Dung lượng:</b> <code>{file_size_kb:.1f} KB</code> | 
                        <b>Định dạng:</b> <span class="metric-chip">{loc_type.upper()}</span> | 
                        <b>Engine:</b> <code>{'pypdf (Local)' if loc_type == 'pdf' else 'python-docx (Local)'}</code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                start_p = 1
                end_p = None
                
                if loc_type == "pdf":
                    pdf_meta = get_pdf_metadata(loc_bytes)
                    total_pages = pdf_meta.get("pages", 1)
                    if isinstance(total_pages, int) and total_pages > 1:
                        p_choice = st.radio("Phạm vi trang cần trích xuất:", ["Toàn bộ tài liệu", "Chọn khoảng trang"], horizontal=True, key="loc_p_choice")
                        if p_choice == "Chọn khoảng trang":
                            col_p1, col_p2 = st.columns(2)
                            with col_p1:
                                start_p = st.number_input("Từ trang:", min_value=1, max_value=total_pages, value=1, key="loc_p_start")
                            with col_p2:
                                end_p = st.number_input("Đến trang:", min_value=start_p, max_value=total_pages, value=min(total_pages, 10), key="loc_p_end")
                
                run_loc_btn = st.button("⚡ Bắt đầu Trích xuất Thông thường", type="primary", use_container_width=True)
            else:
                st.info("👈 Hãy chọn tệp PDF hoặc DOCX ở khung bên trái để bắt đầu trích xuất.")
                run_loc_btn = False

        with col_loc2:
            st.markdown("##### 📤 Kết quả Trích xuất Thông thường:")
            loc_box = st.container()
            
            if uploaded_loc and run_loc_btn:
                t0 = time.time()
                with st.spinner("Đang bóc tách văn bản bằng engine nội bộ..."):
                    if loc_type == "pdf":
                        success, text_out, stats = extract_pdf_full_local(loc_bytes, start_page=start_p, end_page=end_p)
                    else:
                        success, text_out, stats = extract_docx_full_local(loc_bytes)
                    
                    elapsed = time.time() - t0
                    
                    if success:
                        st.session_state.last_local_doc_result = text_out
                        st.session_state.last_local_doc_time = elapsed
                        st.session_state.last_local_doc_stats = stats
                        st.session_state.last_local_doc_filename = loc_name
                        
                        words = stats.get("total_words", 0)
                        chars = stats.get("total_chars", 0)
                        pages_or_p = stats.get("processed_pages", stats.get("paragraphs", 0))
                        
                        st.success(f"✅ Hoàn thành trích xuất trong **{elapsed:.3f} giây** (Engine cục bộ, 0 Quota API)!")
                        st.markdown(
                            f'<span class="metric-chip">⚡ Tốc độ: {elapsed*1000:.1f}ms</span>'
                            f'<span class="metric-chip">📝 Từ: {words:,}</span>'
                            f'<span class="metric-chip">🔤 Ký tự: {chars:,}</span>'
                            f'<span class="metric-chip">📊 Mục/Trang: {pages_or_p}</span>',
                            unsafe_allow_html=True
                        )
                        
                        loc_box.markdown(text_out)
                        
                        col_dl1, col_dl2 = st.columns(2)
                        with col_dl1:
                            st.download_button(
                                "📥 Tải văn bản (.txt)",
                                data=text_out,
                                file_name=f"{Path(loc_name).stem}_local.txt",
                                mime="text/plain",
                                key="btn_dl_loc_txt"
                            )
                        with col_dl2:
                            st.download_button(
                                "📥 Tải Markdown (.md)",
                                data=text_out,
                                file_name=f"{Path(loc_name).stem}_local.md",
                                mime="text/markdown",
                                key="btn_dl_loc_md"
                            )
                    else:
                        st.error(f"❌ {text_out}")
                        
            elif st.session_state.get("last_local_doc_result"):
                loc_box.caption(f"⏱️ Lần chạy gần nhất: {st.session_state.get('last_local_doc_time', 0):.3f}s | Tệp: `{st.session_state.get('last_local_doc_filename', '')}`")
                loc_box.markdown(st.session_state.last_local_doc_result)
                col_dl1, col_dl2 = loc_box.columns(2)
                with col_dl1:
                    st.download_button(
                        "📥 Tải văn bản (.txt)",
                        data=st.session_state.last_local_doc_result,
                        file_name="local_extracted.txt",
                        mime="text/plain",
                        key="btn_dl_cached_loc_txt"
                    )
                with col_dl2:
                    st.download_button(
                        "📥 Tải Markdown (.md)",
                        data=st.session_state.last_local_doc_result,
                        file_name="local_extracted.md",
                        mime="text/markdown",
                        key="btn_dl_cached_loc_md"
                    )
            else:
                loc_box.info("Nội dung văn bản sau khi trích xuất thông thường sẽ hiển thị tại đây.")

    # ========================================================
    # CHẾ ĐỘ 2: TRÍCH XUẤT BẰNG MICROSOFT MARKITDOWN
    # ========================================================
    elif "MarkItDown" in extraction_mode:
        col_md1, col_md2 = st.columns([1, 1], gap="large")
        
        with col_md1:
            st.markdown("##### 📥 Chọn tệp để chuyển đổi sang Markdown:")
            
            st.caption("💡 **Thử nghiệm nhanh với tệp mẫu có sẵn trong thư mục:**")
            col_btn_docx, col_btn_pdf = st.columns(2)
            with col_btn_docx:
                if st.button("📄 Dùng test_sample.docx", use_container_width=True, key="btn_sample_docx"):
                    st.session_state.md_sample_selected = "test_sample.docx"
            with col_btn_pdf:
                if st.button("📑 Dùng test_sample.pdf", use_container_width=True, key="btn_sample_pdf"):
                    st.session_state.md_sample_selected = "test_sample.pdf"
            
            uploaded_md = st.file_uploader(
                "Hoặc tải lên tệp của bạn (PDF, DOCX, PPTX, XLSX, HTML):",
                type=["pdf", "docx", "pptx", "xlsx", "html"],
                key="uploader_markitdown_mode",
                help="Engine Microsoft MarkItDown chuyển đổi tài liệu trực tiếp sang Markdown chuẩn"
            )
            
            target_bytes = None
            target_name = None
            
            if uploaded_md:
                target_bytes = uploaded_md.getvalue()
                target_name = uploaded_md.name
                st.session_state.md_sample_selected = None
            elif st.session_state.get("md_sample_selected"):
                sample_file = st.session_state.get("md_sample_selected")
                if os.path.exists(sample_file):
                    with open(sample_file, "rb") as f:
                        target_bytes = f.read()
                    target_name = sample_file
            
            run_md_btn = False
            if target_bytes and target_name:
                target_ext = Path(target_name).suffix.lower()
                target_size_kb = len(target_bytes) / 1024
                
                st.markdown(
                    f"""
                    <div class="feature-card">
                        <b>📁 Tệp đang chọn:</b> <code>{target_name}</code><br>
                        <b>📦 Dung lượng:</b> <code>{target_size_kb:.1f} KB</code> | 
                        <b>Định dạng:</b> <span class="metric-chip">{target_ext.replace('.', '').upper()}</span> | 
                        <b>Bộ chuyển đổi:</b> <code>Microsoft MarkItDown (Local)</code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if not MARKITDOWN_AVAILABLE:
                    st.error("⚠️ Thư viện `markitdown` chưa được cài đặt trong môi trường hiện tại.")
                else:
                    run_md_btn = st.button("🚀 Bắt đầu Chuyển sang Markdown (MarkItDown)", type="primary", use_container_width=True)
            else:
                st.info("👈 Hãy tải lên tài liệu hoặc bấm một trong 2 nút tệp mẫu phía trên để thử nghiệm.")

        with col_md2:
            st.markdown("##### 📤 Kết quả Markdown (Microsoft MarkItDown):")
            md_box = st.container()
            
            if target_bytes and target_name and run_md_btn:
                t0 = time.time()
                with st.spinner("Đang chuyển đổi tài liệu sang Markdown bằng Microsoft MarkItDown..."):
                    success, md_out, stats = extract_with_markitdown(target_bytes, target_name)
                    elapsed = time.time() - t0
                    
                    if success:
                        st.session_state.last_markitdown_result = md_out
                        st.session_state.last_markitdown_time = elapsed
                        st.session_state.last_markitdown_stats = stats
                        st.session_state.last_markitdown_filename = target_name
                        st.session_state.last_markitdown_bytes = target_bytes
                        
                        words = stats.get("total_words", 0)
                        chars = stats.get("total_chars", 0)
                        lines = stats.get("total_lines", 0)
                        pages = stats.get("total_pages", 1)
                        is_scanned = stats.get("is_scanned_pdf", False)
                        fallback = stats.get("fallback_used")
                        
                        if words > 0:
                            st.success(f"✅ Chuyển đổi thành công trong **{elapsed:.3f} giây** (Microsoft MarkItDown, 0 Quota API)!")
                            stat_chips = (
                                f'<span class="metric-chip">⚡ Tốc độ: {elapsed*1000:.1f}ms</span>'
                                f'<span class="metric-chip">📝 Từ: {words:,}</span>'
                                f'<span class="metric-chip">🔤 Ký tự: {chars:,}</span>'
                                f'<span class="metric-chip">📑 Dòng: {lines:,}</span>'
                            )
                            if pages > 1:
                                stat_chips += f'<span class="metric-chip">📄 Trang: {pages}</span>'
                            st.markdown(stat_chips, unsafe_allow_html=True)
                            
                            if fallback:
                                st.info(f"ℹ️ Đã tự động sử dụng engine dự phòng `{fallback}` để hoàn tất việc trích xuất văn bản.")
                            
                            tab_prev, tab_code = md_box.tabs(["👁️ Xem trước Hiển thị (Rendered)", "💻 Mã nguồn Markdown (.md)"])
                            with tab_prev:
                                tab_prev.markdown(md_out)
                            with tab_code:
                                tab_code.code(md_out, language="markdown")
                                
                            col_dl1, col_dl2 = md_box.columns(2)
                            with col_dl1:
                                st.download_button(
                                    "📥 Tải tệp Markdown (.md)",
                                    data=md_out,
                                    file_name=f"{Path(target_name).stem}.md",
                                    mime="text/markdown",
                                    key="btn_dl_md_out"
                                )
                            with col_dl2:
                                st.download_button(
                                    "📥 Tải tệp Văn bản (.txt)",
                                    data=md_out,
                                    file_name=f"{Path(target_name).stem}.txt",
                                    mime="text/plain",
                                    key="btn_dl_md_txt_out"
                                )
                        else:
                            st.warning(f"⚠️ **Không tìm thấy lớp văn bản số trong tệp `{target_name}` (Kết quả: 0 từ, 0 ký tự).**")
                            if is_scanned:
                                size_mb = len(target_bytes) / (1024 * 1024)
                                st.markdown(
                                    f"""
                                    <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 12px; padding: 18px; margin: 12px 0;">
                                        <div style="font-weight: 700; color: #fbbf24; font-size: 1.05rem; margin-bottom: 8px;">
                                            📑 Nguyên nhân kỹ thuật: Tài liệu là PDF Quét dạng Ảnh (Scanned / Image-Only PDF)
                                        </div>
                                        <ul style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.6; margin-bottom: 14px;">
                                            <li>Tệp <code>{target_name}</code> có dung lượng <b>{size_mb:.2f} MB</b> ({pages} trang). Toàn bộ nội dung là <b>hình ảnh scan hoặc chụp từ văn bản giấy</b> (chứa chữ in, con dấu đỏ, chữ ký).</li>
                                            <li>Tệp này <b>hoàn toàn không có lớp ký tự số (Digital Text Stream)</b> được nhúng bên trong PDF.</li>
                                            <li><b>Chế độ 2 (Microsoft MarkItDown)</b> là thư viện bóc tách cấu trúc văn bản số tĩnh chạy Offline (0 Quota API), <b>không tích hợp OCR quang học</b> nên không thể tự động nhận diện chữ từ ảnh chụp scan.</li>
                                        </ul>
                                        <div style="background: rgba(15, 23, 42, 0.7); border-radius: 10px; padding: 14px; border-left: 4px solid #38bdf8;">
                                            <div style="font-weight: 700; color: #38bdf8; font-size: 0.95rem; margin-bottom: 6px;">
                                                💡 Giải pháp trích xuất toàn diện cho tệp này:
                                            </div>
                                            <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.6;">
                                                👉 <b>Khuyên dùng:</b> Hãy chuyển sang <b>Chế độ 4: DeepSeek AI (Multimodal VLM - OCR Scan)</b> hoặc <b>Chế độ 5: Google Gemini AI (Multimodal VLM)</b> ở phần tùy chọn phía trên.<br>
                                                Cả hai chế độ này đều tự động chụp ảnh từng trang PDF độ nét cao và sử dụng mô hình trí tuệ nhân tạo thị giác (Vision VLM) để bóc tách 100% chữ tiếng Việt, con dấu đỏ, chữ ký và bảng biểu phức tạp!
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                                if PDFIUM_AVAILABLE and len(target_bytes) > 0 and pdfium:
                                    try:
                                        with st.expander("👁️ Xem ảnh trang đầu của tệp PDF (Chứng minh đây là văn bản scan)", expanded=True):
                                            doc_v = pdfium.PdfDocument(io.BytesIO(target_bytes))
                                            if len(doc_v) > 0:
                                                p0 = doc_v[0]
                                                pil_img = p0.render(scale=1.5).to_pil()
                                                st.image(pil_img, caption=f"Trang 1 / {len(doc_v)}: {target_name} (Ảnh scan quang học)", use_container_width=True)
                                            doc_v.close()
                                    except Exception:
                                        pass
                            else:
                                st.info("Tài liệu không chứa văn bản hoặc tệp bị rỗng.")
                    else:
                        st.error(f"❌ {md_out}")
                        
            elif st.session_state.get("last_markitdown_result") or st.session_state.get("last_markitdown_stats"):
                cached_res = st.session_state.get("last_markitdown_result", "")
                cached_time = st.session_state.get("last_markitdown_time", 0)
                cached_name = st.session_state.get("last_markitdown_filename", "")
                cached_stats = st.session_state.get("last_markitdown_stats", {})
                cached_words = cached_stats.get("total_words", len(cached_res.split()) if cached_res else 0)
                
                if cached_words > 0:
                    md_box.caption(f"⏱️ Lần chạy gần nhất: {cached_time:.3f}s | Tệp: `{cached_name}` | Microsoft MarkItDown")
                    
                    tab_prev, tab_code = md_box.tabs(["👁️ Xem trước Hiển thị (Rendered)", "💻 Mã nguồn Markdown (.md)"])
                    with tab_prev:
                        tab_prev.markdown(cached_res)
                    with tab_code:
                        tab_code.code(cached_res, language="markdown")
                        
                    col_dl1, col_dl2 = md_box.columns(2)
                    with col_dl1:
                        st.download_button(
                            "📥 Tải tệp Markdown (.md)",
                            data=cached_res,
                            file_name=f"{Path(cached_name).stem if cached_name else 'markitdown'}.md",
                            mime="text/markdown",
                            key="btn_dl_cached_md"
                        )
                    with col_dl2:
                        st.download_button(
                            "📥 Tải tệp Văn bản (.txt)",
                            data=cached_res,
                            file_name=f"{Path(cached_name).stem if cached_name else 'markitdown'}.txt",
                            mime="text/plain",
                            key="btn_dl_cached_md_txt"
                        )
                else:
                    st.warning(f"⚠️ **Không tìm thấy lớp văn bản số trong tệp `{cached_name}` (Kết quả: 0 từ).**")
            else:
                md_box.info("Nội dung Markdown sau khi trích xuất bằng MarkItDown sẽ hiển thị tại đây.")

    # ========================================================
    # CHẾ ĐỘ 3: TRÍCH XUẤT BẰNG DOCLING (DS4SD / IBM RESEARCH)
    # ========================================================
    elif "Docling" in extraction_mode:
        col_docling1, col_docling2 = st.columns([1, 1], gap="large")
        
        with col_docling1:
            st.markdown("##### 📥 Chọn tệp để chuyển đổi sang Markdown:")
            
            st.caption("💡 **Thử nghiệm nhanh với tệp mẫu có sẵn trong thư mục:**")
            col_btn_docx, col_btn_pdf = st.columns(2)
            with col_btn_docx:
                if st.button("📄 Dùng test_sample.docx", use_container_width=True, key="btn_sample_docx_docling"):
                    st.session_state.docling_sample_selected = "test_sample.docx"
            with col_btn_pdf:
                if st.button("📑 Dùng test_sample.pdf", use_container_width=True, key="btn_sample_pdf_docling"):
                    st.session_state.docling_sample_selected = "test_sample.pdf"
            
            uploaded_docling = st.file_uploader(
                "Hoặc tải lên tệp của bạn (PDF, DOCX, PPTX, XLSX, HTML):",
                type=["pdf", "docx", "pptx", "xlsx", "html"],
                key="uploader_docling_mode",
                help="Engine Docling (IBM Research) chuyển đổi tài liệu trực tiếp sang Markdown chuẩn bằng mô hình AI phân tích bố cục"
            )
            
            target_bytes = None
            target_name = None
            
            if uploaded_docling:
                target_bytes = uploaded_docling.getvalue()
                target_name = uploaded_docling.name
                st.session_state.docling_sample_selected = None
            elif st.session_state.get("docling_sample_selected"):
                sample_file = st.session_state.get("docling_sample_selected")
                if os.path.exists(sample_file):
                    with open(sample_file, "rb") as f:
                        target_bytes = f.read()
                    target_name = sample_file
            
            run_docling_btn = False
            if target_bytes and target_name:
                target_ext = Path(target_name).suffix.lower()
                target_size_kb = len(target_bytes) / 1024
                
                st.markdown(
                    f"""
                    <div class="feature-card">
                        <b>📁 Tệp đang chọn:</b> <code>{target_name}</code><br>
                        <b>📦 Dung lượng:</b> <code>{target_size_kb:.1f} KB</code> | 
                        <b>Định dạng:</b> <span class="metric-chip">{target_ext.replace('.', '').upper()}</span> | 
                        <b>Bộ chuyển đổi:</b> <code>Docling AI (IBM Research - Local)</code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if not DOCLING_AVAILABLE:
                    st.error("⚠️ Thư viện `docling` chưa được cài đặt trong môi trường hiện tại.")
                else:
                    run_docling_btn = st.button("🚀 Bắt đầu Chuyển sang Markdown (Docling)", type="primary", use_container_width=True)
            else:
                st.info("👈 Hãy tải lên tài liệu hoặc bấm một trong 2 nút tệp mẫu phía trên để thử nghiệm.")

        with col_docling2:
            st.markdown("##### 📤 Kết quả Markdown (Docling):")
            docling_box = st.container()
            
            if target_bytes and target_name and run_docling_btn:
                t0 = time.time()
                with st.spinner("Đang chuyển đổi tài liệu sang Markdown bằng Docling..."):
                    success, docling_out, stats = extract_with_docling(target_bytes, target_name)
                    elapsed = time.time() - t0
                    
                    if success:
                        st.session_state.last_docling_result = docling_out
                        st.session_state.last_docling_time = elapsed
                        st.session_state.last_docling_stats = stats
                        st.session_state.last_docling_filename = target_name
                        
                        words = stats.get("total_words", 0)
                        chars = stats.get("total_chars", 0)
                        lines = stats.get("total_lines", 0)
                        pages = stats.get("pages", 1)
                        tables = stats.get("tables", 0)
                        
                        st.success(f"✅ Chuyển đổi thành công trong **{elapsed:.2f} giây** (Docling by IBM, 0 Quota API)!")
                        st.markdown(
                            f'<span class="metric-chip">⚡ Tốc độ: {elapsed:.2f}s</span>'
                            f'<span class="metric-chip">📝 Từ: {words:,}</span>'
                            f'<span class="metric-chip">🔤 Ký tự: {chars:,}</span>'
                            f'<span class="metric-chip">📑 Dòng: {lines:,}</span>'
                            f'<span class="metric-chip">📊 Bảng: {tables}</span>'
                            f'<span class="metric-chip">📄 Trang: {pages}</span>',
                            unsafe_allow_html=True
                        )
                        
                        tab_prev, tab_code = docling_box.tabs(["👁️ Xem trước Hiển thị (Rendered)", "💻 Mã nguồn Markdown (.md)"])
                        with tab_prev:
                            tab_prev.markdown(docling_out)
                        with tab_code:
                            tab_code.code(docling_out, language="markdown")
                            
                        col_dl1, col_dl2 = docling_box.columns(2)
                        with col_dl1:
                            st.download_button(
                                "📥 Tải tệp Markdown (.md)",
                                data=docling_out,
                                file_name=f"{Path(target_name).stem}.md",
                                mime="text/markdown",
                                key="btn_dl_docling_out"
                            )
                        with col_dl2:
                            st.download_button(
                                "📥 Tải tệp Văn bản (.txt)",
                                data=docling_out,
                                file_name=f"{Path(target_name).stem}.txt",
                                mime="text/plain",
                                key="btn_dl_docling_txt_out"
                            )
                    else:
                        st.error(f"❌ {docling_out}")
                        
            elif st.session_state.get("last_docling_result"):
                cached_res = st.session_state.get("last_docling_result")
                cached_time = st.session_state.get("last_docling_time", 0)
                cached_name = st.session_state.get("last_docling_filename", "")
                
                docling_box.caption(f"⏱️ Lần chạy gần nhất: {cached_time:.2f}s | Tệp: `{cached_name}` | Docling (IBM Research)")
                
                tab_prev, tab_code = docling_box.tabs(["👁️ Xem trước Hiển thị (Rendered)", "💻 Mã nguồn Markdown (.md)"])
                with tab_prev:
                    tab_prev.markdown(cached_res)
                with tab_code:
                    tab_code.code(cached_res, language="markdown")
                    
                col_dl1, col_dl2 = docling_box.columns(2)
                with col_dl1:
                    st.download_button(
                        "📥 Tải tệp Markdown (.md)",
                        data=cached_res,
                        file_name=f"{Path(cached_name).stem if cached_name else 'docling'}.md",
                        mime="text/markdown",
                        key="btn_dl_cached_docling_md"
                    )
                with col_dl2:
                    st.download_button(
                        "📥 Tải tệp Văn bản (.txt)",
                        data=cached_res,
                        file_name=f"{Path(cached_name).stem if cached_name else 'docling'}.txt",
                        mime="text/plain",
                        key="btn_dl_cached_docling_txt"
                    )
            else:
                docling_box.info("Nội dung Markdown sau khi trích xuất bằng Docling sẽ hiển thị tại đây.")

    # ========================================================
    # CHẾ ĐỘ 4: TRÍCH XUẤT BẰNG DEEPSEEK AI MODEL
    # ========================================================
    elif "DeepSeek" in extraction_mode:
        col_ds1, col_ds2 = st.columns([1, 1], gap="large")
        
        with col_ds1:
            st.markdown("##### 📥 Chọn tệp để phân tích bằng DeepSeek Multimodal VLM:")
            
            st.caption("💡 **Thử nghiệm nhanh với tệp mẫu có sẵn trong thư mục:**")
            col_btn_docx, col_btn_pdf = st.columns(2)
            with col_btn_docx:
                if st.button("📄 Dùng test_sample.docx", use_container_width=True, key="btn_sample_docx_deepseek"):
                    st.session_state.deepseek_sample_selected = "test_sample.docx"
            with col_btn_pdf:
                if st.button("📑 Dùng test_sample.pdf", use_container_width=True, key="btn_sample_pdf_deepseek"):
                    st.session_state.deepseek_sample_selected = "test_sample.pdf"
            
            uploaded_ds = st.file_uploader(
                "Hoặc tải lên tệp của bạn (PDF, Word .docx, Hình ảnh PNG/JPG/WEBP):",
                type=["pdf", "docx", "png", "jpg", "jpeg", "webp"],
                key="uploader_deepseek_mode",
                help="DeepSeek Multimodal VLM hỗ trợ quét ảnh từng trang PDF, hình ảnh trực tiếp hoặc bóc tách văn bản DOCX."
            )
            
            target_bytes = None
            target_name = None
            
            if uploaded_ds:
                target_bytes = uploaded_ds.getvalue()
                target_name = uploaded_ds.name
                st.session_state.deepseek_sample_selected = None
            elif st.session_state.get("deepseek_sample_selected"):
                sample_file = st.session_state.get("deepseek_sample_selected")
                if os.path.exists(sample_file):
                    with open(sample_file, "rb") as f:
                        target_bytes = f.read()
                    target_name = sample_file
            
            ds_is_vlm_scan = True
            ds_max_pages = 5
            
            if target_bytes and target_name:
                target_ext = Path(target_name).suffix.lower()
                target_size_kb = len(target_bytes) / 1024
                
                ds_tab_options = [
                    "deepseek-flash — 💰 RẺ NHẤT & 🖼️ HỖ TRỢ VISION (Chính thức)",
                    "deepseek-v4-pro — 🚀 Flagship (Văn bản chuyên sâu)",
                    "deepseek-chat (V3) — ⚡ Tương thích ngược",
                    "deepseek-reasoner (R1) — 🧠 Suy luận sâu CoT"
                ]
                tab_def_idx = 0
                if selected_deepseek_model == "deepseek-v4-pro":
                    tab_def_idx = 1
                elif selected_deepseek_model == "deepseek-chat":
                    tab_def_idx = 2
                elif selected_deepseek_model == "deepseek-reasoner":
                    tab_def_idx = 3

                selected_tab_ds_opt = st.selectbox(
                    "🤖 Chọn model DeepSeek để trích xuất:",
                    options=ds_tab_options,
                    index=tab_def_idx,
                    key="ds_tab_model_select",
                    help="Theo tài liệu chính thức: deepseek-flash là model RẺ NHẤT ($0.15/1M input, $0.003 nếu cache hit) và là model DUY NHẤT có hỗ trợ Vision."
                )
                if selected_tab_ds_opt.startswith("deepseek-flash"):
                    ds_model_in_tab = "deepseek-flash"
                elif selected_tab_ds_opt.startswith("deepseek-v4-pro"):
                    ds_model_in_tab = "deepseek-v4-pro"
                elif selected_tab_ds_opt.startswith("deepseek-chat"):
                    ds_model_in_tab = "deepseek-chat"
                else:
                    ds_model_in_tab = "deepseek-reasoner"
                
                if target_ext == ".pdf":
                    pdf_page_count = 1
                    if pdfium:
                        try:
                            pdf_doc_peek = pdfium.PdfDocument(target_bytes)
                            pdf_page_count = len(pdf_doc_peek)
                            pdf_doc_peek.close()
                        except Exception:
                            pass
                    
                    ds_pdf_mode = st.radio(
                        "🖼️ Phương thức xử lý PDF:",
                        [
                            "🖼️ Quét thị giác Multimodal VLM (OCR Scan từng trang bằng ảnh - Tương tự Gemini AI)",
                            "⚡ Trích xuất văn bản thô (Text-only Fast)"
                        ],
                        index=0,
                        key="ds_pdf_mode_radio",
                        help="Multimodal VLM render từng trang PDF sang ảnh độ nét cao và nạp vào DeepSeek AI để đọc cả chữ, chữ scan/viết tay, bảng biểu và biểu đồ."
                    )
                    
                    ds_is_vlm_scan = "Multimodal VLM" in ds_pdf_mode
                    if ds_is_vlm_scan:
                        col_p1, col_p2 = st.columns([2, 1])
                        with col_p1:
                            ds_max_pages = st.slider(
                                "Số trang quét VLM tối đa:",
                                min_value=1,
                                max_value=min(15, max(1, pdf_page_count)),
                                value=min(5, max(1, pdf_page_count)),
                                key="ds_max_pages_slider",
                                help=f"Tài liệu có {pdf_page_count} trang. Mỗi trang sẽ được render thành 1 ảnh độ phân giải cao gửi cho DeepSeek Vision."
                            )
                        with col_p2:
                            st.caption(f"📑 Tổng trang: **{pdf_page_count}**\n\n🎯 Quét: **{ds_max_pages} trang đầu**")
                        
                        with st.expander("👁️ Xem trước ảnh các trang sẽ gửi vào DeepSeek VLM", expanded=False):
                            p_imgs = render_pdf_to_vlm_images(target_bytes, max_pages=ds_max_pages, dpi=100)
                            if p_imgs:
                                p_cols = st.columns(min(len(p_imgs), 4))
                                for idx, p_img in enumerate(p_imgs):
                                    with p_cols[idx % min(len(p_imgs), 4)]:
                                        st.image(p_img, caption=f"Trang {idx + 1}", use_container_width=True)
                    else:
                        st.caption(f"📑 Số trang tài liệu: **{pdf_page_count} trang** (Đọc văn bản thô)")
                        
                elif target_ext in [".png", ".jpg", ".jpeg", ".webp"]:
                    ds_is_vlm_scan = True
                    ds_max_pages = 1
                    try:
                        img_preview = Image.open(io.BytesIO(target_bytes))
                        with st.expander("👁️ Xem trước hình ảnh sẽ phân tích", expanded=True):
                            st.image(img_preview, caption=f"{target_name} ({img_preview.width}x{img_preview.height})", use_container_width=True)
                    except Exception:
                        pass
                        
                elif target_ext == ".docx":
                    ds_is_vlm_scan = False
                    ds_max_pages = 0
                    docx_preview_md = extract_docx_content(target_bytes)
                    word_est = len(docx_preview_md.split())
                    st.caption(f"📝 Số từ ước tính: **~{word_est:,} từ** (Tự động chuyển bảng sang Markdown)")

                st.markdown(
                    f"""
                    <div class="feature-card">
                        <b>📁 Tệp đang chọn:</b> <code>{target_name}</code><br>
                        <b>📦 Dung lượng:</b> <code>{target_size_kb:.1f} KB</code> | 
                        <b>Định dạng:</b> <span class="metric-chip">{target_ext.replace('.', '').upper()}</span> | 
                        <b>Chế độ:</b> <span class="metric-chip">{'🖼️ Multimodal VLM OCR' if ds_is_vlm_scan else '⚡ Text Processing'}</span> | 
                        <b>Model:</b> <code>{ds_model_in_tab}</code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("##### 🎯 Tác vụ gợi ý cho DeepSeek AI:")
                ds_preset_map = {
                    "📝 Trích xuất toàn bộ nội dung (Full OCR Scan & Clean Markdown)":
                        "Hãy quan sát kỹ toàn bộ tài liệu/hình ảnh được cung cấp và thực hiện OCR trích xuất toàn bộ văn bản một cách chi tiết, đầy đủ nhất:\n"
                        "- Sử dụng các cấp đề mục chuẩn (#, ##, ###) đúng thứ tự phân cấp logic.\n"
                        "- Giữ nguyên toàn bộ câu từ, số liệu, tên riêng, thuật ngữ và tiếng Việt có dấu chuẩn xác 100%.\n"
                        "- Chuẩn hóa danh sách gạch đầu dòng, số thứ tự và các khối trích dẫn nếu có.\n"
                        "- Bóc tách và định dạng TOÀN BỘ bảng biểu sang dạng bảng Markdown chuẩn (| Cột 1 | Cột 2 |).\n"
                        "- Đọc cả các ghi chú, con số, chữ nhỏ ở chân trang hoặc biểu mẫu nếu có.",
                    
                    "📊 Bóc tách Bảng biểu & Số liệu (Tables to Markdown)":
                        "Hãy tìm và trích xuất TOÀN BỘ các bảng biểu, số liệu, bảng biểu thống kê, báo cáo tài chính trong tài liệu này.\n"
                        "- Trình bày lại dưới dạng bảng Markdown chuẩn đẹp (| Cột 1 | Cột 2 |) kèm theo tên hoặc ngữ cảnh của từng bảng.\n"
                        "- Đảm bảo số liệu và đơn vị đo lường chính xác 100%.",
                    
                    "📌 Tóm tắt Điều hành & Điểm mấu chốt (Executive Summary)":
                        "Hãy phân tích và viết một bản tóm tắt điều hành (Executive Summary) chất lượng cao cho tài liệu này:\n"
                        "1. **Tổng quan & Mục đích chính** của tài liệu.\n"
                        "2. **Các điểm then chốt / Phát hiện chính** (bullet points rõ ràng).\n"
                        "3. **Số liệu & Mốc thời gian trọng yếu** cần lưu ý.\n"
                        "4. **Kiến nghị / Hành động tiếp theo**.\n"
                        "Trình bày chuyên nghiệp theo định dạng Markdown.",
                    
                    "🔍 Hỏi đáp / Tra cứu theo tài liệu (Doc Q&A)":
                        "Dựa hoàn toàn vào nội dung trực quan và văn bản trong tài liệu/hình ảnh được cung cấp, hãy trả lời chi tiết và chính xác câu hỏi sau:\n"
                        "[Nhập câu hỏi cụ thể của bạn vào đây, ví dụ: Tổng chỉ tiêu tuyển sinh là bao nhiêu? Hạn chót nộp hồ sơ khi nào?]",
                    
                    "🧠 Suy luận logic & Đánh giá rủi ro (DeepSeek-R1 CoT)":
                        "Hãy đóng vai trò chuyên gia phân tích tài liệu và thẩm định rủi ro chuyên sâu:\n"
                        "- Phân tích tính chặt chẽ của các luận điểm, điều khoản hoặc số liệu trong tài liệu.\n"
                        "- Chỉ ra các rủi ro tiềm ẩn, điểm bất hợp lý hoặc thông tin còn thiếu sót.\n"
                        "- Đưa ra kết luận khách quan và các khuyến nghị cụ thể.",
                    
                    "📋 Trích xuất Thực thể & Thông tin có cấu trúc JSON":
                        "Hãy đọc toàn bộ tài liệu và trích xuất các thông tin chính yếu thành một đối tượng JSON chuẩn (bao gồm: title, document_type, date, summary, key_entities, key_metrics, tables). Chỉ trả về JSON hợp lệ trong khối ```json ```.",
                    
                    "🧪 Tùy chỉnh câu lệnh":
                        "Hãy đọc kỹ nội dung tài liệu trên và thực hiện theo yêu cầu sau:"
                }
                
                ds_preset_keys = list(ds_preset_map.keys())
                selected_ds_preset = st.radio("Chọn loại tác vụ:", ds_preset_keys, index=0, key="ds_preset_radio")
            else:
                st.info("👈 Hãy tải lên tài liệu (PDF, Word, Ảnh) hoặc bấm một trong 2 nút tệp mẫu phía trên để thử nghiệm.")
                ds_preset_map = {"🧪 Tùy chỉnh câu lệnh": "Hãy trích xuất và phân tích tài liệu này."}
                selected_ds_preset = "🧪 Tùy chỉnh câu lệnh"
                ds_model_in_tab = selected_deepseek_model

        with col_ds2:
            default_ds_prompt = ds_preset_map.get(selected_ds_preset, "Hãy trích xuất và tái cấu trúc tài liệu này.")
            ds_prompt_input = st.text_area(
                "Câu lệnh yêu cầu DeepSeek AI:",
                value=default_ds_prompt,
                height=130,
                key="ds_prompt_text_area"
            )
            
            run_ds_btn = st.button("🚀 Bắt đầu Phân tích & Trích xuất (DeepSeek Multimodal VLM)", type="primary", use_container_width=True, key="btn_run_deepseek_doc")
            
            ds_output_box = st.container()
            
            if run_ds_btn:
                if not active_deepseek_key:
                    st.error("⚠️ Vui lòng nhập DeepSeek API Key ở Sidebar trước khi thực hiện!")
                elif not target_bytes or not target_name:
                    st.warning("⚠️ Vui lòng tải lên tài liệu hoặc chọn tệp mẫu trước!")
                elif not ds_prompt_input.strip():
                    st.warning("⚠️ Vui lòng nhập câu lệnh yêu cầu!")
                else:
                    target_ext = Path(target_name).suffix.lower()
                    
                    with st.spinner(f"🐋 DeepSeek ({ds_model_in_tab}) đang chuẩn bị và phân tích tài liệu..."):
                        start_time = time.time()
                        full_ds_response = ""
                        full_ds_reasoning = ""
                        
                        reasoning_placeholder = None
                        if ds_model_in_tab in ["deepseek-reasoner", "deepseek-flash", "deepseek-v4-pro"]:
                            with ds_output_box.expander("🧠 Quá trình suy luận (DeepSeek Thinking Mode...)", expanded=True):
                                reasoning_placeholder = st.empty()
                                
                        result_placeholder = ds_output_box.empty()
                        
                        try:
                            client = get_deepseek_client(active_deepseek_key)
                            
                            system_instruction = (
                                "Bạn là chuyên gia phân tích và trích xuất tài liệu thông minh (Multimodal Document AI) hàng đầu. "
                                "Bạn có khả năng OCR quét chữ từ ảnh tài liệu, nhận diện bảng biểu, sơ đồ và tái cấu trúc thành Markdown chuẩn đẹp, "
                                "giữ nguyên vẹn 100% ngữ nghĩa và tiếng Việt có dấu."
                            )
                            
                            vlm_images = []
                            messages = []
                            
                            if ds_is_vlm_scan:
                                if target_ext == ".pdf":
                                    with st.spinner(f"🖼️ Đang render {ds_max_pages} trang PDF sang ảnh quét VLM..."):
                                        vlm_images = render_pdf_to_vlm_images(target_bytes, max_pages=ds_max_pages, dpi=150)
                                elif target_ext in [".png", ".jpg", ".jpeg", ".webp"]:
                                    img_obj = Image.open(io.BytesIO(target_bytes))
                                    if img_obj.mode in ("RGBA", "P"):
                                        img_obj = img_obj.convert("RGB")
                                    vlm_images = [img_obj]
                                
                                if not vlm_images:
                                    st.error("❌ Không thể tạo hình ảnh từ tài liệu để gửi vào DeepSeek VLM.")
                                else:
                                    user_parts = [
                                        {
                                            "type": "text",
                                            "text": (
                                                f"Tên tài liệu: {target_name}\n"
                                                f"Định dạng: {target_ext.upper()}\n"
                                                f"Số trang được quét hình ảnh (VLM OCR Scan): {len(vlm_images)} trang\n\n"
                                                f"--- YÊU CẦU CỤ THỂ ---\n{ds_prompt_input}"
                                            )
                                        }
                                    ]
                                    
                                    for idx, p_img in enumerate(vlm_images):
                                        b64_str = pil_image_to_base64_jpeg(p_img, quality=85)
                                        user_parts.append({
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{b64_str}"
                                            }
                                        })
                                    
                                    messages = [
                                        {"role": "system", "content": system_instruction},
                                        {"role": "user", "content": user_parts}
                                    ]
                            else:
                                if target_ext == ".docx":
                                    ok, raw_text, local_stats = extract_docx_full_local(target_bytes)
                                else:
                                    ok, raw_text, local_stats = extract_pdf_full_local(target_bytes)
                                
                                if not ok or not raw_text.strip():
                                    st.error(f"❌ Không thể đọc văn bản từ tệp: {raw_text}")
                                else:
                                    prompt_content = (
                                        f"Tên tài liệu: {target_name}\n"
                                        f"Định dạng: {target_ext.upper()}\n\n"
                                        f"--- NỘI DUNG TÀI LIỆU ---\n"
                                        f"{raw_text}\n"
                                        f"--- HẾT NỘI DUNG TÀI LIỆU ---\n\n"
                                        f"YÊU CẦU CỤ THỂ:\n{ds_prompt_input}"
                                    )
                                    messages = [
                                        {"role": "system", "content": system_instruction},
                                        {"role": "user", "content": prompt_content}
                                    ]
                            
                            if messages:
                                stream_kwargs = {
                                    "model": ds_model_in_tab,
                                    "messages": messages,
                                    "stream": True,
                                }
                                if ds_model_in_tab != "deepseek-reasoner":
                                    stream_kwargs["temperature"] = temperature
                                    stream_kwargs["top_p"] = top_p
                                    stream_kwargs["max_tokens"] = max_tokens
                                else:
                                    stream_kwargs["max_tokens"] = max_tokens
                                    
                                stream = client.chat.completions.create(**stream_kwargs)
                                
                                for chunk in stream:
                                    if not chunk.choices:
                                        continue
                                    choice = chunk.choices[0]
                                    delta = choice.delta
                                    
                                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                                        full_ds_reasoning += delta.reasoning_content
                                        if reasoning_placeholder:
                                            reasoning_placeholder.markdown(full_ds_reasoning + " ▌")
                                            
                                    if hasattr(delta, "content") and delta.content:
                                        full_ds_response += delta.content
                                        result_placeholder.markdown(full_ds_response + " ▌")
                                
                                if reasoning_placeholder and full_ds_reasoning:
                                    reasoning_placeholder.markdown(full_ds_reasoning)
                                result_placeholder.markdown(full_ds_response)
                                
                                elapsed = time.time() - start_time
                                words = len(full_ds_response.split())
                                chars = len(full_ds_response)
                                lines = len(full_ds_response.splitlines())
                                pages_scanned = len(vlm_images) if ds_is_vlm_scan else 1
                                
                                stats = {
                                    "words": words,
                                    "chars": chars,
                                    "lines": lines,
                                    "model": ds_model_in_tab,
                                    "time": elapsed,
                                    "filename": target_name,
                                    "is_vlm": ds_is_vlm_scan,
                                    "pages_scanned": pages_scanned
                                }
                                
                                st.session_state.last_deepseek_doc_result = full_ds_response
                                st.session_state.last_deepseek_doc_reasoning = full_ds_reasoning if full_ds_reasoning else None
                                st.session_state.last_deepseek_doc_time = elapsed
                                st.session_state.last_deepseek_doc_model = ds_model_in_tab
                                st.session_state.last_deepseek_doc_filename = target_name
                                st.session_state.last_deepseek_doc_stats = stats
                                
                                scan_badge = f'<span class="metric-chip">🖼️ Quét VLM: {pages_scanned} trang</span>' if ds_is_vlm_scan else '<span class="metric-chip">⚡ Chế độ: Văn bản thô</span>'
                                st.success(f"✅ Hoàn thành phân tích bằng DeepSeek AI ({'Multimodal VLM' if ds_is_vlm_scan else 'Text'}) trong **{elapsed:.2f} giây**!")
                                st.markdown(
                                    f'<span class="metric-chip">⚡ Tốc độ: {elapsed:.2f}s</span>'
                                    f'<span class="metric-chip">🤖 Model: {ds_model_in_tab}</span>'
                                    f'{scan_badge}'
                                    f'<span class="metric-chip">📝 Từ: {words:,}</span>'
                                    f'<span class="metric-chip">🔤 Ký tự: {chars:,}</span>'
                                    f'<span class="metric-chip">📑 Dòng: {lines:,}</span>',
                                    unsafe_allow_html=True
                                )
                                
                                tabs_list = ["👁️ Xem trước Hiển thị (Rendered)", "💻 Mã nguồn Markdown (.md)"]
                                if full_ds_reasoning:
                                    tabs_list.append("🧠 Quá trình suy luận R1 (CoT)")
                                rendered_tabs = ds_output_box.tabs(tabs_list)
                                with rendered_tabs[0]:
                                    rendered_tabs[0].markdown(full_ds_response)
                                with rendered_tabs[1]:
                                    rendered_tabs[1].code(full_ds_response, language="markdown")
                                if full_ds_reasoning and len(rendered_tabs) > 2:
                                    with rendered_tabs[2]:
                                        rendered_tabs[2].markdown(full_ds_reasoning)
                                        
                                col_dl1, col_dl2 = ds_output_box.columns(2)
                                with col_dl1:
                                    st.download_button(
                                        "📥 Tải tệp Markdown (.md)",
                                        data=full_ds_response,
                                        file_name=f"{Path(target_name).stem}_deepseek.md",
                                        mime="text/markdown",
                                        key="btn_dl_ds_md"
                                    )
                                with col_dl2:
                                    st.download_button(
                                        "📥 Tải tệp Văn bản (.txt)",
                                        data=full_ds_response,
                                        file_name=f"{Path(target_name).stem}_deepseek.txt",
                                        mime="text/plain",
                                        key="btn_dl_ds_txt"
                                    )
                        except AuthenticationError:
                            st.error("❌ **Lỗi DeepSeek (401 Unauthorized)**: API Key không hợp lệ. Vui lòng kiểm tra lại tại platform.deepseek.com")
                        except Exception as e:
                            st.error(f"❌ **Lỗi DeepSeek API**: {str(e)}")
            
            elif st.session_state.get("last_deepseek_doc_result"):
                cached_res = st.session_state.get("last_deepseek_doc_result")
                cached_reasoning = st.session_state.get("last_deepseek_doc_reasoning")
                cached_time = st.session_state.get("last_deepseek_doc_time", 0)
                cached_name = st.session_state.get("last_deepseek_doc_filename", "")
                cached_model = st.session_state.get("last_deepseek_doc_model", "deepseek-chat")
                
                ds_output_box.caption(f"⏱️ Lần chạy gần nhất: {cached_time:.2f}s | Tệp: `{cached_name}` | Model: `{cached_model}` (DeepSeek AI)")
                
                tabs_list = ["👁️ Xem trước Hiển thị (Rendered)", "💻 Mã nguồn Markdown (.md)"]
                if cached_reasoning:
                    tabs_list.append("🧠 Quá trình suy luận R1 (CoT)")
                rendered_tabs = ds_output_box.tabs(tabs_list)
                with rendered_tabs[0]:
                    rendered_tabs[0].markdown(cached_res)
                with rendered_tabs[1]:
                    rendered_tabs[1].code(cached_res, language="markdown")
                if cached_reasoning and len(rendered_tabs) > 2:
                    with rendered_tabs[2]:
                        rendered_tabs[2].markdown(cached_reasoning)
                        
                col_dl1, col_dl2 = ds_output_box.columns(2)
                with col_dl1:
                    st.download_button(
                        "📥 Tải tệp Markdown (.md)",
                        data=cached_res,
                        file_name=f"{Path(cached_name).stem if cached_name else 'deepseek'}.md",
                        mime="text/markdown",
                        key="btn_dl_cached_ds_md"
                    )
                with col_dl2:
                    st.download_button(
                        "📥 Tải tệp Văn bản (.txt)",
                        data=cached_res,
                        file_name=f"{Path(cached_name).stem if cached_name else 'deepseek'}.txt",
                        mime="text/plain",
                        key="btn_dl_cached_ds_txt"
                    )
            else:
                ds_output_box.info("Nội dung sau khi trích xuất & phân tích bằng DeepSeek AI sẽ hiển thị tại đây.")

    # ========================================================
    # CHẾ ĐỘ 5: TRÍCH XUẤT BẰNG GEMINI AI MODEL
    # ========================================================
    else:
        col_doc1, col_doc2 = st.columns([1, 1], gap="large")
        
        with col_doc1:
            uploaded_doc = st.file_uploader(
                "Tải lên tài liệu PDF hoặc Word (.docx) để phân tích bằng AI:",
                type=["pdf", "docx"],
                key="uploader_ai_mode",
                help="Gemini Multimodal VLM hỗ trợ tối đa 50MB"
            )
            
            doc_bytes = None
            doc_filename = ""
            doc_type = ""
            docx_markdown_content = ""
            
            if uploaded_doc:
                doc_bytes = uploaded_doc.getvalue()
                doc_filename = uploaded_doc.name
                doc_type = "pdf" if doc_filename.lower().endswith(".pdf") else "docx"
                file_size_mb = len(doc_bytes) / (1024 * 1024)
                
                st.markdown(
                    f"""
                    <div class="feature-card">
                        <b>📁 Tệp đã chọn:</b> <code>{doc_filename}</code><br>
                        <b>📦 Dung lượng:</b> <code>{file_size_mb:.2f} MB</code> | 
                        <b>Định dạng:</b> <span class="metric-chip">{doc_type.upper()}</span> | 
                        <b>AI Model:</b> <code>{selected_model}</code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if doc_type == "pdf":
                    meta = get_pdf_metadata(doc_bytes)
                    st.caption(f"📑 Số trang ước tính: **{meta.get('pages', 'N/A')} trang** (Gemini đọc cả text, ảnh scan & biểu đồ)")
                else:
                    docx_markdown_content = extract_docx_content(doc_bytes)
                    word_count = len(docx_markdown_content.split())
                    st.caption(f"📝 Số từ ước tính: **~{word_count:,} từ** (Tự động chuyển bảng sang Markdown)")
                
                st.markdown("##### 🎯 Tác vụ gợi ý cho AI:")
                doc_preset_map = {
                    "📝 Trích xuất toàn bộ nội dung (Full OCR & Extraction)": 
                        "Hãy đọc và trích xuất toàn bộ nội dung văn bản trong tài liệu này một cách đầy đủ và chi tiết nhất. "
                        "Giữ nguyên các đề mục, danh sách, thứ tự xuống dòng và tiếng Việt có dấu. "
                        "Nếu có bảng biểu, hãy chuyển thành bảng Markdown chuẩn (| Cột 1 | Cột 2 |).",
                    
                    "📊 Trích xuất Bảng biểu & Số liệu (Tables to Markdown)": 
                        "Hãy tìm và trích xuất TOÀN BỘ các bảng biểu, số liệu thống kê và danh mục trong tài liệu này. "
                        "Trình bày lại dưới dạng bảng Markdown hoàn chỉnh kèm theo tên hoặc ngữ cảnh của từng bảng.",
                    
                    "📌 Tóm tắt toàn diện tài liệu (Executive Summary)": 
                        "Hãy phân tích và tóm tắt toàn bộ tài liệu này bao gồm:\n"
                        "1. Mục đích và thông điệp chính của tài liệu.\n"
                        "2. Các điểm cốt lõi/điều khoản quan trọng nhất (dạng gạch đầu dòng).\n"
                        "3. Những con số, mốc thời gian hoặc lưu ý bắt buộc cần nhớ.\n"
                        "4. Kết luận ngắn gọn.",
                    
                    "🔍 Hỏi đáp / Tra cứu theo tài liệu (Doc Q&A)": 
                        "Dựa hoàn toàn vào nội dung của tài liệu được cung cấp, hãy trả lời chi tiết và chính xác câu hỏi sau:\n"
                        "[Nhập câu hỏi cụ thể của bạn vào đây, ví dụ: Điều kiện để được xét học bổng là gì? Thời hạn nộp hồ sơ khi nào?]",
                    
                    "📋 Trích xuất thông tin ra JSON có cấu trúc": 
                        "Hãy đọc toàn bộ tài liệu và trích xuất các thông tin quan trọng nhất thành một đối tượng JSON chuẩn xác "
                        "(bao gồm tiêu đề, ngày ban hành, các bên liên quan, nội dung chính, bảng dữ liệu nếu có). Chỉ trả về JSON hợp lệ.",
                    
                    "🧪 Tùy chỉnh yêu cầu": 
                        "Hãy đọc kỹ tài liệu trên và thực hiện theo yêu cầu sau:"
                }
                doc_options = list(doc_preset_map.keys())
                selected_doc_preset = st.radio("Chọn loại tác vụ AI:", doc_options, index=0, key="ai_doc_preset_radio")
            else:
                st.info("👈 Hãy tải lên tệp PDF hoặc Word (.docx) ở khung bên trái để bắt đầu.")
                selected_doc_preset = "🧪 Tùy chỉnh yêu cầu"
                doc_preset_map = {"🧪 Tùy chỉnh yêu cầu": "Hãy phân tích nội dung tài liệu này."}

        with col_doc2:
            default_doc_prompt = doc_preset_map.get(selected_doc_preset, "Hãy trích xuất toàn bộ nội dung tài liệu.")
            
            doc_prompt = st.text_area(
                "Câu lệnh hoặc câu hỏi yêu cầu Gemini AI:",
                value=default_doc_prompt,
                height=130,
                key="ai_doc_prompt_area"
            )
            
            doc_analyze_btn = st.button("🚀 Bắt đầu Trích xuất bằng Gemini AI", type="primary", use_container_width=True, key="btn_run_ai_doc")
            
            doc_output_box = st.container()
            
            if doc_analyze_btn:
                if not active_key:
                    st.error("⚠️ Vui lòng nhập Gemini API Key ở Sidebar!")
                elif not uploaded_doc or not doc_bytes:
                    st.warning("⚠️ Vui lòng tải lên tệp PDF hoặc Word (.docx) trước!")
                elif not doc_prompt.strip():
                    st.warning("⚠️ Vui lòng nhập câu lệnh yêu cầu!")
                else:
                    with st.spinner("✨ Gemini đang đọc và phân tích tài liệu (có thể mất vài giây với tài liệu lớn)..."):
                        doc_result_placeholder = doc_output_box.empty()
                        start_time = time.time()
                        full_doc_resp = ""
                        finish_reason = None
                        actual_model_version = None
                        
                        try:
                            client = get_genai_client(active_key)
                            
                            if doc_type == "pdf":
                                pdf_part = types.Part.from_bytes(data=doc_bytes, mime_type="application/pdf")
                                contents_payload = [pdf_part, doc_prompt]
                            else:
                                contents_payload = [
                                    f"Tên tệp: {doc_filename}\nĐịnh dạng: Microsoft Word (.docx)\n\n--- BẮT ĐẦU NỘI DUNG TÀI LIỆU ---\n{docx_markdown_content}\n--- KẾT THÚC NỘI DUNG TÀI LIỆU ---",
                                    doc_prompt
                                ]
                            
                            # Step 1: Streaming
                            try:
                                stream = client.models.generate_content_stream(
                                    model=selected_model,
                                    contents=contents_payload,
                                    config=client_config
                                )
                                for chunk in stream:
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
                                        full_doc_resp += chunk_text
                                        doc_result_placeholder.markdown(full_doc_resp + " ▌")
                            except Exception:
                                pass
                            
                            # Step 2: Fallback
                            if not full_doc_resp.strip():
                                direct_resp = client.models.generate_content(
                                    model=selected_model,
                                    contents=contents_payload,
                                    config=client_config
                                )
                                if direct_resp.text:
                                    full_doc_resp = direct_resp.text
                                if getattr(direct_resp, "model_version", None):
                                    actual_model_version = direct_resp.model_version
                                if hasattr(direct_resp, "candidates") and direct_resp.candidates:
                                    finish_reason = direct_resp.candidates[0].finish_reason
                            
                            elapsed = time.time() - start_time
                            
                            # Step 3: Render and persist output
                            if full_doc_resp.strip():
                                doc_result_placeholder.markdown(full_doc_resp)
                                st.session_state.last_doc_result = full_doc_resp
                                st.session_state.last_doc_time = elapsed
                                st.session_state.last_doc_model = actual_model_version or selected_model
                                st.session_state.last_doc_filename = doc_filename
                                
                                info_msg = f"⏱️ Thời gian: **{elapsed:.2f}s** | Tệp: `{doc_filename}` | Model: `{selected_model}`"
                                if actual_model_version and actual_model_version != selected_model:
                                    info_msg += f" | ⚡ Phục vụ: `{actual_model_version}`"
                                st.success("✅ Hoàn thành phân tích tài liệu bằng Gemini AI!")
                                st.caption(info_msg)
                                
                                col_dl1, col_dl2 = st.columns(2)
                                with col_dl1:
                                    st.download_button(
                                        "📥 Tải văn bản (.txt)",
                                        data=full_doc_resp,
                                        file_name=f"{Path(doc_filename).stem}_ai_extracted.txt",
                                        mime="text/plain",
                                        key="btn_dl_ai_doc_txt"
                                    )
                                with col_dl2:
                                    st.download_button(
                                        "📥 Tải định dạng Markdown (.md)",
                                        data=full_doc_resp,
                                        file_name=f"{Path(doc_filename).stem}_ai_extracted.md",
                                        mime="text/markdown",
                                        key="btn_dl_ai_doc_md"
                                    )
                            else:
                                st.error(f"⚠️ Không nhận được phản hồi từ Gemini (Lý do: `{finish_reason}`).")
                                st.info("💡 **Gợi ý khắc phục:**\n"
                                        "- Tăng **Max Output Tokens** ở Sidebar lên 4096 hoặc 8192.\n"
                                        "- Chọn model khác như **`gemini-3.1-flash-lite`** hoặc **`gemini-3.5-flash-lite`**.")
                                
                        except errors.APIError as e:
                            if e.code == 429:
                                st.error(f"❌ **Lỗi 429 - Hạn mức (Quota) của model `{selected_model}` đã đạt giới hạn trong ngày!**")
                                st.info(
                                    "💡 **Cách giải quyết ngay lập tức:**\n"
                                    "1. Nhìn sang **Sidebar (thanh bên trái)** -> Mục **Lựa chọn Model**.\n"
                                    "2. Chọn sang model khác (ví dụ: **`gemini-3.1-flash-lite`** hoặc **`gemini-3.5-flash-lite`**) vì mỗi model có hạn mức quota riêng biệt.\n"
                                    "3. Hoặc chuyển sang **Chế độ 1: Trích xuất thông thường (Local Parser)** ở phía trên để đọc nội dung ngay lập tức mà không cần gọi API!"
                                )
                            else:
                                st.error(f"❌ Lỗi Gemini API ({e.code}): {e.message}")
                        except Exception as e:
                            st.error(f"❌ Lỗi: {str(e)}")
                            
            elif st.session_state.get("last_doc_result"):
                doc_output_box.markdown(f"##### 📄 Kết quả phân tích gần nhất (`{st.session_state.get('last_doc_filename', 'Tài liệu')}`):")
                doc_output_box.markdown(st.session_state.last_doc_result)
                if st.session_state.get("last_doc_time"):
                    doc_output_box.caption(f"⏱️ Thời gian phản hồi: {st.session_state.last_doc_time:.2f}s | Model: {st.session_state.get('last_doc_model', '')}")
                
                col_dl1, col_dl2 = doc_output_box.columns(2)
                with col_dl1:
                    st.download_button(
                        "📥 Tải văn bản (.txt)",
                        data=st.session_state.last_doc_result,
                        file_name="ai_extracted_document.txt",
                        mime="text/plain",
                        key="btn_dl_ai_cached_txt"
                    )
                with col_dl2:
                    st.download_button(
                        "📥 Tải định dạng Markdown (.md)",
                        data=st.session_state.last_doc_result,
                        file_name="ai_extracted_document.md",
                        mime="text/markdown",
                        key="btn_dl_ai_cached_md"
                    )

