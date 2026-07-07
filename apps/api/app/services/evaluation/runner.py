import json
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict

class EvaluationQuery(BaseModel):
    query: str
    relevant_chunk_texts: List[str] # Texts that should match

class EvaluationRunner:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path

    def load_dataset(self) -> List[EvaluationQuery]:
        if not Path(self.dataset_path).exists():
            return []
        
        queries = []
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    queries.append(EvaluationQuery(**data))
        return queries
        
    def save_report(self, report: Dict, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
