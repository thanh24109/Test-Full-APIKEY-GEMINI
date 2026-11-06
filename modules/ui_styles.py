import streamlit as st

def apply_custom_css():
    """Apply global premium dark-theme CSS and custom styled components."""
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

    /* ========================================================
       Gemini Live API Voice Studio Styling
       ======================================================== */
    .live-badge {
        background: linear-gradient(90deg, #ef4444, #f97316);
        color: white;
        padding: 3px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.4);
    }
    .live-pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #ffffff;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7);
        animation: live-pulse 1.6s infinite;
    }
    @keyframes live-pulse {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7); }
        70% { transform: scale(1.15); box-shadow: 0 0 0 8px rgba(255, 255, 255, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
    }
    .voice-studio-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(129, 140, 248, 0.3);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .dialog-turn-user {
        background: rgba(49, 46, 129, 0.35);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .dialog-turn-ai {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 16px;
    }
    audio {
        width: 100% !important;
        border-radius: 8px !important;
        margin-top: 6px !important;
        margin-bottom: 6px !important;
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

