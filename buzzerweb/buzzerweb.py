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
STATEFILE = os.path.join(app.root_path, '../state')

def read_state(skey):
    # Read value from shelve db
    d = shelve.open(STATEFILE)
    sval = d[skey]
    d.close()
    return sval

def write_state(skey, sval):
    # Write value to shelve db
    d = shelve.open(STATEFILE, writeback=True)
    d[skey] = sval
    d.close()
    return

def get_state_keys():
    # Read keys in shelve db
    d = shelve.open(STATEFILE)
    skeys = d.keys()
    d.close()
    return skeys

logging.debug('not yet in dashboard()')

@app.route('/')
def dashboard():
    logging.debug('in dashboard()')

    states = {}

    skeys = get_state_keys()
    print skeys

    for thisKey in skeys:
        states[thisKey] = read_state(thisKey)

    if states['STARTED']:
        status = 'running'
    else:
        status = 'not running'

    return render_template('buzzer_dashboard.html', status=status)


@app.route('/buzzer_control', methods=['POST'])
def buzzer_control():
    if request.form('doorreleasehold'):
        write_state('DOOR_RELEASE_BUTTON_INPUT_WEB', True)
        flash('Door release button pressed!')
        time.sleep(2)
        write_state('DOOR_RELEASE_BUTTON_INPUT_WEB', False)

    return redirect(url_for('dashboard'))


#EOF
