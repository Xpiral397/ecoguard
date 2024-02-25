import geemap
import ee

class GeospatialMonitor:
    def __init__(self, roi):
        ee.Initialize(project='eco-guard')
        self.roi = ee.Geometry.Point(roi[0], roi[1])

    def calculate_ndvi(self, image):
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('ndvi')
        return ndvi

    def load_satellite_imagery(self, start_date, end_date, bands=['B4', 'B3', 'B2', 'B8']):
        collection = (ee.ImageCollection('COPERNICUS/S2')
                      .filterBounds(self.roi)
                      .filterDate(ee.Date(start_date), ee.Date(end_date).advance(1, 'day'))  # Advance by 1 day for a single date
                    )

        image = collection
        return image

    def get_ndvi_values(self, start_date, end_date):
        image1 = self.load_satellite_imagery(start_date, end_date, bands=['B4', 'B3', 'B2', 'B8'])
        image2 = self.load_satellite_imagery(start_date, end_date, bands=['B4', 'B3', 'B2', 'B8'])

        ndvi1 = self.calculate_ndvi(image1)
        ndvi2 = self.calculate_ndvi(image2)

        ndvi_values = self.get_ndvi_values_as_integers(ndvi1, ndvi2)

        return ndvi_values

    def get_ndvi_values_as_integers(self, ndvi1, ndvi2):
        ndvi_values1 = ndvi1.multiply(1000).toInt()
        ndvi_values2 = ndvi2.multiply(1000).toInt()

        ndvi_values1_list = ndvi_values1.reduceRegion(reducer=ee.Reducer.toList(), geometry=self.roi).get('nd')
        ndvi_values2_list = ndvi_values2.reduceRegion(reducer=ee.Reducer.toList(), geometry=self.roi).get('nd')

        return ndvi_values1_list.getInfo(), ndvi_values2_list.getInfo()

# Example usage:
# Create an instance of GeospatialMonitor
monitor = GeospatialMonitor([-122.292, 37.9018])

# Get NDVI values for two time periods and convert them to integers
start_date = '2022-01-01'
end_date = '2022-01-01'  # Use the same date for both start and end for a single date
ndvi_values_start, ndvi_values_end = monitor.get_ndvi_values(start_date, end_date)

print("NDVI Values for Start Date:", ndvi_values_start)
print("NDVI Values for End Date:", ndvi_values_end)
