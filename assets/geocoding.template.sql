create index on %prefix%_polygon (admin_level);
create index on %prefix%_polygon (name);

-- setting a2-6 for cities
update %prefix%_polygon t set "addr:country" = (select tags->'int_ref' from %prefix%_polygon p where admin_level='2' and tags?'int_ref' and ST_Intersects(t.way, p.way) limit 1) where "place" is not null and "addr:country" is null;

update %prefix%_polygon t set "addr:region" = (select "name" from %prefix%_polygon p where admin_level='4' and "name" is not null and ST_Intersects(t.way, p.way) limit 1) where "place" is not null and "addr:region" is null;

update %prefix%_polygon t set "addr:district" = (select "name" from %prefix%_polygon p where admin_level='6' and "name" is not null and ST_Intersects(t.way, p.way) limit 1) where "place" is not null and "addr:district" is null;

-- setting a2-8 for building polygons
update %prefix%_polygon t set "addr:city" = (select "name" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name is not null and ST_Intersects(t.way, p.way) order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:city" is null;

update %prefix%_polygon t set "addr:district" = (select "addr:district" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name=t."addr:city" and "addr:district" is not null and t.way && p.way order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:district" is null and "addr:city" is not null;

update %prefix%_polygon t set "addr:region" = (select "addr:region" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name=t."addr:city" and "addr:region" is not null and t.way && p.way order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:region" is null and "addr:city" is not null;

update %prefix%_polygon t set "addr:country" = (select "addr:country" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name=t."addr:city" and "addr:country" is not null and t.way && p.way order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:country" is null and "addr:city" is not null;

-- setting a2-8 for building points
update %prefix%_point t set "addr:city" = (select "name" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name is not null and ST_Intersects(t.way, p.way) order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:city" is null;

update %prefix%_point t set "addr:district" = (select "addr:district" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name=t."addr:city" and "addr:district" is not null and t.way && p.way order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:district" is null and "addr:city" is not null;

update %prefix%_point t set "addr:region" = (select "addr:region" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name=t."addr:city" and "addr:region" is not null and t.way && p.way order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:region" is null and "addr:city" is not null;

update %prefix%_point t set "addr:country" = (select "addr:country" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name=t."addr:city" and "addr:country" is not null and t.way && p.way order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:country" is null and "addr:city" is not null;


-- processing streets
update %prefix%_line t set "addr:city" = (select "name" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name is not null and ST_Intersects(t.way, p.way) order by p.way_area asc limit 1) where "addr:city" is null and tags?'highway';

update %prefix%_polygon t set "addr:street" = (select "name" from %prefix%_line p where (p.tags?'highway') and name is not null and ST_DWithin(t.way, p.way, 400) order by ST_Distance(t.way, p.way) asc limit 1) where "addr:housenumber" is not null and "addr:street" is null;

update %prefix%_point t set "addr:street" = (select "name" from %prefix%_line p where (p.tags?'highway') and name is not null and ST_DWithin(t.way, p.way, 400) order by ST_Distance(t.way, p.way) asc limit 1) where "addr:housenumber" is not null and "addr:street" is null;
