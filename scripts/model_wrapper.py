from tensorflow import keras
from pathlib import Path
from argparse import ArgumentParser

def argparser():
    """
    parser function
    """
    parser = ArgumentParser()
    parser.add_argument('-i', "--input")
    parser.add_argument('-o', "--output")
    parser.add_argument('-s', "--save")
    parser.add_argument('-u', "--update")
    parser.add_argument('-c', "--config")
    return parser.parse_args()

args = argparser()

class ModelWrapper:

    """
    Module for handling keras models and using 
    and updating them.
    """

    def __init__(self):
        return
    
    def load_model(self):
        return
    
    def classify(self):
        return
    
    def update(self):
        return
    
    def load_config(self):
        return
    
    def adapt_input_size(self):
        return

