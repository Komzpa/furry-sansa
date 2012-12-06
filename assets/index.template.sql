create index %prefix%_line_name on %prefix%_line (name);
create index %prefix%_line_name_en on %prefix%_line ("name:en");
create index %prefix%_point_name on %prefix%_point (name);
create index %prefix%_point_addr_street on %prefix%_point ("addr:street");
create index %prefix%_polygon_name on %prefix%_polygon (name);
create index %prefix%_polygon_addr_street on %prefix%_polygon ("addr:street");
create index %prefix%_point_place on %prefix%_point (place);
create index %prefix%_line_man_made on %prefix%_line (man_made);

create index %prefix%_point_int_name on %prefix%_point (int_name);
create index %prefix%_point_name_ru on %prefix%_point ("name:ru");
create index %prefix%_point_name_en on %prefix%_point ("name:en");
create index %prefix%_point_natural on %prefix%_point ("natural");
-- create index %prefix%_point_population on %prefix%_point (population); -- выборки >100 <5000 оказываются неиндексными

create index %prefix%_polygon_name_en on %prefix%_polygon ("name:en");
create index %prefix%_polygon_admin_level on %prefix%_polygon (admin_level);
create index %prefix%_polygon_landuse on %prefix%_polygon (landuse);
create index %prefix%_polygon_natural on %prefix%_polygon ("natural");

create index %prefix%_polygon_waterway on %prefix%_polygon ("waterway"); -- ривербанки неплохо бы перетащить в natural