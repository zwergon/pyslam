import numpy as np

from pyslam.arcgrid import ArcGrid

# Variables globales

nodata = -9999
outside = nodata


R_D = 0.0174532  # Exemple de valeur pour R_D, à ajuster selon vos besoins


def fill_sinks_calc(grid: ArcGrid, itermax=10000):

    inix = -1
    iniy = -1
    # Initialisation des variables
    cotamin = 100000.0
    # Trouver la cellule avec l'élévation minimale
    for j in range(grid.my):
        for i in range(grid.mx):
            if grid.grid[i, j] != nodata and grid.grid[i, j] < cotamin:
                cotamin = grid.grid[i, j]
                inix = i
                iniy = j

    # Boucle principale pour le remplissage des dépressions
    numiter = 0
    numsin = -9999
    while numsin != 0 and numiter < itermax:
        numiter += 1
        numsin = 0

        for j in range(1, grid.my - 1):
            for i in range(1, grid.mx - 1):
                sinkflag = 1
                numoutside = 0

                # Sauter les cellules à l'extérieur et l'exutoire
                if grid.grid[i, j] == outside or (i == inix and j == iniy):
                    continue
                else:
                    for yloc in range(-1, 2):
                        for xloc in range(-1, 2):
                            if xloc != 0 or yloc != 0:
                                if xloc == 0 or yloc == 0:
                                    grad = np.tan(R_D / 10000.0) * grid.dx
                                else:
                                    grad = np.tan(R_D / 10000.0) * \
                                        np.sqrt(grid.dx**2 + grid.dy**2)

                                if grid.grid[i, j] > grid.grid[i + xloc, j + yloc]:
                                    sinkflag = 0

                                if grid.grid[i + xloc, j + yloc] == outside and numiter > 10:
                                    numoutside += 1

                # Si sinkflag == 1, alors nous avons une dépression sauf si elle borde une cellule extérieure
                if sinkflag == 1 and numoutside == 0:
                    numsin += 1
                    elemin = float('inf')

                    # Chercher l'élévation minimale autour d'une cellule et augmenter l'élévation de la cellule dépression
                    for yloc in range(-1, 2):
                        for xloc in range(-1, 2):
                            if grid.grid[i + xloc, j + yloc] != outside and (xloc != 0 or yloc != 0):
                                if grid.grid[i + xloc, j + yloc] < elemin:
                                    elemin = grid.grid[i + xloc, j + yloc]
                                    if xloc == 0 or yloc == 0:
                                        grad = np.tan(R_D / 10000.0) * grid.dx
                                    else:
                                        grad = np.tan(
                                            R_D / 10000.0) * np.sqrt(grid.dx**2 + grid.dy**2)

                    grid.grid[i, j] = elemin + grad

        # Sortie
        print(f"Number of fillsinks iteration: {numiter}")
        print(f"Number of sinks: {numsin}")

    # Sortie finale
    print(f"Number of sinks: {numsin}")
