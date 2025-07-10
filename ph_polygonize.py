import rasterio
import json
from rasterio.features import shapes
import os
import geopandas as gpd
from shapely.geometry import shape
import psycopg2
from sqlalchemy import create_engine

def polygonize(threshold, date_time, save_historical):
    try:
        mask = None
        polygons = []
        aqi_values = []

        with rasterio.Env():
            kriged_file = "./shapefiles/Philippines_Pollution_"+date_time+".tif" if save_historical else "./shapefiles/Philippines_Pollution.tif"
            with rasterio.open(kriged_file) as src:
            # with rasterio.open("./shapefiles/Philippines_Pollution_idw.tif") as src:
                image = src.read(1).astype('int16')
                geoms = [{'type':'Feature','properties': {'id': f'aqi_{int(v)}', 'AQI': int(v)}, 'geometry': s} for s,v in shapes(image, mask=mask, transform=src.transform) if v <= 1000]
                for geom, val in shapes(image, mask=mask, transform=src.transform):
                    if val <= 1000:
                        polygons.append(shape(geom))
                        aqi_values.append(int(val))

        output_dict = {"type": "FeatureCollection", "name": "polygonized", "threshold": threshold, "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84", "date_time": date_time}}, "features": geoms}
        json_output = json.dumps(output_dict)

        polygon_file = "./temp/polygonized_"+date_time+".json" if save_historical else "./temp/polygonized.json"
        with open(polygon_file, "w") as outfile:
            outfile.write(json_output)
        # with open("../shared-data/express-leaflet/public/polygonized.json", "w") as outfile:  # point this to your leaflet+valhalla github folder
        #     outfile.write(json_output)

        database_url = os.getenv('DATABASE_URL')
        
        if database_url is None:
            database_url = "postgresql://postgres:admin@localhost:5432/manila_osm"
        
        engine = create_engine(database_url)

        print("Connected to Database:", database_url)

        gdf = gpd.GeoDataFrame({
            "aqi": aqi_values,
            "data_timestamp": date_time
        }, geometry=polygons, crs=src.crs)

        table_name = "polygonized_aqi"

        gdf.to_postgis(name=table_name, con=engine, if_exists="replace", index=False)

        engine.dispose()

        print(f"Polygonized AQI saved to PostGIS '{table_name}' table.")

    except Exception as err:
        print (err)