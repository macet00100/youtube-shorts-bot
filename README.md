# 🕵️‍♂️ 24/7 AUTOMATED DETECTIVE CRIME RIDDLE SHORTS BOT (GLOBAL / HIGH-RPM)

An autonomous AI engine running **24/7 on GitHub Actions** (100% Free with unlimited runner minutes on Public Repositories).
Produces and uploads **4 high-retention 30-Second Detective Crime Riddle Shorts per day** targeting US/UK/Global audience (High RPM \$2 - \$5+).

---

## 🎯 FORMAT CONCEPT: "30-SECOND CRIME RIDDLE"
- **Hook (0-5s):** Shocking murder mystery setup inside a mansion, cruise, or locked room.
- **Suspects (6-16s):** 3 suspect alibi cards appear dynamically on screen with their statements.
- **Tension Countdown (17-23s):** 5-second countdown timer forcing viewers to pause or replay to inspect the clues.
- **The Twist & Revelation (24-32s):** GUILTY stamp slammed on the culprit with the logical proof, driving viewers to comment YES or NO!

---

## ⚡ UPGRADED DETECTIVE ENGINE
- **Narrator:** Microsoft Edge Neural **Christopher** (`en-US-ChristopherNeural`) – deep, authoritative detective narration.
- **Dynamic UI Overlays:** Top Crime Badge, 3 distinct suspect alibi cards, countdown timer, and red GUILTY stamp.
- **Subtitles:** Fast-paced MrBeast/Alex Hormozi kinetic typography (Yellow & White, thick black outline, 2-3 words per burst).
- **Audio Atmosphere:** Cinematic mystery suspense drone track automatically mixed under narration.

---

## 🔒 SECURITY & PUBLIC REPOSITORY GUARANTEE
This repository is designed to be **PUBLIC** to take advantage of **GitHub's Unlimited Free Actions Minutes**.
- **Zero hardcoded tokens:** No API keys or credentials are saved in code or committed to Git.
- **GitHub Secrets Protection:** Your `YOUTUBE_REFRESH_TOKEN` and client keys are stored in GitHub's encrypted vault. They are completely inaccessible to anyone viewing the public repo and are automatically masked with `***` in execution logs.

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT 1 LẦN DUY NHẤT (MẤT 5 PHÚT)

### BƯỚC 1: Lấy YouTube Client ID & Client Secret (Google Cloud Console)
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Tạo 1 dự án mới (ví dụ: `Youtube-Shorts-Bot`).
3. Vào **APIs & Services** $\rightarrow$ **Library** $\rightarrow$ Tìm kiếm **YouTube Data API v3** $\rightarrow$ Bấm **Enable**.
4. Vào **OAuth consent screen** (Màn hình đồng ý OAuth):
   - Chọn **External** $\rightarrow$ Bấm **Create**.
   - Điền tên ứng dụng, email liên hệ $\rightarrow$ Bấm Lưu.
   - Thêm tài khoản email kênh YouTube của bạn vào mục **Test Users** (Người dùng thử nghiệm).
5. Vào mục **Credentials** (Thông tin xác thực) $\rightarrow$ Bấm **Create Credentials** $\rightarrow$ Chọn **OAuth client ID**:
   - Application type: Chọn **Desktop App** (Ứng dụng dành cho máy tính để bàn).
   - Tên: `Shorts-Bot`.
   - Bấm **Create**. Bạn sẽ nhận được:
     - `Client ID`
     - `Client Secret`

---

### BƯỚC 2: Chạy Script lấy Token vĩnh viễn (YOUTUBE_REFRESH_TOKEN)
Mở terminal tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
python get_refresh_token.py
```
- Dán `Client ID` và `Client Secret` bạn vừa nhận được ở Bước 1.
- Trình duyệt sẽ tự động mở ra, hãy đăng nhập bằng tài khoản kênh YouTube của bạn và chọn **Cho phép**.
- Màn hình terminal sẽ in ra mã **`YOUTUBE_REFRESH_TOKEN`** vĩnh viễn!

---

### BƯỚC 3: Lấy Gemini API Key Miễn Phí (Tùy chọn)
1. Truy cập [Google AI Studio](https://aistudio.google.com/).
2. Bấm **Get API key** $\rightarrow$ Tạo 1 key miễn phí.

---

### BƯỚC 4: Đưa lên GitHub & Cấu hình Secrets
1. Đẩy toàn bộ mã nguồn này lên GitHub Repository của bạn (có thể để chế độ **Private** để bảo mật tuyệt đối).
2. Trên trang GitHub Repository, vào **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions** $\rightarrow$ Bấm **New repository secret**.
3. Thêm lần lượt 4 biến bảo mật sau:

| Tên Secret | Giá trị |
| :--- | :--- |
| `YOUTUBE_CLIENT_ID` | Nhận từ Bước 1 |
| `YOUTUBE_CLIENT_SECRET` | Nhận từ Bước 1 |
| `YOUTUBE_REFRESH_TOKEN` | Nhận từ Bước 2 |
| `GEMINI_API_KEY` | Nhận từ Bước 3 |

---

### BƯỚC 5: Kích hoạt & Tận hưởng
- Vào tab **Actions** trên GitHub.
- Bấm vào workflow **Auto 24/7 YouTube Shorts Bot** $\rightarrow$ Bấm **Run workflow** để bot chạy thử nghiệm video đầu tiên ngay lập tức!
- Từ thời điểm này, GitHub Actions sẽ tự động kích hoạt 4 lần mỗi ngày theo giờ Việt Nam:
  - **07:00 Sáng**
  - **11:30 Trưa**
  - **17:30 Chiều**
  - **20:30 Tối**

Kênh YouTube của bạn sẽ tự động có video Shorts mới mỗi ngày mà không cần bạn phải chạm tay vào máy tính!
