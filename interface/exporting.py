import numpy as np
import pandas as pd
import nrrd
from pathlib import Path

class Exporter:

    def __init__(self, params, filenames, output_dir):
        self.params = params
        self.filenames = filenames
        self.output_dir = Path(output_dir)

    def export_all(self, filenames, outputs):
        return
    
    def scope_to_range(self, volume, scope):
        return
    
    def apply_changes(self, filename, output):
        filename = Path(filename).name
        seg, h_ = nrrd.read(filename)
        shape = seg.shape
        pad = np.zeros_like(shape)
        seg = self.rotate(seg, k=self.params["rot"])
        if self.params["flip"]:
            seg = self.flip(seg)
        mask = self.probability_cutoff(pad, self.params["prob"])
        nrrd.write(str(output/filename), mask)

    def rotate(self, volume, k):
        return np.rot90(volume, k=k)
    
    def flip(self, volume):
        return np.fliplr(volume)
    
    def probability_cutoff(self, volume, p):
        threshold = volume.max() * .75
        mask = np.zeros_like(volume)
        mask[volume > threshold] = 1
        return volume
    
    def pad_scope(self, volume, scope):
        return volume

    def generate_batch_file(self, directory):
        return
