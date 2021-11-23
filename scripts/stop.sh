#!/usr/bin/env bash

for rover_pid in $(ps -ef | grep rover.py | grep python3 | awk '{print $2}'); do
    echo "Killing Rover ${rover_pid}"
    kill ${rover_pid}
done
