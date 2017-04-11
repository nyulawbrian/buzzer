import rpyc
from flask import Flask

import automationhat
import time


app = Flask(__name__)

@app.route('/')
def hello_world():
    automationhat.light.power.on()
    time.sleep(5)
    return 'Power light ={0}'.format(automationhat.light.power.read())


#EOF
