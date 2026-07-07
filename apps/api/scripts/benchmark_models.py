import time
import psutil
import os
import sys

def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def benchmark_model(model_name: str, texts: list[str], batch_size: int = 32):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Please install sentence-transformers: pip install sentence-transformers")
        return

    print(f"--- Benchmarking: {model_name} ---")
    start_mem = get_process_memory()
    
    # Measure Load Time
    t0 = time.time()
    model = SentenceTransformer(model_name)
    t1 = time.time()
    
    end_mem = get_process_memory()
    load_time = t1 - t0
    mem_diff = end_mem - start_mem
    
    print(f"Load Time: {load_time:.2f} seconds")
    print(f"Memory Increase: {mem_diff:.2f} MB")
    
    # Measure Inference Time
    t0 = time.time()
    embeddings = model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
    t1 = time.time()
    
    inference_time = t1 - t0
    print(f"Inference Time for {len(texts)} chunks: {inference_time:.4f} seconds")
    print(f"Inference Time per chunk: {(inference_time/len(texts))*1000:.2f} ms")
    print(f"Embedding Shape: {embeddings.shape}")
    print()
    
    # Help garbage collection
    del model
    del embeddings
    import gc
    gc.collect()


if __name__ == "__main__":
    test_texts = [
        "Welcome to this machine learning course.",
        "In this video we will discuss the concept of gradient descent.",
        "Gradient descent is an optimization algorithm used to minimize a function by iteratively moving in the direction of steepest descent.",
        "The learning rate is a hyperparameter that controls how much to change the model in response to the estimated error each time the model weights are updated.",
        "If the learning rate is too small, gradient descent can be slow. If it is too large, gradient descent can overshoot the minimum."
    ] * 20  # 100 chunks

    print(f"Starting Benchmark. Process memory before load: {get_process_memory():.2f} MB")
    
    models_to_test = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "BAAI/bge-small-en-v1.5"
    ]
    
    for model_name in models_to_test:
        benchmark_model(model_name, test_texts)

    print("Benchmarking Complete.")
