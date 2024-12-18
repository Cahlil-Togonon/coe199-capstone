DROP FUNCTION IF EXISTS public.aqi_filter;

CREATE OR REPLACE FUNCTION public.aqi_filter(z integer, x integer, y integer, threshold integer DEFAULT 50)
RETURNS bytea                                                                                             
LANGUAGE plpgsql                                                                                          
STABLE PARALLEL SAFE                                                                                      
AS $function$                                                                                              
DECLARE                                                                                                    
    result bytea;
    latest_timestamp timestamp without time zone;                                                                                    
BEGIN
    SELECT MAX(data_timestamp)
    INTO latest_timestamp
    FROM street_aqi;
                                                                                            
    WITH                                                                                                   
    bounds AS (                                                                                            
        SELECT ST_TileEnvelope(z, x, y) AS geom                                                              
    ),                                                                                                     
    mvtgeom AS (                                                                                           
    SELECT ST_AsMVTGeom(ST_Transform(t.wkb_geometry, 3857), bounds.geom) AS geom,                        
        t.aqi, t.osm_id, t.data_timestamp                                                                  
    FROM street_aqi t, bounds                                                                            
    WHERE ST_Intersects(t.wkb_geometry, ST_Transform(bounds.geom, 4326))                                 
    AND t.aqi < threshold  
    AND t.data_timestamp = latest_timestamp                                                                          
    )                                                                                                      
    SELECT ST_AsMVT(mvtgeom.*, 'default')                                                                  
    INTO result                                                                                            
    FROM mvtgeom;                                                                                          
                                                                                                        
    RETURN result;                                                                                         
END;                                                                                                       
$function$                                                                                                 