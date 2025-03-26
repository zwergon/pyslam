import numpy as np
from pyslam.asc_grid import AscGrid
from pyslam.cn import CN


class InfitrationCompute:

    def __init__(self, cn: CN) -> None:
        self.cn = cn

    def compute(self, rain: AscGrid) -> np.array:
        assert rain.mx == self.cn.mx and rain.my == self.cn.my, "dimensions of rain and cn don't match"

        array = np.zeros(shape=(rain.grid.shape), dtype=rain.grid.dtype)
        for i in range(rain.mx):
            for j in range(rain.my):
                cn_ij = self.cn.grid[j, i]
                rain_ij = rain.grid[j, i]
                if cn_ij == self.cn.no_data or rain_ij == rain.no_data:
                    array[j, i] = rain.no_data
                else:
                    # Convert CN into Ia (Mockus)
                    ia = 5080.0 / max(cn_ij, 1.0) - 50.8
                    if rain_ij > ia:
                        array[j, i] = rain_ij - \
                            (rain_ij - ia)**2 / (rain_ij + 4 * ia)
                    else:
                        array[j, i] = rain_ij

        return array


class Infiltration(AscGrid):
    def __init__(self, rain: AscGrid, compute: InfitrationCompute) -> None:
        super().__init__(rain.grid, rain.corners, rain.cellsize, rain.no_data)
        self.grid = compute.compute(self)
