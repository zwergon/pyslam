import numpy as np
from scipy import signal

def ajout_cercle(arr, ligne, colonne, r, coef=1, cst=False, p=1, fonction = False): #ajoute dans un cercle centré en (colonne, ligne) de rayon r des valeurs décroissantes avec la distance en centre du cercle à un array
        nb_ligne, nb_col = arr.shape
        x = np.arange(0,nb_col)
        y = np.arange(0, nb_ligne)
        liste_r = [i for i in range(r, 0, -1)]
        arr2 = arr.copy()
        for ray in liste_r:
            masque = ((x[np.newaxis,:] - colonne)**2 + (y[:,np.newaxis] - ligne)**2 < ray**2) & ((x[np.newaxis,:] - colonne)**2 + (y[:,np.newaxis] - ligne)**2 >= (ray-1)**2)
            if cst == True:
                arr2[masque] += coef*r
            else:
                arr2[masque] += coef*((r + 1 - ray)**p)
            if fonction:
                arr2[masque] = fonction(arr2[masque])
        return arr2

def moyenne_mobile_2D(arr, taille_moy): #passe une moyenne mobile carrée de taille taille_moy² sur un array. Dans les faits c'est une convolution avec un kernel rempli de 1 divisé par l'aire de la moyenne mobile.
        moy = np.ones((taille_moy, taille_moy))
        return signal.convolve2d(arr, moy, 'same', 'symm')/(taille_moy**2) # 'same' fait qu'on change pas la taille de notre array et 'symm' fait que la bordure autour utilisée pour les calculs des bords est remplie de la valeur la plus proche et pas de 0.