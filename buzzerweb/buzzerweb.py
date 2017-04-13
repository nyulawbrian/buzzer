from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import rpyc
import automationhat
import time

# Create application instance
app = Flask(__name__)

# Load config from this file
app.config.from_object(__name__)

# Load config
#app.config.update(dict(
#
#))

# Set (export) env var to point to a config file
# app.config.from_envvar('SOMEENVVAR', silent=True)


@app.route('/')
def hello_world():
    automationhat.light.power.toggle()
    time.sleep(5)
    flash('Power light ={0}'.format(automationhat.light.power.read()))
    return 'a'


#EOF
