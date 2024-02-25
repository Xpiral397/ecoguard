
import ee, threading
import time
import ee

import os
import ee
from google.oauth2 import service_account

def init_ee():
    path = os.path.join(os.path.dirname(__file__), 'client-key.json')
    cred = service_account.Credentials.from_service_account_file(path, scopes=['https://www.googleapis.com/auth/earthengine'])
    ee.Initialize(credentials=cred, project ='eco-guard')


# Use ee module in your Django project
# For example:
# collection = ee.ImageCollection('COPERNICUS/S2').filterBounds(ee.Geometry.Point(-122.08, 37.38))
# print("Image Collection Info:", collection.getInfo())
init_ee()

class DeepAnalyzer:
    def __init__(self, polygon):
        self.polygon = polygon
        self.deep_learning = {}
        print('insantited')
        init_ee()

    def _create_geometry_from_polygon(self):
        return ee.Geometry.Polygon(self.polygon)
    
    def classify_ground_displacement(self,image):
        ndvi = image.normalizedDifference(['B4', 'B3']).rename('NDVI')

        # NDWI (Normalized Difference Water Index)
        ndwi = image.normalizedDifference(['B2', 'B4']).rename('NDWI')

        # EVI2 (Enhanced Vegetation Index 2)
        evi2 = image.expression('2.5 * (b4 - b3) / (b4 + 2.4 * b3 + 1)', {
            'b4': image.select('B4'),
            'b3': image.select('B3')
        }).rename('EVI2')

        # MNDWI (Modified Normalized Difference Water Index)
        mndwi = image.normalizedDifference(['B2', 'B5']).rename('MNDWI')

        # NDBI (Normalized Difference Built-up Index)
        ndbi = image.normalizedDifference(['B5', 'B4']).rename('NDBI')

        # Additional Indices (customize as needed)
        evi = image.expression('2.5 * (b4 - b3) / (b4 + 6 * b3 - 7.5 * b1 + 1)', {
            'b4': image.select('B4'),
            'b3': image.select('B3'),
            'b1': image.select('B1')
        }).rename('EVI')

        savi = image.expression('(1 + L) * (NIR - Red) / (NIR + Red + L)', {
            'NIR': image.select('B4'),
            'Red': image.select('B3'),
            'L': 0.5
        }).rename('SAVI')

        msavi2 = image.expression('(2 * NIR + 1 - sqrt((2 * NIR + 1)**2 - 8 * (NIR - Red))) / 2', {
            'NIR': image.select('B4'),
            'Red': image.select('B3')
        }).rename('MSAVI2')

        # Add the indices to the original image
        image_with_indices = image.addBands([ndvi, ndwi, evi2, mndwi, ndbi, evi, savi, msavi2])

        # Compute index values
        ndvi_value = image_with_indices.reduceRegion(reducer=ee.Reducer.mean(), geometry=image.geometry(),
                                                        scale=30, bestEffort=True, maxPixels=10000000).get('NDVI').getInfo()
        ndwi_value = image_with_indices.reduceRegion(reducer=ee.Reducer.mean(), geometry=image.geometry(),
                                                        scale=30, bestEffort=True, maxPixels=1e13).get('NDWI').getInfo()
        evi2_value = image_with_indices.reduceRegion(reducer=ee.Reducer.mean(), geometry=image.geometry(),
                                                        scale=30, bestEffort=True, maxPixels=1e13).get('EVI2').getInfo()
        mndwi_value = image_with_indices.reduceRegion(reducer=ee.Reducer.mean(), geometry=image.geometry(),
                                                        scale=30, bestEffort=True, maxPixels=1e13).get('MNDWI').getInfo()
        ndbi_value = image_with_indices.reduceRegion(reducer=ee.Reducer.mean(), geometry=image.geometry(),
                                                        scale=30, bestEffort=True, maxPixels=1e13).get('NDBI').getInfo()
        evi_value = image_with_indices.reduceRegion(reducer=ee.Reducer.mean(), geometry=image.geometry(),
                                                        scale=30, bestEffort=True, maxPixels=1e13).get('EVI').getInfo()
        savi_value = image_with_indices.reduceRegion(reducer=ee.Reducer.mean(), geometry=image.geometry(),
                                                        scale=30, bestEffort=True, maxPixels=1e13).get('SAVI').getInfo()
        msavi2_value = image_with_indices.reduceRegion(reducer=ee.Reducer.mean(), geometry=image.geometry(),
                                                        scale=30, bestEffort=True, maxPixels=1e13).get('MSAVI2').getInfo()

        # Create a dictionary with index values
        index_values = {
            'NDVI': ndvi_value,
            'NDWI': ndwi_value,
            'EVI2': evi2_value,
            'MNDWI': mndwi_value,
            'NDBI': ndbi_value,
            'EVI': evi_value,
            'SAVI': savi_value,
            'MSAVI2': msavi2_value
        }

        return index_values

    def _calculate_ndvi(self, image):
        nir = image.select('B5')
        red = image.select('B4')
        ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
        return ndvi

    def _calculate_land_cover_diversity(self, image):
        land_cover_bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']
        land_cover_image = image.select(land_cover_bands)
        diversity = land_cover_image.reduce(ee.Reducer.stdDev())
        return diversity

    # ...


    def _calculate_life_measurement(self, image):
        ndvi = self._calculate_ndvi(image)
        land_cover_diversity = self._calculate_land_cover_diversity(image)

        mean_ndvi = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=self._create_geometry_from_polygon(), scale=30
        )
        mean_ndvi_value = ee.Number(mean_ndvi.get('NDVI'))

        # Extract a scalar value from the image
        land_cover_diversity_scalar = land_cover_diversity.reduceRegion(
            reducer=ee.Reducer.first(), geometry=self._create_geometry_from_polygon(), scale=30
        ).get('stdDev')

        # Check if both mean_ndvi_value and land_cover_diversity_scalar are valid numbers
        if mean_ndvi_value.getInfo() is not None and land_cover_diversity_scalar is not None:
            mean_ndvi_value = ee.Number(mean_ndvi_value)
            land_cover_diversity_scalar = ee.Number(land_cover_diversity_scalar)

            multiplied_result = mean_ndvi_value.multiply(land_cover_diversity_scalar)

            return multiplied_result

        return None  # Return a default value if either value is not valid


    def get_deep_analysis(self,image_collection, range_):
        

        ndvi_aggregated = []
        life_measurement_aggregated = []
        # print('start', range_)

        # Iterate over the images in the collection
        for i in range(range_[1],range_[0]):
            image = ee.Image(image_collection.toList(image_collection.size()).get(i))
            # Calculate NDVI
            ndvi = self._calculate_ndvi(image).reduceRegion(
                reducer=ee.Reducer.mean(), geometry=self._create_geometry_from_polygon(), scale=30
            )

            # Check for null values before appending
            if ndvi.get('NDVI') is not None:
                ndvi_aggregated.append(ee.Number(ndvi.get('NDVI')))
                # Calculate life measurement
                life_measurement = self._calculate_life_measurement(image)
                life_measurement_aggregated.append(life_measurement)
            else:
                 ndvi_aggregated.append(ee.Number(0.0))
                 life_measurement_aggregated.append(0.0)
      

        # Check if the aggregated lists are not empty
        if ndvi_aggregated and life_measurement_aggregated:
            # Aggregate the results
            ndvi_array = ee.Array([ndvi_aggregated])
            ndvi_mean = ndvi_array.reduce(ee.Reducer.mean(), [0])

            life_measurement_array = ee.Array([life_measurement_aggregated])
            life_measurement_mean = life_measurement_array.reduce(ee.Reducer.mean(), [0])

            # Store the 
            ndvi_value = ndvi_mean.getInfo()[0]
            self.deep_learning['NDVI'] =sum(ndvi_value)/len(ndvi_value)
            lent =  life_measurement_mean.getInfo()
            percentageValues= (sum(lent[0])) 
            self.deep_learning['Life_Measurement'] =percentageValues
        print('Done')

        return self.deep_learning


