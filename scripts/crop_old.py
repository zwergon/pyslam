import os
import numpy as np
import rasterio
from rasterio.transform import Affine

def crop(xgauche=0, xdroite=1, yhaut=0, ybas=1, dem=np.zeros((2,2)), lulc=np.zeros((2,2)), rain_ant=np.zeros((2,2)), rain=np.zeros((2,2)), soil=np.zeros((2,2)), out_dir=False):
    files = (
        (np.float32, dem, "dem"),
        (np.int32, lulc, "lulc"),
        (np.float32, rain_ant, "rain_ant"),
        (np.float32, rain, "rain"),
        (np.int32, soil, "soil")
    )

    if out_dir == False:
            path_sortie = os.path.join(os.path.dirname(
                __file__), "../data")
    else: #si un out est spécifié, on crée un dossier nommé out dans data pour ne pas mélanger toutes les entrées si on veut itérer le crop.
        path_sortie = os.path.join(os.path.dirname(
            __file__), f"../data/{out_dir}")
        os.mkdir(path_sortie)

    for typ, file, name in files:
        in_dtype = typ
        out_file = f"{name}_8.asc"

        ras_meta = {'driver': 'AAIGrid', 'dtype': in_dtype, 'nodata': 0.0, 'width': xdroite - xgauche + 1, 'height': ybas - yhaut + 1, 'count': 1, 'crs': None,
                    'transform': Affine(40.0, 0.0, 747667.4962 + xgauche*40.0 , 0.0, -40.0, 4882245.0088 - yhaut*40.0), 'blockxsize': xdroite - xgauche + 1, 'blockysize': 1, 'tiled': False}
        with rasterio.open(os.path.join(path_sortie, out_file), 'w', **ras_meta) as dst:
            dst.write(file[yhaut:ybas+1, xgauche:xdroite+1], 1)

if __name__ == "__main__":
    crop(1000, 1599, 1600, 1999)
