import numpy as np
from scipy.stats import norm
from pyslam.cn import CN
from pyslam.infiltration import InfitrationCompute, Infiltration
from pyslam.properties import SoilProperties
from pyslam.traitement import ajout_cercle, moyenne_mobile_2D
from pyslam.asc_grid import AscGrid
from pyslam.asc_indexed import AscIndexed

class Slam:

    def __init__(self, aire: AscGrid, slope_angles: AscGrid, soil: AscIndexed, lulc: AscIndexed, rain:AscGrid, rain_ant: AscGrid):
        """On passe toutes les grandeurs qui seront utiles pour les calculs en attributs, afin de pouvoir modifier leurs valeurs avec la méthode ajout_cercle_attr ou autre
        pour ajouter de la variation dans les données si on le souhaite."""
        self.ascgrid_forvalues = rain #sert à stocker les valeurs de corner, cellsize et nodata afin de pouvoir créer une nouvelle AscGrid en sortie de compute_slam.
        self.aire = aire.grid
        self.g = 9.81
        self.tan_slope_angles = np.tan(slope_angles.grid)
        self.sin_slope_angles = np.sin(slope_angles.grid)
        self.cos_slope_angles = np.cos(slope_angles.grid)
        self.Ks = soil.map('Ks', dtype=np.float32).grid
        self.z = soil.map('h', dtype=np.float32).grid
        self.rhos = soil.map('dens', dtype=np.float32).grid
        self.rhow = 997
        self.n = soil.map('porosity', dtype=np.float32).grid
        self.Cs = SoilProperties(soil).map('C').grid*1000    # On passe de kPa à Pa
        self.Cs_std = SoilProperties(soil).map('C', std=True).grid*1000
        self.tan_phi = SoilProperties(soil).map('tan_phi').grid
        self.tan_phi_std = SoilProperties(soil).map('tan_phi', std=True).grid
        self.cn = CN(soil, lulc)
        self.qe = Infiltration(rain, InfitrationCompute(self.cn)).grid/1000    # On passe de mm à m
        self.qa = rain_ant.grid/(1000*24*3600)      # On passe de mm/j à m/s
        
    def ajout_cercle_attr(self, attr: str, ligne=0, colonne=0, r=0, coef=1, cst=False, p=1, fonction=False):
        """Ajout de valeurs dans un cercle pour un attribut "attr" de notre objet. Modifie directement l'attribut au lieu de renvoyer une valeur 
        (utiliser directement val = ajout_cercle(objet.attr, **) si on veut la valeur)."""
        arr = getattr(self, attr)
        val = ajout_cercle(arr, ligne, colonne, r, coef, cst, p, fonction)
        setattr(self, attr, val)
        return None
    
    def compute_slam(self, coef_pluie=1, coef_cohesion=1) -> tuple[AscGrid, AscGrid, AscGrid]:
        """Fonction qui fait les calculs de Factor of Safety et de Probability of Failure. Applique également une moyenne mobile sur le Factor of Safety mais pas sur la proba.
        Renvoie les 3 résultats en AscGrid dans un tuple."""
        self.C = self.Cs*coef_cohesion
        self.C_std = self.Cs_std*coef_cohesion

        mask = np.where((self.sin_slope_angles!=0) & (self.C!=0) & (self.rhos!=0) & (self.tan_phi!=0) & (self.aire!=0) & (self.Ks!=0) & (self.n!=0))

        wetness = np.full_like(self.aire, 0.0)
        wetness[mask] = self.qe[mask]/(self.n[mask]*self.z[mask]) + self.qa[mask]/(self.z[mask]*10**(-7)*3)
        wetness_min = np.where(wetness < 1, wetness, 1)
        
        FS_C1 = np.full_like(self.C, 0.0)
        FS_C2 = np.full_like(self.C, 0.0)

        FS_C1[mask] = self.C[mask]/(self.g*self.rhos[mask]*self.z[mask]*self.cos_slope_angles[mask]*self.sin_slope_angles[mask]) + self.tan_phi[mask]/self.tan_slope_angles[mask]
        FS_C2[mask] = wetness_min[mask]*(self.rhow/self.rhos[mask])*(self.tan_phi[mask]/self.tan_slope_angles[mask])
        FS = FS_C1 - coef_pluie*FS_C2 #changement dans le but d'accentuer l'effet de la pluie
        FS_petit = np.where(FS < 10, FS, 10) #on tronque FS car les valeurs extrêmes de FS ne nous intéressent pas et déforment les color maps : ce sont celles proches de 0 qui donnent les informations.
        FS_petit2 = np.where(FS_petit > -10, FS_petit, -10)
        FS_moyenne_mobile = moyenne_mobile_2D(FS_petit2, 5)

        A = np.full_like(self.C, 0.0)
        D = np.full_like(self.C, 0.0)
        A[mask] = self.z[mask]*self.cos_slope_angles[mask]*self.sin_slope_angles[mask]*self.rhos[mask]*self.g
        D[mask] = self.tan_slope_angles[mask]/(1 - coef_pluie*(wetness_min[mask])*(self.rhow/self.rhos[mask])) #!!!!!le changement dans le but d'accentuer l'effet de la pluie se répercute ici!!!!!
        FS_mu = np.full_like(A, 0.0)
        FS_mu[mask] = self.tan_phi[mask]/D[mask] + self.C[mask]/A[mask]

        std = np.full_like(A, 0.0)
        std[mask] = np.sqrt(self.tan_phi_std[mask]**2/(D[mask]**2) + (self.C_std[mask]**2)/(A[mask]**2))
        Pof_val = np.full_like(FS_mu, 0.0)
        Pof_val[mask] = (1-FS_mu[mask])/std[mask]
        Pof = np.full_like(Pof_val, 0.0)
        Pof[mask] = norm.cdf(Pof_val[mask])

        AscFS = AscGrid(array=FS_petit2, corners=self.ascgrid_forvalues.corners, cellsize = self.ascgrid_forvalues.cellsize, no_data = self.ascgrid_forvalues.no_data)
        AscFS_moy = AscGrid(array=FS_moyenne_mobile, corners=self.ascgrid_forvalues.corners, cellsize = self.ascgrid_forvalues.cellsize, no_data = self.ascgrid_forvalues.no_data)
        AscPoF = AscGrid(array=Pof, corners=self.ascgrid_forvalues.corners, cellsize = self.ascgrid_forvalues.cellsize, no_data = self.ascgrid_forvalues.no_data)
        return(AscFS, AscFS_moy, AscPoF)



        