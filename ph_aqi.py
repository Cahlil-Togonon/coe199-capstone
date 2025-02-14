import requests
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point

from ph_care import initialize_care_sensors

# from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import time

def init_sensors():
    token = "6f298a6f68c27deb7dcd10aacef33abbd6819fdc"
    WAQI_sensors = {
        "WackWack_Mandaluyong" : "https://api.waqi.info/feed/A132778/?token=6f298a6f68c27deb7dcd10aacef33abbd6819fdc",
        "Baltazar_Caloocan" : "https://api.waqi.info/feed/A64045/?token=6f298a6f68c27deb7dcd10aacef33abbd6819fdc",
        "Forbestown_Taguig" : "https://api.waqi.info/feed/A248974/?token=6f298a6f68c27deb7dcd10aacef33abbd6819fdc",
        "SerendraBamboo_Taguig" : "https://api.waqi.info/feed/A50926/?token=6f298a6f68c27deb7dcd10aacef33abbd6819fdc",
        "Calzada_Taguig" : "https://api.waqi.info/feed/A204484/?token=6f298a6f68c27deb7dcd10aacef33abbd6819fdc",
        "Multinational_Paranaque" : "https://api.waqi.info/feed/A127897/?token=6f298a6f68c27deb7dcd10aacef33abbd6819fdc"
    }

    IQAir_sensors = {
        # "Multinational_Paranaque" : "https://www.iqair.com/philippines/ncr/paranaque/multinational-village", #waqi
        # "Calzada_Taguig" : "https://www.iqair.com/philippines/ncr/taguig/calzada", #waqi
        # "Forbestown_Taguig" : "https://www.iqair.com/philippines/ncr/taguig/forbestown-road", #waqi
        "NorthForbesPark_Makati" : "https://www.iqair.com/philippines/ncr/makati/north-forbes-park",
        "Dasmarinas_Makati" : "https://www.iqair.com/philippines/ncr/makati/dasmarinas-village",
        "AyalaCircuit_Makati" : "https://www.iqair.com/philippines/ncr/makati/circuit-ayala-outside",
        # "WackWack_Mandaluyong" : "https://www.iqair.com/philippines/ncr/mandaluyong/wack-wack-greenhills", #waqi
        "Unioil_Shaw" : "https://www.iqair.com/philippines/ncr/mandaluyong/unioil-shaw",
        "Unioil_Blumentritt" : "https://www.iqair.com/philippines/ncr/san-juan/unioil-f-blumentritt",
        "Unioil_Cainta" : "https://www.iqair.com/philippines/calabarzon/rizal/unioil-cainta-ortigas-ext",
        "Unioil_Congressional" : "https://www.iqair.com/philippines/ncr/quezon-city/unioil-congressional-2",
        "Unioil_WestAve" : "https://www.iqair.com/philippines/ncr/quezon-city/unioil-west-ave",
        "Unioil_EdsaGuadalupe" : "https://www.iqair.com/philippines/ncr/makati/unioil-edsa-guadalupe-2"
        # "Unioil_Meycauayan" : "https://www.iqair.com/philippines/central-luzon/meycauayan/unioil-meycauayan-bulacan"    # 0 always?
        # MISSING: Unioil Katipunan - Quezon Ave - Barangka - Conception, National Children's Hospital, Madison st. Greenhills
    }

    IQAir_locations = {
        # "Multinational_Paranaque" : [121.001488,14.486208], #waqi
        # "Calzada_Taguig" : [121.07563,14.536089], #waqi
        # "Forbestown_Taguig" : [121.043945,14.550762], #waqi
        "NorthForbesPark_Makati" : [121.035596,14.553975],
        "Dasmarinas_Makati" : [121.030732,14.56628],
        "AyalaCircuit_Makati" : [121.019740,14.573594],
        # "WackWack_Mandaluyong" : [121.05573,14.591224], #waqi
        "Unioil_Shaw" : [121.037489,14.589523],
        "Unioil_Blumentritt" : [121.026652,14.6021],
        "Unioil_Cainta" : [121.125296,14.582285],
        "Unioil_Congressional" : [121.064763,14.672367],
        "Unioil_WestAve" : [121.027586,14.644702],
        "Unioil_EdsaGuadalupe" : [121.025319,14.476359]
        # MISSING: Unioil Katipunan - Quezon Ave - Barangka - Conception, National Children's Hospital, Madison st. Greenhills
    }
    return WAQI_sensors, IQAir_locations, IQAir_sensors


