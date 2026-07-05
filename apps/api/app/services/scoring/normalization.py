import math

def safe_ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely compute a ratio, avoiding division by zero.
    """
    if denominator == 0:
        return default
    return numerator / denominator

def min_max_normalize(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a value to the [0, 1] range using min-max scaling.
    If min_val == max_val, returns 0.0 to avoid division by zero.
    Clamps the result to [0, 1].
    """
    if min_val >= max_val:
        return 0.0
    
    normalized = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))

def z_score_normalize(value: float, mean: float, std_dev: float) -> float:
    """
    Normalize a value using Z-score (standardization).
    If std_dev is 0, returns 0.0.
    """
    if std_dev == 0:
        return 0.0
    return (value - mean) / std_dev
