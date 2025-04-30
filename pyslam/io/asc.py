
import numpy as np
import rasterio

from pyslam.asc_grid import AscGrid
from pyslam.asc_indexed import Indirection, AscIndexed
from pyslam.indirection import CategoryMapper, Indirection


def grid_from_asc(filename, dtype=np.float32) -> AscGrid:
    with open(filename, 'r+', encoding='utf-8') as file:
        file.readline()  # n_cols
        file.readline()  # n_rows
        xllcorner = float(file.readline().split()[1])
        yllcorner = float(file.readline().split()[1])
        cellsize = float(file.readline().split()[1])
        nodata_value = float(file.readline().split()[1])

        # Lire les données d'élévation
        data = []
        for line in file:
            data.append(line.split())

        # Convertir les données en tableau NumPy
        array = np.array(data, dtype=dtype)

        return AscGrid(
            array=array,
            corners=(xllcorner, yllcorner),
            cellsize=cellsize,
            no_data=nodata_value
        )


def indexed_from_asc(asc_name, csv_name, dtype=np.int32) -> AscIndexed:

    # read csv part
    with open(csv_name, 'r', encoding='utf-8-sig') as file:
        keys = file.readline().strip().split(";")
        mapper = CategoryMapper({k: i for i, k in enumerate(keys)})
        file.readline()  # unites
        indirections = {}
        for line in file:
            values = line.strip().replace(',', '.').split(';')
            indirections[int(values[0])] = values
    indirection = Indirection(mapper, indirections)

    grid = grid_from_asc(asc_name, dtype=dtype)
    return AscIndexed(grid, indirection)


def grid_to_asc(grid: AscGrid, filename):
    with open(filename, "w+") as file:
        file.write(grid.header())
        for j in range(grid.my):
            for i in range(grid.mx):
                file.write(f"{grid.grid[j, i]} ")
            file.write("\n")
