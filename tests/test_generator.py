import unittest
import torch
from pyslam.torch.generator import Generator
from pyslam.torch.dataset_fs import DatasetFS
from pathlib import Path

class TestGenerator(unittest.TestCase):
    def test_gen(self):
        in_channels = 5
        out_channels = 1
        generator = Generator(in_channels=in_channels, out_channels=out_channels)
        path = Path("D:/repositories/pyslam/output")
        dataset = DatasetFS(path)
        batch_size = 3
        trainloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)
        real_data, e = next(iter(trainloader))
        out = generator(real_data)
        print(out)
        print(out.shape)
        self.assertListEqual(list(out.shape), [batch_size, out_channels, 256, 256])

if __name__ == '__main__':
    unittest.main()