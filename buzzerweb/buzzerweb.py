from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import rpyc
#import automationhat
import time
import logging

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


@app.route('/')
def hello_world():
    logging.debug('in hello_worl()')
    #automationhat.light.power.toggle()
    time.sleep(5)
    #flash('Power light ={0}'.format(automationhat.light.power.read()))
    return 'hi'

logging.debug('no longer in hello_world')

#EOF
