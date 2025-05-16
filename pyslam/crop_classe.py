from pyslam.asc_grid import AscGrid


class Crop:

    def __init__(self):
        pass

    def compute_crop(self, xgauche, xdroite, yhaut, ybas, *args: AscGrid) -> list[AscGrid]:
        """Fonction qui crop autant de AscGrid que fournies, toutes selon les mêmes dimensions. Les renvoie sous forme de liste dans le même ordre que donné.
        Les bornes xgauche, xdroite, yhaut et ybas sont INCLUSES et commencent à partir de 0!"""
        list_cropped = []
        for arg in args:
            grid = arg.grid[yhaut:ybas+1, xgauche:xdroite+1]
            corner = (arg.corners[0] + arg.cellsize*xgauche, arg.corners[1] + arg.cellsize*(arg.grid.shape[0] - ybas - 1))
            list_cropped.append(AscGrid(grid, corner, arg.cellsize, arg.no_data))
        return list_cropped