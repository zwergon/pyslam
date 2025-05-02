import rasterio
import os

def ouvre_fichiers(dossier: str): #un script dédié pour ouvrir les fichiers a été créé afin de n'avoir à les ouvrir qu'une seule fois au lieu de les ouvrir à chaque appel de crop.py puisque l'ouverture des fichiers est une des parties les plus longues de l'algorithme.
    path = os.path.join(os.path.dirname(
            __file__), f"../data/{dossier}")
    dem = rasterio.open(path+"/dem_8.asc").read(1)
    lulc = rasterio.open(path+"/lulc_8.asc").read(1)
    rain_ant = rasterio.open(path+"/rain_ant_8.asc").read(1)
    rain = rasterio.open(path+"/rain_8.asc").read(1)
    soil = rasterio.open(path+"/soil_8.asc").read(1)
    return(dem, lulc, rain_ant, rain, soil)