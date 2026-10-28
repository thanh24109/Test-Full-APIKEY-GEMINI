# ✨ Gemini & DeepSeek AI Explorer & Document Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Google%20GenAI-v1.0+-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google GenAI SDK" />
  <img src="https://img.shields.io/badge/DeepSeek%20API-Compatible-0066FF?style=for-the-badge&logo=deepseek&logoColor=white" alt="DeepSeek API" />
  <img src="https://img.shields.io/badge/Microsoft-MarkItDown-00A4EF?style=for-the-badge&logo=microsoft&logoColor=white" alt="Microsoft MarkItDown" />
  <img src="https://img.shields.io/badge/IBM%20Research-Docling-052FAD?style=for-the-badge&logo=ibm&logoColor=white" alt="IBM Docling" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT" />
</p>

Ứng dụng web đa năng được xây dựng trên nền tảng **Streamlit** hiện đại, tích hợp song song hai hệ sinh thái AI hàng đầu: **Google GenAI SDK (`google-genai`)** và **DeepSeek API (`openai` SDK tương thích)**. Nền tảng cung cấp bộ công cụ toàn diện từ trò chuyện tương tác đa mô hình (hỗ trợ suy luận sâu **DeepSeek-R1 CoT**), phân tích thị giác đa phương thức (Multimodal Vision), đến hệ thống **Trích xuất Tài liệu Thông minh 5 Chế độ** (kết hợp các thư viện chuẩn công nghiệp: *Microsoft MarkItDown*, *IBM Docling*, và *AI Vision VLM OCR*).

---

## 🌟 Các Tính Năng Nổi Bật

### 1. 🔐 Quản lý & Xác thực Đa Provider (Dual AI Providers)
- **Tích hợp kép trên Sidebar:**
  - **Tab ✨ Google Gemini:** Hỗ trợ nhập và kiểm tra API Key trực tiếp qua SDK `google-genai`, tự động tải danh sách mô hình thời gian thực (`gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.1-pro`...).
  - **Tab 🐋 DeepSeek AI:** Kết nối endpoint chính thức `https://api.deepseek.com`, kiểm tra xác thực key tức thì, hỗ trợ đầy đủ các model: `deepseek-flash` (Vision + Thinking), `deepseek-v4-pro`, `deepseek-chat` (V3) và `deepseek-reasoner` (R1).
- **Hệ thống trạng thái trực quan:** 🟢 Hợp lệ & Sẵn sàng | 🔴 Sai key / Lỗi kết nối | 🟡 Chưa kiểm tra | ⚪ Chưa nhập key.
- **Lưu trữ an toàn:** Nút **"💾 Lưu vào .env"** giúp ghi đè cấu hình an toàn vào tệp môi trường nội bộ mà không lộ thông tin.

---

### 2. 💬 Trò chuyện Chatbot Đa Mô hình & Trực quan hóa Suy luận (CoT)
- Chuyển đổi linh hoạt giữa **✨ Google Gemini** và **🐋 DeepSeek AI** ngay trong hội thoại.
- **Trực quan hóa tư duy DeepSeek-R1 (Chain-of-Thought):**
  - Tự động tách biệt và hiển thị khối suy luận từng bước (*Thinking Process*) trong quá trình streaming phản hồi.
  - Người dùng có thể theo dõi cách mô hình phân tích logic trước khi đưa ra câu trả lời cuối cùng.
- **Hỗ trợ ngữ cảnh nhiều lượt (Multi-turn Context):** Lưu trữ toàn bộ lịch sử hội thoại.
- **Prompt Starters:** Gợi ý các câu hỏi thông minh giúp bắt đầu hội thoại nhanh chóng.
- **Đo hiệu năng thời gian thực:** Hiển thị độ trễ phản hồi (*Latency ms*) và tên mô hình phục vụ.

---

### 3. 🖼️ Thị giác Đa phương thức (Multimodal Vision)
- Tải lên hình ảnh dung lượng lên đến 25MB (PNG, JPG, JPEG, WEBP).
- Nhận diện ký tự quang học (OCR) cực kỳ chi tiết, đọc bảng số liệu, phân tích giao diện UI/UX và giải thích biểu đồ phức tạp.
- Tải nhanh kết quả phân tích về máy dưới định dạng văn bản `.txt`.

---

### 4. 📄 Trích xuất Tài liệu Thông minh (PDF, DOCX, PPTX, XLSX, HTML, Ảnh)
Khu vực kéo & thả tệp trực quan (Drag & Drop) cùng hệ thống **5 Chế độ trích xuất chuyên sâu**:

