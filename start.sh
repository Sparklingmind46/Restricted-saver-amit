#!/bin/bash

# Run health check script in the background
python health_check.py &

# Run the bot main.py script in the background
python main.py &

# Start the Flask app with Gunicorn
exec gunicorn -b 0.0.0.0:8000 health_check:app
