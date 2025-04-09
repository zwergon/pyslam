
import numpy as np
from pyslam.asc_indexed import AscIndexed


class Sampler:
    def __init__(self, key: str, indexed: AscIndexed):
        self.key = key
        self.indexed: AscIndexed = indexed

    @property
    def indirection(self):
        return self.indexed.indirection

    def sample(self, value):
        pass


class DirectSampler(Sampler):

    def sample(self, value):
        return np.float32(self.indirection.out_value(self.key, value))


class MinMaxSampler(Sampler):

    def sample(self, value):
        min = np.float32(
            self.indirection.out_value(f"{self.key}min", value))
        max = np.float32(
            self.indirection.out_value(f"{self.key}max", value))

        return np.random.uniform(min, max)


class MeanSampler(Sampler):

    def sample(self, value, std=False):
        min = np.float32(
            self.indirection.out_value(f"{self.key}min", value))
        max = np.float32(
            self.indirection.out_value(f"{self.key}max", value))
        mean = (min + max) / 2.
        stdmin = (max - min) / 4.
        if std == True: #permet de ne récupérer que l'écart type, afin de pouvoir l'utiliser dans la probabilty of failure
            return stdmin
        return np.random.normal(mean, stdmin)
    
class TanMeanSampler(Sampler): #sampler pour la tangente directement, permet d'échantilloner directement dessus puisque la moyenne des tangentes n'est pas égale à la tangente de la moyenne

    def sample(self, value, std=False):
        min = np.float32(
            self.indirection.out_value(f"{(self.key)[4:]}min", value))
        tan_min = np.tan(min*np.pi/180)
        max = np.float32(
            self.indirection.out_value(f"{(self.key)[4:]}max", value))
        tan_max = np.tan(max*np.pi/180)
        tan_mean = (tan_min + tan_max) / 2.
        tan_stdmin = (tan_max - tan_min) / 4.
        if std == True:
            return tan_stdmin
        return np.random.normal(tan_mean, tan_stdmin)
