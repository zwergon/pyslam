from pyslam.io.asc import grid_from_asc
import matplotlib.pyplot as plt
import sys

def ouvre(path: str):
    """Prends le chemin menant à une image en entrée et le type de données de l'image et affiche l'image. S'utilise depuis une ligne de commande"""
    img = grid_from_asc(path, dtype=float).grid
    plt.imshow(img)
    plt.show()
    return None

if __name__ == '__main__':
    ouvre(sys.argv[1])