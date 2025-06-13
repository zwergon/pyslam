from pyslam.creation_feuille_experience import CreationFeuilleExperience
from pathlib import Path
from pyslam.crop import Crop
from pyslam.io.asc import grid_from_asc
import numpy as np

path = Path(__file__).parent.parent/"data"
path_csv = path/"feuille_exp.csv"
liste_noms = ['numéro', 'xgauche', 'xdroite', 'yhaut', 'ybas', 'grid', 'ligne', 'colonne', 'r', 'coef', 'flip_counterclockwise', 'cst', 'moyenne', 'ecart_type']
liste_types = ['int', 'int', 'int', 'int', 'int', 'str', 'int', 'int', 'int', 'float', 'int', 'bool', 'float', 'float']

path_dem = path/"dem_8.asc"
dem = grid_from_asc(path_dem)
cropper = Crop([dem])
createur = CreationFeuilleExperience(liste_noms_colonnes_csv=liste_noms, liste_types_colonnes_csv=liste_types, path_csv=path_csv)
total_it = 0
for i in range(15):
    xgauche = 256*i
    xdroite = 256*(i+1) - 1
    for j in range(15):
        yhaut = 256*j
        ybas = 256*(j+1) - 1
        cropper.compute(xgauche, xdroite, yhaut, ybas)
        dem = cropper.cropped[0]
        compte_valeurs_non_nulles = np.sum(np.where(dem.grid>0, 1, 0))
        if compte_valeurs_non_nulles <= 256*256/3: # On considère que si au moins un tiers du dem n'est pas rempli, alors ça n'a pas d'intérêt de garder la donnée.
            continue
        createur.ajout_ligne([total_it, xgauche, xdroite, yhaut, ybas, 'rain', 0, 0, 0, 0, 0, 'True', 0, 1])
        total_it += 1

for i in range(2000):
    xgauche = np.random.randint(0, 14*256 + 1) #la borne supérieure du randint est exclusive
    xdroite = xgauche + 255
    yhaut = np.random.randint(0, 14*256 + 1)
    ybas = yhaut + 255
    cropper.compute(xgauche, xdroite, yhaut, ybas)
    dem = cropper.cropped[0]
    compte_valeurs_non_nulles = np.sum(np.where(dem.grid>0, 1, 0))
    if compte_valeurs_non_nulles <= 256*256/3: # On considère que si au moins un tiers du dem n'est pas rempli, alors ça n'a pas d'intérêt de garder la donnée.
        continue
    which_rain = np.random.rand()
    which_rain = np.where(which_rain>0.5, 'rain', 'rain_ant') #tire au hasard quelle carte de pluie sera modifiée, les deux ayant la même probabilité d'être choisies.
    ligne = np.random.randint(0, 256)
    colonne = np.random.randint(0, 256)
    r = np.random.randint(0, 256)
    if which_rain == "rain":
        coef = 30/r if r>0 else 0
        ecart_type = 15
    else:
        coef = 2/r if r>0 else 0
        ecart_type = 1
    flip_counterclockwise = 90*np.random.randint(0, 4)
    cst = np.random.rand()
    cst = np.where(cst>0.5, 'True', '')
    moyenne = 0
    createur.ajout_ligne([total_it, xgauche, xdroite, yhaut, ybas, which_rain, ligne, colonne, r, coef, flip_counterclockwise, cst, moyenne, ecart_type])
    total_it += 1
createur.exporte_csv()