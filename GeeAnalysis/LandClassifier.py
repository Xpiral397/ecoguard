# LandClassifier.py
from Train import Train
from TerrestrialModel import TerrestrialModel
from MarineModel import MarineModel
import ee  # Make sure to have Earth Engine Python API installed

class LandClassifier:
    def __init__(self):
        # Initialize authentication for Google Earth Engine
        ee.Initialize()

        # Load models
        self.terrestrial_model = TerrestrialModel()
        self.marine_model = MarineModel()

        # Create a Train instance for each model
        self.terrestrial_trainer = Train(self.terrestrial_model)
        self.marine_trainer = Train(self.marine_model)

    def train_models(self):
        # Train terrestrial model
        terrestrial_dataset = "Datasets/Terrestrial/terrestrial_dataset.csv"
        self.terrestrial_trainer.train_data(terrestrial_dataset)
        self.terrestrial_trainer.save_model("terrestrial_model")

        # Train marine model
        marine_dataset = "Datasets/Marine/marine_dataset.csv"
        self.marine_trainer.train_data(marine_dataset)
        self.marine_trainer.save_model("marine_model")

    def predict_landcover(self, landcover_dataset):
        # Load the landcover dataset and perform predictions
        pass
