import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def recommend_videos(content, max_results=5):
    """
    Uses YouTube Data API to search and rank videos related to the content.
    """
    if not YOUTUBE_API_KEY:
        raise ValueError("Missing YOUTUBE_API_KEY in environment!")

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    # Use a relevant query (first line of content or summary)
    query = content.strip().split("\n")[0][:100]

    # Step 1: Search for videos
    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=15  # fetch more to filter
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]
    if not video_ids:
        return []

    # Step 2: Get video stats (views, likes, channel subscribers)
    stats_response = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    ).execute()

    ranked_videos = []
    for item in stats_response["items"]:
        try:
            title = item["snippet"]["title"]
            video_id = item["id"]
            views = int(item["statistics"].get("viewCount", 0))
            likes = int(item["statistics"].get("likeCount", 0))
            url = f"https://www.youtube.com/watch?v={video_id}"
            ranked_videos.append({
                "title": title,
                "url": url,
                "views": views,
                "likes": likes
            })
        except Exception:
            continue

    # Step 3: Rank videos by views + likes (simple heuristic)
    ranked_videos.sort(key=lambda x: (x["views"] + 2 * x["likes"]), reverse=True)

    return ranked_videos[:max_results]
