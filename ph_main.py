from time import sleep
from datetime import datetime
from random import randint

from ph_aqi import init_sensors, get_sensor_data, df_to_csv, df_to_shp
from ph_idw import get_idw
from ph_polygonize import polygonize
from ph_filter import filter

while 1:
    format = "%d-%m-%Y_%H-%M-%S"        # dd-mm-yyyy_HH-MM-SS format
    date_time = datetime.now().strftime(format)

    #ph_aqi functions
    WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
    Sensor_Name, X_location, Y_location, US_AQI, df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)
    # df_to_csv(df, date_time)
    df_to_shp(df, date_time)

    #ph_idw functions
    get_idw(date_time)

    #ph_polygonize functions
    max_AQI = max([int(i) for i in US_AQI])
    threshold = randint(2*max_AQI//3,max_AQI)
    print("threshold: "+str(threshold))
    polygonize(threshold, date_time)

    #ph_filter functions
    # filter(threshold, date_time)
    
    sleep_timer = randint(1*15*60,1*60*60)  # random time sampling
    print("Sleeping for "+str(sleep_timer)+" seconds...")
    sleep(sleep_timer)