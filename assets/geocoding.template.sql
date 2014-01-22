update %prefix%_polygon t set "addr:city" = (select "name" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name is not null and ST_Intersects(t.way, p.way) order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:city" is null;

update %prefix%_point t set "addr:city" = (select "name" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name is not null and ST_Intersects(t.way, p.way) order by p.way_area asc limit 1) where "addr:housenumber" is not null and "addr:city" is null;

update %prefix%_line t set "addr:city" = (select "name" from %prefix%_polygon p where place in ('city', 'town', 'village', 'hamlet') and name is not null and ST_Intersects(t.way, p.way) order by p.way_area asc limit 1) where "addr:city" is null and tags?'highway';

update %prefix%_polygon t set "addr:street" = (select "name" from %prefix%_line p where (p.tags?'highway') and name is not null and ST_DWithin(t.way, p.way, 400) order by ST_Distance(t.way, p.way) asc limit 1) where "addr:housenumber" is not null and "addr:street" is null;

update %prefix%_point t set "addr:street" = (select "name" from %prefix%_line p where (p.tags?'highway') and name is not null and ST_DWithin(t.way, p.way, 400) order by ST_Distance(t.way, p.way) asc limit 1) where "addr:housenumber" is not null and "addr:street" is null;
