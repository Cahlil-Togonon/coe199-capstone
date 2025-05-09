from time import sleep
from datetime import datetime
from random import randint

from ph_aqi import init_sensors, get_sensor_data, df_to_csv, df_to_shp
from ph_idw import get_idw
from ph_kriging import kriging_interpolation
from ph_polygonize import polygonize
from ph_postgre import upload_to_db
from ph_filter import filter

while 1:
    format = "%d-%m-%Y_%H-%M-%S"        # dd-mm-yyyy_HH-MM-SS format
    date_time = datetime.now().strftime(format)

    psql_format = "%Y-%m-%d %H:%M:%S"        # dd-mm-yyyy_HH-MM-SS format
    psql_date_time = datetime.now().strftime(psql_format)

    #ph_aqi functions
    WAQI_sensors, IQAir_locations, IQAir_sensors = init_sensors()
    
    try:
        df = get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors)
    except Exception as err:
        print(err)
        continue
    
    # print(df.to_string())
    df.to_csv("./temp/aqi_"+date_time+".csv", index=False, encoding='utf-8')
    df.to_csv("../express-leaflet/public/aqi.csv", index=False, encoding='utf-8')
    df_to_shp(df, date_time)

    #ph_idw functions
    # get_idw(date_time)

    #ph_kriging functions
    try:
        kriging_interpolation(date_time)
    except Exception as err:
        print(err)
        continue


    #ph_polygonize functions
        # max_AQI = max([int(i) for i in US_AQI])
        # threshold = randint(2*max_AQI//3,max_AQI)
        # print("threshold: "+str(threshold))
    polygonize(200, date_time)

    #ph_postgre functions
    upload_to_db(date_time, psql_date_time)

    #ph_filter functions
    # filter(threshold, date_time)
    
    sleep_timer = 1*1*1
    print("Sleeping for "+str(sleep_timer)+" seconds...")
    sleep(sleep_timer)