#! /bin/bash

# Start buzzer control back end
python buzzerctl.py --noautostart --debug &


# Start buzzer control web front end
# Set environmental variables
export FLASK_APP=buzzerweb
export FLASK_DEBUG=true

# Run flask application
flask run --host=0.0.0.0

#EOF
