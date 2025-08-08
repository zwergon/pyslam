from pathlib import Path
from pyproj import Transformer


class Config:

    def __init__(self) -> None:

        self.data_path = Path(__file__).parent.parent.parent / "data"

        # Emprise de la couche CLC 2012
        # en EPSG:32632 (UTM zone 32N, utilisé par le CLC 2012)
        self.bbox_clc2012 = [
            747547.4962000000523403,  # Ouest
            4721805.0087999999523163,  # Nord
            901147.4962000000523403,  # Est
            4875405.0087999999523163  # Sud
        ]

        # Ne pas excéder 2048x2048 pixels, le serveur WMS peut refuser les requêtes plus grandes
        self.nrows = 2048
        self.ncols = 2048

    def bbox(self, crs: str = None):
        if crs == 'EPSG:32632' or crs is None:
            return self.bbox_clc2012

        transformer = Transformer.from_crs("EPSG:32632", crs, always_xy=True)
        xmin, ymin = transformer.transform(
            self.bbox_clc2012[0], self.bbox_clc2012[1])
        xmax, ymax = transformer.transform(
            self.bbox_clc2012[2], self.bbox_clc2012[3])
        return [xmin, ymin, xmax, ymax]

    @property
    def cellsize_x(self):
        return (self.bbox_clc2012[2] - self.bbox_clc2012[0]) / self.ncols

    @property
    def cellsize_y(self):
        return (self.bbox_clc2012[3] - self.bbox_clc2012[1]) / self.nrows

    @property
    def xllcorner(self):
        return self.bbox_clc2012[0]

    @property
    def yllcorner(self):
        return self.bbox_clc2012[3]


config = Config()
