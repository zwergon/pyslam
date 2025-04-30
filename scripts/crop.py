import os
import numpy as np
from pysheds.grid import Grid
from pysheds.pview import Raster

from pyslam.asc_grid import AscGrid
from pyslam.io.asc import grid_to_asc

import matplotlib.pyplot as plt

if __name__ == "__main__":

    ratio = 8
    crop = ((300, 480), (320, 420))

    files = (
        ("dem", np.float32),
        ("lulc", np.int32),
        ("rain_ant", np.float32),
        ("rain_event", np.float32),
        ("soil", np.int32)
    )

    for f, t in files:
        in_file = f"{f}.asc"
        in_dtype = t
        out_file = f"{f}_{ratio}.asc"

        path = os.path.join(os.path.dirname(
            __file__), "../data")

        glissement_path = os.path.join(path, "glissements")

        grid: Grid = Grid.from_ascii(os.path.join(glissement_path, in_file))

        dem: Raster = grid.read_ascii(os.path.join(
            glissement_path, in_file), dtype=in_dtype)

        dem = dem[crop[1][0]:crop[1][1]:ratio, crop[0][0]:crop[0][1]:ratio]
        asc_grid = AscGrid(dem, cellsize=40.*ratio, no_data=grid.nodata)
        print(asc_grid.header())
        grid_to_asc(asc_grid, os.path.join(path, out_file))

    plt.imshow(dem)
    plt.show()
