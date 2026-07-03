import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_aggregation.youtube_scraper import scrape_youtube
from ml_layer.difficulty_classifier import train_and_predict_difficulty
from ml_layer.sentiment_scorer import score_quality

def run_pipeline(topics=None):
    if topics is None:
        topics = ["Machine Learning", "Data Science", "System Design"]
        
    print("--- Starting Data Aggregation Phase ---")
    for topic in topics:
        print(f"\nScraping for topic: {topic}")
        scrape_youtube(topic, max_results=5)
        
    print("\n--- Starting ML Scoring Phase ---")
    print("1. Predicting Difficulty Levels...")
    train_and_predict_difficulty()
    
    print("\n2. Scoring Quality (Sentiment + Engagement)...")
    score_quality()
    
    print("\n--- Pipeline Execution Complete ---")

if __name__ == "__main__":
    run_pipeline()
