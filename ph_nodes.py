import psycopg2
from shapely import wkb
from shapely.geometry import LineString, MultiLineString
import csv

# Database connection settings
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "manila_osm"
DB_USER = "postgres"
DB_PASSWORD = "admin"

# Connect to Postgres
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

# Get the latest timestamp from data_timestamps
cur.execute("SELECT MAX(data_timestamp) FROM public.data_timestamps")
latest_timestamp = cur.fetchone()[0]

print(f"Using latest timestamp: {latest_timestamp}")

# Fetch geometry rows from street_aqi that match this timestamp
cur.execute("""
    SELECT wkb_geometry
    FROM public.street_aqi
    WHERE data_timestamp = %s
    AND wkb_geometry IS NOT NULL
""", (latest_timestamp,))

# Use a set to store unique nodes
unique_nodes = set()

for (geom_wkb,) in cur.fetchall():
    geom = wkb.loads(geom_wkb, hex=False)

    if isinstance(geom, LineString):
        for coord in geom.coords:
            unique_nodes.add(coord)

    elif isinstance(geom, MultiLineString):
        for line in geom.geoms:
            for coord in line.coords:
                unique_nodes.add(coord)

# Save to CSV
with open("unique_nodes.csv", mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["lat", "lon"])  # Header
    for lon, lat in unique_nodes:  # Note: Shapely coords are (x, y) = (lon, lat)
        writer.writerow([lat, lon])

print(f"Saved {len(unique_nodes)} unique nodes to unique_nodes.csv")

# Cleanup
cur.close()
conn.close()
