
import numpy as np
from pyslam.asc_grid import AscGrid
from pyslam.indirection import Indirection


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
