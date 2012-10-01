import os
import sys
import logging
import datetime
import subprocess


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
    A method that calls the coomandline, logs properly and measures exectution time.
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
    

action = sys.argv[2]

if not os.path.exists(instance['tmpdir']):
    logger.info('creating temp directory %s'%instance['tmpdir'])
    os.makedirs(instance['tmpdir'])

if action == 'import':
    logger.debug('starting osm2pgsql import')
    execute('osm2pgsql ' +osm2pgsql_actions['create'])
    # TODO: create index

elif action == 'synthdump':
    logger.debug('starting dump synthesis')
    logger.info('downloading dumps')
    os.chdir(instance['tmpdir'])
    for name, url in instance['external_dumps']:
        execute('wget -c -O "%s" "%s"'%(name, url))

    logger.info('merging final dump')
    local_filenames = '"' + '" "'.join([i[0] for i in instance['external_dumps']]) + '"'
    execute('osmconvert %s > %s'%( local_filenames, instance['dump'] ))
    
else:
    logger.error('unknown action %s'%action)
    exit(10)