
import numpy as np
from pyslam.asc_grid import AscGrid


class Indirection:

    def __init__(self, keys_to_idx: dict, indirections: dict) -> None:
        self.keys_to_idx = keys_to_idx
        self.indirections = indirections

    def out_value(self, key, in_value):
        assert in_value in self.indirections, "this value is not defined in indirected map"
        assert key in self.keys_to_idx, "this key is not defined in indirected map"
        return self.indirections[in_value][self.keys_to_idx[key]]


class AscIndexed(AscGrid):

    def __init__(self, grid: AscGrid, indirection: Indirection) -> None:
        super().__init__(grid.grid, grid.corners, grid.cellsize, grid.no_data)
        self.indirection = indirection

    def map(self, key, dtype=np.float32) -> AscGrid:
        array = np.zeros(shape=(self.grid.shape), dtype=dtype)
        for i in range(self.mx):
            for j in range(self.my):
                if self.grid[j, i] == self.no_data:
                    continue
                array[j, i] = self.indirection.out_value(key, self.grid[j, i])

        return AscGrid(array,
                       corners=self.corners,
                       cellsize=self.cellsize,
                       no_data=self.no_data
                       )
