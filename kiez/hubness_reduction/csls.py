from __future__ import annotations

import warnings

import numpy as np
from sklearn.utils.validation import check_consistent_length, check_is_fitted
from tqdm.auto import tqdm

from .base import HubnessReduction


class CSLS(HubnessReduction):
    def __init__(self, k: int = 5, verbose: int = 0, *args, **kwargs):
        super().__init__(**kwargs)
        self.k = k
        self.verbose = verbose

    def fit(
        self,
        neigh_dist,
        neigh_ind,
        source=None,
        target=None,
        assume_sorted=None,
        *args,
        **kwargs
    ) -> CSLS:
        # Check equal number of rows and columns
        check_consistent_length(neigh_ind, neigh_dist)
        check_consistent_length(neigh_ind.T, neigh_dist.T)

        # increment to include the k-th element in slicing
        k = self.k + 1

        if assume_sorted:
            self.r_dist_train_ = neigh_dist[:, :k]
            self.r_ind_train_ = neigh_ind[:, :k]
        else:
            kth = np.arange(self.k)
            mask = np.argpartition(neigh_dist, kth=kth)[:, :k]
            self.r_dist_train_ = np.take_along_axis(neigh_dist, mask, axis=1)
            self.r_ind_train_ = np.take_along_axis(neigh_ind, mask, axis=1)
        return self

    def transform(
        self,
        neigh_dist,
        neigh_ind,
        query=None,
        assume_sorted: bool = True,
        *args,
        **kwargs
    ) -> (np.ndarray, np.ndarray):
        check_is_fitted(self, "r_dist_train_")

        n_test, n_indexed = neigh_dist.shape

        if n_indexed == 1:
            warnings.warn(
                "Cannot perform hubness reduction with a single neighbor per query. "
                "Skipping hubness reduction, and returning untransformed distances."
            )
            return neigh_dist, neigh_ind

        # increment to include the k-th element in slicing
        # k = self.k + 1
        k = self.k

        # Find average distances to the k nearest neighbors
        if assume_sorted:
            r_dist_test = neigh_dist[:, :k]
        else:
            kth = np.arange(self.k)
            mask = np.argpartition(neigh_dist, kth=kth)[:, :k]
            r_dist_test = np.take_along_axis(neigh_dist, mask, axis=1)

        hub_reduced_dist = np.empty_like(neigh_dist)

        # Optionally show progress of local scaling loop
        disable_tqdm = not self.verbose
        range_n_test = tqdm(
            range(n_test),
            desc="CSLS",
            disable=disable_tqdm,
        )

        r_train = self.r_dist_train_.mean(axis=1)
        r_test = r_dist_test.mean(axis=1)
        for i in range_n_test:
            hub_reduced_dist[i, :] = (
                2 * neigh_dist[i] - r_test[i] - r_train[neigh_ind[i]]
            )
        # Return the hubness reduced distances
        # These must be sorted downstream
        return hub_reduced_dist, neigh_ind
