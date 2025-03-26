import unittest
import numpy as np
from pyslam.asc_grid import AscGrid
from pyslam.asc_indexed import AscIndexed
from pyslam.indirection import Indirection, CategoryMapper
from pyslam.properties import (
    SoilProperties,
    DirectSampler,
    MeanSampler,
    MinMaxSampler,
    Properties
)


class TestProperties(unittest.TestCase):

    def setUp(self):
        # Create a dummy AscGrid for testing
        self.grid_data = np.array(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.int32)
        self.asc_grid = AscGrid(self.grid_data, corners=(
            0., 0.), cellsize=1., no_data=-9999)

        # Create a dummy Indirection for testing
        self.mapper = CategoryMapper({'hsg': 0, 'Ks': 1, 'C': 2, 'Cmin': 3, 'Cmax': 4,
                                     'phi': 5, 'phimin': 6, 'phimax': 7, 'h': 8, 'dens': 9, 'porosity': 10})
        self.indirections = {
            1: [10, 0.1, 0.2, 0.1, 0.3, 0.3, 0.2, 0.4, 100, 1.5, 0.4],
            2: [20, 0.2, 0.3, 0.2, 0.4, 0.4, 0.3, 0.5, 200, 1.6, 0.5],
            3: [30, 0.3, 0.4, 0.3, 0.5, 0.5, 0.4, 0.6, 300, 1.7, 0.6],
            4: [40, 0.4, 0.5, 0.4, 0.6, 0.6, 0.5, 0.7, 400, 1.8, 0.7],
            5: [50, 0.5, 0.6, 0.5, 0.7, 0.7, 0.6, 0.8, 500, 1.9, 0.8],
            6: [60, 0.6, 0.7, 0.6, 0.8, 0.8, 0.7, 0.9, 600, 2.0, 0.9],
            7: [70, 0.7, 0.8, 0.7, 0.9, 0.9, 0.8, 1.0, 700, 2.1, 1.0],
            8: [80, 0.8, 0.9, 0.8, 1.0, 1.0, 0.9, 1.1, 800, 2.2, 1.1],
            9: [90, 0.9, 1.0, 0.9, 1.1, 1.1, 1.0, 1.2, 900, 2.3, 1.2],
        }
        self.indirection = Indirection(self.mapper, self.indirections)

        # Create an AscIndexed instance
        self.asc_indexed = AscIndexed(self.asc_grid, self.indirection)

        # Create a SoilProperties instance
        self.soil_properties = SoilProperties(self.asc_indexed)

    def test_init(self):
        self.assertEqual(self.soil_properties.indexed, self.asc_indexed)
        self.assertEqual(self.soil_properties.keys,
                         SoilProperties.sampler_types.keys())
        self.assertEqual(self.soil_properties.indirection, self.indirection)
        self.assertEqual(self.soil_properties.sampler_types,
                         SoilProperties.sampler_types)

    def test_map_valid_key(self):
        # Test with a valid key
        self.soil_properties.map('Ks')
        self.soil_properties.map('C')
        self.soil_properties.map('phi')
        self.soil_properties.map('h')
        self.soil_properties.map('dens')
        self.soil_properties.map('porosity')

    def test_map_invalid_key(self):
        # Test with an invalid key
        with self.assertRaises(AssertionError):
            self.soil_properties.map('invalid_key')

    def test_sampler_direct_sampler(self):
        # Test with a key that should return a DirectSampler
        sampler = self.soil_properties.sampler('Ks', 1)
        self.assertIsInstance(sampler, DirectSampler)
        self.assertEqual(sampler.value(), 0.1)

        sampler = self.soil_properties.sampler('h', 2)
        self.assertIsInstance(sampler, DirectSampler)
        self.assertEqual(sampler.value(), 200)

        sampler = self.soil_properties.sampler('dens', 3)
        self.assertIsInstance(sampler, DirectSampler)
        self.assertEqual(sampler.value(), 1.7)

        sampler = self.soil_properties.sampler('porosity', 4)
        self.assertIsInstance(sampler, DirectSampler)
        self.assertEqual(sampler.value(), 0.7)

    def test_sampler_mean_sampler(self):
        # Test with a key that should return a MinMaxSampler
        sampler = self.soil_properties.sampler('C', 1)
        self.assertIsInstance(sampler, MeanSampler)
        self.assertEqual(sampler.mean, 0.2)
        # self.assertGreaterEqual(sampler.value(), sampler.min)
        # self.assertLessEqual(sampler.value(), sampler.max)

        sampler = self.soil_properties.sampler('phi', 2)
        self.assertIsInstance(sampler, MeanSampler)
        self.assertEqual(sampler.mean, 0.4)
        # self.assertGreaterEqual(sampler.value(), sampler.min)
        # self.assertLessEqual(sampler.value(), sampler.max)

    def test_sampler_invalid_key(self):
        # Test with an invalid key
        with self.assertRaises(AssertionError):
            self.soil_properties.sampler('invalid_key', 1)

    def test_direct_sampler_value(self):
        sampler = DirectSampler(10)
        self.assertEqual(sampler.value(), 10)

    def test_min_max_sampler_value(self):
        sampler = MinMaxSampler(1, 10)
        self.assertGreaterEqual(sampler.value(), 1)
        self.assertLessEqual(sampler.value(), 10)

    def test_sampler_unsupported_type(self):
        class DummySampler:
            pass

        class DummyProperties(Properties):
            sampler_types = {'dummy': DummySampler}

            def __init__(self, indexed):
                super().__init__(self.sampler_types, indexed)

        dummy_properties = DummyProperties(self.asc_indexed)
        with self.assertRaises(ValueError):
            dummy_properties.sampler('dummy', 1)


if __name__ == '__main__':
    unittest.main()
