import os
import time
import json
import io
import base64
import tempfile
from pathlib import Path
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# Document processing libraries
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

# pypdfium2 for fast, high-quality visual PDF page rendering (Multimodal VLM OCR)
try:
    import pypdfium2 as pdfium
    PDFIUM_AVAILABLE = True
except ImportError:
    PDFIUM_AVAILABLE = False

# Microsoft MarkItDown library
try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False

# Docling library (IBM Research / DS4SD)
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

# Import Google GenAI SDK
try:
    from google import genai
    from google.genai import types, errors
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Import OpenAI SDK for DeepSeek API
try:
    from openai import OpenAI, AuthenticationError, APIError as OpenAIAPIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ========================================================
# Page Configuration
# ========================================================
st.set_page_config(
    page_title="Gemini API Explorer & Demo",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv(override=True)
ENV_FILE_PATH = Path(".env")

# ========================================================
# Custom CSS for Modern, Premium UI
# ========================================================
st.markdown("""
<style>
    /* Google / Gemini Gradient Header */
    .gemini-gradient-text {
        background: linear-gradient(135deg, #4285F4 0%, #9B72CF 50%, #D96570 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        display: inline-block;
    }
    
    .hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
    }
    
    .status-badge-ok {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.4);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .status-badge-warn {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .feature-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .feature-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(30, 41, 59, 0.8);
    }
    
    .metric-chip {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-family: monospace;
        margin-right: 6px;
    }

    /* Streamlit components refinement */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
    }
    
    /* Pre code block styling */
    pre {
        border-radius: 8px !important;
        background-color: #0d1117 !important;
    }

    /* ========================================================
       Spacious & Beautiful Drag & Drop File Upload Zone
       ======================================================== */
    [data-testid="stFileUploader"] {
        margin-bottom: 16px;
    }
    
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #6366f1 !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.85) 100%) !important;
        border-radius: 14px !important;
        padding: 30px 20px !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        min-height: 160px !important;
        cursor: pointer !important;
        transition: all 0.25s ease-in-out !important;
    }
    
    [data-testid="stFileUploader"] section:hover,
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #818cf8 !important;
        background: linear-gradient(135deg, rgba(49, 46, 129, 0.45) 0%, rgba(30, 41, 59, 0.95) 100%) !important;
        box-shadow: 0 0 24px rgba(99, 102, 241, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* Prominent Drag & Drop Guidance Label */
    [data-testid="stFileUploader"] section::before,
    [data-testid="stFileUploadDropzone"]::before {
        content: "📥 Kéo & thả tệp vào đây (Drag & Drop)";
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        display: block !important;
        letter-spacing: 0.3px !important;
        margin-bottom: 4px !important;
    }
    
    [data-testid="stFileUploader"] section:has([data-testid="stFileUploaderFile"])::before,
    [data-testid="stFileUploadDropzone"]:has([data-testid="stFileUploaderFile"])::before {
        content: "✅ Tệp đã được chọn (Kéo thả tệp khác để thay thế)" !important;
        font-size: 0.95rem !important;
        color: #4ade80 !important;
    }

    /* Modern Gradient Upload Button inside Dropzone */
    [data-testid="stFileUploader"] section button,
    [data-testid="stFileUploadDropzone"] button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        padding: 8px 26px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    
    [data-testid="stFileUploader"] section button:hover,
    [data-testid="stFileUploadDropzone"] button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
        transform: scale(1.03) !important;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.5) !important;
    }

    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploadDropzone"] span {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stFileUploader"] section small,
    [data-testid="stFileUploadDropzone"] small {
        color: #64748b !important;
    }
</style>
""", unsafe_allow_html=True)

# ========================================================
# Helper Functions
# ========================================================
def get_env_api_key() -> str:
    """Retrieve Gemini API key from environment variable or .env file."""
    return os.getenv("GEMINI_API_KEY", "").strip()

def get_env_deepseek_key() -> str:
    """Retrieve DeepSeek API key from environment variable or .env file."""
    return os.getenv("DEEPSEEK_API_KEY", "").strip()

def save_both_keys_to_env(gemini_key: str = None, deepseek_key: str = None) -> bool:
    """Save both Gemini and DeepSeek API keys to .env file preserving existing values."""
    try:
        g_key = gemini_key if gemini_key is not None else get_env_api_key()
        d_key = deepseek_key if deepseek_key is not None else get_env_deepseek_key()
        
        lines = [
            "# AI API Configurations",
            f"GEMINI_API_KEY={g_key.strip()}",
            f"DEEPSEEK_API_KEY={d_key.strip()}",
            ""
        ]
        with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        os.environ["GEMINI_API_KEY"] = g_key.strip()
        os.environ["DEEPSEEK_API_KEY"] = d_key.strip()
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu vào file .env: {e}")
        return False

def save_api_key_to_env(key: str) -> bool:
    """Save Gemini API key to .env file."""
    return save_both_keys_to_env(gemini_key=key)

def save_deepseek_key_to_env(key: str) -> bool:
    """Save DeepSeek API key to .env file."""
    return save_both_keys_to_env(deepseek_key=key)

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

def get_genai_client(api_key: str):
    """Create and return a Google GenAI Client instance."""
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def validate_gemini_api_key(api_key: str):
    """Validate API key by querying client.models.list()."""
    if not api_key:
        return False, "Vui lòng nhập API Key.", []
    
    try:
        client = get_genai_client(api_key)
        # Fetch available models
        models_pager = client.models.list()
        gemini_models = []
        for m in models_pager:
            name = m.name or ""
            # Strip 'models/' prefix if present
            clean_name = name.replace("models/", "")
            if "gemini" in clean_name.lower():
                gemini_models.append({
                    "id": clean_name,
                    "display_name": getattr(m, "display_name", clean_name),
                    "description": getattr(m, "description", ""),
                    "input_token_limit": getattr(m, "input_token_limit", "N/A"),
                    "output_token_limit": getattr(m, "output_token_limit", "N/A")
                })
        return True, "API Key hợp lệ! Đã kết nối thành công tới Gemini API.", gemini_models
    except errors.APIError as e:
        error_msg = f"Lỗi API ({e.code}): {e.message}"
        if "API_KEY_INVALID" in str(e) or e.code == 400:
            error_msg = "API Key không hợp lệ. Vui lòng kiểm tra lại trên Google AI Studio."
        return False, error_msg, []
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", []

def get_deepseek_client(api_key: str):
    """Create and return an OpenAI client configured for DeepSeek API."""
    if not api_key or not OPENAI_AVAILABLE:
        return None
    return OpenAI(
        api_key=api_key.strip(),
        base_url="https://api.deepseek.com"
    )

def validate_deepseek_api_key(api_key: str):
    """Validate DeepSeek API key by querying the /models endpoint."""
    if not api_key:
        return False, "Vui lòng nhập DeepSeek API Key.", []
    if not OPENAI_AVAILABLE:
        return False, "Thư viện openai chưa được cài đặt. Chạy: pip install openai", []
    
    try:
        client = get_deepseek_client(api_key)
        models_resp = client.models.list()
        deepseek_models = []
        for m in getattr(models_resp, "data", []):
            m_id = getattr(m, "id", "")
            deepseek_models.append({
                "id": m_id,
                "display_name": m_id,
                "description": "DeepSeek Official Model"
            })
        if not deepseek_models:
            deepseek_models = [
                {"id": "deepseek-chat", "display_name": "deepseek-chat (V3)", "description": "Mô hình đa năng, tốc độ cao, giá siêu rẻ"},
                {"id": "deepseek-reasoner", "display_name": "deepseek-reasoner (R1)", "description": "Mô hình suy luận logic chuyên sâu với Chain of Thought"}
            ]
        return True, "DeepSeek API Key hợp lệ! Đã kết nối thành công tới DeepSeek API.", deepseek_models
    except AuthenticationError:
        return False, "DeepSeek API Key không hợp lệ hoặc đã hết hạn (401 Unauthorized). Hãy kiểm tra lại tại platform.deepseek.com.", []
    except Exception as e:
        return False, f"Lỗi kết nối DeepSeek: {str(e)}", []

# ========================================================
# Session State Initialization
# ========================================================
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = None

if "available_models" not in st.session_state:
    st.session_state.available_models = []

if "last_tested_key" not in st.session_state:
    st.session_state.last_tested_key = ""

# Quick starter prompt placeholder
if "starter_prompt" not in st.session_state:
    st.session_state.starter_prompt = None

if "last_vision_result" not in st.session_state:
    st.session_state.last_vision_result = None

if "last_vision_time" not in st.session_state:
    st.session_state.last_vision_time = None

if "last_doc_result" not in st.session_state:
    st.session_state.last_doc_result = None

if "last_doc_time" not in st.session_state:
    st.session_state.last_doc_time = None

if "last_local_doc_result" not in st.session_state:
    st.session_state.last_local_doc_result = None

if "last_local_doc_time" not in st.session_state:
    st.session_state.last_local_doc_time = None

if "last_local_doc_stats" not in st.session_state:
    st.session_state.last_local_doc_stats = {}

if "last_markitdown_result" not in st.session_state:
    st.session_state.last_markitdown_result = None

if "last_markitdown_time" not in st.session_state:
    st.session_state.last_markitdown_time = None

if "last_markitdown_stats" not in st.session_state:
    st.session_state.last_markitdown_stats = {}

if "last_markitdown_filename" not in st.session_state:
    st.session_state.last_markitdown_filename = ""

if "md_sample_selected" not in st.session_state:
    st.session_state.md_sample_selected = None

if "last_docling_result" not in st.session_state:
    st.session_state.last_docling_result = None

if "last_docling_time" not in st.session_state:
    st.session_state.last_docling_time = None

if "last_docling_stats" not in st.session_state:
    st.session_state.last_docling_stats = {}

if "last_docling_filename" not in st.session_state:
    st.session_state.last_docling_filename = ""

if "docling_sample_selected" not in st.session_state:
    st.session_state.docling_sample_selected = None

if "deepseek_api_key_valid" not in st.session_state:
    st.session_state.deepseek_api_key_valid = None

if "last_tested_deepseek_key" not in st.session_state:
    st.session_state.last_tested_deepseek_key = ""

if "available_deepseek_models" not in st.session_state:
    st.session_state.available_deepseek_models = []

if "last_deepseek_doc_result" not in st.session_state:
    st.session_state.last_deepseek_doc_result = None

if "last_deepseek_doc_reasoning" not in st.session_state:
    st.session_state.last_deepseek_doc_reasoning = None

if "last_deepseek_doc_time" not in st.session_state:
    st.session_state.last_deepseek_doc_time = None

if "last_deepseek_doc_model" not in st.session_state:
    st.session_state.last_deepseek_doc_model = ""

if "last_deepseek_doc_filename" not in st.session_state:
    st.session_state.last_deepseek_doc_filename = ""

if "last_deepseek_doc_stats" not in st.session_state:
    st.session_state.last_deepseek_doc_stats = {}

if "deepseek_sample_selected" not in st.session_state:
    st.session_state.deepseek_sample_selected = None

if "chat_provider" not in st.session_state:
    st.session_state.chat_provider = "gemini"

# ========================================================
# Sidebar: API Key Configuration & Hyperparameters
# ========================================================
with st.sidebar:
    st.markdown("### ⚙️ Cấu hình API Key & Providers")
    
    sidebar_tab_gemini, sidebar_tab_deepseek = st.tabs(["✨ Google Gemini", "🐋 DeepSeek AI"])
    
    with sidebar_tab_gemini:
        # 1. Gemini API Key Input
        saved_key = get_env_api_key()
        api_key_input = st.text_input(
            "🔑 Gemini API Key",
            value=saved_key,
            type="password",
            placeholder="AIzaSy...",
            help="Lấy API Key miễn phí từ Google AI Studio (https://aistudio.google.com/app/apikey)"
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
            unsafe_allow_html=True
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
            key="sel_gemini_model_box"
        )
        if selected_option == "Tùy chỉnh (Nhập tên model)...":
            selected_model = st.text_input("Tên model tùy chỉnh:", value="gemini-3.5-flash", key="custom_gemini_name")
        else:
            selected_model = selected_option

    with sidebar_tab_deepseek:
        saved_ds_key = get_env_deepseek_key()
        deepseek_key_input = st.text_input(
            "🐋 DeepSeek API Key",
            value=saved_ds_key,
            type="password",
            placeholder="sk-...",
            help="Lấy API Key tại DeepSeek Platform: https://platform.deepseek.com/api_keys"
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
            unsafe_allow_html=True
        )

        st.markdown("##### 🐋 Mô hình DeepSeek:")
        ds_models_list = [
            "deepseek-flash — 💰 RẺ NHẤT & 🖼️ VISION ($0.003 - $0.15 / 1M)",
            "deepseek-v4-pro — 🚀 Flagship ($0.66 - $1.32 / 1M)",
            "deepseek-chat (V3 Legacy Alias) — ⚡ Tương thích ngược",
            "deepseek-reasoner (R1 Legacy Alias) — 🧠 Suy luận sâu CoT",
            "Tùy chỉnh (Nhập tên model)..."
        ]
        selected_ds_opt = st.selectbox(
            "Chọn model DeepSeek:",
            options=ds_models_list,
            index=0,
            key="sel_deepseek_model_box",
            help="Theo tài liệu DeepSeek Pricing chính thức: deepseek-flash là model RẺ NHẤT ($0.15/1M input, $0.003 nếu cache hit) và là model DUY NHẤT hỗ trợ Vision."
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

        # Quick price badge & summary below selector
        if selected_deepseek_model == "deepseek-flash":
            st.caption("💵 **Giá rẻ nhất & Vision:** Cache Hit **$0.003 - $0.006**/1M | Input **$0.15 - $0.30**/1M | Output **$0.60 - $1.20**/1M.")
        elif selected_deepseek_model == "deepseek-v4-pro":
            st.caption("🚀 **Pro Flagship:** Cache Hit **$0.022 - $0.044**/1M | Input **$0.66 - $1.32**/1M | Output **$1.98 - $3.96**/1M (Không hỗ trợ Vision).")
        elif selected_deepseek_model == "deepseek-chat":
            st.caption("⚡ **Legacy V3 Alias:** Input **$0.14**/1M tokens ($0.014 nếu Cache Hit) | Output **$0.28**/1M tokens.")
        elif selected_deepseek_model == "deepseek-reasoner":
            st.caption("🧠 **Legacy R1 Alias:** Input **$0.55**/1M tokens | Output **$2.19**/1M tokens (kèm CoT Thinking).")

    st.markdown("---")

    # 3. Hyperparameters
    st.markdown("### 🎛️ Tham số sinh nội dung")
    temperature = st.slider(
        "Nhiệt độ (Temperature)",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.05,
        help="0.0: Logic, nhất quán, sự thật | 1.0+: Sáng tạo, phong phú"
    )
    
    top_p = st.slider(
        "Top-P (Nucleus Sampling)",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        step=0.05,
        help="Giới hạn phân phối xác suất các token được chọn"
    )
    
    max_tokens = st.slider(
        "Max Output Tokens",
        min_value=128,
        max_value=8192,
        value=2048,
        step=128,
        help="Độ dài tối đa của phản hồi trả về"
    )

    system_instruction = st.text_area(
        "System Instruction (Chỉ dẫn hệ thống)",
        value="Bạn là một trợ lý trí tuệ nhân tạo chuyên nghiệp, nhiệt tình và luôn trả lời bằng tiếng Việt rõ ràng, mạch lạc.",
        help="Định hình vai trò và nguyên tắc phản hồi của Gemini"
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
        unsafe_allow_html=True
    )

# ========================================================
# Main Page Header & Hero Section
# ========================================================
st.markdown("""
<div class="hero-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem;">
                <span class="gemini-gradient-text">Gemini API Explorer</span> ✨
            </h1>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 1.05rem;">
                Ứng dụng trải nghiệm và kiểm thử Google Gemini API Key: Trò chuyện Streaming, Thị giác Đa phương thức và Prompt Lab.
            </p>
        </div>
        <div>
            <a href="https://aistudio.google.com/app/apikey" target="_blank" style="text-decoration: none;">
                <button style="
                    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                    color: white;
                    border: none;
                    padding: 10px 18px;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.4);
                ">
                    🔑 Lấy API Key miễn phí ↗
                </button>
            </a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Warning banner if API keys are missing
active_key = api_key_input or get_env_api_key()
active_deepseek_key = deepseek_key_input or get_env_deepseek_key()

if not active_key and not active_deepseek_key:
    st.info(
        "👋 **Chào bạn!** Ứng dụng hỗ trợ cả **Google Gemini API** và **DeepSeek API**. "
        "Hãy nhập API Key ở thanh bên trái (Sidebar) để bắt đầu trải nghiệm!\n\n"
        "- Lấy Gemini API Key miễn phí: [Google AI Studio](https://aistudio.google.com/app/apikey)\n"
        "- Lấy DeepSeek API Key: [DeepSeek Platform](https://platform.deepseek.com/api_keys)",
        icon="👉"
    )

# Safety settings to avoid false positives on administrative, legal, and academic documents
safety_settings = [
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, threshold=types.HarmBlockThreshold.BLOCK_NONE),
] if GENAI_AVAILABLE else None

# Create Client Config
client_config = types.GenerateContentConfig(
    temperature=temperature,
    top_p=top_p,
    max_output_tokens=max_tokens,
    safety_settings=safety_settings,
    system_instruction=system_instruction.strip() if system_instruction.strip() else None
) if GENAI_AVAILABLE else None

# ========================================================
# Main Navigation Tabs
# ========================================================
tab_chat, tab_vision, tab_docs_extract, tab_tools, tab_docs = st.tabs([
    "💬 Trò chuyện Chatbot",
    "🖼️ Thị giác Đa phương thức (Vision)",
    "📄 Trích xuất Tài liệu (PDF & DOCX)",
    "⚡ Prompt Lab & Tác vụ mẫu",
    "📚 Thông tin Models & Tài liệu"
])

# ========================================================
# TAB 1: 💬 Trò chuyện Chatbot (Chat & Streaming)
# ========================================================
with tab_chat:
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

# ========================================================
# TAB 2: 🖼️ Thị giác Đa phương thức (Vision / Multimodal)
# ========================================================
with tab_vision:
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
            
            # Quick presets with rich, effective prompts
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
                            
                            # Step 1: Attempt streaming for instant visual feedback
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
                                    
                                    # Inspect parts directly if chunk.text was empty
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
                            except Exception as stream_ex:
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
                                st.success(f"✅ Hoàn thành phân tích!")
                                st.caption(info_msg)
                                
                                # Download option
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

# ========================================================
# TAB 3: 📄 Trích xuất Tài liệu (PDF & DOCX)
# ========================================================
with tab_docs_extract:
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
                "- **Hỗ trợ 2 model hàng đầu:**\n"
                "  • **`deepseek-chat` (V3):** Phản hồi siêu nhanh, chi phí siêu rẻ ($0.14/1M tokens), bóc tách văn bản cực sạch.\n"
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
            
            # Quick sample buttons
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
                                
                                if PDFIUM_AVAILABLE and len(target_bytes) > 0:
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
                cached_bytes = st.session_state.get("last_markitdown_bytes")
                
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
                    if cached_stats.get("is_scanned_pdf"):
                        st.markdown(
                            f"""
                            <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 12px; padding: 18px; margin: 12px 0;">
                                <div style="font-weight: 700; color: #fbbf24; font-size: 1.05rem; margin-bottom: 8px;">
                                    📑 Nguyên nhân kỹ thuật: Tài liệu là PDF Quét dạng Ảnh (Scanned / Image-Only PDF)
                                </div>
                                <ul style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.6; margin-bottom: 14px;">
                                    <li>Tệp <code>{cached_name}</code> là tài liệu scan/chụp ảnh giấy tờ (hoàn toàn không chứa lớp văn bản kỹ thuật số).</li>
                                    <li><b>Chế độ 2 (Microsoft MarkItDown)</b> là thư viện bóc tách văn bản offline, không hỗ trợ nhận diện ký tự quang học (OCR Vision).</li>
                                </ul>
                                <div style="background: rgba(15, 23, 42, 0.7); border-radius: 10px; padding: 14px; border-left: 4px solid #38bdf8;">
                                    <div style="font-weight: 700; color: #38bdf8; font-size: 0.95rem; margin-bottom: 6px;">
                                        💡 Giải pháp trích xuất toàn diện:
                                    </div>
                                    <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.6;">
                                        👉 Hãy chọn <b>Chế độ 4: DeepSeek AI (Multimodal VLM - OCR Scan)</b> hoặc <b>Chế độ 5: Google Gemini AI (Multimodal VLM)</b> ở phần tùy chọn phía trên để OCR quét 100% hình ảnh sang Markdown!
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                md_box.info("Nội dung Markdown sau khi trích xuất bằng MarkItDown sẽ hiển thị tại đây.")

    # ========================================================
    # CHẾ ĐỘ 3: TRÍCH XUẤT BẰNG DOCLING (DS4SD / IBM RESEARCH)
    # ========================================================
    elif "Docling" in extraction_mode:
        col_docling1, col_docling2 = st.columns([1, 1], gap="large")
        
        with col_docling1:
            st.markdown("##### 📥 Chọn tệp để chuyển đổi sang Markdown:")
            
            # Quick sample buttons
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
                cached_stats = st.session_state.get("last_docling_stats", {})
                
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
            
            # Quick sample buttons
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
                
                # Model selection inside mode
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
                
                # Configuration per file type
                if target_ext == ".pdf":
                    pdf_page_count = 1
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
                                # Multimodal VLM Mode: Convert PDF pages or image to Base64 JPEG
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
                                # Text Mode (DOCX or text-only PDF)
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
                cached_stats = st.session_state.get("last_deepseek_doc_stats", {})
                
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
                            
                            # Step 2: Fallback to direct call if stream was empty
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

# ========================================================
# TAB 4: ⚡ Prompt Lab & Tác vụ mẫu
# ========================================================
with tab_tools:
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
                        
                        # Streaming result
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

# ========================================================
# TAB 5: 📚 Thông tin Models & Hướng dẫn API Providers
# ========================================================
with tab_docs:
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