| Chế độ | Công nghệ / Thư viện | Tốc độ | Quota / Chi phí | Nhận diện Tài liệu Scan / Ảnh | Đầu ra Markdown |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **⚡ Chế độ 1** | `pypdf` & `python-docx` | ~0.02s | 0 Quota (Miễn phí) | ❌ Chỉ đọc text số | Cắt trang & dựng bảng cơ bản |
| **📑 Chế độ 2** | `Microsoft MarkItDown` | ~0.10s | 0 Quota (Miễn phí) | ❌ Hỗ trợ text số + Fallback | Chuẩn Header (`#`), Bảng (`\|---\|`) |
| **🦆 Chế độ 3** | `Docling (IBM Research)` | ~1.5 - 3s | 0 Quota (AI Offline) | ⚠️ Phân tích Layout AI | Đa cột, DocLayNet, TableFormer |
| **🐋 Chế độ 4** | `DeepSeek Multimodal VLM` | ~2 - 5s | Rẻ nhất (`$0.003/1M`) | ✅ **OCR 100% tài liệu scan & con dấu** | Chuẩn Markdown + Tóm tắt + Q&A |
| **✨ Chế độ 5** | `Google Gemini AI VLM` | ~1 - 3s | Quota Gemini API | ✅ **OCR Native Multimodal toàn diện** | Bảng biểu phức tạp, Tóm tắt & Q&A |

#### 💡 Cơ chế Chẩn đoán Thông minh đối với Tài liệu Scan (Scanned PDF):
- **Nguyên nhân kỹ thuật:** Các văn bản hành chính, quyết định, hợp đồng có con dấu đỏ thường được in ra giấy rồi scan bằng máy quét. Trong các tệp PDF này, toàn bộ nội dung là ảnh chụp bitmap, **hoàn toàn không có lớp văn bản kỹ thuật số (Digital Text Layer)**.
- **Xử lý thông minh trong Chế độ 2 (MarkItDown):**
  - Tự động kích hoạt cơ chế dự phòng (*Fallback Engine*) qua `pypdfium2` (Google Chrome Engine) để dò tìm ký tự số.
  - Nếu tệp là PDF scan thuần ảnh (0 từ), hệ thống **tự động phát hiện và hiển thị hộp chẩn đoán nguyên nhân kỹ thuật**, kèm mục mở rộng **xem trước ảnh trang scan thực tế**, đồng thời hướng dẫn người dùng chuyển sang **Chế độ 4 (DeepSeek VLM)** hoặc **Chế độ 5 (Gemini VLM)** để OCR đọc 100% văn bản, con dấu và chữ ký.

---

### 5. ⚡ Prompt Lab & Mẫu Tác vụ Tự động
- Tích hợp các bộ prompt chuẩn mực: Tóm tắt văn bản, Dịch thuật đa ngữ, Viết code & Unit Test, Trích xuất dữ liệu có cấu trúc JSON.

---

### 6. 📚 Tra cứu Thông số & Bảng Giá API (Pricing Reference)
- Bảng tổng hợp chi phí token minh bạch từ tài liệu chính thức:
  - **`deepseek-flash`**: Model **rẻ nhất** của DeepSeek ($0.003 - $0.006 / 1M token cache hit, $0.15 - $0.30 input), hỗ trợ đầy đủ cả Vision và Thinking.
  - **`deepseek-v4-pro` & `deepseek-chat` (V3)**: Tối ưu cho code và tác vụ ngôn ngữ.
  - **`gemini-2.5-flash` / `gemini-3.5-flash`**: Tối ưu tốc độ, ngữ cảnh 1 triệu token.

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
├── .streamlit/
│   └── config.toml          # Cấu hình giao diện Streamlit (Dark Theme, upload limit 25MB)
├── .env.example             # Mẫu biến môi trường an toàn (KHÔNG chứa secret thực)
├── .gitignore               # Loại trừ .env, .venv, bytecode, cache tạm, file nhạy cảm
├── app.py                   # Mã nguồn ứng dụng chính (Full UI, Dual Providers, 5 Extraction Modes)
├── requirements.txt         # Danh sách dependencies chuẩn
├── run.bat                  # Script khởi động nhanh 1-click cho người dùng Windows
├── test_api.py              # Script CLI kiểm tra kết nối và tính hợp lệ của Gemini API Key
├── test_sample.docx         # Tệp Word mẫu chuẩn dùng để test trích xuất bảng biểu
├── test_sample.pdf          # Tệp PDF mẫu chuẩn dùng để test trích xuất Markdown
└── README.md                # Tài liệu hướng dẫn sử dụng dự án
```

---

## 🛠️ Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Yêu cầu hệ thống
- **Python**: Phiên bản 3.10, 3.11 hoặc 3.12 (khuyên dùng 3.12).
- **Hệ điều hành**: Windows 10/11, macOS hoặc Linux.

---

### Cách 1: Khởi động nhanh 1-Click (Dành cho Windows)
Chỉ cần nhấp đúp (Double-click) vào tệp **`run.bat`**. 
Script sẽ tự động:
1. Nhận diện môi trường ảo `.venv`.
2. Kiểm tra các thư viện cần thiết.
3. Tự động mở ứng dụng trên trình duyệt web mặc định.

---

### Cách 2: Khởi chạy thủ công qua Terminal / PowerShell

#### 1. Tạo và kích hoạt môi trường ảo (Virtual Environment):
* **Trên Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
* **Trên macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### 2. Cài đặt các gói phụ thuộc (Dependencies):
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Cấu hình biến môi trường:
Sao chép tệp mẫu `.env.example` thành `.env`:
* **Windows PowerShell:**
  ```powershell
  Copy-Item .env.example .env
  ```
* **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

Mở tệp `.env` và điền các khóa API của bạn:
```env
# Google Gemini API Key (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=AIzaSy...

