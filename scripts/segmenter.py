from pathlib import Path
import nrrd
import numpy as np
from tensorflow import keras

class Segmenter:

    def __init__(self, model, input_directory,
                 output_directory, glob_pattern) -> None:

        self.model = Path(model)
        self.input_directory = Path(input_directory)
        self.output_directory = Path(output_directory)
        self.glob_pattern = glob_pattern
    
    def segment(self, reshape=False):
        print(f"Loading data from: {self.input_directory}")

        nrrds = self.input_directory.glob(
            self.glob_pattern
        )
        print(f"Loading model: {self.model}")
        model = self.load_model(self.model)
        model.name = "model"
        if reshape:
            model = self.reshape_input(model)


        for file in nrrds:
            data, header = nrrd.read(str(file)) 
            volume = np.expand_dims(data, axis=-1)
            seg_out = self.output_directory/ Path(file.stem + ".seg.nrrd")
            # try:
            predictions = model.predict(volume)
            nrrd.write(str(seg_out), predictions)
            # except:
            print(file)
        print("Done...")
        return
    

    def reshape_input(self, model):
        input_layer = keras.Input(shape=(128, 128, 1))
        resized = keras.layers.Resizing(96, 96)(input_layer)
        output = model(resized)

        wrapped_model = keras.Model(inputs=input_layer, outputs=output)
        return wrapped_model

    def load_model(self, model):
        if model == None:
            print("specify path first")
            return
        return keras.models.load_model(model, compile=True)

    def prob_cutoff(self):
        return
    
    def scale_data(self, volume, upper=3517):
        return np.array(volume)/upper
    
    def clip_data(self, vol, upper=None, lower=None):
        return


if __name__ == "__main__":
    # T1 exvivo
    # segmenter = Segmenter(model="../models/unet_T1_exvivo_v2_exvivo.model.keras",
    #                       input_directory="../data/processed/nrrds",
    #                       output_directory="../data/processed/segmentations",
    #                       glob_pattern="T1*exvivo_*.nrrd")
    # DWI exvivo
    segmenter = Segmenter(model="../models/unet_DWI_exvivo_v2.model.keras",
                          input_directory="../data/processed/nrrds",
                          output_directory="../data/raw/segmentations",
                          glob_pattern="DWI*exvivo*_*.nrrd")
    # ASL exvivo
    segmenter.segment(reshape=True)