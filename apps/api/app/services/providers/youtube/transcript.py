from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app.schemas.ingestion import TranscriptTrack, TranscriptResult, TranscriptSegmentDTO
from app.services.providers.interfaces import TranscriptProvider
from .exceptions import TranscriptUnavailableError

class YouTubeTranscriptProvider(TranscriptProvider):
    async def list_tracks(self, external_id: str) -> List[TranscriptTrack]:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(external_id)
            tracks = []
            for transcript in transcript_list:
                tracks.append(TranscriptTrack(
                    language_code=transcript.language_code,
                    language_name=transcript.language,
                    is_generated=transcript.is_generated,
                    is_translatable=transcript.is_translatable
                ))
            return tracks
        except TranscriptsDisabled:
            return []
        except NoTranscriptFound:
            return []
        except Exception:
            return []

    async def fetch_transcript(self, external_id: str, language_code: str) -> TranscriptResult:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(external_id)
            transcript = transcript_list.find_transcript([language_code])
            
            raw_segments = transcript.fetch()
            
            segments = []
            for item in raw_segments:
                segments.append(TranscriptSegmentDTO(
                    start_seconds=float(item['start']),
                    duration_seconds=float(item['duration']),
                    text=item['text']
                ))
                
            return TranscriptResult(
                external_id=external_id,
                language=transcript.language_code,
                source_type="AUTO_CAPTION" if transcript.is_generated else "MANUAL_CAPTION",
                segments=segments,
                is_generated=transcript.is_generated
            )
        except TranscriptsDisabled as e:
            raise TranscriptUnavailableError(f"Transcripts disabled for {external_id}") from e
        except NoTranscriptFound as e:
            raise TranscriptUnavailableError(f"Transcript not found for {external_id} in {language_code}") from e
        except Exception as e:
            raise TranscriptUnavailableError(f"Failed to fetch transcript: {e}") from e
