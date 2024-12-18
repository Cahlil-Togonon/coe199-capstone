import psycopg2
import geopandas as gpd
import json
from shapely.geometry import shape

def upload_to_db(date_time, psql_date_time):
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

    aqi_polygons = gpd.read_file("./temp/polygonized_"+date_time+".json")
    print(aqi_polygons.head())

    streets_aqi = streets.sjoin(aqi_polygons, how="inner", predicate="intersects")

    cursor.execute(f"INSERT INTO data_timestamps (data_timestamp) VALUES ('{psql_date_time}') ON CONFLICT DO NOTHING")
    for street in streets_aqi.itertuples():
        cursor.execute(f"INSERT INTO street_aqi (osm_id, wkb_geometry, aqi, data_timestamp) VALUES ({street.osm_id}, ST_AsBinary('{street.geometry}'::geometry), {street.AQI}, '{psql_date_time}')")
    conn.commit()

    print("Successfully updated database")

    conn.close()