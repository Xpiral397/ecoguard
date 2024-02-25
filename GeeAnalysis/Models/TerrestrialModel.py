from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import ee
from typing import Optional
import numpy as np
import pandas as pd

class TerrestrialModel:
    def __init__(self):
        self.model = None

    def extract_and_convert_to_dataset(self, roi, label_band, start_date, end_date):
        """
        Extract data from Google Earth Engine and convert it to a meaningful dataset.

        Parameters:
        - roi (list): Region of Interest coordinates.
        - label_band (str): The label band in the Earth Engine dataset.
        - start_date (str): Start date for data extraction.
        - end_date (str): End date for data extraction.

        Returns:
        - pd.DataFrame: Extracted and converted dataset.
        """
        print('Extracting and Converting to Dataset')

        # Initialize Earth Engine
        ee.Initialize()

        # Load Landsat image collection
        landsat_collection = (
            ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
            .filterBounds(ee.Geometry.Polygon(roi))
            .filterDate(ee.Date(start_date), ee.Date(end_date))
        )

        # Extract spectral bands and vegetation indices
        input_data = landsat_collection.select(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'])
        input_data = input_data.addBands(input_data.normalizedDifference(['B5', 'B4']).rename('NDVI'))
        input_data = input_data.addBands(
            input_data.expression('2.5 * (B5 - B4) / (B5 + 6 * B4 - 7.5 * B2 + 1)').rename('EVI')
        )

        # Sample the data at the specified ROI
        sampled_data = input_data.sampleRegions(
            collection=input_data.select(label_band),
            properties=[label_band],
            scale=30,
            geometries=ee.Geometry.Polygon(roi)
        )

        # Convert Earth Engine FeatureCollection to a NumPy array
        array_data = np.array(sampled_data.getInfo()['features'])

        # Extract features and labels from the NumPy array
        features = []
        labels = []
        for feature in array_data:
            properties = feature['properties']
            labels.append(properties[label_band])
            features.append([properties[band] for band in ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'NDVI', 'EVI']])

        # Convert to pandas DataFrame
        df = pd.DataFrame(features, columns=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'NDVI', 'EVI'])
        df[label_band] = labels

        print('Extraction and Conversion Completed')
        return df

    def train(self, data: Optional[pd.DataFrame] = None):
        print('Start Training')

        if data is None:
            raise ValueError("Training data is required. Use extract_and_convert_to_dataset method to obtain data.")

        # Split the data into training and testing sets
        train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

        # Extract features and labels from the training set
        features = train_data[['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'NDVI', 'EVI']]
        labels = train_data['land_cover']

        # Train the model using scikit-learn RandomForestClassifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(features, labels)

        print('Train Successfully')

    def predict(self, data):
        if self.model is not None:
            # Implement your prediction logic here using the trained model and new data
            # You may need to preprocess the new data similarly to the training data
            pass
        else:
            print('Model not trained. Train the model before making predictions.')
