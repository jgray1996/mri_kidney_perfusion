import matplotlib.pyplot as plt

class Tester:

    def __init__(self, model,
                 training_data,
                 test_data, 
                 validation_data) -> None:
        self.model = model
        self.training_data = training_data
        self.test_data = test_data
        self.validation_data = validation_data
        pass

    def run_tests(self) -> None:
        pass

    def AUC(self) -> None:
        pass 

    def DICE(self) -> None:
        pass

    def plot_segmentations(self) -> None:
        pass

class Comparer:

    def __init__(self, model_a, model_b,
                 name_a=None, name_b=None):
        pass