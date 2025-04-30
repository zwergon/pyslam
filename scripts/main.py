import static_maps
import slam
import time

if __name__ == "__main__":
    static_maps.static_maps()
    slam.slam(ligne=250, colonne=400, r=50, coef_cercle=0.005, cst=True, coef_pluie=2)