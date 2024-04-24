#!/bin/bash

echo "Starting Near Realtime RIC"
echo "Building E2 Termination"
python3 e2term/main.py 

echo "Staring xapp"
python3 signal-storm-xapp/main.py 

echo "Starting traffic patterns"
python3 ns3-simulator/main.py 