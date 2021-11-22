#!/usr/bin/env bash

for peer_pid in $(ps -ef | grep peer.py | grep python3 | awk '{print $2}'); do
    echo "Killing peer ${peer_pid}"
    kill ${peer_pid}
done

for coordinator_pid in $(ps -ef | grep coordinator.py | grep python3 | awk '{print $2}'); do
    echo "Killing coordinator ${coordinator_pid}"
    kill ${coordinator_pid}
done
