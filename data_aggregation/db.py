from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    resource_type = Column(String, nullable=False) # 'youtube', 'github', 'blog', 'reddit'
    topic = Column(String, nullable=False)
    
    # Raw Data
    text_content = Column(Text, nullable=True) # Transcript or README
    comments = Column(JSON, nullable=True) # List of comments for sentiment analysis
    
    # Metadata for quality/engagement
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    publish_date = Column(DateTime, default=datetime.utcnow)
    
    # ML Features (Populated later by ML pipeline)
    difficulty_level = Column(String, nullable=True) # 'beginner', 'intermediate', 'advanced'
    quality_score = Column(Float, nullable=True) # Sentiment + Engagement
    estimated_hours = Column(Float, default=1.0) # Estimated time to consume
    
    def __repr__(self):
        return f"<Resource(title='{self.title}', type='{self.resource_type}', topic='{self.topic}')>"

def get_engine(db_path='sqlite:///resources.db'):
    return create_engine(db_path)

def setup_db(db_path='sqlite:///resources.db'):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

if __name__ == '__main__':
    setup_db()
    print("Database schema created.")
