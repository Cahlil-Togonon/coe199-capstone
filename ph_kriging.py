import pandas as pd
import numpy as np
import geopandas as gpd
from pykrige.ok import OrdinaryKriging
import psycopg2
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Point
import os

def kriging_interpolation(date_time, save_historical):
    aqi_file = "./temp/aqi_"+date_time+".csv" if save_historical else "./temp/aqi.csv"
    df = pd.read_csv(aqi_file)
    # gdf = gpd.read_file('./shapefiles/Philippines_Border.shp')

    # bounds = gdf.total_bounds
    # Xmin = bounds[0]
    # Ymin = bounds[1]
    # Xmax = bounds[2]
    # Ymax = bounds[3]

    # # filter sensors to RENETZeros
    # df = df[df['Sensor Name'].str.match(r'^RENET.*')]
    
    # filter sensors to Metro Manila Baguio
    df = df[ (df['Y'] <= 14.8) & (14.4 <= df['Y']) ]
    df = df[ (df['X'] <= 121.15) & (120.90 <= df['X']) ]
    print(df)

    path = '../routing-backend/maps/aqi.csv'
    df.to_csv(path, index=False)
    print("DataFrame has been saved to " + path)

    data = df[["X","Y","US AQI"]].to_numpy()
    # print data

    offset = 0.002
    Xmin = min(df['X']) - offset
    Xmax = max(df['X']) + offset
    Ymin = min(df['Y']) - offset
    Ymax = max(df['Y']) + offset

    X_size = Xmax - Xmin
    Y_size = Ymax - Ymin
    # print(X_size, Y_size)
    
    pixel_size = max(X_size,Y_size)/500
    gridx = np.arange(Xmin, Xmax, pixel_size)
    gridy = np.arange(Ymin, Ymax, pixel_size)

    OK = OrdinaryKriging(
        data[:, 0],
        data[:, 1],
        data[:, 2],
        variogram_model="spherical",
        nlags = 6,
        verbose=False,
        enable_plotting=False,
        exact_values=True,
        coordinates_type="geographic",
    )

    z_pred, ss = OK.execute("grid", gridx, gridy)

    z_pred = np.flipud(z_pred)

    output_raster_path = "./shapefiles/Philippines_Pollution_"+date_time+".tif" if save_historical else "./shapefiles/Philippines_Pollution.tif"
    # pixel_size = 0.0001

    transform = from_origin(gridx.min(), gridy.max(), pixel_size, pixel_size)

    with rasterio.open(output_raster_path, 'w', driver='GTiff', 
                    height=z_pred.shape[0], width=z_pred.shape[1],
                    count=1, dtype=z_pred.dtype,
                    crs='EPSG:4326', transform=transform) as dst:
        dst.write(z_pred, 1)

    print(f"Raster file saved as: {output_raster_path}")

    # ---- Configuration ----
    CSV_NODE_PATH = "../shared-data/unique_nodes.csv"

    # ---- Interpolate AQI for Unique Nodes ----
    df_nodes = pd.read_csv(CSV_NODE_PATH)
    # Convert lat/lon from DataFrame to NumPy arrays
    lat_arr = df_nodes['lat'].to_numpy()
    lon_arr = df_nodes['lon'].to_numpy()

    # Check bounds mask
    in_bounds_mask = (
        (lon_arr >= Xmin) & (lon_arr <= Xmax) &
        (lat_arr >= Ymin) & (lat_arr <= Ymax)
    )

    # Run OK only for in-bound nodes
    predicted_aqi = np.full(lat_arr.shape, 500.0)  # default AQI 500
    in_bounds_indices = np.where(in_bounds_mask)[0]

    if len(in_bounds_indices) > 0:
        lat_in = lat_arr[in_bounds_indices]
        lon_in = lon_arr[in_bounds_indices]
        z, _ = OK.execute("points", lon_in, lat_in)
        z = np.maximum(z, 0)  # ensure positive predictions
        predicted_aqi[in_bounds_indices] = z

    # Combine results (adding geometry for PostGIS)
    predicted_nodes = [
        (lat, lon, aqi, Point(lon, lat).wkt)  # Create geometry column with WKT format
        for lat, lon, aqi in zip(lat_arr, lon_arr, predicted_aqi)
    ]

    # ---- Insert to PostgreSQL ----
    DB_CONFIG = os.getenv('DATABASE_URL')

    if DB_CONFIG is None:
        DB_CONFIG = {
            "host": "localhost",
            "port": "5432",
            "dbname": "manila_osm",
            "user": "postgres",
            "password": "admin"
        }
        conn = psycopg2.connect(**DB_CONFIG)
    else:
        conn = psycopg2.connect(DB_CONFIG)

    print("Connected to Database:", DB_CONFIG)

    cur = conn.cursor()

    # Create the table with geom (PostGIS Point)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id SERIAL PRIMARY KEY,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            predicted_aqi DOUBLE PRECISION,
            geom GEOMETRY(Point, 4326),  -- Add the geometry column for PostGIS
            UNIQUE (lat, lon)
        )
    """)

    # Insert with ON CONFLICT clause to update predicted_aqi
    cur.executemany("""
        INSERT INTO nodes (lat, lon, predicted_aqi, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326))
        ON CONFLICT (lat, lon)
        DO UPDATE SET predicted_aqi = EXCLUDED.predicted_aqi
    """, predicted_nodes)

    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted {len(predicted_nodes)} interpolated nodes into `nodes` table.")