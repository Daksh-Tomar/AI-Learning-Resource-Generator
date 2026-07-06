from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging

from app.models.resource import ResourceModel
from app.repositories.transcript import TranscriptRepository
from app.services.providers.interfaces import TranscriptProvider
from app.services.providers.youtube.exceptions import TranscriptUnavailableError

logger = logging.getLogger(__name__)

class TranscriptIngestionService:
    def __init__(self, db: Session, provider: TranscriptProvider):
        self.db = db
        self.provider = provider
        self.transcript_repo = TranscriptRepository(db)

    async def _select_language(self, external_id: str, preferred_language: str = "en") -> Optional[str]:
        tracks = await self.provider.list_tracks(external_id)
        if not tracks:
            return None
            
        # Priority:
        # 1. Preferred language (manual)
        # 2. Preferred language (auto)
        # 3. English (manual)
        # 4. English (auto)
        # 5. Any manual
        # 6. Any auto
        
        pref_manual = next((t for t in tracks if t.language_code.startswith(preferred_language) and not t.is_generated), None)
        if pref_manual: return pref_manual.language_code
        
        pref_auto = next((t for t in tracks if t.language_code.startswith(preferred_language) and t.is_generated), None)
        if pref_auto: return pref_auto.language_code
        
        en_manual = next((t for t in tracks if t.language_code.startswith("en") and not t.is_generated), None)
        if en_manual: return en_manual.language_code
        
        en_auto = next((t for t in tracks if t.language_code.startswith("en") and t.is_generated), None)
        if en_auto: return en_auto.language_code
        
        any_manual = next((t for t in tracks if not t.is_generated), None)
        if any_manual: return any_manual.language_code
        
        any_auto = next((t for t in tracks if t.is_generated), None)
        if any_auto: return any_auto.language_code
        
        return tracks[0].language_code

    def _normalize_text(self, text: str) -> str:
        # Basic normalization: trim, collapse spaces
        import re
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    async def fetch_transcripts_batch(self, resources: List[ResourceModel]) -> Dict[UUID, Dict[str, Any]]:
        result = {}
        for r in resources:
            logger.info(f"Fetching transcript for {r.external_id}")
            existing = self.transcript_repo.get_by_resource_id(r.id)
            if existing and existing.status == "AVAILABLE":
                result[r.id] = {"status": "SUCCESS", "message": "Already fetched"}
                continue
                
            try:
                lang = await self._select_language(r.external_id)
                if not lang:
                    if not existing:
                        self.transcript_repo.create(r.id, None, None, None)
                    else:
                        self.transcript_repo.update_status(existing.id, "UNAVAILABLE")
                    result[r.id] = {"status": "UNAVAILABLE", "error_message": "No tracks found"}
                    continue
                    
                transcript_result = await self.provider.fetch_transcript(r.external_id, lang)
                
                # Normalize text and join
                segments_data = []
                full_text_parts = []
                for idx, seg in enumerate(transcript_result.segments):
                    norm = self._normalize_text(seg.text)
                    if norm:
                        segments_data.append({
                            "segment_index": idx,
                            "start_seconds": seg.start_seconds,
                            "duration_seconds": seg.duration_seconds,
                            "text": norm
                        })
                        full_text_parts.append(norm)
                        
                full_text = " ".join(full_text_parts)
                
                if not existing:
                    t_model = self.transcript_repo.create(r.id, transcript_result.language, transcript_result.source_type, full_text)
                else:
                    self.transcript_repo.update_status(existing.id, "AVAILABLE")
                    existing.language = transcript_result.language
                    existing.source_type = transcript_result.source_type
                    existing.full_text = full_text
                    t_model = existing
                
                self.db.flush()
                
                for sd in segments_data:
                    sd["transcript_id"] = t_model.id
                    
                self.transcript_repo.bulk_create_segments(segments_data)
                self.db.commit()
                result[r.id] = {"status": "SUCCESS"}
                
            except TranscriptUnavailableError as e:
                logger.warning(f"Transcript unavailable for {r.external_id}: {e}")
                if not existing:
                    self.transcript_repo.create(r.id, None, None, None).status = "UNAVAILABLE"
                else:
                    self.transcript_repo.update_status(existing.id, "UNAVAILABLE")
                self.db.commit()
                result[r.id] = {"status": "UNAVAILABLE", "error_message": str(e)}
            except Exception as e:
                logger.error(f"Failed to fetch transcript for {r.external_id}: {e}")
                self.db.rollback()
                result[r.id] = {"status": "FAILED", "error_message": str(e)}
                
        return result
