import os
import sys
# Add parent dir to path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_aggregation.db import setup_db, Resource
from feature_extractor import extract_features
from sklearn.linear_model import LogisticRegression
import numpy as np

def train_and_predict_difficulty():
    Session = setup_db()
    session = Session()
    
    resources = session.query(Resource).all()
    if not resources:
        print("No resources found in database.")
        return
    
    # In a real scenario, we would have manually labeled data.
    # Since we don't, we will use a simple heuristic to create "pseudo-labels"
    # for the sake of the prototype, then train a model on those features to demonstrate the ML pipeline.
    
    features = []
    labels = []
    ids = []
    
    for r in resources:
        feats = extract_features(r.text_content)
        X = [feats['word_count'], feats['beginner_term_freq'], feats['advanced_term_freq']]
        features.append(X)
        ids.append(r.id)
        
        # Pseudo-labeling logic for training the classifier
        if feats['advanced_term_freq'] > 0.01 or "backpropagation" in r.text_content.lower():
            labels.append("advanced")
        elif feats['beginner_term_freq'] > 0.01 or "beginner" in r.text_content.lower():
            labels.append("beginner")
        else:
            labels.append("intermediate")
            
    # Train classifier
    X_train = np.array(features)
    y_train = np.array(labels)
    
    clf = LogisticRegression(random_state=42, max_iter=1000)
    # Check if there are at least two classes to train
    if len(set(y_train)) > 1:
        clf.fit(X_train, y_train)
        predictions = clf.predict(X_train)
    else:
        # Fallback if only one class exists in mock data
        predictions = y_train
        
    # Update DB
    for r_id, pred in zip(ids, predictions):
        res = session.query(Resource).filter(Resource.id == r_id).first()
        res.difficulty_level = pred
        print(f"Assigned difficulty '{pred}' to '{res.title}'")
        
    session.commit()
    print("Difficulty classification complete.")

if __name__ == '__main__':
    train_and_predict_difficulty()
