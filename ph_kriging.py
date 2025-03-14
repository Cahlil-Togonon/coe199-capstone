import pandas as pd
import numpy as np
import geopandas as gpd
from pykrige.ok import OrdinaryKriging
import rasterio
from rasterio.transform import from_origin

def kriging_interpolation(date_time):
    df = pd.read_csv("./temp/aqi_"+date_time+".csv")
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

    # path = '../routing-backend/aqi.csv'
    # df.to_csv(path, index=False)
    # print("DataFrame has been saved to " + path)

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

    output_raster_path="./shapefiles/Philippines_Pollution_"+date_time+".tif"
    # pixel_size = 0.0001

    transform = from_origin(gridx.min(), gridy.max(), pixel_size, pixel_size)

    with rasterio.open(output_raster_path, 'w', driver='GTiff', 
                    height=z_pred.shape[0], width=z_pred.shape[1],
                    count=1, dtype=z_pred.dtype,
                    crs='EPSG:4326', transform=transform) as dst:
        dst.write(z_pred, 1)

    print(f"Raster file saved as: {output_raster_path}")