from influxdb_client import InfluxDBClient, Point, WritePrecision
import os
import re
import requests
from owslib.wcs import WebCoverageService
from owslib.wms import WebMapService
from PIL import Image
from io import BytesIO
import urllib.request
from urllib.parse import urlencode
from urllib.error import HTTPError
import rasterio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from pykrige.ok import OrdinaryKriging

from rasterio.features import rasterize
from rasterio.transform import from_bounds


from pyslam.utils.config import config
from pyslam.indirection import CategoryMapper


class Map:

    def __init__(self, filename) -> None:
        self.array: np.array = None
        self.palette = None
        self.filename: str = filename

    def download(self):
        pass

    def __repr__(self):
        return f"type array {type(self.array)}, shape {self.array.shape}, dtype {self.array.dtype}"

    def display(self, title: str = None, to_file=True):

        if self.array.dtype == np.dtype('uint8') and self.palette is not None:
            # Afficher l'image en utilisant la palette
            img = Image.fromarray(self.array).convert('P')
            img.putpalette(self.palette)
            plt.imshow(img)
        else:
            plt.imshow(self.array, cmap='ocean')
        plt.axis('off')
        if title is not None:
            plt.title(title)

        if to_file:
            plt.savefig(self.filename)
            plt.close()
        else:
            plt.show()


class DEM(Map):

    # url du service WCS
    wcs_url = "http://tinitaly.pi.ingv.it/TINItaly_1_1/wcs?"

    def __proxy_handler(self):
        # Il faut être authetifié sur le proxy et les variables d'environnement doivent être définies

        proxy = "http://irproxy:8082"
        proxy_handler = urllib.request.ProxyHandler({
            'http': proxy,
            'https': proxy
        })
        return proxy_handler

    def __init__(self) -> None:
        super().__init__(filename="dem_tinitaly.png")
        # GetCoverage direct et par wcs à cause du proxy
        self.layer_name = "TINItaly_1_1:tinitaly_dem"

    def download(self):

        params = {
            "service": "WCS",
            "request": "GetCoverage",
            "version": "1.0.0",
            "coverage": self.layer_name,
            "CRS": "EPSG:32632",
            "BBOX": ",".join(map(str, config.bbox())),
            "format": "geotiff",
            "width": str(config.ncols),
            "height": str(config.nrows)
        }
        full_url = self.wcs_url + urlencode(params)

        print("start download from", full_url)
        try:
            proxy_handler = None  # self.__proxy_handler()
            opener = urllib.request.build_opener()
            with opener.open(full_url) as response:
                coverage_data = response.read()
        except HTTPError as err:
            print(f"proxy error: {err.code}")
            return None

        # Lire avec rasterio
        with rasterio.open(BytesIO(coverage_data)) as src:
            print("CRS :", src.crs)
            print("Taille :", src.width, src.height)
            print("Bbox :", src.bounds)
            self.array = src.read(1)

    def describe(self):
        wcs = WebCoverageService(self.wcs_url, version="1.0.0")
        print("Title: ", wcs.identification.title)
        print("Type: ", wcs.identification.type)
        print("Operations: ", [op.name for op in wcs.operations])
        # Récupérer les couches disponibles
        for layer_name in wcs.contents.keys():
            print(f"Nom de la couche : {layer_name}")
            coverage = wcs.contents[layer_name]
            for format in coverage.supportedFormats:
                print("Format supporté :", format)
            # Affiche les CRS supportés
            crs_list = coverage.supportedCRS
            for crs in crs_list:
                print("CRS:", crs)


