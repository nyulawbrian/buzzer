#! /usr/bin/python

import time, sys, logging
import argparse, threading
import RPi.GPIO as GPIO
import automationhat
import shelve
import settings as bs

# Get command line arguments
DESCRIPTION = """Interface Raspberry Pi Pimoroni Automation HAT with Lee Dan
                style apartment station intercom."""
parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument(
    '--debug',
    action='store_true',
    help='Enable console debug logging')
parser.add_argument(
    '-dt', '--doortimeout',
    type=int,
    default=5,
    help='Seconds to wait after door tone detected, default 5')
parser.add_argument(
    '-dr', '--doorreleasehold',
    type=int,
    default=1,
    help='Seconds to hold door release button, default 1')
parser.add_argument(
    '--noautostart',
    action='store_true',
    help='Require power button press for startup sequence')
args = parser.parse_args()

# Configure logging options
loggingLevel = 'logging.DEBUG' if args.debug else 'logging.INFO'
FORMAT = """%(asctime)-15s [%(levelname)s] (%(threadName)-10s) %(message)s"""
logging.basicConfig(
    level=eval(loggingLevel),
    format=FORMAT)
logging.info('Logging level is {0}'.format(loggingLevel))

# Set constants
DOOR_TIMEOUT = args.doortimeout
logging.debug('Door timeout is {0} second(s)'.format(DOOR_TIMEOUT))
DOOR_RELEASE_HOLD = args.doorreleasehold
logging.debug('Door release hold is {0} second(s)'.format(DOOR_RELEASE_HOLD))
AUTO_START_OFF = args.noautostart
logging.debug('Auto start disabled.')
STARTED = False
logging.debug('STARTED = False')

# Alias I/O ports to meaningful names
APT_STATION_AUDIO_DISABLE   = automationhat.relay.one
DOOR_BUTTON_PRESS           = automationhat.relay.two
DOOR_TONE_DETECT_INDICATOR  = automationhat.output.one
DOOR_TONE_INPUT             = automationhat.input.one
POWER_BUTTON                = automationhat.input.two
DOOR_RELEASE_BUTTON_INPUT   = automationhat.input.three
STATEKEYS = [
    'APT_STATION_AUDIO_DISABLE',
    'DOOR_BUTTON_PRESS',
    'DOOR_TONE_DETECT_INDICATOR',
    'DOOR_TONE_INPUT',
    'POWER_BUTTON',
    'DOOR_RELEASE_BUTTON_INPUT',
    'NOTIFICATION',
    'STARTED',
    'DOOR_RELEASE_BUTTON_INPUT_WEB',
]


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
    return


def press_door_release():
    # Emulate door release button press

    # Press button
    DOOR_BUTTON_PRESS.on()
    write_state('DOOR_BUTTON_PRESS', True)
    logging.debug('Door release button pressed.')

    # Wait to release button for predetermiend time
    time.sleep(DOOR_RELEASE_HOLD)

    # Release button
    DOOR_BUTTON_PRESS.off()
    write_state('DOOR_BUTTON_PRESS', False)
    logging.debug('Door release button released.')
    return


def write_state(skey, sval):
    # Write value to shelve db
    d = shelve.open(bs.STATEFILE, writeback=True)
    d[skey] = sval
    d.close()
    return


def read_state(skey):
    # Read value from shelve db
    d = shelve.open(bs.STATEFILE)
    sval = d[skey]
    d.close()
    return sval


def is_started(setval=None):
    global STARTED

    if setval is True:
        STARTED = True
    elif setval is False:
        STARTED = False

    # Write value to shelve db
    write_state('STARTED', STARTED)
    return STARTED


# Class to control blinking of lights, outputs, or relays
class Blink():
    """Threaded class to blink Pimoroni Automation HAT interfaces"""

    def __init__(self, targetType, targetID, blinkRate=0.25):
        self.targetID         = targetID
        self.targetType       = targetType
        self.blinkRate        = blinkRate
        self.func             = 'automationhat.{0}.{1}'.format(self.targetType,
                                self.targetID)
        self.threadName       = 'Blink {0} {1}'.format(self.targetType,
                                self.targetID)
        self.thisThread       = threading.Thread(name=self.threadName,
                                target=self.blink)
        self.thisThread.event = threading.Event()

    def blink(self):
        logging.debug('Blink STARTED')

        # Loop to blink output by using toggle() function
        # Using event handler for signal to end loop
        while self.thisThread.event.isSet():
            toggleState = '{0}.toggle()'.format(self.func)
            eval(toggleState)
            time.sleep(self.blinkRate)

        logging.debug('Blink STOPPED')

    def on(self):
        # Read current state of output
        readState = '{0}.read()'.format(self.func)
        self.originalState = eval(readState)
        logging.debug('Current state of output: {0}'.format(self.originalState))

        # Turn output off
        # Necessary for toggle() method to function if output previously set
        # to a float value via the write() method
        turnOff = '{0}.off()'.format(self.func)
        eval(turnOff)

        # Set event state and start thread
        self.thisThread.event.set()
        self.thisThread.start()

    def off(self):
        # Clear event state to end blink loop
        self.thisThread.event.clear()

        # Set output back to original state
        revertState = '{0}.write({1})'.format(self.func, self.originalState)
        eval(revertState)
        logging.debug('Reverting output to original state: {0}'.format(self.originalState))


