import pytest
from app.services.scoring.normalization import safe_ratio, min_max_normalize, z_score_normalize

def test_safe_ratio():
    assert safe_ratio(10, 2) == 5.0
    assert safe_ratio(10, 0) == 0.0
    assert safe_ratio(10, 0, default=1.0) == 1.0

def test_min_max_normalize():
    assert min_max_normalize(5, 0, 10) == 0.5
    assert min_max_normalize(15, 0, 10) == 1.0 # clamped
    assert min_max_normalize(-5, 0, 10) == 0.0 # clamped
    assert min_max_normalize(5, 10, 10) == 0.0 # handles min >= max

def test_z_score_normalize():
    assert z_score_normalize(10, 5, 2) == 2.5
    assert z_score_normalize(10, 5, 0) == 0.0 # handles zero std_dev