class CLCCategoryMapper(CategoryMapper):

    CLC_DICT = {
        1: "230-000-077",
        2: "255-000-000",
        3: "204-077-242",
        4: "204-000-000",
        5: "230-204-204",
        6: "230-204-230",
        7: "166-000-204",
        8: "166-077-000",
        9: "255-077-255",
        10: "255-166-255",
        11: "255-230-255",
        12: "255-255-168",
        13: "255-255-000",
        14: "230-230-000",
        15: "230-128-000",
        16: "242-166-077",
        17: "230-166-000",
        18: "230-230-077",
        19: "255-230-166",
        20: "255-230-077",
        21: "230-204-077",
        22: "242-204-166",
        23: "128-255-000",
        24: "000-166-000",
        25: "077-255-000",
        26: "204-242-077",
        27: "166-255-128",
        28: "166-230-077",
        29: "166-242-000",
        30: "230-230-230",
        31: "204-204-204",
        32: "204-255-204",
        33: "000-000-000",
        34: "166-230-204",
        35: "166-166-255",
        36: "077-077-255",
        37: "204-204-255",
        38: "230-230-255",
        39: "166-166-230",
        40: "000-204-242",
        41: "128-242-230",
        42: "000-255-166",
        43: "166-255-230",
        50: "230-242-255",
        49: "255-255-255",  # Couleur par défaut pour les pixels non classés
    }

    def __init__(self, *args, **kwargs):
        super().__init__(self.CLC_DICT)

    def get_key_from_rgb(self, rgb):
        """
        Retourne la clé correspondant à la valeur RGB.
        :param rgb: tuple (R, G, B)
        :return: clé correspondante ou None si non trouvée
        """
        if rgb is None or len(rgb) < 3:
            return 49

        rgb_str = f"{rgb[0]:03}-{rgb[1]:03}-{rgb[2]:03}"
        return self.get_key(rgb_str)


class LandCover(Map):

    wms_url = "https://image.discomap.eea.europa.eu/arcgis/services/Corine/CLC2012_WM/MapServer/WMSServer?"

    def __init__(self) -> None:
        super().__init__(filename="land_cover.png")
        self.layer_name = "Corine_Land_Cover_2012_raster59601"
        self.clc_category_mapper: CLCCategoryMapper = CLCCategoryMapper()

    def describe(self):
        wms = WebMapService(self.wms_url, version="1.3.0")
        print("Title: ", wms.identification.title)
        print("Type: ", wms.identification.type)
        print("Operations: ", [op.name for op in wms.operations])
        print("GetMap options: ", wms.getOperationByName('GetMap').formatOptions)
        for k in wms.contents.keys():
            print(f"Layer: {k}")
            layer = wms.contents[k]
            print("Title:", layer.title)
            print("CRS:", layer.crsOptions)

    def download(self):
        wms = WebMapService(self.wms_url, version="1.3.0")
        layer = wms.contents[self.layer_name]

        style = layer.styles['default']
        print("Style name: ", style['title'])
        print(style.keys())

        img = wms.getmap(
            layers=[self.layer_name],
            styles=[''],
            srs='EPSG:3035',
            bbox=config.bbox('EPSG:3035'),
            size=(config.ncols, config.nrows),
            format='image/png',  # pour avoir une image indexée avec une palette de couleurs
            transparent=True
        )

        land_cover_img = Image.open(BytesIO(img.read()))
        rgba_array = np.array(land_cover_img)
        self.array = np.zeros(
            shape=(rgba_array.shape[0], rgba_array.shape[1]), dtype=np.uint8)

        for i in range(rgba_array.shape[0]):
            for j in range(rgba_array.shape[1]):
                try:
                    r, g, b, a = rgba_array[i, j, :]

                    self.array[i, j] = self.clc_category_mapper.get_key_from_rgb(
                        [r, g, b])
                except TypeError as e:
                    print(
                        f"Erreur de conversion pour le pixel ({i}, {j}) {[r, g, b]}: {e}")
                    self.array[i, j] = 49

        palette = [0] * 256 * 3
        for code, rgb in self.clc_category_mapper.items():
            try:
                r, g, b = map(int, rgb.split("-"))
            except ValueError:
                print(f"error on {rgb} with code {code}")
                r, g, b = 255, 255, 255
            palette[code * 3 + 0] = r
            palette[code * 3 + 1] = g
            palette[code * 3 + 2] = b

        self.palette = palette


