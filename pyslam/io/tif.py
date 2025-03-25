import rasterio

from pyslam.asc_grid import AscGrid


def grid_from_tif(filename) -> AscGrid:

    # Ouvrir le fichier GeoTIFF
    with rasterio.open(filename) as src:
        # Lire toutes les bandes dans un tableau NumPy
        array = src.read()  # (bands, height, width)

        # Vérifier le type des données
        # (nombre_de_bandes, hauteur, largeur)
        print(f"Shape du tableau : {array.shape}")
        # Exemple: uint16, float32, etc.
        print(f"Type des données : {array.dtype}")

        # Résolution (taille des pixels en X et Y)
        resolution = src.res  # (pixel_width, pixel_height)

        # Coordonnées du coin supérieur gauche (origine)
        top_left = src.transform * (0, 0)  # (longitude, latitude)

        print(f"Résolution des pixels : {resolution}")
        print(f"Coordonnées du coin supérieur gauche : {top_left}")

        grid = AscGrid(np.transpose(np.array(array[0, :, :])),
                       corners=(top_left[1], top_left[0]), cellsize=resolution[0])

    return grid
