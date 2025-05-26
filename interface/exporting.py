import numpy as np
import pandas as pd
import nrrd
from pathlib import Path

class Exporter:

    def __init__(self, params, filenames, output_dir):
        self.params = params
        self.filenames = filenames
        self.output_dir = Path(output_dir)
        self.export_all(self.filenames, self.output_dir)

    def export_all(self, filenames, outputs):
        for file in filenames.Mask:
            self.apply_changes(file, outputs)
     
    def apply_changes(self, filename, output):
        filename = Path(filename)
        raw_filename = Path(filename).name
        seg, h_ = nrrd.read(filename)
        seg = self.rotate(seg, k=self.params["rot"])
        if self.params["flip"]:
            seg = self.flip(seg)
        mask = self.probability_cutoff(seg, self.params["prob"])
        mask = self.pad_scope(mask, self.params["scope"])
        mask = np.astype(mask, np.int8)
        nrrd.write(str(output/raw_filename), mask)

    def rotate(self, volume, k):
        return np.rot90(volume, k=k)
    
    def flip(self, volume):
        return np.fliplr(volume)
    
    def probability_cutoff(self, volume, p):
        threshold = volume.max() * .75
        mask = np.zeros_like(volume)
        mask[volume > threshold] = 1
        return mask
    
    def pad_scope(self, volume, scope):
        lower = scope[0]
        upper = scope[1]
        if lower != 0:
            zeros = np.zeros_like(volume[...,0:lower])
            volume[...,0:lower] = zeros
        if upper != volume.shape[2]:
            zeros = np.zeros_like(volume[...,upper:])
            volume[...,upper:] = zeros
        return volume

    def generate_batch_file(self, directory):
        return
