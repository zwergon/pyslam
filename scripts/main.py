import static_maps
import slam
import crop
import ouvre_fichiers

if __name__ == "__main__":
    print("starting")
    """pour utiliser ce script il y a comme prérequis : mettre les rasters à crop dans un dossier dans pyslam/data/VOTRE_DOSSIER et mettre "VOTRE_DOSSIER" en argument de ouvre_fichiers.
    VOTRE_DOSSIER s'appelle to_crop par défaut mais vous pouvez l'appeller comme vous voulez. Si pas de crop voulu, mettre les raster dans pyslam/data et ne pas donner d'argument à ouvre_fichiers.
    Il faut aussi deux dossiers pyslam/output/static_maps et pyslam/output/slam créés au préalable et vides. Enfin, les deux CSV sont dans pyslam/data."""
    dem, lulc, rain_ant, rain, soil = ouvre_fichiers.ouvre_fichiers("to_crop") #on charge les fichiers une seule fois plutôt qu'à chaque appel de crop (a beaucoup d'impact si on fait plusieurs itérations)
    for i in range(13):
        crop.crop(256*i, 256*(i+1) - 1, 256*i, 256*(i+1) - 1, dem=dem, lulc=lulc, rain_ant=rain_ant, rain=rain, soil=soil, out_dir=f"{i}")
        static_maps.static_maps(in_dir=f"{i}", out_dir=f"{i}")
        slam.slam(ligne=100, colonne=100, r=0, coef_cercle=0.005, cst=True, coef_pluie=1, coef_cohesion=0.1, in_dir=f"{i}", static_maps_dir=f"{i}", out_dir=f"{i}")