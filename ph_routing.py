from routingpy import Valhalla
from routingpy.utils import decode_polyline6
import json

client = Valhalla(base_url='https://valhalla1.openstreetmap.de')

coords = [[120.9927158,14.6096897],[121.0175177,14.6316460]]

# with open("route_request_test2.json","r") as f:
#     data = json.load(f)
#     exclude_poly = data["features"][0]["geometry"]["coordinates"]

route = client.directions(locations=coords,instructions=True,profile="pedestrian",points_encoded=False)

json_output = json.dumps(route.raw, indent=4)
with open("route_results.json","w") as f:
    f.write(json_output)

route_polyline = route.raw['trip']['legs'][0]['shape']
print(route_polyline)
decoded_polyline = decode_polyline6(route_polyline)
print(type(decoded_polyline[0][0]))