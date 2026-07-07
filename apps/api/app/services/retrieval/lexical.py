from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text, desc
from app.models.transcript import TranscriptChunkModel
from app.schemas.retrieval import RetrievalCandidate, RetrievalScores

class LexicalRetriever:
    def __init__(self, db: Session):
        self.db = db

    def retrieve(
        self, 
        query: str, 
        top_k: int = 20, 
        resource_id_filter: Optional[str] = None
    ) -> List[RetrievalCandidate]:
        import re
        
        # Detect potential technical tokens (e.g., C++, .NET, React.js)
        # Anything with symbols commonly found in tech terms that tsvector might strip
        technical_terms = []
        words = query.split()
        for w in words:
            if re.search(r'[+#.-]', w) and len(w) > 1:
                technical_terms.append(w)
                
        stmt = select(
            TranscriptChunkModel,
            func.ts_rank(
                func.to_tsvector('english', TranscriptChunkModel.text),
                func.websearch_to_tsquery('english', query)
            ).label("rank")
        )
        
        # Apply filters
        filters = [
            func.to_tsvector('english', TranscriptChunkModel.text).op('@@')(func.websearch_to_tsquery('english', query))
        ]
        
        # If technical terms exist, add strict substring requirements
        for term in technical_terms:
            filters.append(TranscriptChunkModel.text.ilike(f"%{term}%"))
            
        stmt = stmt.filter(*filters)

        if resource_id_filter:
            stmt = stmt.filter(TranscriptChunkModel.resource_id == resource_id_filter)
            
        stmt = stmt.order_by(desc("rank")).limit(top_k)
        
        results = self.db.execute(stmt).all()
        
        candidates = []
        for row in results:
            chunk = row[0]
            lexical_score = float(row[1])
            
            candidate = RetrievalCandidate(
                chunk_id=chunk.id,
                resource_id=chunk.resource_id,
                start_seconds=chunk.start_seconds,
                end_seconds=chunk.end_seconds,
                text=chunk.text,
                scores=RetrievalScores(lexical_score=lexical_score)
            )
            candidates.append(candidate)
            
        return candidates
