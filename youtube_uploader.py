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

def set_video_thumbnail(youtube, video_id: str, thumbnail_path: str = None):
    """
    Sets custom thumbnail if provided and permitted by channel permissions.
    """
    if not thumbnail_path or not os.path.exists(thumbnail_path):
        return

    print(f"Setting custom thumbnail from {thumbnail_path}...")
    try:
        media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
        req = youtube.thumbnails().set(videoId=video_id, media_body=media)
        req.execute()
        print(f"✅ Đã cập nhật ảnh đại diện (Thumbnail) cho video {video_id}!")
    except Exception as e:
        print(f"ℹ️ Lưu ý đặt thumbnail: {e}")

def upload_short(video_file: str, title: str, description: str, tags: list, privacy_status: str = "public", thumbnail_path: str = None) -> str:
    """
    Uploads a video to YouTube with Shorts tags and resumable upload.
    Outputs clean non-repetitive metadata and returns the YouTube Video ID.
    """
    if not os.path.exists(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")

    # Ensure title contains #Shorts for algorithmic classification
    clean_title = title.strip()
    if "#Shorts" not in clean_title and "#shorts" not in clean_title:
        clean_title = f"{clean_title} #Shorts"

    youtube = get_authenticated_service()

    # Clean description without duplicate boilerplate
    clean_desc = description.strip()
    if "#Shorts" not in clean_desc:
        clean_desc = f"{clean_desc}\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle"

    # Crisp, relevant tags (maximum 5-6 tags)
    clean_tags = ["Shorts", "CrimeRiddle", "Detective", "Mystery", "Puzzle", "Riddle"]
    if tags:
        for t in tags:
            if t not in clean_tags and len(clean_tags) < 10:
                clean_tags.append(t)

    body = {
        "snippet": {
            "title": clean_title[:100],
            "description": clean_desc,
            "tags": clean_tags,
            "categoryId": "24",  # 24 = Entertainment (High viral reach for Shorts)
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en-US"
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

    print(f"Uploading '{clean_title}' to YouTube...")
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

    if thumbnail_path and os.path.exists(thumbnail_path):
        set_video_thumbnail(youtube, video_id, thumbnail_path)

    return video_id

if __name__ == "__main__":
    print("YouTube Uploader module ready.")
