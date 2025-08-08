import os
import unittest

from pyslam.utils.config import config


class TestConfig(unittest.TestCase):

    def test_config(self):
        self.assertTrue(os.path.exists(config.data_path))
        self.assertAlmostEqual(config.cellsize_x, config.cellsize_y)

    def test_bbox(self):
        self.assertSequenceEqual(config.bbox(), config.bbox_clc2012)
        self.assertSequenceEqual(config.bbox(
            "EPSG:32632"), config.bbox_clc2012)
        print(config.bbox("EPSG:3035"))


if __name__ == "__main__":
    unittest.main()
