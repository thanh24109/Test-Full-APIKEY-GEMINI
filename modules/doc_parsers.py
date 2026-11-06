import os
import io
import base64
import tempfile
from pathlib import Path
from PIL import Image
import streamlit as st

# Document processing libraries availability
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import pypdfium2 as pdfium
    PDFIUM_AVAILABLE = True
except ImportError:
    PDFIUM_AVAILABLE = False

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

def extract_docx_content(docx_bytes: bytes) -> str:
    """Extract paragraphs and tables from DOCX and convert to structured Markdown text."""
    if not DOCX_AVAILABLE:
        return "Lỗi: Thư viện python-docx chưa được cài đặt."
    try:
        doc = docx.Document(io.BytesIO(docx_bytes))
        sections = []
        
        # Extract paragraphs
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                if p.style and p.style.name and p.style.name.startswith("Heading"):
                    level = p.style.name.replace("Heading", "").strip()
                    prefix = "#" * (int(level) if level.isdigit() else 2)
                    sections.append(f"{prefix} {text}")
                else:
                    sections.append(text)
                    
        # Extract tables
        for idx, table in enumerate(doc.tables):
            table_rows = []
            for r_idx, row in enumerate(table.rows):
                row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                table_rows.append("| " + " | ".join(row_cells) + " |")
                if r_idx == 0:
                    table_rows.append("| " + " | ".join(["---"] * len(row_cells)) + " |")
            if table_rows:
                sections.append(f"\n**[Bảng {idx+1}]**\n" + "\n".join(table_rows))
                
        return "\n\n".join(sections)
    except Exception as e:
        return f"Lỗi đọc file DOCX: {str(e)}"

def get_pdf_metadata(pdf_bytes: bytes):
    """Retrieve basic PDF metadata like page count."""
    if not PYPDF_AVAILABLE:
        return {"pages": "N/A", "error": "pypdf chưa cài đặt"}
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        return {
            "pages": len(reader.pages),
            "is_encrypted": reader.is_encrypted
        }
    except Exception as e:
        return {"pages": "N/A", "error": str(e)}

def pil_image_to_base64_jpeg(pil_img: Image.Image, quality: int = 85, max_dim: int = 1500) -> str:
    """Convert a PIL Image to a base64 JPEG string, optimizing resolution for AI VLM tokens."""
    w, h = pil_img.size
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        pil_img = pil_img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
    if pil_img.mode in ("RGBA", "P"):
        pil_img = pil_img.convert("RGB")
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def render_pdf_to_vlm_images(pdf_bytes: bytes, start_page: int = 1, end_page: int = None, max_pages: int = 10, scale: float = 1.5):
    """
    Render PDF pages to PIL Images and base64 strings for Multimodal VLM OCR (DeepSeek).
    Returns (success, images_list, base64_list, total_pages, error_message).
    """
    if not PDFIUM_AVAILABLE:
        return False, [], [], 0, "Thư viện pypdfium2 chưa được cài đặt."
    try:
        pdf = pdfium.PdfDocument(pdf_bytes)
        total_pages = len(pdf)
        if total_pages == 0:
            return False, [], [], 0, "Tệp PDF không có trang nào."
            
        start_idx = max(0, start_page - 1)
        end_idx = min(total_pages, end_page) if end_page else min(total_pages, start_idx + max_pages)
        
        images_list = []
        base64_list = []
        for i in range(start_idx, end_idx):
            page = pdf[i]
            img = page.render(scale=scale).to_pil()
            b64_str = pil_image_to_base64_jpeg(img, quality=85, max_dim=1400)
            images_list.append(img)
            base64_list.append(b64_str)
            
        return True, images_list, base64_list, total_pages, ""
    except Exception as e:
        return False, [], [], 0, f"Lỗi render PDF sang ảnh VLM: {str(e)}"

def extract_pdf_local_text(pdf_bytes: bytes, max_pages: int = 5) -> str:
    """Extract raw text from PDF using pypdf for quick preview."""
    if not PYPDF_AVAILABLE:
        return ""
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        extracted = []
        num_pages = min(len(reader.pages), max_pages)
        for i in range(num_pages):
            page_text = reader.pages[i].extract_text() or ""
            if page_text.strip():
                extracted.append(f"--- [Trang {i+1}] ---\n{page_text.strip()}")
        return "\n\n".join(extracted)
    except Exception:
        return ""

