from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

path = Path(__file__).parent.parent/"data"
path_csv = path/"feuille_exp.csv"
array = np.zeros((3840, 3840))
with open(path_csv) as f:
    f.readline()
    f.readline()
    for line in tqdm(f):
        values = line.strip().replace(',', '.').split(';')
        arr1 = np.ones((256, 256))
        xgauche = int(values[1])
        xdroite = int(values[2])
        yhaut = int(values[3])
        ybas = int(values[4])
        array[yhaut:ybas+1, xgauche:xdroite+1] += arr1
plt.imshow(array)
plt.show()
