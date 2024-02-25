# TerrestrialTrain.py
from ..Train import Train
from ..Models.TerrestrialModel import TerrestrialModel
import ee

class TerrestrialTrain(Train):
    def __init__(self):
        print('Training Terrestrial Model')
        super().__init__(TerrestrialModel())

    def train_data(self, dataset, output_folder):
        print('Traiing_Started')
        # Assume dataset is an Earth Engine image collection
        self.model.train()

        # Export the sampled regions data to a CSV file
        training_data = dataset.select(self.model.get_feature_names()).sampleRegions(collection=dataset.select('land_cover'), scale=30)
        task = ee.batch.Export.table.toDrive(collection=training_data, description='Training_Data', folder=output_folder, fileFormat='CSV')
        task.start()
        print('Training data exported to CSV. Check the Tasks tab in the Earth Engine Code Editor for export status.')

    def save_model(self, filepath):
        # Save the trained Terrestrial model to a file
        self.model.save(filepath)
        print(f'Trained model saved to: {filepath}')

