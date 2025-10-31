#!/bin/bash

# Start MediaMTX in background
mediamtx mediamtx.yml &

# Wait for MediaMTX to start
sleep 2

# Start the Python application
python src/main.py
