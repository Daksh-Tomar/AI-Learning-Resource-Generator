import os
import sys
# Add parent dir to path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_aggregation.db import setup_db, Resource
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load the model once
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def rank_resources(user_goal: str, top_k: int = 5):
    """
    Rank resources based on cosine similarity to the user's goal.
    Returns a list of ranked resource dictionaries.
    """
    if model is None:
        print("Model not loaded.")
        return []

    Session = setup_db()
    session = Session()
    
    resources = session.query(Resource).all()
    if not resources:
        print("No resources found.")
        return []

    # Prepare texts to embed
    # We combine title and content to give a better representation of the resource
    resource_texts = [f"{r.title}. {r.text_content}" for r in resources]
    
    # Generate embeddings
    print("Generating embeddings for resources...")
    resource_embeddings = model.encode(resource_texts)
    
    print(f"Generating embedding for user goal: '{user_goal}'")
    goal_embedding = model.encode([user_goal])
    
    # Calculate cosine similarity
    similarities = cosine_similarity(goal_embedding, resource_embeddings)[0]
    
    # Rank indices by similarity score (descending)
    ranked_indices = np.argsort(similarities)[::-1]
    
    ranked_results = []
    for idx in ranked_indices[:top_k]:
        r = resources[idx]
        score = similarities[idx]
        ranked_results.append({
            'resource': r,
            'similarity_score': round(float(score), 4)
        })
        
    return ranked_results

if __name__ == '__main__':
    # Test with a mock query
    goal = "I want to learn the basics of machine learning without complex math."
    results = rank_resources(goal)
    print(f"\nTop results for: '{goal}'")
    for res in results:
        print(f"- {res['resource'].title} (Score: {res['similarity_score']})")
