from torch.utils.data import DataLoader
from pyslam.torch.dataset import DatasetFS
import matplotlib.pyplot as plt
from pathlib import Path

path = Path("D:/repositories/pyslam/output")
train_data = DatasetFS(path)
train_dataloader = DataLoader(train_data, batch_size=1, shuffle=True)
for step, (train_features, train_labels) in enumerate(train_dataloader):
    print(f"Feature batch shape: {train_features.size()}")
    print(f"Labels batch shape: {train_labels.size()}")
    img = train_labels[0].squeeze()
    plt.imshow(img)
    plt.show()
