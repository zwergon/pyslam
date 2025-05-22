from pathlib import Path
import numpy as np
from pyslam.crop import Crop
from pyslam.static_maps import StaticMaps
from pyslam.slam import Slam
from pyslam.io.asc import grid_from_asc, indexed_from_asc, indexed_from_grid, grid_to_asc
from pysheds.grid import Grid
from pyslam.asc_grid import AscGrid
from tqdm import tqdm


if __name__ == "__main__":
    path = Path(__file__).parent.parent
    if (path/"data").exists() == False:
        print("A directory pyslam/data is needed. Modify the path if your files are found elsewhere.")
    dem = grid_from_asc(path/"data"/"dem_8.asc")
    lulc = indexed_from_asc(path/'data'/'lulc_8.asc', path/'data'/'htmu.csv')
    rain = grid_from_asc(path/'data'/'rain_8.asc')
    rain_ant = grid_from_asc(path/'data'/'rain_ant_8.asc')
    soil = indexed_from_asc(path/'data'/'soil_8.asc', path/'data'/'soil.csv')
    
    crop = Crop([dem, lulc, rain, rain_ant, soil])

    path_out = path/"output"
    path_out.mkdir(exist_ok=True)

    skipped = 0 #on va skip les endroits où le dem est nul partout (ie l'eau ou les endroits hors des marches) et on en garde le compte pour le nom des dossiers créés.
    for i in tqdm(range(225)):
        crop.compute(256*(i%15), 256*(i%15+1) - 1, 256*(i//15), 256*(i//15+1) - 1)
        dem_crop = crop.cropped[0]

        if not dem_crop.grid.any(): #si le dem est nul partout, alors on arrête l'itération ici et on garde le compte de nombre de skips.
            skipped += 1
            continue
        
        lulc_crop = indexed_from_grid(crop.cropped[1], path/'data'/'htmu.csv')
        rain_crop = crop.cropped[2]
        rain_ant_crop = crop.cropped[3]
        soil_crop = indexed_from_grid(crop.cropped[4], path/'data'/'soil.csv')

        path_i = path_out/ f"{i-skipped}" #le i-skipped sert à avoir une numérotation linéaire (ie sans trous là où on a skip).
        path_i.mkdir()
        path_i_input = path_i / "model_input"
        path_i_input.mkdir()
        path_i_output = path_i / "model_output"
        path_i_output.mkdir()

        grid_to_asc(dem_crop, path_i_input / "dem_8.asc")
        grid_to_asc(rain_ant_crop, path_i_input / "rain_ant_8.asc")
        grid_to_asc(rain_crop, path_i_input / "rain_8.asc")
        grid_to_asc(lulc_crop, path_i_input / "lulc_8.asc")
        grid_to_asc(soil_crop, path_i_input / "soil_8.asc")
        grid = Grid.from_ascii(path_i_input / "dem_8.asc")

        dem_asc = grid.read_ascii(path_i_input / 'dem_8.asc', dtype=np.float32)
        rain_ant_asc = grid.read_ascii(path_i_input / 'rain_ant_8.asc', dtype=np.float32)

        static_maker = StaticMaps(dem_asc, soil_crop, grid, rain_ant_asc)
        asc_slope_angles, asc_aire, asc_rain_acc = static_maker.compute_static_maps()

        slamer = Slam(asc_aire, asc_slope_angles, soil_crop, lulc_crop, rain_crop, asc_rain_acc)
        slamer.ajout_cercle_attr('qe', 100, 100, 0, 0.005, cst=True, p=1)
        asc_fs, asc_fs_moy, asc_pof = slamer.compute_slam(coef_pluie=1, coef_cohesion=0.1)
        
        arr = asc_pof.grid.copy()
        arr = np.where((0.9<=arr)&(arr<=1), 0.9, arr)
        arr = np.where((0.8<=arr)&(arr<0.9), 0.8, arr)
        arr = np.where((0.7<=arr)&(arr<0.8), 0.7, arr)
        arr = np.where((0.6<=arr)&(arr<0.7), 0.6, arr)
        arr = np.where((0.5<=arr)&(arr<0.6), 0.5, arr)
        arr = np.where((0.4<=arr)&(arr<0.5), 0.4, arr)
        arr = np.where((0.3<=arr)&(arr<0.4), 0.3, arr)
        arr = np.where((0.2<=arr)&(arr<0.3), 0.2, arr)
        arr = np.where((0.1<=arr)&(arr<0.2), 0.1, arr)
        arr = np.where((0<=arr)&(arr<0.1), 0, arr)
        asc_pof_levels = AscGrid(array=arr, corners=asc_pof.corners, cellsize=asc_pof.cellsize, no_data=asc_pof.no_data)

        grid_to_asc(asc_fs, path_i_output / 'FS.asc')
        grid_to_asc(asc_fs_moy, path_i_output / 'FS_moy.asc')
        grid_to_asc(asc_pof, path_i_output / 'PoF.asc')
        grid_to_asc(asc_pof_levels, path_i_output / 'PoF_levels.asc')

