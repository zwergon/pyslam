from pathlib import Path
from pyslam.io.asc import grid_from_asc, indexed_from_asc
from pyslam.calc_ligne import CalcLigne

if __name__ == "__main__":
    path = Path(__file__).parent.parent
    if (path/"data").exists() == False:
        print("A directory pyslam/data is needed. Modify the path if your files are found elsewhere.")
    dem = grid_from_asc(path/"data"/"dem_8.asc")
    lulc = indexed_from_asc(path/'data'/'lulc_8.asc', path/'data'/'htmu.csv')
    rain = grid_from_asc(path/'data'/'rain_8.asc')
    rain_ant = grid_from_asc(path/'data'/'rain_ant_8.asc')
    soil = indexed_from_asc(path/'data'/'soil_8.asc', path/'data'/'soil.csv')
    path_feuille_exp = "D:/repositories/pyslam/data/feuille_exp.csv"
    calc_ligne = CalcLigne(path_feuille_exp=path_feuille_exp, dem=dem, lulc=lulc, rain=rain, rain_ant=rain_ant, soil=soil)
    numéro = [i for i in range(9)]
    for num in numéro:
        calc_ligne.calc_ligne(num)