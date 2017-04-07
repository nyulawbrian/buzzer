#! /usr/bin/python

import time, sys, logging
import argparse, threading
import RPi.GPIO as GPIO
import automationhat

# Get command line arguments
parser = argparse.ArgumentParser(description='Interface Raspberry Pi Pimoroni Automation HAT with Lee Dan style apartment station intercom.')
parser.add_argument('--debug', help='Enable console debug logging',
    action='store_true')
parser.add_argument('-dt', '--doortimeout', type=int, default=5,
    help='Length of time to wait after door tone detected in sec')
args = parser.parse_args()

# Configure logging options
loggingLevel = 'logging.DEBUG' if args.debug else 'logging.INFO'
logging.basicConfig(level=eval(loggingLevel),
        format='%(asctime)-15s [%(levelname)s] (%(threadName)-10s) %(message)s')
logging.info('Logging level {0}'.format(loggingLevel))

# Set constants
doortimeout = args.doortimeout

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

        # Turn light off
        # Necessary if light previously set to float brightness value
        func = '{0}.off()'.format(self.func)
        eval(func)

        while self.thisThread.event.isSet():
            func = '{0}.toggle()'.format(self.func)
            eval(func)
            time.sleep(self.blinkRate)

        logging.debug('Blink STOPPED')

    def on(self):
        self.thisThread.event.set()
        self.thisThread.start()

    def off(self):
        self.thisThread.event.clear()

        # Leave light off
        func = '{0}.off()'.format(self.func)
        eval(func)


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
    automationhat.relay.one.on()
    time.sleep(0.1)

    # Set door button open
    automationhat.relay.two.off()
    time.sleep(0.1)

    # Set door tone detect indicator off
    automationhat.output.one.off()
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
    # Dim power light until startup sequence
    logging.debug('dimming Warn light')
    automationhat.light.warn.write(0.25)
    time.sleep(0.1)

    logging.debug('calling startup()')
    startup()

    # Set comms light on to indicate program running
    automationhat.light.comms.on()

    logging.info('Ready.')

    # Check inputs and perform actions accordingly until "power" button pressed
    while not automationhat.input.two.read():
        time.sleep(0.1)

        # Check if Input 1 is high
        # This indicates that door tone is detected
        if automationhat.input.one.read():
            time.sleep(0.1)
            logging.info('Door tone detected.')
            logging.debug('Input 1 is HIGH')

            # Blink notification light via Output 1
            indicator = Blink('output','one')
            indicator.on()
            time.sleep(0.1)

            # Turn Relay 1 off
            # This enables apartment station audio
            automationhat.relay.one.off()
            logging.debug('Relay 1 turned off')
            time.sleep(doortimeout)

            # Turn Relay 1 on
            # This disables the apartment station audio
            automationhat.relay.one.on()
            logging.debug('Relay 1 turned on')
            #time.sleep(5)

            # Stop blinking indicator light
            indicator.off()
            #time.sleep(1)
            continue

    logging.info('Shutting down.')



# EOF
