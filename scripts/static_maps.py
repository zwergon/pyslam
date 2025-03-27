import os
import numpy as np
import yaml
from pysheds.grid import Grid
from pysheds.pview import Raster

import matplotlib.pyplot as plt
import matplotlib.colors as colors


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

    grid: Grid = Grid.from_ascii(os.path.join(path, in_file))
    dem: Raster = grid.read_ascii(os.path.join(path, in_file), dtype=in_type)
    grid.mask = np.where(dem > 0., True, False)

    pit_filled_dem = grid.fill_pits(dem)
    flooded_dem = grid.fill_depressions(pit_filled_dem)
    inflated_dem = grid.resolve_flats(flooded_dem)

    fdir = grid.flowdir(inflated_dem)

    acc = grid.accumulation(fdir)
    grid.to_ascii(acc, os.path.join(path, files['dem']['acc']))

    plot_acc('DEM', grid, acc)
    plot_acc('Flow', grid, acc)

    in_file = files['rain']['map']
    basename = os.path.splitext(os.path.basename(in_file))[0]
    rain: Raster = grid.read_ascii(os.path.join(path, in_file), dtype=in_type)

    rain_acc = grid.accumulation(fdir, weights=rain)
    plot_acc('Rain', grid, rain_acc)
    grid.to_ascii(acc, os.path.join(path, files['rain']['acc']))
