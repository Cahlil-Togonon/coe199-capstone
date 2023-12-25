import rasterio
import json
from rasterio.features import shapes

def polygonize(threshold, date_time):
    mask = None
    with rasterio.Env():
        with rasterio.open("./shapefiles/Philippines_Pollution_"+date_time+"_idw.tif") as src:
        # with rasterio.open("./shapefiles/Philippines_Pollution_idw.tif") as src:
            image = src.read(1) # first band
            image = image.astype('int16')
            geoms = [{'type':'Feature','properties': {'AQI': v}, 'geometry': s} for s,v in shapes(image, mask=mask, transform=src.transform) if v <= 1000]
    output_dict = {"type": "FeatureCollection", "name": "polygonized", "threshold": threshold, "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features": geoms}
    json_output = json.dumps(output_dict)
    with open("./temp/polygonized_"+date_time+".json", "w") as outfile:
        outfile.write(json_output)
    with open("../express+leaflet/public/polygonized.json", "w") as outfile:  # point this to your leaflet+valhalla github folder
        outfile.write(json_output)