class Sensor_Data:
    def __init__(self):
        self.sensor_name = []
        self.X_location = []
        self.Y_location = []
        self.US_AQI = []
        self.source = []
    
    def add_sensor(self, sensor_name, X_location, Y_location, US_AQI, source):
        self.sensor_name.append(sensor_name)
        self.X_location.append(X_location)
        self.Y_location.append(Y_location)
        self.US_AQI.append(US_AQI)
        self.source.append(source)
    
    def return_dict(self):
        return {'Sensor Name':self.sensor_name,'X':self.X_location,'Y':self.Y_location,'US AQI':self.US_AQI,'source':self.source}


def waqi_API(sensor_data, WAQI_sensors):
    for sensor in WAQI_sensors:
        try:
            response = requests.request("GET", WAQI_sensors[sensor], timeout=5)
        except Exception as err:
            print("Error with "+ sensor + f" sensor: {err=}, {type(err)=}")
            continue

        try:
            sensor_aqi = float(response.json()["data"]["aqi"])
            sensor_x = float(response.json()["data"]["city"]["geo"][1])
            sensor_y = float(response.json()["data"]["city"]["geo"][0])
        except Exception as err:
            print("Error with "+ sensor + f" sensor: {err=}, {type(err)=}")
            continue

        # print(sensor+": "+str(sensor_aqi))
        sensor_data.add_sensor(sensor, sensor_x, sensor_y, sensor_aqi, "WAQI")


def IQair_API(sensor_data, IQAir_locations, IQAir_sensors):
    for sensor in IQAir_sensors:
        # page = urlopen(IQAir_sensors[sensor])
        # html = page.read().decode("utf-8")
        try:
            headers = requests.utils.default_headers()
            headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            })
            page = requests.get(IQAir_sensors[sensor], timeout=5, headers=headers)
        except Exception as err:
            print("Error with "+ sensor + f" sensor: {err=}, {type(err)=}")
            continue
        soup = BeautifulSoup(page.content, "html.parser")
        try:
            sensor_aqi = float(soup.find('p', attrs={'class':'aqi-value__value'}).string)
        except Exception as err:
            print("Error with "+ sensor + f" sensor: {err=}, {type(err)=}")
            continue

        # print(sensor+": "+str(sensor_aqi))
        sensor_data.add_sensor(sensor, IQAir_locations[sensor][0], IQAir_locations[sensor][1], sensor_aqi, "IQAir")


def get_sensor_data(WAQI_sensors, IQAir_locations, IQAir_sensors):
    sensor_data = Sensor_Data()
    
    # waqi_API(sensor_data, WAQI_sensors)
    # IQair_API(sensor_data, IQAir_locations, IQAir_sensors)

    care_sensors = initialize_care_sensors()
    for care_sensor in care_sensors:
        # if care_sensor.organization == None or care_sensor.aqi == None:
        #     continue
        sensor_data.add_sensor(care_sensor.location_id, care_sensor.longitude, care_sensor.latitude, care_sensor.aqi, "UPCARE")

    df = pd.DataFrame(sensor_data.return_dict())
    return df


def df_to_csv(df, date_time):
    # to csv file
    df.to_csv("./temp/test_aqis_"+date_time+".csv", index=False, encoding='utf-8')


def df_to_shp(df, date_time):
    # save to shapefile
    geometry = [Point(xy) for xy in zip(df.X, df.Y)]
    df = df.drop(['X', 'Y'], axis=1)
    gdf = GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
    gdf.to_file("./shapefiles/Philippines_Pollution_"+date_time+".shp")