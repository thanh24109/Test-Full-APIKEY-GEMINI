import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Reconfigure stdout to utf-8 for Windows terminal
sys.stdout.reconfigure(encoding="utf-8")

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY", "").strip()

print("=" * 60)
print("     KIỂM TRA KẾT NỐI GOOGLE GEMINI API KEY")
print("=" * 60)

if not api_key:
    print("❌ LỖI: Không tìm thấy GEMINI_API_KEY trong file .env!")
    print("Vui lòng thêm: GEMINI_API_KEY=AIzaSy... vào file .env")
    sys.exit(1)

masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
print(f"🔑 API Key phát hiện : {masked_key} (Độ dài: {len(api_key)} ký tự)")
print("-" * 60)

try:
    from google import genai
    from google.genai import types, errors
    from PIL import Image, ImageDraw
except ImportError as e:
    print(f"❌ Thiếu thư viện: {e}")
    sys.exit(1)

try:
    client = genai.Client(api_key=api_key)
    
    # --- TEST 1: Xác thực & Liệt kê Models ---
    print("1️⃣ Đang kiểm tra tính hợp lệ và truy vấn danh sách Model...")
    t0 = time.time()
    models = list(client.models.list())
    t_models = time.time() - t0
    gemini_models = [m.name.replace("models/", "") for m in models if "gemini" in m.name]
    print(f"   ✅ Xác thực thành công! ({t_models:.2f}s)")
    print(f"   📋 Tổng cộng: {len(gemini_models)} models khả dụng trên API Key của bạn.")
    print(f"   💡 Một số model chính: {', '.join(gemini_models[:5])}")
    print("-" * 60)

    # --- TEST 2: Sinh văn bản (Text Generation) ---
    test_model = "gemini-3.5-flash"
    print(f"2️⃣ Đang kiểm tra sinh nội dung văn bản (Model: {test_model})...")
    t0 = time.time()
    resp = client.models.generate_content(
        model=test_model,
        contents="Hãy trả lời ngắn gọn đúng 1 câu bằng tiếng Việt: Bạn có đang kết nối và hoạt động tốt không?"
    )
    t_gen = time.time() - t0
    response_text = resp.text.strip()
    print(f"   ✅ Phản hồi thành công! ({t_gen:.2f}s)")
    print(f"   🤖 Gemini trả lời: \"{response_text}\"")
    print("-" * 60)

    # --- TEST 3: Thị giác Đa phương thức (Multimodal Vision / OCR) ---
    print(f"3️⃣ Đang kiểm tra năng lực thị giác (VLM / OCR) với ảnh mẫu...")
    img = Image.new("RGB", (320, 80), color=(240, 244, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 28), "GEMINI API OK - 2026", fill=(30, 41, 59))
    
    t0 = time.time()
    v_resp = client.models.generate_content(
        model=test_model,
        contents=[img, "Đọc chính xác chữ viết trong hình ảnh này."]
    )
    t_vis = time.time() - t0
    ocr_result = v_resp.text.strip()
    print(f"   ✅ Phân tích ảnh thành công! ({t_vis:.2f}s)")
    print(f"   📸 Kết quả OCR: \"{ocr_result}\"")
    print("-" * 60)

    print("🎉 KẾT LUẬN: API KEY CỦA BẠN HỢP LỆ VÀ HOẠT ĐỘNG HOÀN HẢO 100%!")
    print("=" * 60)

except errors.APIError as e:
    print(f"❌ LỖI GEMINI API ({e.code}): {e.message}")
    sys.exit(1)
except Exception as e:
    print(f"❌ LỖI KẾT NỐI: {str(e)}")
    sys.exit(1)
