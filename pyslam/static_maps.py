import numpy as np
from pysheds.grid import Grid
from pysheds.pview import Raster
from pyslam.asc_grid import AscGrid
from pyslam.asc_indexed import AscIndexed


class StaticMaps:

    def __init__(self, dem: Raster, soil: AscIndexed, grid: Grid, rain_ant: AscGrid):
        self.ascsoil_forvalues = soil   #gardé en mémoire pour avoir les valeurs de corners et nodata afin de pouvoir créer une nouvelle AscGrid en sortie de compute_static_maps.
        self.dem = dem
        self.cellsize = soil.cellsize
        self.soil = soil
        self.grid = grid
        self.rain = rain_ant

    def compute_static_maps(self, remplir_bords=True) -> tuple[AscGrid, AscGrid, AscGrid]:
        """fonction qui va calculer les cartes de pente, d'aire et d'accumulation de pluie, les retournant sous forme de tuple contenant les 3 AscGrid."""
        self.grid.mask = np.where(self.dem > 0., True, False)
        pit_filled_dem = self.grid.fill_pits(self.dem, apply_mask=True)
        flooded_dem = self.grid.fill_depressions(pit_filled_dem, apply_mask=True)
        inflated_dem = self.grid.resolve_flats(flooded_dem, apply_mask=True)

        fdir = self.grid.flowdir(inflated_dem, apply_mask=True)

        slopes = self.grid.cell_slopes(fdir=fdir, dem=inflated_dem, apply_mask=True)
        slopes_copy = slopes.copy()
        if remplir_bords:
            slopes_copy[0,1:-1] = slopes_copy[1, 1:-1] #l'algorithme de calcul de pente ne calcule pas les bords et les laisse à 0 donc je préfère les remplir par les valeurs les plus proches pour ne pas avoir d'enveloppe nulle.
            slopes_copy[-1,1:-1] = slopes_copy[-2, 1:-1]
            slopes_copy[1:-1,0] = slopes_copy[1:-1,1]
            slopes_copy[1:-1,-1] = slopes_copy[1:-1,-2]
            slopes_copy[0,0] = slopes_copy[1,1]
            slopes_copy[0,-1] = slopes_copy[1,-1]
            slopes_copy[-1,0] = slopes_copy[-1,1]
            slopes_copy[-1,-1] = slopes_copy[-1,-2]
        slope_angles = np.arctan(slopes_copy)
        asc_slope_angles = AscGrid(slope_angles, corners=self.ascsoil_forvalues.corners, cellsize=self.cellsize, no_data=self.ascsoil_forvalues.no_data)

        racine = np.sqrt(slope_angles)/np.sqrt(np.pi/2)
        Ks = self.soil.map('Ks', dtype=np.float32).grid
        K = np.where(Ks>0, Ks, 1)
        val = -0.1*np.log(K)/np.log(10)
        acc = self.grid.accumulation(fdir, apply_mask=True)
        acc_aire = acc*self.cellsize*self.cellsize
        asc_aire = AscGrid(acc_aire, corners=self.ascsoil_forvalues.corners, cellsize=self.cellsize, no_data=self.ascsoil_forvalues.no_data)
        
        rain_ant_acc_weight = self.grid.accumulation(fdir, weights=self.rain, efficiency=racine*val, apply_mask=True)
        AscRainAcc = AscGrid(rain_ant_acc_weight, corners=self.ascsoil_forvalues.corners, cellsize=self.cellsize, no_data=self.ascsoil_forvalues.no_data)

        return(asc_slope_angles, asc_aire, AscRainAcc)
