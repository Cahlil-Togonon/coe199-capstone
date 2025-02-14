import requests
from random import randint

class Sensor:
    def __init__(self) -> None:
        pass
    
    def populate_metadata(self,input_data) -> None:
        self.device_id = input_data["device_id"]
        self.device_name = input_data["device_name"]
        self.device_type = input_data["device_type"]
        self.location_id = input_data["location_id"]
        self.organization = input_data["organization"]
        self.user_id = input_data["user_id"]
        self.database_name = input_data["mapping"][0]["database_name"]
        self.topic = input_data["mapping"][0]["topic"]
        self.source = input_data["mapping"][0]["source"]
        # print(self.organization)
    
    def get_location(self) -> None:
        SENSOR_LOCATION_URL = f"https://sync.upcare.ph/api/location"
        response = requests.request("GET", SENSOR_LOCATION_URL, timeout=5)
        input_data = response.json()
        print("location:", self.location_id)

        for location in input_data:
            if location["location_id"] == self.location_id:
                self.latitude = location["latitude"]
                self.longitude = location["longitude"]
                break
        # assert self.latitude
        # assert self.longitude

    def get_latest_sensor_data(self) -> None:
        CARE_SENSORINSIGHTS_URL = f"https://sync.upcare.ph/api/sensorinsights/{self.organization}/aqi/latest"
        self.aqi = randint(0,200)
        if self.organization == None:
            print(f"No database table for {self.database_name}")
            return

        response = requests.request("GET", CARE_SENSORINSIGHTS_URL, timeout=5)
        raw_data = response.json()

        for sensor_data in raw_data:
            try:
                if self.location_id == sensor_data["location_id"]:
                    self.aqi = float(sensor_data["aqi"])
                    return
            except Exception as err:
                print(err)
                break

        print(f"Sensor data not found for {self.location_id}")

    def __str__(self):
        return f"Latitude: {self.latitude}, Longitude: {self.longitude}, AQI: {self.aqi}"


def initialize_care_sensors() -> list:
    CARE_DEVICES_URL = f"https://sync.upcare.ph/api/device"

    response = requests.request("GET", CARE_DEVICES_URL, timeout=5)
    sensors_raw = response.json()

    sensors = []
    for sensor_data in sensors_raw:
        sensor = Sensor()
        sensor.populate_metadata(sensor_data)
        if sensor.location_id:
            sensor.get_location()
            sensor.get_latest_sensor_data()
            sensors.append(sensor)

    return sensors