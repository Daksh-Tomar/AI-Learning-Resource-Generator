import os
import sys
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Add parent dir to path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_aggregation.db import setup_db, Resource

load_dotenv()
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def scrape_youtube(topic: str, max_results: int = 5):
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "your_youtube_api_key_here":
        print("Error: YOUTUBE_API_KEY is missing or invalid.")
        return

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    print(f"Searching YouTube for topic: '{topic}'...")
    search_response = youtube.search().list(
        q=topic,
        part="id,snippet",
        maxResults=max_results,
        type="video"
    ).execute()
    
    Session = setup_db()
    session = Session()

    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Check if already in DB
        if session.query(Resource).filter_by(url=url).first():
            print(f"Skipping already existing resource: {url}")
            continue
            
        print(f"Processing: {title}")
        
        # Get video statistics (views, likes)
        stats_response = youtube.videos().list(
            part="statistics,contentDetails",
            id=video_id
        ).execute()
        
        stats = stats_response["items"][0]["statistics"]
        content_details = stats_response["items"][0]["contentDetails"]
        
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        
        # Estimate hours from duration (ISO 8601 format like PT15M33S)
        import isodate
        duration_td = isodate.parse_duration(content_details.get("duration", "PT0S"))
        estimated_hours = round(duration_td.total_seconds() / 3600, 2)
        if estimated_hours == 0:
            estimated_hours = 0.5
            
        # Get comments
        comments = []
        try:
            comment_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=10,
                textFormat="plainText"
            ).execute()
            
            for c_item in comment_response.get("items", []):
                top_comment = c_item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(top_comment)
        except Exception as e:
            print(f"  Warning: Could not fetch comments for {video_id}: {e}")
            
        # Get transcript
        transcript_text = ""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([t['text'] for t in transcript_list])
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"  Warning: No transcript for {video_id}")
            transcript_text = item["snippet"]["description"] # fallback to description
        except Exception as e:
            print(f"  Warning: Error fetching transcript for {video_id}: {e}")
            transcript_text = item["snippet"]["description"]
            
        resource = Resource(
            title=title,
            url=url,
            resource_type="youtube",
            topic=topic,
            text_content=transcript_text,
            comments=comments,
            views=views,
            likes=likes,
            publish_date=datetime.utcnow(),
            estimated_hours=estimated_hours
        )
        
        try:
            session.add(resource)
            session.commit()
            print(f"  Added to DB: {url}")
        except IntegrityError:
            session.rollback()
            print(f"  Skipped duplicate (IntegrityError): {url}")

    print("Scraping completed.")

if __name__ == "__main__":
    scrape_youtube("Machine Learning", 5)
