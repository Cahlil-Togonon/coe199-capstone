DROP TABLE street_aqi_linestring;
DROP TABLE street_aqi_linestring_vertices_pgr;
CREATE TABLE street_aqi_linestring AS (
    SELECT osm_id, (dump_set).path AS line_part, ST_AsText((dump_set).geom) AS line_string, aqi, data_timestamp
    FROM (
        SELECT osm_id, ST_Dump(wkb_geometry) AS dump_set, aqi, data_timestamp
        FROM (SELECT * FROM street_aqi)
        ) AS dump_results
);

ALTER TABLE public.street_aqi_linestring ADD COLUMN "id" SERIAL PRIMARY KEY;
ALTER TABLE public.street_aqi_linestring ADD COLUMN "source" integer;
ALTER TABLE public.street_aqi_linestring ADD COLUMN "target" integer;