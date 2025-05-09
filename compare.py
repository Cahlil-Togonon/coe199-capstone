import csv

# Helper to read lat-lon from a CSV and convert to a set of rounded tuples
def load_nodes_from_csv(file_path):
    nodes = set()
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                lat = round(float(row['lat']), 5)
                lon = round(float(row['lon']), 5)
                nodes.add((lat, lon))
            except (ValueError, KeyError):
                continue
    return nodes

# Load nodes from both CSVs
postgis_nodes = load_nodes_from_csv("unique_nodes.csv")
graphhopper_nodes = load_nodes_from_csv("../routing-backend/unique_nodes.csv")

# Compute intersection and differences
matched_nodes = postgis_nodes & graphhopper_nodes
only_in_postgis = postgis_nodes - graphhopper_nodes
only_in_graphhopper = graphhopper_nodes - postgis_nodes

# Report results
print(f"Total PostGIS nodes: {len(postgis_nodes)}")
print(f"Total GraphHopper nodes: {len(graphhopper_nodes)}")
print(f"Matching nodes: {len(matched_nodes)}")
print(f"Only in PostGIS: {len(only_in_postgis)}")
print(f"Only in GraphHopper: {len(only_in_graphhopper)}")

# # Optional: Save mismatches to CSVs
# with open("only_in_postgis.csv", "w", newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(["lat", "lon"])
#     for lat, lon in sorted(only_in_postgis):
#         writer.writerow([lat, lon])

# with open("only_in_graphhopper.csv", "w", newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(["lat", "lon"])
#     for lat, lon in sorted(only_in_graphhopper):
#         writer.writerow([lat, lon])
