from pydantic import BaseModel, Field, model_validator

class SearchPlan(BaseModel):
    primary_topic: str = Field(min_length=2, max_length=150)
    search_queries: list[str] = Field(min_length=3, max_length=10)
    required_concepts: list[str] = Field(min_length=3, max_length=30)
    project_queries: list[str] = Field(default_factory=list, max_length=5)
    interview_queries: list[str] = Field(default_factory=list, max_length=5)
    preferred_resource_types: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_lists(self) -> 'SearchPlan':
        self.search_queries = list(set([q.strip() for q in self.search_queries if q.strip()]))
        self.required_concepts = list(set([c.strip() for c in self.required_concepts if c.strip()]))
        self.project_queries = list(set([q.strip() for q in self.project_queries if q.strip()]))
        self.interview_queries = list(set([q.strip() for q in self.interview_queries if q.strip()]))
        
        if len(self.search_queries) < 3:
            raise ValueError("At least 3 valid search queries are required after normalization.")
            
        return self

class SearchPlanRequest(BaseModel):
    profile_id: str

class SearchPlanResponse(BaseModel):
    profile_id: str
    search_plan: SearchPlan