def startup():
    """Run through startup sequence to check software and
    hardware presence and states, then setup default states"""

    logging.info('Starting up...')
    logging.debug('Startup sequence STARTED')

    if automationhat.is_automation_hat():
        logging.info('Automation HAT detected.')
    else:
        logging.critical('Automation HAT not detected, check hardware.')

    # Initialize hardware
    logging.debug('Hardware initialization STARTED')

    # Reset hardware state
    reset_automation_hat()

    # Blink power light to indicate startup sequence in progress
    blinkPower = Blink('light','power')
    blinkPower.on()

    time.sleep(0.1)
    logging.debug('Hardware initialization COMPLETED')

    # Set default hardware states
    logging.debug('Setting default hardware states STARTED')

    # Disable apartment station audio
    APT_STATION_AUDIO_DISABLE.on()
    write_state('APT_STATION_AUDIO_DISABLE', True)
    time.sleep(0.1)

    # Set door button open
    DOOR_BUTTON_PRESS.off()
    write_state('DOOR_BUTTON_PRESS', False)
    time.sleep(0.1)

    # Set door tone detect indicator off
    DOOR_TONE_DETECT_INDICATOR.off()
    write_state('DOOR_TONE_DETECT_INDICATOR', False)
    time.sleep(0.1)

    # Set GPIO 14 HIGH for indicator light
    GPIO.setup(14, GPIO.OUT)
    GPIO.output(14, GPIO.HIGH)

    logging.debug('Setting default hardware states COMPLETED')
    blinkPower.off()
    time.sleep(0.1)
    automationhat.light.power.on()

    logging.debug('Startup sequence COMPLETED')


if __name__ == '__main__':
    # Dim warn light until startup sequence
    logging.debug('dimming Warn light')
    automationhat.light.warn.write(0.25)
    time.sleep(0.1)

    is_started(False)

    # Set current states to None
    for thisKey in STATEKEYS:
        write_state(thisKey, None)

    # If auto start diabled, wait for power button press
    if AUTO_START_OFF:
        logging.info('Waiting for power button press...')
        while not POWER_BUTTON.read():
            time.sleep(0.1)
        logging.debug('Power button pressed.')

    # Run startup sequence
    logging.debug('is_started() {0}'.format(is_started()))
    startup()
    is_started(True)
    logging.debug('is_started() {0}'.format(is_started()))

    # Set comms light on to indicate program running
    automationhat.light.comms.on()
    logging.info('Ready.')

    # Run until power button is pressed
    while not POWER_BUTTON.read():
        time.sleep(0.1)

        # Check if door tone is detected
        if DOOR_TONE_INPUT.read():
            time.sleep(0.1)
            write_state('DOOR_TONE_INPUT', True)
            logging.info('Door tone detected.')
            logging.debug('DOOR_TONE_INPUT is HIGH')

            # Blink notification light
            notification = Blink('output','one')
            notification.on()
            write_state('NOTIFICATION', True)
            time.sleep(0.1)

            # Enable apartment station audio
            APT_STATION_AUDIO_DISABLE.off()
            write_state('APT_STATION_AUDIO_DISABLE', False)
            logging.debug('APT_STATION_AUDIO_DISABLE is OFF')

            # Poll for door release button press
            for i in range(DOOR_TIMEOUT * 10):
                # Hardware door release button state
                DRBI  = DOOR_RELEASE_BUTTON_INPUT.read()
                # Web door release button state
                DRBIW = read_state('DOOR_RELEASE_BUTTON_INPUT_WEB')

                if DRBI or DRBIW:
                    logging.info('Door release button press detected.')
                    press_door_release()

                time.sleep(0.1)

            # Disable apartment station audio
            APT_STATION_AUDIO_DISABLE.on()
            write_state('APT_STATION_AUDIO_DISABLE', True)
            logging.debug('APT_STATION_AUDIO_DISABLE is ON')

            # Stop blinking notification light
            notification.off()
            write_state('NOTIFICATION', False)
            #continue

        # Poll for door release button press, even if door tone not detected
        # Hardware door release button state
        DRBI  = DOOR_RELEASE_BUTTON_INPUT.read()
        # Web door release button state
        DRBIW = read_state('DOOR_RELEASE_BUTTON_INPUT_WEB')
        
        elif DRBI or DRBIW:
            logging.debug('Door release button detected without door tone')
            press_door_release()
            time.sleep(0.1)

    logging.info('Shutting down...')
    is_started(False)
    logging.info('HALTED')

# EOF
