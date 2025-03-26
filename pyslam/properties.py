import numpy as np
from pyslam.asc_grid import AscGrid
from pyslam.asc_indexed import AscIndexed


class Properties:

    def __init__(self, sampler_types: dict, indexed: AscIndexed) -> None:
        self.indexed: AscIndexed = indexed
        self.keys = sampler_types.keys()
        self.sampler_types = sampler_types

    @property
    def indirection(self):
        return self.indexed.indirection

    def sampler(self, key, value):
        """
        Generic sampler method.

        Args:
            key: The key to sample.
            value: The index value from the AscIndexed grid.

        Returns:
            A Sampler instance.
        """
        assert key in self.keys, f"Key '{key}' is not defined for this property set."

        sampler_type = self.sampler_types.get(key)

        params = {}
        if sampler_type in [DirectSampler]:
            params['value'] = np.float32(
                self.indirection.out_value(key, value))
        elif sampler_type in [MinMaxSampler, MeanSampler]:
            params['min'] = np.float32(
                self.indirection.out_value(f"{key}min", value))
            params['max'] = np.float32(
                self.indirection.out_value(f"{key}max", value))
        else:
            raise ValueError(
                f"Sampler type '{sampler_type}' is not supported.")

        return sampler_type(**params)

    def map(self, key) -> AscGrid:
        assert key in self.keys, "this map properties is not set"

        indexed_grid = self.indexed.grid

        array = np.zeros(shape=(indexed_grid.shape), dtype=np.float32)

        for i in range(self.indexed.mx):
            for j in range(self.indexed.my):
                grid_ij = indexed_grid[j, i]
                if grid_ij == self.indexed.no_data:
                    continue
                sampler = self.sampler(key, grid_ij)
                array[j, i] = sampler.value()

        return AscGrid(array, self.indexed.corners, self.indexed.cellsize, 0.0)


class Sampler:
    def __init__(self, **kwargs):
        pass

    def value(self):
        pass


class DirectSampler(Sampler):
    def __init__(self, value) -> None:
        super().__init__()
        self._value = value

    def value(self):
        return self._value


class MinMaxSampler(Sampler):
    def __init__(self, min, max) -> None:
        super().__init__()
        self.min = min
        self.max = max

    def value(self):
        return np.random.uniform(self.min, self.max)


class MeanSampler(Sampler):
    def __init__(self, min, max) -> None:
        super().__init__()
        self.mean = (min + max) / 2.
        self.stdmin = (max - min) / 4.

    def value(self):
        return np.random.normal(self.mean, self.stdmin)


class SoilProperties(Properties):

    sampler_types = {
        'Ks': DirectSampler,
        'C': MeanSampler,
        'phi': MeanSampler,
        'h': DirectSampler,
        'dens': DirectSampler,
        'porosity': DirectSampler
    }

    def __init__(self, soil: AscIndexed) -> None:
        super().__init__(SoilProperties.sampler_types, soil)


class LuLcProperties(Properties):

    sampler_types = {
        'Cr': MinMaxSampler
    }

    def __init__(self, lulc: AscIndexed) -> None:
        super().__init__(LuLcProperties.sampler_types, lulc)
