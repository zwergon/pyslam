
import numpy as np
from pyslam.asc_indexed import AscIndexed


class Sampler:
    def __init__(self, key: str, indexed: AscIndexed):
        self.key = key
        self.indexed: AscIndexed = indexed

    @property
    def indirection(self):
        return self.indexed.indirection

    def sample(self, value):
        pass


class DirectSampler(Sampler):

    def sample(self, value):
        return np.float32(self.indirection.out_value(self.key, value))


class MinMaxSampler(Sampler):

    def sample(self, value):
        min = np.float32(
            self.indirection.out_value(f"{self.key}min", value))
        max = np.float32(
            self.indirection.out_value(f"{self.key}max", value))

        return np.random.uniform(min, max)


class MeanSampler(Sampler):

    def sample(self, value):
        min = np.float32(
            self.indirection.out_value(f"{self.key}min", value))
        max = np.float32(
            self.indirection.out_value(f"{self.key}max", value))
        mean = (min + max) / 2.
        stdmin = (max - min) / 4.

        return np.random.normal(mean, stdmin)
