import os
import sys
# Add parent dir to path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_aggregation.db import setup_db, Resource
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def score_quality():
    Session = setup_db()
    session = Session()
    analyzer = SentimentIntensityAnalyzer()
    
    resources = session.query(Resource).all()
    
    for r in resources:
        # Calculate sentiment score
        compound_scores = []
        if r.comments:
            for comment in r.comments:
                vs = analyzer.polarity_scores(comment)
                compound_scores.append(vs['compound'])
        
        avg_sentiment = sum(compound_scores) / len(compound_scores) if compound_scores else 0.0
        
        # Calculate engagement score (normalized roughly)
        engagement_ratio = 0
        if r.views and r.views > 0:
            engagement_ratio = r.likes / r.views
            
        # Quality score = 70% sentiment + 30% engagement
        # Scale engagement_ratio (usually 0.01 - 0.1) up to a 0-1 scale by multiplying by 10
        normalized_engagement = min(engagement_ratio * 10, 1.0)
        
        # Scale sentiment (-1 to 1) to (0 to 1)
        normalized_sentiment = (avg_sentiment + 1) / 2
        
        quality_score = (0.7 * normalized_sentiment) + (0.3 * normalized_engagement)
        
        r.quality_score = round(quality_score, 2)
        print(f"Scored '{r.title}': Sentiment={normalized_sentiment:.2f}, Engagement={normalized_engagement:.2f} -> Quality={r.quality_score}")
        
    session.commit()
    print("Quality scoring complete.")

if __name__ == '__main__':
    score_quality()
