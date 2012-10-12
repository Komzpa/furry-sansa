furry-sansa
===========

Updater for osm2pgsql database and rendering stylesheets used by Komzpa.

Name suggested by github project name generator :3

Special thanks to:
 * Kai Krueger aka apmon, osm2pgsql maintainer who added almost all features I needed;
 * Jochen Topf, for openstreetmapdata.com source of coastlines;
 * OSM community, who created the best world map.

Depends:
 * osm2pgsql 0.81.0+ https://github.com/openstreetmap/osm2pgsql
 * osm-c-tools http://gitorious.org/osm-c-tools
 * wget

 
Workflow:
 * Write a config file for your hardware and intentions;
 * get OpenStreetMap dump. If you define a set of dumps in config file, it's as easy as:
```bash
python furry.py config/your_config.conf synthdump
```

 The process will automatically update merged dump with latest data using minutely, hourly and daily diffs.

 * alternatively, if you downloaded dump yourself and want to update it,
```bash
python furry.py config/your_config.conf updatedump
```

 * load data to postgres database. 
```bash
python furry.py config/your_config.conf import
```

 * for minutely updates, you need to get new diffs from OpenStreetMap server
``` bash
python furry.py config/your_config.conf getdiff
```

 * to actually apply diff to database, 
``` bash
python furry.py config/your_config.conf diff2db
```

 * to update your dump afterwards using the same downloaded diffs, once you have some diffs downloaded:
``` bash
python furry.py config/your_config.conf updatedump
```