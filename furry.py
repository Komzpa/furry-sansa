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


def execute(commandline):
    """
    A method that calls the commandline, logs properly and measures exectution time.
    """
    time = datetime.datetime.now()
    logger.info('starting "%s"'% commandline)
    process = subprocess.Popen(commandline, bufsize=1, shell=True)
    process.wait()
    if process.returncode:
        logger.error('[%s] failed "%s" in %s'%(process.returncode, commandline, str(datetime.datetime.now() - time)))
    else:
        logger.info('[%s] completed "%s" in %s'%(process.returncode, commandline, str(datetime.datetime.now() - time)))
    return process.returncode


def sql(cursor, query):
    """
    A wrapper that measures query execution time.
    """
    time = datetime.datetime.now()
    logger.info('executing query [%s]'% query)
    cursor.execute(query)
    logger.info('[%s] completed in %s'%(query, str(datetime.datetime.now() - time)))

action = sys.argv[2]

if not os.path.exists(instance['tmpdir']):
    logger.info('creating temp directory %s'%instance['tmpdir'])
    os.makedirs(instance['tmpdir'])

if action == 'import':
    logger.debug('starting osm2pgsql import')
    execute('osm2pgsql ' +osm2pgsql_actions['create'])

elif action == "index":
    logger.debug('starting database index')
    logger.debug('preparing queries from %s' % instance['index_template'])
    queries = [line.split('-- ')[0].strip().replace('%prefix%', instance['pg_table_prefix']) for line in open(instance['index_template']) if line.split('-- ')[0].strip()]
    logger.debug('loaded %s queries, connecting to %s' % (len(queries), pg_database))
    database_connection = psycopg2.connect(pg_database)
    database_connection.set_isolation_level(0) # now we don't have to COMMIT everything
    database_cursor = database_connection.cursor()

    for query in queries:
        sql(database_cursor, query)


elif action == 'synthdump':
    logger.debug('starting dump synthesis')
    logger.info('downloading dumps')
    local_filenames = ""
    os.chdir(instance['tmpdir'])
    for name, url in instance['external_dumps']:
        if 0 == execute('wget -c -O "%s" "%s"'%(name, url)): # downloading file finished well
            if not os.path.exists(name+'.o5m'):
                execute('osmconvert --out-o5m "%s" > "%s"'%( name, name+'.o5m'))
                local_filenames += ' "%s.o5m"'%name

    logger.info('merging final dump')
    execute('osmconvert --out-pbf %s > %s'%( local_filenames, instance['dump'] ))

elif action == 'getdiff':
    # TODO
    pass
    
else:
    logger.error('unknown action %s'%action)
    exit(10)