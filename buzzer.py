#! /usr/bin/python

# Sandbox Python script
import automationhat
import time
import threading
import logging
import sys

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


# Class to control blinking of lights, outputs, or relays
class Blink():
    """Threaded class to blink built-in Pimoroni Automation HAT lights"""

    def __init__(self, targetType, targetID, blinkRate=0.25):
        self.targetID         = targetID
        self.targetType       = targetType
        self.blinkRate        = blinkRate
        self.func             = "automationhat" + "." + self.targetType + "." + self.targetID
        self.threadName       = "Blink %s", self.targetID
        self.thisThread       = threading.Thread(name=self.threadName,target=self.blink)
        self.thisThread.event = threading.Event()

    def blink(self):
        # Turn light off
        # Necessary if light previously set to float brightness value
        func = self.func + ".off()"
        eval(func)

        while self.thisThread.event.isSet():
            func = self.func + ".toggle()"
            eval(func)
            time.sleep(self.blinkRate)

    def on(self):
        self.thisThread.event.set()
        self.thisThread.start()
        logging.debug('Blink STARTED')

    def off(self):
        self.thisThread.event.clear()
        logging.debug('Blink STOPPED')

        # Leave light off
        func = self.func + ".off()"
        eval(func)


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
    blinkPower = Blink("light","power")
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
    logging.debug('Setting default hardware states COMPLETED')
    blinkPower.off()
    time.sleep(0.1)
    automationhat.light.power.on()
    logging.info('Startup sequence COMPLETED')


if __name__ == '__main__':
    # Dim power light until startup sequence
    logging.debug("dimming Warn light")
    automationhat.light.warn.write(0.25)
    time.sleep(0.1)

    logging.debug("calling startup()")
    startup()

    # Set comms light on to indicate program running
    automationhat.light.comms.on()

    while not automationhat.input.two.read():
        time.sleep(0.1)

        # Check if Input 1 is high
        # This indicates that door tone is detected
        if automationhat.input.one.read():
            time.sleep(0.1)
            logging.debug("Input 1 is HIGH")

            # Blink notification light via Output 1
            indicator = Blink("output","one")
            indicator.on()
            time.sleep(0.1)

            # Turn Relay 1 off
            # This enables apartment station audio
            automationhat.relay.one.off()
            logging.debug("Relay 1 turned off")
            time.sleep(5)

            # Turn Relay 1 on
            # This disables the apartment station audio
            automationhat.relay.one.on()
            logging.debug("Relay 1 turned on")
            #time.sleep(5)

            # Stop blinking indicator light
            indicator.off()
            #time.sleep(1)
            continue





# EOF
