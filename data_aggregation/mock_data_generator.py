import random
from datetime import datetime, timedelta
from db import setup_db, Resource

def generate_mock_data():
    Session = setup_db()
    session = Session()

    if session.query(Resource).count() > 0:
        print("Database already contains data. Skipping mock generation.")
        return

    topics = ['Machine Learning']
    
    mock_resources = [
        {
            "title": "What is Machine Learning? A Beginner's Guide",
            "url": "https://youtube.com/watch?v=mock1",
            "resource_type": "youtube",
            "topic": "Machine Learning",
            "text_content": "Machine learning is a subfield of artificial intelligence. In this video, we will learn about supervised and unsupervised learning. It's very simple. We just use data to train a model to make predictions. No complex math required to start!",
            "comments": [
                "This was so helpful for a beginner like me!",
                "Great explanation, very clear.",
                "I still don't understand."
            ],
            "views": 150000,
            "likes": 12000,
            "estimated_hours": 0.5
        },
        {
            "title": "Understanding Backpropagation and Gradient Descent",
            "url": "https://youtube.com/watch?v=mock2",
            "resource_type": "youtube",
            "topic": "Machine Learning",
            "text_content": "Today we dive deep into the math behind neural networks. We will calculate the partial derivatives using the chain rule for backpropagation. Understanding the Hessian matrix and eigenvalues is crucial for diagnosing vanishing gradients.",
            "comments": [
                "The math is a bit heavy, but good content.",
                "I got lost at the partial derivatives part.",
                "Excellent deep dive."
            ],
            "views": 50000,
            "likes": 4000,
            "estimated_hours": 1.5
        },
        {
            "title": "Build a Linear Regression Model from Scratch in Python",
            "url": "https://github.com/mockuser/linear-regression-scratch",
            "resource_type": "github",
            "topic": "Machine Learning",
            "text_content": "# Linear Regression\nThis repository shows how to implement basic linear regression using numpy. We just calculate the slope and intercept. Great for your first project.",
            "comments": [],
            "views": 2000,
            "likes": 150,
            "estimated_hours": 2.0
        },
        {
            "title": "Attention is All You Need - Paper Implementation",
            "url": "https://github.com/mockuser/transformers-pytorch",
            "resource_type": "github",
            "topic": "Machine Learning",
            "text_content": "# Transformers in PyTorch\nImplementation of the Transformer architecture. Includes multi-head attention, positional encoding, and the complete encoder-decoder stack. Requires strong understanding of tensor operations.",
            "comments": [],
            "views": 8000,
            "likes": 1200,
            "estimated_hours": 5.0
        },
        {
            "title": "Top 5 Machine Learning Algorithms to Know",
            "url": "https://blog.mock/top-5-ml",
            "resource_type": "blog",
            "topic": "Machine Learning",
            "text_content": "If you are starting out, you should know these 5 algorithms: Linear Regression, Logistic Regression, Decision Trees, Random Forests, and K-Means clustering. They are the foundation of data science.",
            "comments": ["Nice list!"],
            "views": 10000,
            "likes": 500,
            "estimated_hours": 1.0
        }
    ]

    for item in mock_resources:
        resource = Resource(
            title=item['title'],
            url=item['url'],
            resource_type=item['resource_type'],
            topic=item['topic'],
            text_content=item['text_content'],
            comments=item.get('comments', []),
            views=item.get('views', 0),
            likes=item.get('likes', 0),
            publish_date=datetime.utcnow() - timedelta(days=random.randint(10, 365)),
            estimated_hours=item.get('estimated_hours', 1.0)
        )
        session.add(resource)
    
    session.commit()
    print("Mock data inserted successfully!")

if __name__ == '__main__':
    generate_mock_data()
