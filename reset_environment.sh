#!/bin/bash

# Example of resetting a Python environment for a user

# Killing the Python script (example)
pkill -f my_python_script.py

# Reset the virtual environment (if needed)
source /path/to/venv/bin/activate
pip install --upgrade -r /path/to/requirements.txt

# Restart the Python script (example)
nohup python /path/to/my_python_script.py &
