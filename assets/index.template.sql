create index on %prefix%_line (name);
create index on %prefix%_line ("name:en");
create index on %prefix%_point (name);
create index on %prefix%_point ("addr:street");
create index on %prefix%_polygon (name);
create index on %prefix%_polygon ("addr:street");
create index on %prefix%_point (place);
create index on %prefix%_line (man_made);

create index on %prefix%_point (int_name);
create index on %prefix%_point ("name:ru");
create index on %prefix%_point ("name:en");
create index on %prefix%_point ("natural");
-- create index on %prefix%_point (population); -- выборки >100 <5000 оказываются неиндексными

create index on %prefix%_polygon ("name:en");
create index on %prefix%_polygon (admin_level);
create index on %prefix%_polygon (landuse);
create index on %prefix%_polygon ("natural");

create index on %prefix%_polygon ("waterway"); -- ривербанки неплохо бы перетащить в natural