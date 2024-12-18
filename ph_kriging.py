import pandas as pd
import numpy as np
import geopandas as gpd
from pykrige.ok import OrdinaryKriging
import rasterio
from rasterio.transform import from_origin

def kriging_interpolation(date_time):
    df = pd.read_csv("./temp/aqi_"+date_time+".csv")
    gdf = gpd.read_file('./shapefiles/Philippines_Border.shp')

    data = df[["X","Y","US AQI"]].to_numpy()
    print(data)

    bounds = gdf.total_bounds
    Xmin = bounds[0]
    Ymin = bounds[1]
    Xmax = bounds[2]
    Ymax = bounds[3]

    gridx = np.arange(Xmin, Xmax, 0.001)
    gridy = np.arange(Ymin, Ymax, 0.001)

    OK = OrdinaryKriging(
        data[:, 0],
        data[:, 1],
        data[:, 2],
        variogram_model="spherical",
        nlags = 1,
        verbose=False,
        enable_plotting=False,
        exact_values=True,
        coordinates_type="geographic",
    )

    z_pred, ss = OK.execute("grid", gridx, gridy)

    output_raster_path="./shapefiles/Philippines_Pollution_"+date_time+".tif"
    pixel_size = 0.001

    transform = from_origin(gridx.min(), gridy.max(), pixel_size, pixel_size)

    with rasterio.open(output_raster_path, 'w', driver='GTiff', 
                    height=z_pred.shape[0], width=z_pred.shape[1],
                    count=1, dtype=z_pred.dtype,
                    crs='EPSG:4326', transform=transform) as dst:
        dst.write(z_pred, 1)

    print(f"Raster file saved as: {output_raster_path}")