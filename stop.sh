#!/usr/bin/env bash

for rover_pid in $(ps -ef | grep rover.py | grep python3 | awk '{print $2}'); do
    echo "Killing Rover ${rover_pid}"
    kill ${rover_pid}
done


for nv_pid in $(ps -ef | grep networkVisualizer.py | grep python3 | awk '{print $2}'); do
    echo "Killing Network Visualizer ${nv_pid}"
    kill ${nv_pid}
done


