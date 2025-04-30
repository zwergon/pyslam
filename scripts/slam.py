import os
import yaml
import numpy as np
import rasterio
from scipy.stats import norm
from pyslam.io.asc import grid_from_asc, indexed_from_asc
from pyslam.cn import CN
from pyslam.infiltration import InfitrationCompute, Infiltration
from pyslam.properties import SoilProperties, LuLcProperties
from pyslam.traitement import ajout_cercle, moyenne_mobile_2D

def slam(ligne=0, colonne=0, r=0, coef=1, cst=False, p=1, fonction=False):
    path_entree = os.path.join(os.path.dirname(
        __file__), "../data")
    
    path_sortie = os.path.join(os.path.dirname(
        __file__), "../output")

    with open(os.path.join(os.path.dirname(__file__), 'files.yml')) as file:
        files = yaml.load(file, Loader=yaml.FullLoader)
    
    in_file = files['dem']['acc_aire']
    in_type = np.float32

    aire = grid_from_asc(os.path.join(path_entree, in_file), dtype=in_type).grid

    cellsize = grid_from_asc(os.path.join(path_entree, in_file), dtype=in_type).cellsize

    g = 9.81

    in_file = files['dem']['slope_angles']
    slope_angles = grid_from_asc(os.path.join(path_entree, in_file), dtype=in_type).grid
    tan_slope_angles = np.tan(slope_angles)
    sin_slope_angles = np.sin(slope_angles)
    cos_slope_angles = np.cos(slope_angles)

    in_file = files['soil']['map']
    csv_file = files['soil']['csv']
    in_type = np.int32

    soil = indexed_from_asc(
        os.path.join(path_entree, in_file),
        os.path.join(path_entree, csv_file),
        dtype=in_type)

    Ks = soil.map('Ks', dtype=np.float32).grid
    z = soil.map('h', dtype=np.float32).grid    #on peut aussi utiliser la formule de z variable en espace
    rhos = soil.map('dens', dtype=np.float32).grid
    rhow = 997
    n = soil.map('porosity', dtype=np.float32).grid

    soil_properties = SoilProperties(soil)
    Cs = soil_properties.map('C').grid
    Cs *= 1000 #on passe de kPa à Pa pour être en unités SI
    Cs_std = soil_properties.map('C', std=True).grid
    Cs_std *= 1000

    tan_phi = soil_properties.map('tan_phi').grid
    tan_phi_std = soil_properties.map('tan_phi', std=True).grid

    in_file = files['lulc']['map']
    csv_file = files['lulc']['csv']
    in_type = np.int32

    lulc = indexed_from_asc(
        os.path.join(path_entree, in_file),
        os.path.join(path_entree, csv_file),
        dtype=in_type)
    
    lulc_properties = LuLcProperties(lulc)
    Cr = lulc_properties.map('Cr').grid
    Cr *= 1000 #on passe de kPa à Pa pour être en unités SI
    Cr_std = lulc_properties.map('Cr', std=True).grid
    Cr_std *= 1000

    C = Cs/10# + Cr

    cn = CN(soil, lulc)

    rain = grid_from_asc(os.path.join(
        path_entree, files['rain']['map']), dtype=np.float32)

    infiltration_compute = InfitrationCompute(cn)
    qe = Infiltration(rain, infiltration_compute).grid
    qe /= 1000 #on passe de mm à mètres pour être en unités SI

    rain_ant = grid_from_asc(os.path.join(
        path_entree, files['rain_ant']['acc_weight']), dtype=np.float32).grid
    qa = rain_ant/(1000*24*3600) #on passe de mm/j en m/s pour être en unités SI

    mask = np.where((slope_angles!=0) & (C!=0) & (rhos!=0) & (tan_phi!=0) & (aire!=0) & (Ks!=0) & (n!=0))

    # z = np.full_like(aire, 1)
    # z[mask] = 0.1*np.log(aire[mask]/(tan_slope_angles[mask]*cellsize)) #on divise par la cellsize pour normaliser et faire que le résultat ne dépende pas de la taille de nos grid

    qecercle = ajout_cercle(qe, ligne, colonne, r, coef, cst, p, fonction)

    wetness = np.full_like(aire, 0.0)
    wetness[mask] = qecercle[mask]/(n[mask]*z[mask]) + qa[mask]/(z[mask]*10**(-7)*3)
    wetness_min = np.where(wetness < 1, wetness, 1)

    FS_C1 = np.full_like(C, 0.0)
    FS_C2 = np.full_like(C, 0.0)

    FS_C1[mask] = C[mask]/(g*rhos[mask]*z[mask]*cos_slope_angles[mask]*sin_slope_angles[mask]) + tan_phi[mask]/tan_slope_angles[mask]
    FS_C2[mask] = wetness_min[mask]*(rhow/rhos[mask])*(tan_phi[mask]/tan_slope_angles[mask])

    FS = FS_C1 - 2*FS_C2 #changement dans le but d'accentuer l'effet de la pluie
    FS_petit = np.where(FS < 10, FS, 10) #on tronque FS car les valeurs extrêmes de FS ne nous intéressent pas et déforment les color maps : ce sont celles proches de 0 qui donnent les informations.
    FS_petit2 = np.where(FS_petit > -10, FS_petit, -10)
    FStest = moyenne_mobile_2D(FS_petit2, 5)

    A = np.full_like(C, 0.0)
    D = np.full_like(C, 0.0)
    A[mask] = z[mask]*cos_slope_angles[mask]*sin_slope_angles[mask]*rhos[mask]*g
    D[mask] = tan_slope_angles[mask]/(1 - 2*(wetness_min[mask])*(rhow/rhos[mask])) #!!!!!le changement dans le but d'accentuer l'effet de la pluie se répercute ici dans le facteur 2!!!!!

    FS_mu = np.full_like(A, 0.0)
    FS_mu[mask] = tan_phi[mask]/D[mask] + C[mask]/A[mask]
    
    with rasterio.open(os.path.join(path_entree, 'dem_8.asc')) as src:
        ras_meta = src.profile
    with rasterio.open(os.path.join(path_sortie, 'FS.asc'), 'w', **ras_meta) as dst:
        dst.write(FS_petit2, 1)
    with rasterio.open(os.path.join(path_sortie, 'FS_convolve.asc'), 'w', **ras_meta) as dst:
        dst.write(FStest, 1)

    std = np.full_like(A, 0.0)
    std[mask] = np.sqrt(tan_phi_std[mask]**2/(D[mask]**2) + (Cr_std[mask]**2 + Cs_std[mask]**2)/(A[mask]**2))
    Pof_val = np.full_like(FS_mu, 0.0)
    Pof_val[mask] = (1-FS_mu[mask])/std[mask]

    Pof = np.full_like(Pof_val, 0.0)
    Pof[mask] = norm.cdf(Pof_val[mask])

    with rasterio.open(os.path.join(path_sortie, 'PoF.asc'), 'w', **ras_meta) as dst:
        dst.write(Pof, 1)


if __name__ == "__main__":
    slam()