class Soil(Map):

    url = "https://download.pangaea.de/dataset/935673/files/litology_italy.gpkg"

    def __init__(self) -> None:
        super().__init__(filename="soil.png")
        self.layer_name = "Soil_Properties"
        self.gpkg_filename = config.data_path / "litology_italy.gpkg"

    def download(self):

        # 1. download le fichier GPKG depuis l'URL
        if os.path.exists(self.gpkg_filename):
            print(f"Le fichier {self.gpkg_filename} existe déjà.")
        else:
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()
                with open(self.gpkg_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

        # 2. Lire le fichier GPKG avec geopandas et clipping

        gdf = gpd.read_file(self.gpkg_filename)
        print("Nombre de géométries :", len(gdf))
        print("CRS :", gdf.crs)
        print("Bbox :", gdf.total_bounds)
        print("Colonnes :", gdf.columns)
        # Afficher les 5 premières lignes
        # print(gdf.head())

        # Projection vers EPSG:4326 du gpkg https://epsg.io/4326
        assert gdf.crs == "EPSG:4326", "Le GeoDataFrame doit être en EPSG:4326"

        bbox = config.bbox('EPSG:4326')

        gdf_clip = gpd.clip(gdf, box(*bbox))
        print("Nombre de géométries après clipping :", len(gdf_clip))
        print("Bbox après clipping :", gdf_clip.total_bounds)
        print("Colonnes après clipping :", gdf_clip.columns)

        # 3. Créer une image raster à partir du GeoDataFrame
        bounds = gdf_clip.total_bounds

        transform = from_bounds(
            *bounds, width=config.ncols, height=config.nrows)

        # Préparer les shapes (géométrie, valeur)
        shapes = [(geom, value)
                  for geom, value in zip(gdf_clip.geometry, gdf_clip["cat"])]

        # Rasteriser
        self.array = np.array(rasterize(
            shapes=shapes,
            out_shape=(config.ncols, config.nrows),
            transform=transform,
            fill=0,  # ID de fond (optionnel)
            dtype='uint8'
        ))

        # Récupérer la colormap tab20b
        cmap = plt.get_cmap('tab20b')
        self.palette = []
        for i in range(cmap.N):
            r, g, b, _ = cmap(i)
            self.palette.extend([int(r * 255), int(g * 255), int(b * 255)])
        self.palette += [0] * (768 - len(self.palette))


class Rain(Map):

    stations_filename = config.data_path / "stations.gpkg"

    token = "bdfWYR9mSnsAOUy2cVfiGe_AIlpMby_JkJBgMCXI0_IyLSwjmmSiNlbpG1yBjSlaNUVfook4_iXfTZfBmuYCEg=="
    org = "IFPEN"
    url = "http://10.25.11.36:8086"

    def __init__(self, rain_start="2013-01-01T00:00:00Z", delay="1m") -> None:
        super().__init__(filename=f"rain_{delay}.png")
        self.delay = delay
        self.rain_start = rain_start
        self.df_stations_with_rain = None

    @staticmethod
    def __parse_offset(delai):
        match = re.fullmatch(r"(\d+)([ymwdh])", delai)
        if not match:
            raise ValueError(
                "Délai invalide : utiliser des formats comme '1y', '6m', '30d'")
        value, unit = match.groups()
        value = int(value)
        if unit == "y":
            return pd.DateOffset(years=value)
        elif unit == "m":
            return pd.DateOffset(months=value)
        elif unit == "w":
            return pd.Timedelta(weeks=value)
        elif unit == "d":
            return pd.Timedelta(days=value)
        elif unit == "h":
            return pd.Timedelta(hours=value)
        else:
            raise ValueError("Unité non reconnue")

    def __krige(self, value_column='rain'):

        gdf = self.df_stations_with_rain
        """
        Interpolation par krigeage sur une grille régulière.
        """
        # S'assurer du bon système de coordonnées
        if gdf.crs.to_epsg() != 32632:
            gdf = gdf.to_crs(epsg=32632)

        # Extraire les coordonnées et valeurs
        x = gdf.geometry.x.values
        y = gdf.geometry.y.values
        z = gdf[value_column].values

        # Définir la grille
        xmin, ymin, xmax, ymax = config.bbox()
        gridx = np.linspace(xmin, xmax, config.ncols)
        gridy = np.linspace(ymin, ymax, config.nrows)

        # Appliquer le krigeage
        OK = OrdinaryKriging(
            x, y, z,
            variogram_model='spherical',  # 'linear', 'gaussian', 'spherical', 'exponential'
            verbose=True,
            enable_plotting=False
        )
        z_kriged, ss = OK.execute('grid', gridx, gridy)
        print("Krigeage terminé.")

        return z_kriged[::-1, :]

    def add_precipitation(self, dfita):

        client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        """
        Ajoute la colonne 'rain' au DataFrame dfita avec les précipitations pour chaque station.
        Les paramètres rain_start et delai définissent la période de récupération des données.
        Le paramètre delai doit être au format '1y', '6m', '30d', '1w', '12h' etc.
        """
        rain_stop = pd.to_datetime(self.rain_start) + \
            self.__parse_offset(self.delay)

        query = """from(bucket: "rainfall")
            |> range(start: {}, stop: {})
            |> filter(fn: (r) => r._measurement == "rainfall")
            |> filter(fn: (r) => r._field == "Precipitazione")
            |> filter(fn: (r) => r.Codice_sensore == "{}")
            |> sum()"""

        dfita = dfita.copy()  # Ensure we are working on a copy to avoid SettingWithCopyWarning
        dfita["rain"] = np.nan
        query_api = client.query_api()
        for id in dfita["id"]:
            tables = query_api.query(query.format(
                self.rain_start, rain_stop.strftime('%Y-%m-%dT%H:%M:%SZ'), id))
            if len(tables) > 0:
                record = tables[0].records[0]
                dfita.loc[dfita["id"] == id, "rain"] = record.get_value()

        dfita = dfita.dropna(subset=["rain"])
        dfita = dfita[dfita['rain'] > 0]
        return dfita

    def download(self):

        # 1. load dataframe of stations
        print("load stations")
        df_stations = gpd.read_file(self.stations_filename)
        print("Nombre de géométries :", len(df_stations))
        print("CRS :", df_stations.crs)
        print("Bbox :", df_stations.total_bounds)
        print("Colonnes :", df_stations.columns)
        # Afficher les 5 premières lignes
        # print(df_stations.head())

        # Projection vers EPSG:4326 du gpkg https://epsg.io/4326
        assert df_stations.crs == "EPSG:4326", "Le GeoDataFrame doit être en EPSG:4326"

        bbox = config.bbox("EPSG:4326")
        df_stations_clip = gpd.clip(df_stations, box(*bbox))
        print("Nombre de géométries :", len(df_stations_clip))
        print("CRS :", df_stations_clip.crs)
        print("Bbox :", df_stations_clip.total_bounds)
        print("Colonnes :", df_stations_clip.columns)

        self.df_stations_with_rain = self.add_precipitation(df_stations_clip)
        self.array = self.__krige()


    # Affichage
if __name__ == "__main__":
    # dem = DEM()
    # # dem.describe()
    # dem.download()
    # print(dem)
    # dem.display(title="DEM TINItaly")

    # land_cover = LandCover()
    # # land_cover.describe()
    # land_cover.download()
    # print(land_cover)
    # land_cover.display(title="Land Cover Corine 2012")

    # soil = Soil()
    # soil.download()
    # soil.display(title="Soil Marche (Italy)")

    rain_1m = Rain()
    rain_1m.download()
    rain_1m.display("Krigeage Rain (1m)")
