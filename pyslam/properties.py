import numpy as np
from pyslam.asc_grid import AscGrid
from pyslam.asc_indexed import AscIndexed
from pyslam.samplers import (
    Sampler,
    DirectSampler,
    MinMaxSampler,
    MeanSampler,
    TanMeanSampler
)


class Properties:

    def __init__(self, sampler_types: dict, indexed: AscIndexed) -> None:
        self.indexed: AscIndexed = indexed
        self.samplers = {
            key: sampler_type(key, self.indexed)
            for key, sampler_type in sampler_types.items()
        }

    def add_sampler(self, key, sampler: Sampler):
        self.samplers[key] = sampler

    def map(self, key, std=False) -> AscGrid:
        assert key in self.samplers.keys(), "this map properties is not set"

        indexed_grid = self.indexed.grid
        sampler: Sampler = self.samplers[key]

        array = np.zeros(shape=(indexed_grid.shape), dtype=np.float32)

        for i in range(self.indexed.mx):
            for j in range(self.indexed.my):
                grid_ij = indexed_grid[j, i]
                if grid_ij == self.indexed.no_data:
                    continue
                if std == True:
                    array[j, i] = sampler.sample(grid_ij, std=True) #récupère l'écart type is demandé
                else:
                    array[j, i] = sampler.sample(grid_ij)

        return AscGrid(array, self.indexed.corners, self.indexed.cellsize, 0.0)


class SoilProperties(Properties):

    sampler_types = {
        'Ks': DirectSampler,
        'C': MeanSampler,
        'phi': MeanSampler,
        'h': DirectSampler,
        'dens': DirectSampler,
        'porosity': DirectSampler,
        'tan_phi': TanMeanSampler
    }

    def __init__(self, soil: AscIndexed) -> None:
        super().__init__(SoilProperties.sampler_types, soil)


class LuLcProperties(Properties):

    sampler_types = {
        'Cr': MeanSampler
    }

    def __init__(self, lulc: AscIndexed) -> None:
        super().__init__(LuLcProperties.sampler_types, lulc)
