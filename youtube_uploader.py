import os
import time
import httplib2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_URI = "https://oauth2.googleapis.com/token"

def get_authenticated_service():
    """
    Creates an authenticated YouTube API service using the permanent Refresh Token.
    Runs 100% headlessly on GitHub Actions without any user prompts.
    """
    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET or not YOUTUBE_REFRESH_TOKEN:
        raise ValueError(
            "Missing YouTube credentials! Ensure YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, "
            "and YOUTUBE_REFRESH_TOKEN are configured in GitHub Secrets."
        )

    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri=TOKEN_URI,
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
        scopes=SCOPES
    )

    return build("youtube", "v3", credentials=creds)

def set_video_thumbnail(youtube, video_id: str, thumbnail_path: str = "assets/thumbnail.png"):
    """
    Sets a custom thumbnail for the video if permitted by YouTube channel status.
    If the channel lacks Intermediate Features (phone verification), catches gracefully.
    """
    if not thumbnail_path or not os.path.exists(thumbnail_path):
        return

    print(f"Setting custom thumbnail from {thumbnail_path}...")
    try:
        media = MediaFileUpload(thumbnail_path, mimetype="image/png")
        req = youtube.thumbnails().set(videoId=video_id, media_body=media)
        req.execute()
        print(f"✅ Đã cập nhật ảnh đại diện (Thumbnail) thành công cho video {video_id}!")
    except HttpError as e:
        if "doesn't have permissions to upload and set custom video thumbnails" in str(e) or (hasattr(e, 'resp') and e.resp.status == 403):
            print(
                "ℹ️ [Thông báo Thumbnail API]: Kênh chưa bật xác minh số điện thoại trong YouTube Studio để mở quyền Custom Thumbnail qua API.\n"
                "👉 Ảnh bìa này đã được nhúng sẵn vào khung hình đầu tiên của video Shorts để làm ảnh đại diện tự động!"
            )
        else:
            print(f"⚠️ Lưu ý API Thumbnail: {e}")
    except Exception as e:
        print(f"⚠️ Lưu ý đặt thumbnail: {e}")

def upload_short(video_file: str, title: str, description: str, tags: list, privacy_status: str = "public", thumbnail_path: str = "assets/thumbnail.png") -> str:
    """
    Uploads a video to YouTube with Shorts tags and resumable upload.
    Returns the YouTube Video ID.
    """
    if not os.path.exists(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")

    # Ensure title contains #Shorts for guaranteed Shorts algorithmic pickup
    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title} #Shorts"

    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": "27"  # 27 = Education, 28 = Science & Technology
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_file,
        mimetype="video/mp4",
        chunksize=1024 * 1024 * 4,  # 4MB chunks
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print(f"Uploading '{title}' to YouTube...")
    response = None
    retry_count = 0

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%...")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                retry_count += 1
                if retry_count > 5:
                    raise
                print(f"Temporary YouTube API error: {e}. Retrying in 10s...")
                time.sleep(10)
            else:
                raise

    video_id = response.get("id", "")
    video_url = f"https://youtube.com/shorts/{video_id}"
    print(f"SUCCESS! Video published live at: {video_url}")

    # Set custom thumbnail if provided
    set_video_thumbnail(youtube, video_id, thumbnail_path)

    return video_id

if __name__ == "__main__":
    print("YouTube Uploader module ready.")