def extract_pdf_full_local(pdf_bytes: bytes, start_page: int = 1, end_page: int = None):
    """Extract full text from PDF using pypdf locally with page-by-page breakdown."""
    if not PYPDF_AVAILABLE:
        return False, "Thư viện pypdf chưa được cài đặt.", {}
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        if total_pages == 0:
            return False, "Tệp PDF không có trang nào.", {}
        
        start_idx = max(0, start_page - 1)
        end_idx = min(total_pages, end_page) if end_page else total_pages
        
        extracted_pages = []
        total_words = 0
        total_chars = 0
        empty_pages = 0
        
        for idx in range(start_idx, end_idx):
            page = reader.pages[idx]
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            total_words += len(page_text.split())
            total_chars += len(page_text)
            
            if page_text:
                extracted_pages.append(f"### 📄 Trang {idx + 1} / {total_pages}\n\n{page_text}")
            else:
                empty_pages += 1
                extracted_pages.append(f"### 📄 Trang {idx + 1} / {total_pages}\n\n*(Trang này là hình ảnh scan hoặc không có lớp text có thể đọc bằng phương thức thông thường. Bạn hãy chuyển sang chế độ **Trích xuất bằng Gemini AI** để OCR toàn diện).*")
                
        result_text = "\n\n---\n\n".join(extracted_pages)
        stats = {
            "total_pages": total_pages,
            "processed_pages": end_idx - start_idx,
            "total_words": total_words,
            "total_chars": total_chars,
            "empty_pages": empty_pages
        }
        return True, result_text, stats
    except Exception as e:
        return False, f"Lỗi đọc PDF thông thường: {str(e)}", {}

def extract_docx_full_local(docx_bytes: bytes):
    """Extract paragraphs and tables from DOCX with detailed stats."""
    if not DOCX_AVAILABLE:
        return False, "Thư viện python-docx chưa được cài đặt.", {}
    try:
        doc = docx.Document(io.BytesIO(docx_bytes))
        sections = []
        p_count = 0
        t_count = len(doc.tables)
        
        # Extract paragraphs
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                p_count += 1
                if p.style and p.style.name and p.style.name.startswith("Heading"):
                    level = p.style.name.replace("Heading", "").strip()
                    prefix = "#" * (int(level) if level.isdigit() else 2)
                    sections.append(f"{prefix} {text}")
                else:
                    sections.append(text)
                    
        # Extract tables
        for idx, table in enumerate(doc.tables):
            table_rows = []
            for r_idx, row in enumerate(table.rows):
                row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                table_rows.append("| " + " | ".join(row_cells) + " |")
                if r_idx == 0:
                    table_rows.append("| " + " | ".join(["---"] * len(row_cells)) + " |")
            if table_rows:
                sections.append(f"\n**[Bảng {idx+1}]**\n" + "\n".join(table_rows))
                
        result_text = "\n\n".join(sections)
        stats = {
            "paragraphs": p_count,
            "tables": t_count,
            "total_words": len(result_text.split()),
            "total_chars": len(result_text)
        }
        return True, result_text, stats
    except Exception as e:
        return False, f"Lỗi đọc DOCX: {str(e)}", {}

