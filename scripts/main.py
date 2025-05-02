import static_maps
import slam
import crop
import ouvre_fichiers

if __name__ == "__main__":
    dem, lulc, rain_ant, rain, soil = ouvre_fichiers.ouvre_fichiers("to_crop") #on charge les fichiers une seule fois plutôt qu'à chaque appel de crop (a beaucoup d'impact si on fait plusieurs itérations)
    crop.crop(1000, 1599, 1600, 1999, dem=dem, lulc=lulc, rain_ant=rain_ant, rain=rain, soil=soil)
    static_maps.static_maps()
    slam.slam(ligne=250, colonne=400, r=50, coef_cercle=0.005, cst=True, coef_pluie=2)