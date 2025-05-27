import numpy as np
from pyslam.asc_grid import AscGrid


class Crop:

    def __init__(self, to_crop: list[AscGrid]):
        self.to_crop = to_crop
        self.cropped = []
   
   
    def compute(self, xgauche, xdroite, yhaut, ybas, flip_counterclockwise: int = 0) -> list[AscGrid]:
        """Fonction qui crop autant de AscGrid que fournies, toutes selon les mêmes dimensions. Les renvoie sous forme de liste dans le même ordre que donné.
        Les bornes xgauche, xdroite, yhaut et ybas sont INCLUSES et commencent à partir de 0!"""
        list_cropped = []
        for arg in self.to_crop:
            grid = arg.grid[yhaut:ybas+1, xgauche:xdroite+1]
            if flip_counterclockwise == 90:
                grid = np.rot90(grid)
            elif flip_counterclockwise == 180:
                grid = np.rot90(grid, 2)
            elif flip_counterclockwise == 270:
                grid = np.rot90(grid, 3)
            corner = (arg.corners[0] + arg.cellsize*xgauche, arg.corners[1] + arg.cellsize*(arg.grid.shape[0] - ybas - 1))
            list_cropped.append(AscGrid(grid, corner, arg.cellsize, arg.no_data))
        self.cropped = list_cropped