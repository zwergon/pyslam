import os
import numpy as np
import yaml
from pysheds.grid import Grid
from pysheds.pview import Raster
from pyslam.io.asc import grid_from_asc, indexed_from_asc
import matplotlib.pyplot as plt


def static_maps(remplir_bords=True):
    path_entree = os.path.join(os.path.dirname(
        __file__), "../data")
    path_sortie = os.path.join(os.path.dirname(
        __file__), "../output/static_maps")

    with open(os.path.join(os.path.dirname(__file__), 'files.yml')) as file:
        files = yaml.load(file, Loader=yaml.FullLoader)

    in_file = files['dem']['map']
    in_type = np.float32

    dem = grid_from_asc(os.path.join(path_entree, in_file)) 
    cellsize=dem.cellsize #on récupère la taille des cellules du dem pour multiplier l'accumulation afin d'avoir une aire

    grid: Grid = Grid.from_ascii(os.path.join(path_entree, in_file))
    dem: Raster = grid.read_ascii(os.path.join(path_entree, in_file), dtype=in_type)
    grid.mask = np.where(dem > 0., True, False)

    pit_filled_dem = grid.fill_pits(dem, apply_mask=True)
    flooded_dem = grid.fill_depressions(pit_filled_dem, apply_mask=True)
    inflated_dem = grid.resolve_flats(flooded_dem, apply_mask=True)

    fdir = grid.flowdir(inflated_dem, apply_mask=True)

    slopes = grid.cell_slopes(fdir=fdir, dem=inflated_dem, apply_mask=True)
    testslopes = slopes.copy()
    if remplir_bords:
        testslopes[0,1:-1] = testslopes[1, 1:-1] #l'algorithme de calcul de pente ne calcule pas les bords et les laisse à 0 donc je préfère les remplir par les valeurs les plus proches pour ne pas avoir d'enveloppe nulle.
        testslopes[-1,1:-1] = testslopes[-2, 1:-1]
        testslopes[1:-1,0] = testslopes[1:-1,1]
        testslopes[1:-1,-1] = testslopes[1:-1,-2]
        testslopes[0,0] = testslopes[1,1]
        testslopes[0,-1] = testslopes[1,-1]
        testslopes[-1,0] = testslopes[-1,1]
        testslopes[-1,-1] = testslopes[-1,-2]
    slope_angles = np.arctan(testslopes)
    grid.to_ascii(slope_angles, os.path.join(path_sortie, files['dem']['slope_angles']))
    
    racine = np.sqrt(slopes)/np.sqrt(np.pi/2)

    in_file = files['soil']['map']
    csv_file = files['soil']['csv']
    in_type = np.int32

    soil = indexed_from_asc(
        os.path.join(path_entree, in_file),
        os.path.join(path_entree, csv_file),
        dtype=in_type)

    Ks = soil.map('Ks', dtype=np.float32).grid
    K = np.where(Ks>0, Ks, 1)
    val = -0.1*np.log(K)/np.log(10)

    acc = grid.accumulation(fdir, apply_mask=True)
    acc_aire = acc*cellsize*cellsize
    grid.to_ascii(acc_aire, os.path.join(path_sortie, files['dem']['acc_aire']))

    in_type = np.float32

    in_file = files['rain_ant']['map']
    rain_ant: Raster = grid.read_ascii(os.path.join(path_entree, in_file), dtype=in_type)

    rain_ant_acc = grid.accumulation(fdir, weights=rain_ant, apply_mask=True)*cellsize**2/np.where(acc_aire>0, acc_aire, 1) #on peut remplacer 0 par 1 puisque les endroits concernés sont en dehors de notre DEM et donc ignorées par le masque de toute façon.
    grid.to_ascii(rain_ant_acc, os.path.join(path_sortie, files['rain_ant']['acc']))

    rain_ant_acc_weight = grid.accumulation(fdir, weights=rain_ant, efficiency=racine*val, apply_mask=True)
    grid.to_ascii(rain_ant_acc_weight, os.path.join(path_sortie, files['rain_ant']['acc_weight']))


if __name__ == "__main__":
    static_maps()