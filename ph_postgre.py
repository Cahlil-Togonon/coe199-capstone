import psycopg2
import geopandas as gpd
import json
from shapely.geometry import shape
import os
from shapely.wkb import dumps as wkb_dumps
from psycopg2.extras import execute_values

def upload_to_db(date_time, psql_date_time, save_historical):

    database_url = os.getenv('DATABASE_URL')

    if database_url is None:
        conn = psycopg2.connect(database = "manila_osm",
                        host = "localhost",
                        user = "postgres",
                        password = "admin",
                        port = "5432")
    
    else:
        conn = psycopg2.connect(database_url)

    print("Connected to Database:", database_url)

    cursor = conn.cursor()

    cursor.execute('SELECT osm_id, ST_AsGeoJson(wkb_geometry) FROM osm_id_geometry')

    streets = []
    for osm_id, feature in cursor:
        street = {}
        geometry = json.loads(feature)
        street["osm_id"] = osm_id
        street["geometry"] = shape(geometry)
        streets.append(street)
    streets = gpd.GeoDataFrame(streets, crs="EPSG:4326")

    polygon_file = "./temp/polygonized_"+date_time+".json" if save_historical else "./temp/polygonized.json"
    aqi_polygons = gpd.read_file(polygon_file)

    streets_aqi = streets.sjoin(aqi_polygons, how="inner", predicate="intersects")

    cursor.execute(f"INSERT INTO data_timestamps (data_timestamp) VALUES ('{psql_date_time}') ON CONFLICT DO NOTHING")

    cursor.execute("DELETE FROM street_aqi")

    print("Truncated database, inserting new data...")

    values = [
        (street.osm_id, wkb_dumps(street.geometry), street.AQI, psql_date_time)
        for street in streets_aqi.itertuples()
    ]
    
    execute_values(cursor, """
        INSERT INTO street_aqi (osm_id, wkb_geometry, aqi, data_timestamp)
        VALUES %s
    """, values, template="(%s, ST_GeomFromWKB(%s, 4326), %s, %s)")

    if save_historical:
        execute_values(cursor, """
            INSERT INTO street_aqi_historical (osm_id, wkb_geometry, aqi, data_timestamp)
            VALUES %s
        """, values, template="(%s, ST_GeomFromWKB(%s, 4326), %s, %s)")
    # for street in streets_aqi.itertuples():

    #     cursor.execute(f"INSERT INTO street_aqi (osm_id, wkb_geometry, aqi, data_timestamp) VALUES ({street.osm_id}, ST_AsBinary('{street.geometry}'::geometry), {street.AQI}, '{psql_date_time}')")

    #     if save_historical:
    #         cursor.execute(f"INSERT INTO street_aqi_historical (osm_id, wkb_geometry, aqi, data_timestamp) VALUES ({street.osm_id}, ST_AsBinary('{street.geometry}'::geometry), {street.AQI}, '{psql_date_time}')")
    conn.commit()

    print("Successfully updated database")

    conn.close()