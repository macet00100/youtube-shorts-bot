import os
import sys
import json
import urllib.parse
import webbrowser
import requests
import base64
from nacl import encoding, public
from http.server import HTTPServer, BaseHTTPRequestHandler

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load local credentials if present
_creds_path = "data/youtube_credentials.json"
_local_creds = {}
if os.path.exists(_creds_path):
    try:
        with open(_creds_path, "r", encoding="utf-8") as _f:
            _local_creds = json.load(_f)
    except Exception:
        pass

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", _local_creds.get("YOUTUBE_CLIENT_ID", ""))
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", _local_creds.get("YOUTUBE_CLIENT_SECRET", ""))
REDIRECT_URI = "http://localhost:8080/"
GITHUB_PAT = os.getenv("GH_PAT", _local_creds.get("GITHUB_PAT", ""))
GITHUB_REPO = "macet00100/youtube-shorts-bot"

captured_creds = {}

def sync_secret_to_github(secret_name: str, secret_value: str):
    """Encrypts and pushes secret directly to GitHub Actions Secrets."""
    headers = {
        "Authorization": f"token {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }
    key_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key"
    r = requests.get(key_url, headers=headers)
    if r.status_code != 200:
        print(f"⚠️ Không lấy được public key từ GitHub: {r.status_code}")
        return False
    
    key_data = r.json()
    public_key = public.PublicKey(key_data["key"].encode("utf-8"), encoding.Base64Encoder)
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")
    
    put_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{secret_name}"
    put_data = {
        "encrypted_value": encrypted_b64,
        "key_id": key_data["key_id"]
    }
    pr = requests.put(put_url, headers=headers, json=put_data)
    if pr.status_code in [201, 204]:
        print(f"✅ Đã tự động cập nhật GitHub Secret: {secret_name}!")
        return True
    else:
        print(f"⚠️ Lỗi cập nhật GitHub Secret {secret_name}: {pr.status_code}")
        return False

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            code = params["code"][0]
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI
            }
            resp = requests.post(token_url, data=data)
            tokens = resp.json()

            if "refresh_token" in tokens:
                captured_creds["refresh_token"] = tokens["refresh_token"]
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding-top: 60px; background: #0f172a; color: #ffffff;">
                    <div style="background: #1e293b; max-width: 500px; margin: 0 auto; padding: 40px; border-radius: 16px; border: 2px solid #22c55e;">
                        <h1 style="color: #22c55e; margin-bottom: 10px;">🎉 XÁC THỰC THÀNH CÔNG!</h1>
                        <p style="font-size: 18px; color: #cbd5e1;">Hệ thống đã nhận được <b>YouTube Refresh Token</b> mới.</p>
                        <p style="color: #94a3b8; font-size: 14px; margin-top: 20px;">Token đã được tự động đồng bộ lên GitHub Secrets. Bạn có thể đóng tab này lại!</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode("utf-8"))
            else:
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"Lỗi nhận token: {tokens}".encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No code parameter found.")

    def log_message(self, format, *args):
        pass

def main():
    print("=" * 60)
    print("🚀 BẮT ĐẦU QUY TRÌNH LẤY YOUTUBE REFRESH TOKEN VĨNH VIỄN")
    print("=" * 60)

    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"response_type=code&"
        f"scope={urllib.parse.quote('https://www.googleapis.com/auth/youtube.upload')}&"
        f"access_type=offline&"
        f"prompt=consent"
    )

    server = HTTPServer(("localhost", 8080), OAuthHandler)
    server.allow_reuse_address = True

    print("\n👉 Đang mở trình duyệt đăng nhập Google...")
    try:
        os.system(f'start "" "{auth_url}"')
    except Exception:
        webbrowser.open(auth_url)

    print(f"👉 Link đăng nhập (nếu trình duyệt không tự mở):\n{auth_url}\n")
    print("Đang lắng nghe phản hồi tại http://localhost:8080/...")

    # Wait for the single callback request
    server.handle_request()
    server.server_close()

    if "refresh_token" in captured_creds:
        refresh_token = captured_creds["refresh_token"]
        print("\n" + "=" * 60)
        print("🎉 ĐĂNG NHẬP THÀNH CÔNG! DƯỚI ĐÂY LÀ TOKEN CỦA BẠN:")
        print("=" * 60)
        print(f"YOUTUBE_REFRESH_TOKEN = {refresh_token}")
        print("=" * 60)

        # Preserve other existing keys
        _local_creds["YOUTUBE_CLIENT_ID"] = CLIENT_ID
        _local_creds["YOUTUBE_CLIENT_SECRET"] = CLIENT_SECRET
        _local_creds["YOUTUBE_REFRESH_TOKEN"] = refresh_token

        os.makedirs("data", exist_ok=True)
        with open(_creds_path, "w", encoding="utf-8") as f:
            json.dump(_local_creds, f, indent=2, ensure_ascii=False)
        print("✅ Đã lưu cấu hình vào data/youtube_credentials.json!")

        # Sync to GitHub Secrets
        sync_secret_to_github("YOUTUBE_REFRESH_TOKEN", refresh_token)
        print("=" * 60)
        print("🚀 Đang kích hoạt chạy thử workflow trên GitHub Actions...")
        headers = {
            "Authorization": f"token {GITHUB_PAT}",
            "Accept": "application/vnd.github.v3+json"
        }
        dr = requests.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/auto_shorts.yml/dispatches",
            headers=headers,
            json={"ref": "master"}
        )
        if dr.status_code == 204:
            print("🎉 ĐÃ KÍCH HOẠT WORKFLOW THÀNH CÔNG! Bot đang sản xuất video ngay lập tức.")
        else:
            print(f"Thông báo kích hoạt: {dr.status_code}")
    else:
        print("\n❌ Chưa lấy được refresh_token. Vui lòng kiểm tra lại quá trình đăng nhập.")

if __name__ == "__main__":
    main()
