#! /usr/bin/python

# Sandbox Python script
import automationhat
import time
import threading
import logging

# Configure logging options
logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s')
logging.debug('logging config SUCESSS')

# Set running state to false
isRunning = False

def reset_automation_hat():
    """Reset all hardware to off state"""

    logging.debug('Resetting Automation HAT hardware')

    # Turn all lights off
    logging.debug('Turning all lights off')
    automationhat.light.power.off()
    automationhat.light.comms.off()
    automationhat.light.warn.off()

    # Turn all relays off
    logging.debug('Turning all relays off')
    automationhat.relay.one.off()
    automationhat.relay.two.off()
    automationhat.relay.three.off()

    # Turn all outputs off
    logging.debug('Turning all outputs off')
    automationhat.output.one.off()
    automationhat.output.two.off()
    automationhat.output.three.off()

def test_automation_hat():
    """Read state of each input and output and compare to ref value
    return dict of any failures"""

    logging.debug('Testing Automation HAT hardware')

    status = {}
    results = {}

    # All hardware statuses should read 0
    ref = 0

    # Read status of lights
    status['light power'] = automationhat.light.power.read()
    logging.debug(status['light power'])
    status['light comms'] = automationhat.light.comms.read()
    status['light warn']  = automationhat.light.warn.read()

    # Read status of relays
    status['relay one']   = automationhat.relay.one.read()
    logging.debug(status['relay one'])
    status['relay two']   = automationhat.relay.two.read()
    status['relay three'] = automationhat.relay.three.read()

    # Read status of outputs
    status['output one']   = automationhat.output.one.read()
    logging.debug(status['output one'])
    status['output two']   = automationhat.output.two.read()
    status['output three'] = automationhat.output.three.read()

    # Read status of inputs
    status['inputs one']   = automationhat.input.one.read()
    logging.debug(status['inputs one'])
    status['inputs two']   = automationhat.input.two.read()
    status['inputs three'] = automationhat.input.three.read()

    # Read status of ADC
    status['analog one']   = automationhat.analog.one.read()
    logging.debug(status['analog one'])
    status['analog two']   = automationhat.analog.two.read()
    status['analog three'] = automationhat.analog.three.read()

    # loop through each dict, compare value to ref, log the result
    # add any failures to results and return
    for name, val in status:
        if val != ref:
            results[name] = val

    return results


def set_run_conditions():
    """Threaded function to setup event handlers which trigger run()"""


def set_stop_conditions():
    """Threaded function to setup event handlers which stop run()"""


def run():
    """Main program function"""


    # Set comms light on to indicate program running
    automationhat.light.comms.on()

    # if Input 1 or ADC 1 is high
    # turn Output 1 on to indicate door tone detected
    # turn Relay 1 on to enable apartment station audio
    # after inactivity, turn both off

    while True:
        # should be exit condition?
        a=1

# Class to control blinking of built-in lights
class BlinkLight():
    """Threaded class to blink built-in Pimoroni Automation HAT lights"""

    def __init__(self, lightname, blinkRate=0.25):
        import time #try test if imported
        import threading #try test if imported
        import logging #try test if imported

        try:
            import automationhat
        except ImportError:
            exit("Could not import autiomationhat")

        self.lightname = lightname
        doblink = 0
        self.doblink = doblink
        self.blinkRate = blinkRate
        self.func = "automationhat.light." + self.lightname
        self.threadName = "BlinkLight %s", self.lightname

    def blink(self):
        # Turn light off
        # Necessary if light previously set to float brightness value
        func = self.func + ".off()"
        eval(func)

        while self.doblink:
            func = self.func + ".toggle()"
            eval(func)
            time.sleep(self.blinkRate)

        # Leave light off
        func = self.func + ".off()"
        eval(func)

    def on(self):
        self.doblink = 1
        thisThread = threading.Thread(name=self.threadName,target=self.blink)
        thisThread.start()
        logging.debug('BlinkLight STARTED')

    def off(self):
        self.doblink = 0
        logging.debug('BlinkLight STOPPED')


# Class to detect button press
class DetectButtonPress():
    """Threaded class to detect digital input HIGH"""
    def __init__(self, inputName):
        self.inputName = inputName
        self.func = "automationhat.input." + self.inputName
        self.threadName = "DetectButtonPress %s", self.inputName

    def isPressed(self):
        while True:
            func = self.func + 'read()'
            inputState = eval(func)
            if inputState:
                return


# Class to detect input


# Class to set output?



def startup():
    """Run through startup sequence to check software and
    hardware presence and states, then setup default states"""

    logging.info('Startup sequence STARTED')

    if automationhat.is_automation_hat():
        logging.info('Automation HAT detected.')
    else:
        logging.critical('Automation HAT not detected, check hardware.')

    # Initialize hardware
    logging.debug('Hardware initialization STARTED')

    # Reset hardware state
    reset_automation_hat()

    # Blink power light to indicate startup sequence in progress
    blinkPower = BlinkLight("power")
    blinkPower.on()

    # Test hardware
    #test_automation_hat()

    time.sleep(1)
    logging.debug('Hardware initialization COMPLETED')

    # Set default hardware states
    logging.debug('Setting default hardware states STARTED')
    # Disable apartment station audio
    automationhat.relay.one.on()
    time.sleep(1)
    # Set door button open
    automationhat.relay.two.off()
    time.sleep(1)
    # Set door tone detect indicator off
    automationhat.output.one.off()
    time.sleep(1)
    logging.debug('Setting default hardware states COMPLETED')
    blinkPower.off()
    time.sleep(1)
    automationhat.light.power.on()
    logging.info('Startup sequence COMPLETED')


# Dim power light until startup sequence
automationhat.light.warn.write(0.25)
time.sleep(1)

# Setup threads for user input and power button events
# when either detected, call startup(), setup exit events, call run()
set_run_conditions()

startup()

set_stop_conditions()
    # wait for user input?
    # exit when button pushed

threading.Thread(name="run", target=run).start() # remove once set_run_conditions works

# EOF
