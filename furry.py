import os
import sys
import logging
import datetime
import subprocess
import psycopg2


if len(sys.argv) < 3:
    print """
    Furry Sansa osm database updater.
    
    Usage:
    %s [config] [action]
    """ % sys.argv[0]
    exit()

execfile(sys.argv[1])

logger = logging.getLogger('furry-sansa')
hdlr = logging.FileHandler(instance['log'])
formatter = logging.Formatter('[%(process)s] %(asctime)s %(levelname)5s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

logger.debug('started with options: '+ ' '.join(sys.argv))


def execute(commandline, need_output = False):
    """
    A method that calls the commandline, logs properly and measures exectution time.
    """
    time = datetime.datetime.now()
    logger.info('starting "%s"'% commandline)
    if need_output:
        process = subprocess.Popen(commandline, bufsize=1, stdout=subprocess.PIPE, shell=True)
    else:
        process = subprocess.Popen(commandline, bufsize=1, shell=True)
    process.wait()
    if process.returncode:
        logger.error('[%s] failed "%s" in %s'%(process.returncode, commandline, str(datetime.datetime.now() - time)))
    else:
        logger.info('[%s] completed "%s" in %s'%(process.returncode, commandline, str(datetime.datetime.now() - time)))
    if need_output:
        return process.stdout.read()
    return process.returncode


def sql(query):
    """
    A wrapper that measures query execution time.
    """
    database_connection = psycopg2.connect(pg_database)
    database_connection.set_isolation_level(0) # now we don't have to COMMIT everything
    database_cursor = database_connection.cursor()
    time = datetime.datetime.now()
    logger.info('executing query [%s]'% query)
    res = database_cursor.execute(query)
    logger.info('[%s] completed in %s, result %s'%(query, str(datetime.datetime.now() - time), str(res)))

action = sys.argv[2]

if not os.path.exists(instance['tmpdir']):
    logger.info('creating temp directory %s'%instance['tmpdir'])
    os.makedirs(instance['tmpdir'])

if action == 'import':
    logger.debug('starting osm2pgsql import')
    if 0 == execute('osm2pgsql ' +osm2pgsql_actions['create']):
        os.remove(instance['pg_timestamp'])
        execute("osmconvert --out-timestamp %s > %s "%(instance['dump'],instance['pg_timestamp']))
        if "(" in open(instance['pg_timestamp']).read():
            # recalculating timestamp
            os.remove(instance['pg_timestamp'])
            timestamp = execute('osmconvert --out-statistics %s | grep "timestamp max"'%(instance['dump']), need_output = True)
            open(instance['pg_timestamp'], 'w').write(timestamp.strip()[:11]+"00:00:00Z")

elif action == "index":
    logger.debug('starting database index')
    logger.debug('preparing queries from %s' % instance['index_template'])
    queries = [line.split('-- ')[0].strip().replace('%prefix%', instance['pg_table_prefix']) for line in open(instance['index_template']) if line.split('-- ')[0].strip()]
    logger.debug('loaded %s queries, connecting to %s' % (len(queries), pg_database))
    for query in queries:
        sql(query)

elif action == 'synthdump':
    logger.debug('starting dump synthesis')
    logger.info('downloading dumps')
    local_filenames = ""
    os.chdir(instance['tmpdir'])
    for name, url in instance['external_dumps']:
        if 0 == execute('wget -c -O "%s" "%s"'%(name, url)): # downloading file finished well
            if not os.path.exists(name+'.o5m'):
                execute('osmconvert --out-o5m "%s" |gzip > "%s"'%( name, name+'.o5m.gz'))
                local_filenames += ' "%s.o5m.gz"'%name

    logger.info('merging final dump')
    execute('osmconvert --out-o5m %s | gzip > %s'%( local_filenames, 'merged.o5m.gz' ))

    logger.info('updating dump')
    execute('osmupdate %s %s'%( 'merged.o5m.gz', instance['dump'] ))

elif action == 'updatedump':
    logger.info('updating dump')
    if os.path.exists(instance['cumulative_diff']):
        if 0 == execute("osmconvert --out-o5m %s %s > %s.new"%(instance['dump'], instance['cumulative_diff'], instance['dump'])):
            os.remove(instance['dump'])
            os.rename(instance['dump']+".new", instance['dump'])
    else:
        tmpfile = os.path.join(instance['tmpdir'], 'newdump.o5m')
        if 0 == execute('osmupdate %s %s'%( instance['dump'], tmpfile)):
            os.remove(instance['dump'])
            os.rename(tmpfile, instance['dump'])

elif action == 'getdiff':
    logger.debug('getting diffs')
    try:
        timestamp = open(instance['pg_timestamp']).read().strip()
    except:
        logger.error('can not read timestamp file %s, please fill it!'%instance['pg_timestamp'])
        exit(1)
    if os.path.exists(instance['current_diff']):
        timestamp_diff = execute('osmconvert --out-timestamp "%s"'%instance['current_diff'] , need_output = True).strip()
        if timestamp_diff == timestamp:
            os.remove(instance['current_diff'])
    if not os.path.exists(instance['current_diff']):
        logger.debug('getting new diffs')
        execute('osmupdate --fake-lonlat %s %s'%(timestamp, instance['current_diff']))
        timestamp_diff = execute('osmconvert --out-timestamp "%s"'%instance['current_diff'] , need_output = True).strip()
        logger.debug('got new diffs, old timestamp %s, new %s'%(timestamp, timestamp_diff))
    #updating cumulative diff
    if os.path.exists(instance['current_diff']):
        if not os.path.exists(instance['cumulative_diff']):
            execute("osmconvert --out-o5c %s > %s"%(instance['current_diff'], instance['cumulative_diff']))
        else:
            if 0 == execute("osmconvert --merge-versions --out-o5c %s %s > %s.new" % (instance['cumulative_diff'], instance['current_diff'], instance['cumulative_diff'])):
                os.remove(instance['cumulative_diff'])
                os.rename(instance['cumulative_diff']+".new", instance['cumulative_diff'])

elif action == 'diff2db':
    logger.debug('applying diffs to db')
    if 0 == execute('osm2pgsql ' +osm2pgsql_actions['append']):
        execute("osmconvert --out-timestamp %s > %s "%(instance['current_diff'],instance['pg_timestamp']))
        

else:
    logger.error('unknown action %s'%action)
    exit(10)