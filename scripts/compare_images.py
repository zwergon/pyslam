from pyslam.io.asc import grid_from_asc
import matplotlib.pyplot as plt
import sys
from pathlib import Path

def compare(img1: Path|str, img2: Path|str):
    """fais la différence pixel par pixel entre deux arrays et affiche le résultat. Prends en entrée les chemins respectifs des images. S'utilise depuis la ligne de commande."""
    i1 = grid_from_asc(img1, dtype=float).grid
    i2 = grid_from_asc(img2, dtype=float).grid
    i = i1 - i2
    plt.imshow(i)
    plt.show()
    return None

if __name__ == "__main__":
    compare(sys.argv[1], sys.argv[2])