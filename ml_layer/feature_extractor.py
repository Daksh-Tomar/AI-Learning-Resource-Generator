import re

def extract_features(text: str) -> dict:
    if not text:
        return {
            'word_count': 0,
            'advanced_term_freq': 0.0,
            'beginner_term_freq': 0.0
        }
        
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)
    
    if word_count == 0:
        return {
            'word_count': 0,
            'advanced_term_freq': 0.0,
            'beginner_term_freq': 0.0
        }

    # Simplified feature sets
    beginner_terms = {'what', 'intro', 'basics', 'simple', 'beginner', 'start', 'how', 'foundation', 'easy'}
    advanced_terms = {'backpropagation', 'eigenvalues', 'hessian', 'transformer', 'attention', 'gradient', 'derivative', 'matrix', 'tensor', 'architecture'}
    
    beginner_count = sum(1 for w in words if w in beginner_terms)
    advanced_count = sum(1 for w in words if w in advanced_terms)
    
    return {
        'word_count': word_count,
        'beginner_term_freq': beginner_count / word_count,
        'advanced_term_freq': advanced_count / word_count
    }

if __name__ == '__main__':
    # Test
    sample = "In this intro video we learn what machine learning is. It is very simple for a beginner to start."
    print(extract_features(sample))
    
    sample2 = "We calculate the derivative of the tensor using backpropagation and inspect the hessian matrix."
    print(extract_features(sample2))