# DeepSeek API Key (https://platform.deepseek.com/api_keys)
DEEPSEEK_API_KEY=sk-...
```
*(Lưu ý: Bạn cũng có thể bỏ qua bước này và nhập API Key trực tiếp trên giao diện Sidebar của ứng dụng).*

#### 4. Chạy ứng dụng Streamlit:
```bash
streamlit run app.py
```
Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ: `http://localhost:8501`.

---

## 🔑 Hướng Dẫn Nhận API Key Miễn Phí / Trả Phí

### 1. Google Gemini API Key:
1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Đăng nhập bằng tài khoản Google cá nhân hoặc tổ chức.
3. Nhấp chọn nút **"Create API key"**.
4. Sao chép chuỗi khóa có định dạng `AIzaSy...` và dán vào tab **Google Gemini** trên Sidebar.

### 2. DeepSeek API Key:
1. Truy cập [DeepSeek Platform](https://platform.deepseek.com/api_keys).
2. Đăng ký tài khoản và truy cập vào mục **API Keys**.
3. Nhấp chọn **"Create new API key"**, đặt tên gợi nhớ và bấm tạo khóa.
4. Sao chép chuỗi khóa có định dạng `sk-...` và dán vào tab **DeepSeek AI** trên Sidebar.

---

## 🚀 Hướng Dẫn Đưa Dự Án Lên GitHub / GitLab

Để tải mã nguồn lên repository cá nhân một cách an toàn và chuyên nghiệp, bạn hãy thực hiện theo các bước sau trong terminal:

```bash
# 1. Khởi tạo repository Git nội bộ (nếu chưa có)
git init

# 2. Kiểm tra trạng thái các tệp (Đảm bảo .env KHÔNG xuất hiện trong danh sách)
git status

# 3. Đánh dấu theo dõi tất cả tệp dự án hợp lệ
git add .

# 4. Thực hiện commit đầu tiên
git commit -m "feat: initial commit - Gemini & DeepSeek AI Explorer with 5 document extraction modes"

# 5. Đổi tên nhánh mặc định thành main
git branch -M main

# 6. Liên kết với kho lưu trữ từ xa trên GitHub / GitLab
git remote add origin https://github.com/<tai-khoan-cua-ban>/<ten-repository>.git

# 7. Đẩy toàn bộ mã nguồn lên nhánh chính
git push -u origin main
```

---

## 🛡️ Chính Sách Bảo Mật & An Toàn Dữ Liệu (Security Best Practices)

- **Tuyệt đối không đẩy tệp `.env` lên Git:** Tệp `.gitignore` trong dự án đã được cấu hình chặt chẽ để loại trừ `.env`, `.venv`, `.streamlit/secrets.toml` và các tệp nhạy cảm khác.
- **Tệp `.env.example` an toàn:** Luôn giữ `.env.example` với các giá trị mẫu để người khác khi tải mã nguồn về biết cách thiết lập cấu hình.
- **Bảo mật cục bộ:** Chế độ 1 (Local Parser), Chế độ 2 (MarkItDown) và Chế độ 3 (Docling) hoạt động 100% trên phần cứng máy tính của bạn, không gửi bất kỳ dữ liệu tài liệu nào ra internet.

---

## 📄 Bản Quyền (License)

Dự án được phân phối dưới giấy phép **MIT License**. Bạn được tự do sử dụng, chỉnh sửa, phân phối và tích hợp vào các dự án cá nhân hoặc thương mại.
