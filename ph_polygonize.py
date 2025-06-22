import rasterio
import json
from rasterio.features import shapes

def polygonize(threshold, date_time, save_historical):
    try:
        mask = None
        with rasterio.Env():
        
            kriged_file = "./shapefiles/Philippines_Pollution_"+date_time+".tif" if save_historical else "./shapefiles/Philippines_Pollution.tif"
            with rasterio.open(kriged_file) as src:
            # with rasterio.open("./shapefiles/Philippines_Pollution_idw.tif") as src:
                image = src.read(1) # first band
                image = image.astype('int16')
                geoms = [{'type':'Feature','properties': {'id': f'aqi_{int(v)}', 'AQI': int(v)}, 'geometry': s} for s,v in shapes(image, mask=mask, transform=src.transform) if v <= 1000]
        
        output_dict = {"type": "FeatureCollection", "name": "polygonized", "threshold": threshold, "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84", "date_time": date_time}}, "features": geoms}
        json_output = json.dumps(output_dict)

        polygon_file = "./temp/polygonized_"+date_time+".json" if save_historical else "./temp/polygonized.json"
        with open(polygon_file, "w") as outfile:
            outfile.write(json_output)
        with open("../express-leaflet/public/polygonized.json", "w") as outfile:  # point this to your leaflet+valhalla github folder
            outfile.write(json_output)
    except Exception as err:
        print (err)