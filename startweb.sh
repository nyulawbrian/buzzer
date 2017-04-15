#! /bin/bash

# Set environmental variables
export FLASK_APP=buzzerweb
export FLASK_DEBUG=true

# Run flask application
cd /buzzer/
flask run --host=0.0.0.0

#EOF
