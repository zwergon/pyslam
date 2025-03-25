
import numpy


class AscGrid:
    def __init__(self, array, corners=(0., 0.), cellsize=1., no_data=-9999.) -> None:
        self.corners = corners
        self.cellsize = cellsize
        self.no_data = numpy.array([no_data], dtype=array.dtype)[0]
        self.grid = array

    @property
    def my(self):
        return self.grid.shape[0]

    @property
    def mx(self):
        return self.grid.shape[1]

    @property
    def dx(self):
        return self.cellsize

    @property
    def dy(self):
        return self.cellsize

    def header(self) -> str:
        str = f"ncols\t{self.mx}\n"
        str += f"nrows\t{self.my}\n"
        str += f"xllcorners\t{self.corners[1]}\n"
        str += f"yllcorners\t{self.corners[0]}\n"
        str += f"cellsize\t{self.cellsize}\n"
        str += f"NODATA_value\t{self.no_data}\n"
        return str

    def __repr__(self) -> str:
        return self.header()
