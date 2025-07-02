import requests
from random import randint

class Sensor:
    def __init__(self) -> None:
        self.aqi = None
        self.latitude = None
        self.longitude = None
        self.location_id = None
    
    def populate_metadata(self,input_data) -> None:
        try:
            self.device_id = input_data["device_id"]
            self.device_name = input_data["device_name"]
            self.device_type = input_data["device_type"]
            self.location_id = input_data["location_id"]
            self.organization = input_data["organization"]
            self.user_id = input_data["user_id"]
            self.database_name = input_data["mapping"][0]["database_name"]
            self.topic = input_data["mapping"][0]["topic"]
            self.source = input_data["mapping"][0]["source"]
        except Exception as err:
            print(err)

    def validate_data(self) -> bool:
        try:
            assert self.location_id is not None
            assert self.latitude is not None
            assert self.longitude is not None
            if not isinstance(self.aqi, float):
                raise TypeError
            return True
        except (AssertionError,TypeError):
            return False


    def get_location(self) -> None:
        try:
            assert self.location_id is not None
            SENSOR_LOCATION_URL = f"https://sync.upcare.ph/api/location"
            response = requests.request("GET", SENSOR_LOCATION_URL, timeout=5)
            input_data = response.json()

            for location in input_data:
                if location["location_id"] == self.location_id:
                    self.latitude = location["latitude"]
                    self.longitude = location["longitude"]
                    break
                
        except Exception as err:
            print(f"Error with getting location for {self.device_name}:", err)

        return


    def get_latest_sensor_data(self) -> None:
        try:
            assert self.database_name is not None
            CARE_SENSORINSIGHTS_URL = f"https://sync.upcare.ph/api/sensorinsights/{self.database_name}/aqi/latest"
            response = requests.request("GET", CARE_SENSORINSIGHTS_URL, timeout=5)
            raw_data = response.json()

            if not isinstance(raw_data, list):
                raise NotImplementedError(raw_data["message"])

            for sensor_data in raw_data:
                if self.location_id == sensor_data["location_id"]:
                    latest_aqi = float(sensor_data["aqi"])
                    self.aqi = latest_aqi
                    return
            # If not found
            raise NotImplementedError("No data from API")
        
        except TypeError:
            print(f"Sensor data not found for {self.location_id}:", "AQI is null")
        
        except Exception as err:
            print(f"Sensor data not found for {self.location_id}:", err)
        
        # randomize if no data
        # self.aqi = self.aqi = randint(0,100)
        return

    def __str__(self):
        return f"Latitude: {self.latitude}, Longitude: {self.longitude}, AQI: {self.aqi}"


def initialize_care_sensors() -> list:
    CARE_DEVICES_URL = f"https://sync.upcare.ph/api/device"
    sensors_raw = []

    try:
        response = requests.request("GET", CARE_DEVICES_URL, timeout=30)
        sensors_raw = response.json()
    except Exception as err:
        print(err)

    sensors = []
    for sensor_data in sensors_raw:
        sensor = Sensor()
        sensor.populate_metadata(sensor_data)
        sensor.get_location()
        sensor.get_latest_sensor_data()
        if sensor.validate_data():
            print([sensor.location_id,sensor.aqi,sensor.latitude,sensor.longitude])
            sensors.append(sensor)

    return sensors