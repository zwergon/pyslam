from pathlib import Path
import torch
from torch.utils.data import Dataset
import numpy as np
from pyslam.io.asc import grid_from_asc

class DatasetFS(Dataset):
    def __init__(self, directory : Path, transform=None, target_transform=None):
        self.dir = directory
        self.transform = transform
        self.traget_transform = target_transform

    def __len__(self):
        return len(list(self.dir.glob('*')))
    
    def __getitem__(self, idx):
        input_path = self.dir / f"{idx}" / "model_input"
        output_path = self.dir / f"{idx}" /  "model_output"
        
        dem = grid_from_asc(input_path/"dem_8.asc").grid
        lulc = grid_from_asc(input_path/"lulc_8.asc").grid
        rain_ant = grid_from_asc(input_path/"rain_ant_8.asc").grid
        rain = grid_from_asc(input_path/"rain_8.asc").grid
        soil = grid_from_asc(input_path/"soil_8.asc").grid

        stacked = np.stack([dem, lulc, soil, rain_ant, rain], axis=-1)
        inputs = torch.from_numpy(stacked)

        proba = grid_from_asc(output_path/"PoF_levels.asc").grid
        output = torch.from_numpy(proba)

        if self.transform:
            inputs = self.transform(inputs)
        if self.traget_transform:
            output = self.target_transform(output)
        return(inputs, output)