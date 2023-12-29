import psycopg2
import geopandas as gpd
import json
from shapely.geometry import shape

conn = psycopg2.connect(database = "manila_osm",
                        host = "localhost",
                        user = "postgres",
                        password = "admin",
                        port = "5432")

cursor = conn.cursor()

cursor.execute('SELECT osm_id, ST_AsGeoJson(wkb_geometry) FROM test2')

streets = []
for osm_id, feature in cursor:
    street = {}
    geometry = json.loads(feature)
    street["osm_id"] = osm_id
    street["geometry"] = shape(geometry)
    streets.append(street)
streets = gpd.GeoDataFrame(streets, crs="EPSG:4326")
print(streets.head())

aqi_polygons = gpd.read_file("./temp/polygonized_29-12-2023_19-35-57.json")
print(aqi_polygons.head())

streets_aqi = streets.sjoin(aqi_polygons, how="inner", predicate="intersects")
streets_aqi.plot(column="AQI", cmap="RdYlGn_r", legend=True)