import os
import numpy as np
import yaml
from pysheds.grid import Grid
from pysheds.pview import Raster

import matplotlib.pyplot as plt
import matplotlib.colors as colors
from pyslam.io.asc import grid_from_asc, indexed_from_asc

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
    # plt.imshow(slope_angles)
    # plt.show()

    sin_slope_angles = np.sin(slope_angles)
    # plt.imshow(sin_slope_angles)
    # plt.show()

    def fracine(x):
        return (np.sqrt(x)/np.sqrt(np.pi/2))
    
    racine = fracine(slopes)
    # plt.imshow(racine)
    # plt.show()

    # def ftest(x):
    #     return (-(1/(2*x +1))+1)/(-(1/(np.pi +1))+1)
    
    # test = ftest(slope_angles)
    # plt.imshow(test)
    # plt.show()

    def racinetest(x):
        return np.maximum(0.5, fracine(x))
    
    testracine = racinetest(slope_angles)
    # plt.imshow(testracine)
    # plt.show()

    in_file = files['soil']['map']
    csv_file = files['soil']['csv']
    in_type = np.int32

    soil = indexed_from_asc(
        os.path.join(path, in_file),
        os.path.join(path, csv_file),
        dtype=in_type)

    Ks = soil.map('Ks', dtype=np.float32).grid
    # plt.imshow(Ks)
    # plt.show()
    val = -0.1*np.log(Ks)/np.log(10)
    # plt.imshow(val)
    # plt.show()

    acc = grid.accumulation(fdir)
    grid.to_ascii(acc, os.path.join(path, files['dem']['acc']))

    acc_aire = acc*cellsize*cellsize
    grid.to_ascii(acc_aire, os.path.join(path, files['dem']['acc_aire']))

    # plot_acc('DEM', grid, acc)
    # plot_acc('Aire', grid, acc_aire)

    in_type = np.float32

    # in_file = files['rain']['map']
    # basename = os.path.splitext(os.path.basename(in_file))[0]
    # rain: Raster = grid.read_ascii(os.path.join(path, in_file), dtype=in_type)
    # 
    # rain_acc = grid.accumulation(fdir, weights=rain)
    # plot_acc('Rain', grid, rain_acc)
    # grid.to_ascii(rain_acc, os.path.join(path, files['rain']['acc']))

    in_file = files['rain_ant']['map']
    basename = os.path.splitext(os.path.basename(in_file))[0]
    rain_ant: Raster = grid.read_ascii(os.path.join(path, in_file), dtype=in_type)

    plt.imshow(rain_ant)
    plt.show()

    rain_ant_acc = grid.accumulation(fdir, weights=rain_ant, efficiency=racine*val)
    plt.imshow(rain_ant_acc)
    plt.show()
    grid.to_ascii(rain_ant_acc, os.path.join(path, files['rain_ant']['acc']))

    rain_ant_acc_weight = grid.accumulation(fdir, weights=rain_ant, efficiency=racine*val)
    grid.to_ascii(rain_ant_acc_weight, os.path.join(path, files['rain_ant']['acc_weight']))
    plt.imshow(rain_ant_acc_weight)
    plt.show()

