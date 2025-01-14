import numpy as np
import pytest
from kiez.neighbors import HNSW
from numpy.testing import assert_array_equal

rng = np.random.RandomState(2)


def test_wrong_metric():
    with pytest.raises(ValueError) as exc_info:
        HNSW(metric="jibberish")
    assert "Unknown" in str(exc_info.value)


def test_sqeuclidean(n_samples=20, n_features=5, n_neighbors=5):
    source = rng.rand(n_samples, n_features)
    target = rng.rand(n_samples, n_features)
    hnsw1 = HNSW(n_candidates=n_neighbors, metric="sqeuclidean")
    hnsw1.fit(source, target)
    d, i = hnsw1.kneighbors(
        query=source[
            :5,
        ]
    )
    hnsw2 = HNSW(n_candidates=n_neighbors)
    hnsw2.fit(source, target)
    i2 = hnsw2.kneighbors(
        query=source[
            :5,
        ],
        return_distance=False,
    )
    assert_array_equal(i, i2)


def test_cosine(n_samples=20, n_features=5, n_neighbors=5):
    source = rng.rand(n_samples, n_features)
    target = rng.rand(n_samples, n_features)
    hnsw1 = HNSW(n_candidates=n_neighbors, metric="cosine")
    hnsw1.fit(source, target)
    d, i = hnsw1.kneighbors(
        query=source[
            :5,
        ]
    )
    hnsw2 = HNSW(n_candidates=n_neighbors, metric="cosinesimil")
    hnsw2.fit(source, target)
    i2 = hnsw2.kneighbors(
        query=source[
            :5,
        ],
        return_distance=False,
    )
    assert_array_equal(i, i2)
