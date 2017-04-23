#! /bin/bash

# Start buzzer control back end
echo Starting backend...
python /home/pi/buzzer/buzzerctl.py --noautostart --debug &

sleep 2

# Start buzzer control web front end
echo Starting web frontend...

# Set environmental variables
export FLASK_APP=buzzerweb
export FLASK_DEBUG=true

# Run flask application
flask run --host=0.0.0.0 &

#EOF