def extract_with_markitdown(file_bytes: bytes, filename: str):
    """
    Extract document (PDF, DOCX, PPTX, XLSX, HTML, etc.) directly into Markdown
    using Microsoft MarkItDown library (100% Local, zero API Quota).
    Includes intelligent fallback for PDFs and scanned-document detection.
    """
    if not MARKITDOWN_AVAILABLE:
        return False, "Thư viện markitdown chưa được cài đặt. Vui lòng cài đặt: pip install 'markitdown[all]'", {}
    
    ext = Path(filename).suffix.lower()
    if not ext:
        ext = ".pdf"
        
    tmp_path = None
    fallback_used = None
    total_pages = 1
    
    # Pre-calculate PDF page count if applicable
    if ext == ".pdf":
        if PDFIUM_AVAILABLE:
            try:
                pdf_peek = pdfium.PdfDocument(io.BytesIO(file_bytes))
                total_pages = len(pdf_peek)
                pdf_peek.close()
            except Exception:
                pass
        elif PYPDF_AVAILABLE:
            try:
                r_peek = pypdf.PdfReader(io.BytesIO(file_bytes))
                total_pages = len(r_peek.pages)
            except Exception:
                pass

    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
            
        md = MarkItDown()
        result = md.convert(tmp_path)
        markdown_text = (result.text_content or "").strip()
        
        # If MarkItDown extracted nothing from a PDF, try local digital fallback (Chrome PDFium / pypdf)
        if not markdown_text and ext == ".pdf":
            if PDFIUM_AVAILABLE:
                try:
                    pdf_doc = pdfium.PdfDocument(io.BytesIO(file_bytes))
                    extracted_parts = []
                    for p_idx in range(len(pdf_doc)):
                        page = pdf_doc[p_idx]
                        textpage = page.get_textpage()
                        p_text = (textpage.get_text_range() or "").strip()
                        if p_text:
                            extracted_parts.append(f"### 📄 Trang {p_idx + 1} / {len(pdf_doc)}\n\n{p_text}")
                    pdf_doc.close()
                    if extracted_parts:
                        markdown_text = "\n\n---\n\n".join(extracted_parts)
                        fallback_used = "pypdfium2 (Chrome Engine)"
                except Exception:
                    pass
                    
            if not markdown_text and PYPDF_AVAILABLE:
                try:
                    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                    extracted_parts = []
                    for p_idx, page in enumerate(reader.pages):
                        p_text = (page.extract_text() or "").strip()
                        if p_text:
                            extracted_parts.append(f"### 📄 Trang {p_idx + 1} / {len(reader.pages)}\n\n{p_text}")
                    if extracted_parts:
                        markdown_text = "\n\n---\n\n".join(extracted_parts)
                        fallback_used = "pypdf"
                except Exception:
                    pass
        
        words = len(markdown_text.split())
        chars = len(markdown_text)
        lines = len(markdown_text.splitlines()) if markdown_text else 0
        is_scanned = (words == 0 and ext == ".pdf")
        
        stats = {
            "total_words": words,
            "total_chars": chars,
            "total_lines": lines,
            "filename": filename,
            "file_type": ext.replace(".", "").upper(),
            "total_pages": total_pages,
            "is_scanned_pdf": is_scanned,
            "fallback_used": fallback_used
        }
        return True, markdown_text, stats
    except Exception as e:
        return False, f"Lỗi Microsoft MarkItDown: {str(e)}", {}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

@st.cache_resource
def get_docling_converter():
    """Cache DocumentConverter instance across runs to avoid reloading layout models."""
    if not DOCLING_AVAILABLE:
        return None
    try:
        return DocumentConverter()
    except Exception:
        return None

def extract_with_docling(file_bytes: bytes, filename: str):
    """
    Extract document (PDF, DOCX, PPTX, Images, HTML, etc.) using Docling (IBM Research / DS4SD).
    Performs AI-based deep layout analysis, reading order reconstruction, and table understanding.
    Returns (success, markdown_text, stats).
    """
    if not DOCLING_AVAILABLE:
        return False, "Thư viện docling chưa được cài đặt. Vui lòng cài đặt: pip install docling", {}
    
    ext = Path(filename).suffix.lower()
    if not ext:
        ext = ".pdf"
        
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
            
        converter = get_docling_converter()
        if converter is None:
            converter = DocumentConverter()
            
        conv_result = converter.convert(tmp_path)
        markdown_text = (conv_result.document.export_to_markdown() or "").strip()
        
        words = len(markdown_text.split())
        chars = len(markdown_text)
        lines = len(markdown_text.splitlines())
        
        doc = conv_result.document
        pages = len(getattr(doc, "pages", [])) if hasattr(doc, "pages") else 1
        tables = len(getattr(doc, "tables", [])) if hasattr(doc, "tables") else 0
        
        stats = {
            "total_words": words,
            "total_chars": chars,
            "total_lines": lines,
            "filename": filename,
            "file_type": ext.replace(".", "").upper(),
            "pages": pages,
            "tables": tables
        }
        return True, markdown_text, stats
    except Exception as e:
        return False, f"Lỗi Docling: {str(e)}", {}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

