
from twms import projections
import lxml.etree as etree
from shapely.ops import polygonize_full, linemerge
from shapely.geometry import Polygon


def parse_augmented_diff(diff_stream):
    geom = {
        "delete":
            {"way":set(), "node": set(), "relation": set()},
        "add":
            {"node":{}, "way": {}, 'relation':{}}
    }

    mode = 'delete'
    tags = {}
    linestring = []
    members = []



    context = etree.iterparse(diff_stream, events = ('start', 'end'))
    for action, elem in context:
        items = dict(elem.items())
        if action == "start":
            #if elem.tag in ('osm', 'note', 'meta', 'old', 'new', 'bounds', 'tag', 'member', 'nd'):
            #    continue
            if elem.tag in ('node', 'way', 'relation'):
                tags = {}
                linestring = []
                if items.get('visible') == 'false':
                    mode = 'delete'
                #if mode == 'delete':
                geom['delete'][elem.tag].add(int(items['id']))
            elif elem.tag == 'member':
                linestring = []
            elif elem.tag == 'action':
                if items['type'] == 'delete':
                    mode = 'delete'
                else:
                    mode = 'add'
            elif elem.tag == 'old':
                mode = 'delete'
            elif elem.tag == 'new':
                mode = 'add'
            elif elem.tag == 'nd':
                linestring.append((float(items['lon']), float(items['lat'])))

        elif action == "end":
            if mode == 'add':
                if elem.tag == 'tag':
                    tags[items['k']] = items['v']
                elif elem.tag == 'node':
                    if tags:
                        geom[mode][elem.tag][int(items['id'])] = {'geom': (float(items['lon']), float(items['lat'])), 'tags': tags}
                elif elem.tag == 'way':
                    if tags:
                        geom[mode][elem.tag][int(items['id'])] = {'geom': linestring, 'tags': tags}
                elif elem.tag == 'member':
                    if linestring:
                        members.append(linestring)
                elif elem.tag == 'relation':
                    if tags and members:
                        if tags.get('type') in ('multipolygon', 'route', 'boundary'):
                            geom[mode][elem.tag][int(items['id'])] = {'geom': members, 'tags': tags}
            continue
        #print action, elem
    return geom

def check_tags_if_polygon(tags):
    return True

def build_deletes(diff, db_options = {"prefix": "planet_osm"}):
    sql = []
    if diff["delete"]["node"]:
        ids = list(diff["delete"]["node"])
        ids.sort()

        sql.append("DELETE FROM {prefix}_point where osm_id in (".format(**db_options)+ ",".join([str(i) for i in ids]) +");")
    ids = list(diff["delete"]["way"])
    ids += [-i for i in diff["delete"]["relation"]]
    if ids:
        ids.sort()
        sql.append("DELETE FROM {prefix}_line where osm_id in (".format(**db_options)+ ",".join([str(i) for i in ids]) +");")
        sql.append("DELETE FROM {prefix}_polygon where osm_id in (".format(**db_options)+ ",".join([str(i) for i in ids]) +");")

    return sql

def merge_rings(lines):
    rings = []
    unclosed = []

    while lines:
        cur_line = lines.pop()
        if cur_line[0] == cur_line[-1]:
            rings.append(cur_line)
        else:
            unclosed.append(cur_line)




def build_geometries(diff, srid):
    srid_txt = "EPSG:{}".format(srid)
    geom = {'line': [], 'point': [], 'polygon': []}
    for osm_id, node in diff['add']['node'].iteritems():
        x, y = projections.from4326(node["geom"], srid_txt)
        geom["point"].append({"geom": "SRID={};POINT({} {})".format(srid, x, y), "osm_id": osm_id, "tags": node["tags"]})
    for osm_id, way in diff['add']['way'].iteritems():
        line = projections.from4326(way["geom"], srid_txt)
        polygonize = check_tags_if_polygon(way["tags"])
        if polygonize:
            result, dangles, cuts, invalids = polygonize_full([line])
            #print result, dangles, cuts, invalids
            for poly in result:
                geom["polygon"].append({"geom": "SRID={};{}".format(srid, poly.wkt), "osm_id": osm_id, "way_area":poly.area, "tags": way["tags"]})
            for line in dangles:
                geom["line"].append({"geom": "SRID={};{}".format(srid, line.wkt), "osm_id": osm_id, "tags": way["tags"]})
            for line in cuts:
                geom["line"].append({"geom": "SRID={};{}".format(srid, line.wkt), "osm_id": osm_id, "tags": way["tags"]})
            for line in invalids:
                geom["line"].append({"geom": "SRID={};{}".format(srid, line.wkt), "osm_id": osm_id, "tags": way["tags"]})
        else:
            ll = ",".join([a[0] + a[1] for a in line])
            geom["line"].append({"geom": "SRID={};LINESTRING({})".format(srid, ll), "osm_id": osm_id, "tags": way["tags"]})
    for osm_id, relation in diff['add']['relation'].iteritems():
        lines = [projections.from4326(way, srid_txt) for way in relation["geom"]]
        polygonize = check_tags_if_polygon(relation["tags"])
        if polygonize:
            merged = linemerge(lines)
            polys = []
            lines = []
            for line in merged:
                if line.is_ring:
                    polys.append(line)
                else:
                    lines.append(line)
            if polys:
                # TODO: repair geometry
                poly = Polygon(polys[0], polys[1:])
                geom["polygon"].append({"geom": "SRID={};{}".format(srid, poly.wkt), "osm_id": -osm_id, "way_area":0, "tags": relation["tags"]})
            for line in lines:
                geom["line"].append({"geom": "SRID={};{}".format(srid, line.wkt), "osm_id": -osm_id, "tags": relation["tags"]})

            #result, dangles, cuts, invalids = polygonize_full(lines)
            ##print result, dangles, cuts, invalids
            #result = list(result)
            #sd = result[0]
            #for poly in result[1:]:
                #sd = sd.symmetric_difference(poly)
            #geom["polygon"].append({"geom": "SRID={};{}".format(srid, sd.wkt), "osm_id": -osm_id, "way_area":sd.area, "tags": relation["tags"]})
            #for line in dangles:
                #geom["line"].append({"geom": "SRID={};{}".format(srid, line.wkt), "osm_id": -osm_id, "tags": relation["tags"]})
            #for line in cuts:
                #geom["line"].append({"geom": "SRID={};{}".format(srid, line.wkt), "osm_id": -osm_id, "tags": relation["tags"]})

        else:
            ll = ",".join([a[0] + a[1] for a in line])
            geom["line"].append({"geom": "SRID={};LINESTRING({})".format(srid, ll), "osm_id": osm_id, "tags": relation["tags"]})
    return geom

def braindead_psql_inserter(geom, db_options = {"prefix": "planet_osm"}):
    sql = []
    for geom_type, geoms in geom.iteritems():
        for feature in geoms:
            sql.append("insert into {prefix}_{geom_type} (osm_id, way) values ({osm_id}, '{geom}');".format(**{"prefix": db_options["prefix"], "geom_type": geom_type, "osm_id": feature["osm_id"], "geom": feature["geom"]}))

    return sql


if __name__ == '__main__':
    augmented_diff = open('adiff.xml', 'r')

    diff = parse_augmented_diff(augmented_diff)

    sql = build_deletes(diff)
    geom = build_geometries(diff, 900913)
    sql += braindead_psql_inserter(geom)
    for q in sql:
        print q