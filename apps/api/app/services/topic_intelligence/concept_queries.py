from typing import List
from app.models.search_session import SearchPlanModel

class ConceptQueryGenerator:
    """
    Generates specific retrieval queries from SearchPlan concepts.
    """
    def generate_queries(self, search_plan: SearchPlanModel) -> List[str]:
        queries = []
        if search_plan.required_concepts:
            for concept in search_plan.required_concepts:
                # E.g. "React Hooks" -> "explaining React Hooks concept or examples"
                # A simple generation just uses the concept name for now.
                queries.append(concept)
        return queries
