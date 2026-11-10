# Voting precinct boundaries

Pulled 2026-11-10 (November 10, 2026) from Denton County GIS.

Official source: MapServer layer 9, “Voter Precincts (Effective 1/1/2026)”. The service describes that layer as “The current Denton County Voter Precincts.” Copyright: Denton County.

Service: https://gis.dentoncounty.gov/arcgis/rest/services/PoliticalBoundaries_GC/MapServer/9

GeoJSON query used for this file (WGS 84):

https://gis.dentoncounty.gov/arcgis/rest/services/PoliticalBoundaries_GC/MapServer/9/query?where=Comm%3D%274%27&outFields=FullNum%2CComm%2CPct&returnGeometry=true&outSR=4326&f=geojson

`Comm='4'` returned 67 polygons. Their `FullNum` values are exactly the 67 precincts listed on this site. None of the 67 precincts were missing from this layer.

Feature `last_edited_date` values on that query were 2025-08-28 for 65 precincts, 2025-10-29 for precinct 4204, and 2026-08-05 for precinct 4205.

`data/pct4-precincts.geojson` keeps those official polygons. Coordinates are rounded to 5 decimal places (about 1 meter) and consecutive duplicate points were removed. The boundaries were not traced or redrawn.

Commissioner Precinct 4 on the same service, layer 4 (`COMMISH='4'`), has an extent within about 2 meters of the union of these 67 voting precincts:

https://gis.dentoncounty.gov/arcgis/rest/services/PoliticalBoundaries_GC/MapServer/4

That commissioner polygon is not stored in this repository. The map fits the 67 voting precincts, which are the county’s Commissioner Precinct 4 voting precincts.
