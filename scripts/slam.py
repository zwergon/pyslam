import os
import yaml
import numpy as np
import matplotlib.pyplot as plt
import rasterio


from pyslam.io.asc import grid_from_asc, indexed_from_asc
from pyslam.cn import CN
from pyslam.infiltration import InfitrationCompute, Infiltration
from pyslam.properties import SoilProperties, LuLcProperties
from scipy.stats import norm


if __name__ == "__main__":

    path = os.path.join(os.path.dirname(
        __file__), "../data")

    with open(os.path.join(os.path.dirname(__file__), 'files.yml')) as file:
        files = yaml.load(file, Loader=yaml.FullLoader)
        print(files)
    
    in_file = files['dem']['acc_aire']
    in_type = np.float32

    aire = grid_from_asc(os.path.join(path, in_file), dtype=in_type).grid

    cellsize = grid_from_asc(os.path.join(path, in_file), dtype=in_type).cellsize

    g = 9.81

    in_file = files['dem']['slope_angles']
    slope_angles = grid_from_asc(os.path.join(path, in_file), dtype=in_type).grid
    tan_slope_angles = np.tan(slope_angles)
    sin_slope_angles = np.sin(slope_angles)
    cos_slope_angles = np.cos(slope_angles)

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

    # z = soil.map('h', dtype=np.float32).grid    #on peut utiliser plutôt la formule de z variable en espace
    # plt.imshow(z)
    # plt.show()

    rhos = soil.map('dens', dtype=np.float32).grid
    # plt.imshow(rhos)
    # plt.show()

    rhow = 997

    n = soil.map('porosity', dtype=np.float32).grid
    # plt.imshow(n)
    # plt.show()

    soil_properties = SoilProperties(soil)
    Cs = soil_properties.map('C').grid
    Cs *= 1000 #on passe de kPa à Pa pour être en unités SI
    Cs_std = soil_properties.map('C', std=True).grid
    Cs_std *= 1000
    # plt.imshow(Cs_std)
    # plt.show()

    phi = soil_properties.map('phi').grid
    phi *= (np.pi/180) #on passe en radians pour ne pas se faire arrêter par la police des mathématiques
    tan_phi = np.tan(phi)
    # plt.imshow(tan_phi)
    # plt.show()
    tan_phi2 = soil_properties.map('tan_phi').grid
    # plt.imshow(tan_phi2)
    # plt.show()
    tan_phi_std = soil_properties.map('tan_phi', std=True).grid

    in_file = files['lulc']['map']
    csv_file = files['lulc']['csv']
    in_type = np.int32

    lulc = indexed_from_asc(
        os.path.join(path, in_file),
        os.path.join(path, csv_file),
        dtype=in_type)
    
    lulc_properties = LuLcProperties(lulc)
    Cr = lulc_properties.map('Cr').grid
    Cr *= 1000 #on passe de kPa à Pa pour être en unités SI
    Cr_std = lulc_properties.map('Cr', std=True).grid
    Cr_std *= 1000

    C = Cs + Cr

    # plt.imshow(C)
    # plt.show()

    cn = CN(soil, lulc)
    # plt.imshow(cn.grid)
    # plt.show()

    rain = grid_from_asc(os.path.join(
        path, files['rain']['map']), dtype=np.float32)

    infiltration_compute = InfitrationCompute(cn)
    qe = Infiltration(rain, infiltration_compute).grid
    qe /= 1000 #on passe de mm à mètres pour être en unités SI

    # plt.imshow(qe)
    # plt.show()

    rain_ant = grid_from_asc(os.path.join(
        path, files['rain_ant']['acc_weight']), dtype=np.float32).grid
    qa = rain_ant/(1000*24*3600) #on passe de mm/j en m/s pour être en unités SI

    # plt.imshow(qa)
    # plt.show()

    mask = np.where((slope_angles!=0) & (C!=0) & (rhos!=0) & (tan_phi!=0) & (aire!=0) & (Ks!=0) & (n!=0))

    z = np.full_like(aire, 1)
    # z[mask] = 0.1*np.log(aire[mask]/(tan_slope_angles[mask]*cellsize)) #on divise par la cellsize pour normaliser et faire que le résultat ne dépende pas de la taille de nos grid
    # plt.imshow(z)
    # plt.show()
    
    FS_C1 = np.full_like(C, 0.0)
    FS_C2 = np.full_like(C, 0.0)
    FS_C3 = np.full_like(C, 0.0)

    wetness = np.full_like(aire, 0.0)
    wetness[mask] = qe[mask]/(n[mask]*z[mask]) + qa[mask]/(z[mask]*10**(-7)*3)
    wetness_min = np.where(wetness < 1, wetness, 1)

    plt.imshow(np.where(wetness<1, wetness, 1))
    plt.show()

    test = np.full_like(z, 0)
    test[mask] = qe[mask]/(n[mask]*z[mask])
    plt.imshow(test)
    plt.show()
    test[mask] = qa[mask]/(z[mask]*10**(-7)*3)
    plt.imshow(np.where(test<1, test, 1))
    plt.show()

    FS_C1[mask] = C[mask]/(10*g*rhos[mask]*z[mask]*cos_slope_angles[mask]*sin_slope_angles[mask]) + tan_phi2[mask]/tan_slope_angles[mask]
    FS_C2[mask] = wetness_min[mask]*(rhow/rhos[mask])*(tan_phi2[mask]/tan_slope_angles[mask])

    FS = FS_C1 - FS_C2
    FS_petit = np.where(FS < 10, FS, 10) #on tronque FS car les valeurs extrêmes de FS ne nous intéressent pas et déforment les color maps : ce sont celles proches de 0 qui donnent les informations.
    FS_petit2 = np.where(FS_petit > -10, FS_petit, -10)
    plt.imshow(FS_petit2)
    plt.show()
    print(FS[np.where((FS_petit2 < 1) & (FS_petit2 > 0))].size)

    A = np.full_like(C, 0.0)
    D = np.full_like(C, 0.0)
    A[mask] = z[mask]*cos_slope_angles[mask]*sin_slope_angles[mask]*rhos[mask]*g
    D[mask] = tan_slope_angles[mask]/(1 - (wetness_min[mask])*(rhow/rhos[mask]))

    FS_mu = np.full_like(A, 0.0)
    FS_mu[mask] = tan_phi2[mask]/D[mask] + C[mask]/A[mask]
    FS_mu_petit = np.where(FS_mu < 10, FS_mu, 10)
    FS_mu_petit2 = np.where(FS_mu_petit > -10, FS_mu_petit, -10)
    # plt.imshow(FS_mu_petit2)
    # plt.show()

    plt.imshow(np.where(FS_C1<10, FS_C1, 10))
    plt.show()
    plt.imshow(np.where(FS_C2<10, FS_C2, 10))
    plt.show()

    with rasterio.open(os.path.join(path, 'dem_8.asc')) as src:
        ras_data = src.read()
        ras_meta = src.profile
    with rasterio.open(os.path.join(path, 'FS.asc'), 'w', **ras_meta) as dst:
        dst.write(FS_petit2, 1)

    # std = np.full_like(A, 0.0)
    # std[mask] = np.sqrt(tan_phi_std[mask]**2/(D[mask]**2) + (Cr_std[mask]**2 + Cs_std[mask]**2)/(A[mask]**2))
    # # plt.imshow(std)
    # # plt.show()
    # Pof_val = np.full_like(FS_mu, 0.0)
    # Pof_val[mask] = (1-FS_mu[mask])/std[mask]
    # # plt.imshow(Pof_val)
    # # plt.show()
    # Pof = np.full_like(Pof_val, 0.0)
    # Pof[mask] = norm.cdf(Pof_val[mask])
    # # plt.imshow(Pof)
    # # plt.show()
    # with rasterio.open(os.path.join(path, 'PoF.asc'), 'w', **ras_meta) as dst:
    #     dst.write(Pof, 1)
