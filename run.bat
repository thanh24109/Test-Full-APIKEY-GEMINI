@echo off
title Gemini API Key Streamlit Demo
echo ========================================================
echo   KHOI DONG STREAMLIT DEMO - GOOGLE GEMINI API
echo ========================================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [!] Khong tim thay thu muc .venv. Dang tao moi...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo Dang khoi dong ung dung Streamlit...
streamlit run app.py

pause