class ConcurrencyAnalyzer:
    def __init__(self,start,end,cordinate):
        init_ee()
        self.start_date = start
        self.end_date = end
        self.size = 0
        self.coordinate = cordinate
        self.getImageCollection()
        self.result = {}
        self.threads = []
        self.earthData = []
        self.current_eq_break_point = 0
        self.analyzer = DeepAnalyzer(self.coordinate)
        
        
    def _create_geometry_from_polygon(self):
        return ee.Geometry.Polygon(self.coordinate)
    
    
    def calculate_ndti(self,image):
        # Select the relevant bands
        green_band = image.select('B3')  # Replace 'B3' with the actual band name for the green band
        swir_band = image.select('B6')   # Replace 'B6' with the actual band name for the Shortwave Infrared band
        ndti = green_band.subtract(swir_band).divide(green_band.add(swir_band)).rename('NDTI')
        return ndti

    
    def getImageCollection(self):
        self.landset_collection = (
            ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
            .filterBounds(self._create_geometry_from_polygon())
            .filterDate(ee.Date(self.start_date), ee.Date(self.end_date))
            .sort('CLOUDY_PIXEL_PERCENTAGE')
        )
        self.COPERNICUS_Collection =(
            ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
            .filterBounds(self._create_geometry_from_polygon())
            .filterDate(ee.Date(self.start_date), ee.Date(self.end_date))
            .sort('CLOUDY_PIXEL_PERCENTAGE')
        ) 
    #     (
    #     ee.ImageCollection('COPERNICUS/S2')
    #     .filterBounds(self._create_geometry_from_polygon())
    #     .filterDate(ee.Date(self.start_date), ee.Date(self.end_date))
    #     .sort('CLOUDY_PIXEL_PERCENTAGE')
    # )
        self.size = self.landset_collection.size().getInfo()
        print(self.COPERNICUS_Collection.size().getInfo())
        
        
    def CreateThredingPoint(self, minimixer = 3 , size = 0):
        size = size if size else self.size
        if size == 0:
            raise ValueError('Zero found as value are you sure you initialized the class or you called getImageCoetion')
        threading_point = []
        maximixer = size
        while maximixer !=0:
            if minimixer <  maximixer:
                maximixer -=minimixer;
                threading_point.append(( threading_point[-1][1] if len(threading_point) > 0 else size ,maximixer))
                continue
            threading_point.append(( threading_point[-1][1] if len(threading_point) > 0 else size ,maximixer))
            maximixer = 0 
        return threading_point
    
    
    
    def __setitem__(self, key, value):
        if not key in list(self.result):
            self.result[key] = value
        else:
            if type(self.result[key]) == type(float(value)) or type(self.result[key]) == type(float(value)):
                if isinstance(value, (str,int,float)):
                    self.result[key] = (float(self.result[key]) + float(value))/2
                elif isinstance(value,list):
                    self.result[key] = self.result[key].concat(value)
                else:
                    raise TypeError('Type not expcted', key, type(value))
            else:
                raise TypeError('Type did not match',key, value)
            
            
    
    def dissolveThread(self):
        pool = self.currentThreadPoint
        try:          
            result = self.analyzer.get_deep_analysis(self.landset_collection, pool);
        except Exception:
            pass
        else:
            for key,value in result.items():
                self[key] = value
                                
                
                
    def EarthQuakeAlert(self):
        print('Reach hrer')
        for i in self.CreateThredingPoint(minimixer=20 , size=self.COPERNICUS_Collection.size().getInfo())[0]:
            self.current_eq_break_point = i
            try:
                self.threads.append(threading.Thread(target=self.simplify))
            except Exception as e :
                print(e)
            self.threads[-1].start()
            print('start')
            
            
    def simplify(self):
        
        print(self.current_eq_break_point[0],self.current_eq_break_point[1])
        for index in range(self.current_eq_break_point[1],self.current_eq_break_point[0]):
            result = self.analyzer.classify_ground_displacement(  ee.Image(self.COPERNICUS_Collection.toList(self.COPERNICUS_Collection.size()).get(index)))
            print(result)
            for k,v in result.items():
                self[k] = v
                
                
    def execute(self, minimixer = 20):
        return {"NDVI": 0.85, "NDWI": 0.75, "SDVI": 0.65, "NDBI": 0.55, "SAVI": 0.45, "MSAVI2": 0.35, "EVI": 0.25, "MNDWI": 0.15, "DeforestMeasure": 0.05, "LMI": 0.95}
        print('executing')
        self.EarthQuakeAlert()
        threadingPoint = self.CreateThredingPoint(minimixer=minimixer)
        for num in threadingPoint[0]:
            self.currentThreadPoint = num
            thread = threading.Thread(target=self.dissolveThread)
            self.threads.append(thread)
            thread.start()
        while not ([thred.is_alive() for thred in self.threads]).count(False) == len(self.threads) :
            continue
        return self.result
# Example usage: 

# polygon_coordinates = [[-122.5, 37.5], [-122.5, 37.6], [-122.4, 37.6], [-122.4, 37.5], [-122.5, 37.5]]
# deep_analyzer = ConcurrencyAnalyzer('2012-04-01','2017-04-02',polygon_coordinates)
# deep_analysis_result = deep_analyzer.execute()
# print("Deep Analysis Report:", deep_analysis_result)

        