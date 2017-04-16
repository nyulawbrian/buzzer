from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import time
import logging
import os
import shelve
import settings as bs

STATEFILE = '../{0}'.format(bs.STATEFILE)

# Configure logging options
loggingLevel = 'logging.DEBUG'
FORMAT = """%(asctime)-15s [%(levelname)s] (%(threadName)-10s) %(message)s"""
logging.basicConfig(
    level=eval(loggingLevel),
    format=FORMAT)
logging.info('Logging level is {0}'.format(loggingLevel))

# Create application instance
app = Flask(__name__)
logging.debug('created application instance')

# Load config from this file
app.config.from_object(__name__)
logging.debug('loaded config from __name__')

# Load config
#app.config.update(dict(
#
#))

# Set (export) env var to point to a config file
# app.config.from_envvar('SOMEENVVAR', silent=True)

# Configure path
resource_path = os.path.join(app.root_path, '../state')

# debugging output
logging.debug('app.root_path ={0}'.format(app.root_path))
logging.debug('resource_path = {0}'.format(resource_path))

def read_state(skey):
    # Read value from shelve db
    d = shelve.open(resource_path)
    sval = d[skey]
    d.close()
    return sval

def get_state_keys():
    # Read keys in shelve db
    d = shelve.open(resource_path)
    skeys = d.keys()
    d.close()
    return skeys

logging.debug('not yet in main()')

@app.route('/')
def main():
    logging.debug('in main()')
    #logging.debug('bs.STATEFILE = {0}'.format(bs.STATEFILE))
    #logging.debug('shelve file path = {0}'.format(STATEFILE))

    states = {}
    logging.debug('states dict initialized')

    skeys = get_state_keys()
    print skeys

    for thisKey in skeys:
        states[thisKey] = read_state(thisKey)
        print thisKey
        print read_state(thisKey)
        #flash('{0} is {1}'.format(thisKey,states[thisKey]))
        #logging.debug('thisKey = {0}'.format(thisKey))
        #logging.debug('thisKey value = {0}'.format(read_state(thisKey))
        #logging.debug('states[{0}] = {1}'.format(thisKey, states[thisKey]))

    time.sleep(1)

    return jsonify(states)

#EOF
