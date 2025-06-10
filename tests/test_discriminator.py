import unittest
import torch
from pyslam.torch.discriminator import Discriminator
from pyslam.torch.dataset_fs import DatasetFS
from pathlib import Path

class TestDiscriminator(unittest.TestCase):
    
    def test_disc(self):
        path = Path("D:/repositories/pyslam/output")
        dataset = DatasetFS(path)
        trainloader = torch.utils.data.DataLoader(dataset, batch_size=3, shuffle=True)
        real_data, e = next(iter(trainloader))
        e = torch.unsqueeze(e, 1)
        print(e.shape)
        print(real_data.shape)
        disc = Discriminator(6)
        out = disc(real_data, e)
        print(out.shape)



if __name__ == '__main__':
    unittest.main()