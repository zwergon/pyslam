import os
import yaml
import numpy as np
import matplotlib.pyplot as plt


from pyslam.io.asc import grid_from_asc, indexed_from_asc
from pyslam.cn import CN
from pyslam.infiltration import InfitrationCompute, Infiltration
from pyslam.properties import SoilProperties


if __name__ == "__main__":

    path = os.path.join(os.path.dirname(
        __file__), "../data")

    with open(os.path.join(os.path.dirname(__file__), 'files.yml')) as file:
        files = yaml.load(file, Loader=yaml.FullLoader)
        print(files)

    in_file = files['dem']['map']
    in_type = np.float32

    dem = grid_from_asc(os.path.join(path, in_file), dtype=in_type)
    print(dem)

    plt.imshow(dem.grid)
    plt.show()

    in_file = files['soil']['map']
    csv_file = files['soil']['csv']
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

    in_file = files['lulc']['map']
    csv_file = files['lulc']['csv']
    in_type = np.int32

    lulc = indexed_from_asc(
        os.path.join(path, in_file),
        os.path.join(path, csv_file),
        dtype=in_type)

    cn = CN(soil, lulc)
    plt.imshow(cn.grid)
    plt.show()

    rain = grid_from_asc(os.path.join(
        path, files['rain']['map']), dtype=np.float32)
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
