import os
import unittest

from pyslam.utils.config import config
from pyslam.io.maps import CLCCategoryMapper


class TestMaps(unittest.TestCase):

    def test_clc_mapper(self):
        clc_mapper = CLCCategoryMapper()
        self.assertTrue(isinstance(clc_mapper, dict))
        self.assertEqual(len(clc_mapper), 45)
        print(clc_mapper.get_key("077-077-255"))
        print(clc_mapper.get_key_from_rgb([77, 77, 255]))
        print(clc_mapper.get_key_from_rgb([77, 77, 255, 255]))
        print(clc_mapper.get_key_from_rgb(None))


if __name__ == "__main__":
    unittest.main()
