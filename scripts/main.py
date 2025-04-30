import static_maps
import slam

if __name__ == "__main__":
    static_maps.static_maps()
    slam.slam(ligne=250, colonne=400, r=50, coef=0.005, cst=True)