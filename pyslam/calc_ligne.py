from pathlib import Path
import numpy as np
from pyslam.crop import Crop
from pyslam.static_maps import StaticMaps
from pyslam.slam import Slam
from pyslam.io.asc import indexed_from_grid, grid_to_asc
from pysheds.grid import Grid
from pyslam.asc_grid import AscGrid
from pyslam.asc_indexed import AscIndexed


class CalcLigne:
    def __init__(self, path_feuille_exp: str|Path, dem: AscGrid, lulc: AscIndexed, rain: AscGrid, rain_ant: AscGrid, soil: AscIndexed):
        self.path = path_feuille_exp
        self.dem = dem
        self.lulc = lulc
        self.rain = rain
        self.rain_ant= rain_ant
        self.soil = soil

    def calc_ligne(self, numéro_ligne: str|int):
        path_feuille_exp = self.path
        dem = self.dem
        lulc = self.lulc
        rain = self.rain
        rain_ant = self.rain_ant
        soil = self.soil
        
        num_ligne = str(numéro_ligne)

        path = Path(__file__).parent.parent
        
        crop = Crop([dem, lulc, rain, rain_ant, soil])

        path_out = path/"output"
        path_out.mkdir(exist_ok=True)

        feuille_experience = Path(path_feuille_exp)

        with open(feuille_experience, "r") as file:
            ligne_noms_params = file.readline().strip().split(";")
            ligne_type_params = file.readline().strip().split(";")
            for line in file:
                ligne_val_params = line.strip().split(";")
                if ligne_val_params[0] != num_ligne:
                    continue #On ne s'intéresse qu'à une seule ligne. Itérer ainsi est très rapide (0.01 secondes pour chercher 10000 lignes).
                dico_params = {}
                for k, arg in enumerate(ligne_noms_params):
                    if ligne_type_params[k] == "int":
                        dico_params[arg] = int(ligne_val_params[k])
                    elif ligne_type_params[k] == "float":
                        dico_params[arg] = float(ligne_val_params[k])
                    else:
                        dico_params[arg] = ligne_val_params[k]

                crop.compute(dico_params["xgauche"], dico_params["xdroite"], dico_params["yhaut"], dico_params["ybas"])
                dem_crop = crop.cropped[0]

                lulc_crop = indexed_from_grid(crop.cropped[1], path/'data'/'htmu.csv')
                rain_crop = crop.cropped[2]
                rain_ant_crop = crop.cropped[3]
                soil_crop = indexed_from_grid(crop.cropped[4], path/'data'/'soil.csv')

                path_i = path_out/ f"{dico_params["numéro"]}"
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
                slamer.ajout_cercle_attr(dico_params["attr"], dico_params["ligne"], dico_params["colonne"], dico_params["r"], dico_params["coef"], cst=True, p=1)
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
                break #On ne fait qu'un seule itération dans ce fichier donc dès qu'on l'a terminée on arrête la boucle sur les lignes.