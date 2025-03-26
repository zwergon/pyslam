import numpy as np
from pyslam.asc_grid import AscGrid
from pyslam.asc_indexed import AscIndexed


class CNComputer:

    def __init__(self, soil_cn_key='hsg'):
        self.soil_cn_key = soil_cn_key

    def compute(self, soil: AscIndexed, lulc: AscIndexed, no_data) -> np.array:

        assert soil.mx == lulc.mx and soil.my == lulc.my, "dimensions of soil and lulc don't match"

        array = np.zeros(shape=(soil.grid.shape), dtype=np.dtype(no_data))
        for i in range(soil.mx):
            for j in range(soil.my):
                soil_ij = soil.grid[j, i]
                lulc_ij = lulc.grid[j, i]
                if soil_ij == soil.no_data or lulc_ij == lulc.no_data:
                    array[j, i] = no_data
                else:
                    soil_cn_key = soil.indirection.out_value(
                        self.soil_cn_key, soil_ij)
                    cn = lulc.indirection.out_value(soil_cn_key, lulc_ij)
                    array[j, i] = float(cn)

        return array


class CN(AscGrid):

    def __init__(self, soil: AscIndexed, lulc: AscIndexed, computer=CNComputer()) -> None:
        super().__init__(
            # dummy array just for the dtype
            np.array([0.0], dtype=np.float32),
            soil.corners,
            cellsize=soil.cellsize,
            no_data=0.0)
        self.grid = computer.compute(soil, lulc, self.no_data)
