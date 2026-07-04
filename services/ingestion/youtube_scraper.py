from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse as urlparse

class YouTubeScraper:
    def __init__(self, api_key: str = None):
        self.api_key = api_key # We'll use this later for metadata if needed

    def extract_video_id(self, url: str) -> str:
        """Extracts the video ID from a YouTube URL."""
        parsed_url = urlparse.urlparse(url)
        if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed_url.path[1:]
        if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
            if parsed_url.path == '/watch':
                p = urlparse.parse_qs(parsed_url.query)
                return p['v'][0]
            if parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            if parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
        raise ValueError(f"Could not extract video ID from {url}")

    def fetch_transcript(self, video_id: str) -> list:
        """Fetches the transcript for a given video ID."""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            print(f"Error fetching transcript for {video_id}: {e}")
            return []

    def get_full_text(self, transcript_data: list) -> str:
        """Combines the transcript parts into a single full text string."""
        if not transcript_data:
            return ""
        return " ".join([item['text'] for item in transcript_data]).replace('\n', ' ')
