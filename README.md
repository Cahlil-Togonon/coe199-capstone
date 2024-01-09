# CoE199 Capstone Project Repository

This repository is for SSL7's capstone project titled "Air Quality Index-Adjusted Routing for Pedestrians in Metro Manila"

## Notes:
  * Run ``python ph_main.py``

## TO-DO LIST:
  1. ~~Update postgreSQL database with street level AQI data.~~
      * issue: ``sjoin()`` is one-to-many; line features will be divided to multiple entries if it crosses multiple polygons
  2. automate ``ph_postgre.py`` and integrate to ``ph_main.py``
  3. Plug street level AQI data to OSRM/Valhalla routing engines.
  4. Get street level AQI data from postgreSQL database using Javascript (see express-leaflet repository)
  4. Plot street level AQI data on interactive Leaflet map (see express-leaflet repository)
