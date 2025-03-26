import os
import numpy as np
import matplotlib.pyplot as plt


from pysheds.grid import Grid
from pysheds.pview import Raster

from pyslam.io.asc import grid_from_asc, indexed_from_asc
from pyslam.cn import CN
from pyslam.infiltration import InfitrationCompute, Infiltration
from pyslam.properties import SoilProperties


if __name__ == "__main__":

    path = os.path.join(os.path.dirname(
        __file__), "../data")
    # grid: ArcGrid = from_tif(os.path.join(path, "dem.tif"))

    in_file = "dem_8.asc"
    in_type = np.float32

    # grid: Grid = Grid.from_ascii(os.path.join(path, in_file))
    # dem: Raster = grid.read_ascii(os.path.join(path, in_file), dtype=in_type)

    # pit_filled_dem = grid.fill_pits(dem)
    # flooded_dem = grid.fill_depressions(pit_filled_dem)
    # inflated_dem = grid.resolve_flats(flooded_dem)
    dem = grid_from_asc(os.path.join(path, in_file), dtype=in_type)
    print(dem)

    plt.imshow(dem.grid)
    plt.show()

    in_file = "soil_8.asc"
    csv_file = "soil.csv"
    in_type = np.int32

    soil = indexed_from_asc(
        os.path.join(path, in_file),
        os.path.join(path, csv_file),
        dtype=in_type)

    Ks = soil.map('Ks', dtype=np.float32)
    plt.imshow(Ks.grid)
    plt.show()

    soil_properties = SoilProperties(soil)
    C = soil_properties.map('C')
    plt.imshow(C.grid)
    plt.show()

    in_file = "lulc_8.asc"
    csv_file = "htmu.csv"
    in_type = np.int32

    lulc = indexed_from_asc(
        os.path.join(path, in_file),
        os.path.join(path, csv_file),
        dtype=in_type)

    cn = CN(soil, lulc)
    plt.imshow(cn.grid)
    plt.show()

    rain = grid_from_asc(os.path.join(path, "rain_8.asc"), dtype=np.float32)
    print(rain)

    plt.imshow(rain.grid)
    plt.show()

    infiltration_compute = InfitrationCompute(cn)
    infiltration = Infiltration(rain, infiltration_compute)

    plt.imshow(infiltration.grid)
    plt.show()

    # hsg = soil.map('hsg', dtype=np.char)
    # plt.imshow(hsg.grid)
    # plt.show()
