import requests
import csv
import time
import random
from datetime import datetime

today = datetime.now().strftime("%m%d%Y")

CSV_FILE = f"./routing_logs/routing_log_{today}.csv"
INTERVAL_SECONDS = 30
LAT_MIN, LAT_MAX = 14.5, 14.8
LON_MIN, LON_MAX = 120.90, 121.15

VEHICLES = ["car", "foot", "bike", "motorcycle"]

def initialize_csv():
    try:
        with open(CSV_FILE, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "vehicle", "route_type",
                "from_lat", "from_lon", "to_lat", "to_lon",
                "distance", "weight", "time", "route_name"
            ])
    except FileExistsError:
        pass

def random_point():
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lon = random.uniform(LON_MIN, LON_MAX)
    return lat, lon

def log_all_routes(vehicle, from_lat, from_lon, to_lat, to_lon):
    try:
        url = "http://localhost:9098/routing"
        params = [
            ("point", f"{from_lon},{from_lat}"),
            ("point", f"{to_lon},{to_lat}"),
            ("Vehicle", vehicle),
            ("RouteType", "all"),
            ("mediaType", "json")
        ]

        response = requests.get(url, params=params)
        response.raise_for_status()
        routes = response.json()

        timestamp = datetime.utcnow().isoformat()

        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            for route in routes:
                writer.writerow([
                    timestamp,
                    vehicle,
                    route.get("name", "unknown"),
                    from_lat, from_lon,
                    to_lat, to_lon,
                    route.get("distance"),
                    route.get("weight"),
                    route.get("time"),
                    route.get("name")
                ])
                print(f"[{timestamp}] {vehicle} - {route.get('name')}: {route.get('distance')}m, {route.get('time')}s")

    except Exception as e:
        print(f"Error querying {vehicle} route: {e}")


def main():
    initialize_csv()
    while True:
        from_lat, from_lon = random_point()
        to_lat, to_lon = random_point()

        for vehicle in VEHICLES:
            log_all_routes(vehicle, from_lat, from_lon, to_lat, to_lon)
            time.sleep(1)

        print(f"Sleeping for {INTERVAL_SECONDS} seconds...\n")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
