import os
import numpy as np
import yaml
from pysheds.grid import Grid
from pysheds.pview import Raster

import matplotlib.pyplot as plt
import matplotlib.colors as colors
from pyslam.io.asc import grid_from_asc

def plot_acc(key: str, grid: Grid, acc: Raster):
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_alpha(0)
    plt.grid('on', zorder=0)
    im = ax.imshow(acc, extent=grid.extent, zorder=2,
                   cmap='cubehelix',
                   norm=colors.LogNorm(1, acc.max()),
                   interpolation='bilinear')
    plt.colorbar(im, ax=ax, label='Upstream Cells')
    plt.title(f'{key} Accumulation', size=14)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    path = os.path.join(os.path.dirname(
        __file__), "../data")

    with open(os.path.join(os.path.dirname(__file__), 'files.yml')) as file:
        files = yaml.load(file, Loader=yaml.FullLoader)
        print(files)

    in_file = files['dem']['map']
    in_type = np.float32

    dem = grid_from_asc(os.path.join(path, in_file)) #on récupère la taille des cellules du dem pour multiplier l'accumulation afin d'avoir une aire
    cellsize=dem.cellsize

    grid: Grid = Grid.from_ascii(os.path.join(path, in_file))
    dem: Raster = grid.read_ascii(os.path.join(path, in_file), dtype=in_type)
    grid.mask = np.where(dem > 0., True, False)

    pit_filled_dem = grid.fill_pits(dem)
    flooded_dem = grid.fill_depressions(pit_filled_dem)
    inflated_dem = grid.resolve_flats(flooded_dem)
    grid.to_ascii(inflated_dem, os.path.join(path, files['dem']['inflated']))



    fdir = grid.flowdir(inflated_dem)

    slopes = grid.cell_slopes(fdir=fdir, dem=inflated_dem)
    slope_angles = np.arctan(slopes)
    grid.to_ascii(slope_angles, os.path.join(path, files['dem']['slope_angles']))
    plt.imshow(slope_angles)
    plt.show()

    acc = grid.accumulation(fdir)
    grid.to_ascii(acc, os.path.join(path, files['dem']['acc']))

    acc_aire = acc*cellsize*cellsize
    grid.to_ascii(acc_aire, os.path.join(path, files['dem']['acc_aire']))

    plot_acc('DEM', grid, acc)
    plot_acc('Aire', grid, acc_aire)

    in_file = files['rain']['map']
    basename = os.path.splitext(os.path.basename(in_file))[0]
    rain: Raster = grid.read_ascii(os.path.join(path, in_file), dtype=in_type)

    rain_acc = grid.accumulation(fdir, weights=rain)
    plot_acc('Rain', grid, rain_acc)
    grid.to_ascii(rain_acc, os.path.join(path, files['rain']['acc']))

    in_file = files['rain_ant']['map']
    basename = os.path.splitext(os.path.basename(in_file))[0]
    rain_ant: Raster = grid.read_ascii(os.path.join(path, in_file), dtype=in_type)

    rain_ant_acc = grid.accumulation(fdir, weights=rain_ant)
    plot_acc('Rain_ant', grid, rain_ant_acc)
    grid.to_ascii(rain_acc, os.path.join(path, files['rain_ant']['acc']))

    rain_ant_acc_weight = grid.accumulation(fdir, weights=rain_ant)*cellsize*cellsize/acc_aire
    grid.to_ascii(rain_ant_acc_weight, os.path.join(path, files['rain_ant']['acc_weight']))

    plt.imshow(rain_ant_acc_weight)
    plt.show()
