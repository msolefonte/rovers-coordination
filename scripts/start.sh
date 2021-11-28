#!/usr/bin/env bash

mkdir -p /tmp/p3/logs

hostname=$(hostname | awk '{print $1}')

python3 lib/rover.py rover0 ${hostname} 7000 ${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 0,0,999,999 20 1500 1,2,3,4,5,6,7,8> /tmp/p3/logs/rover0.log 2>&1 &
python3 lib/rover.py rover1 ${hostname} 7001 ${hostname}:7000,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 0,1000,999,1999 20 1500 0,2,3,4,5,6,7,8 1> /tmp/p3/logs/rover1.log 2>&1 &
python3 lib/rover.py rover2 ${hostname} 7002 ${hostname}:7000,${hostname}:7001,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 0,2000,999,2999 20 1500 0,1,3,4,5,6,7,8 1> /tmp/p3/logs/rover2.log 2>&1 &
python3 lib/rover.py rover3 ${hostname} 7003 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 1000,0,1999,999 20 1500 0,1,2,4,5,6,7,8 1> /tmp/p3/logs/rover3.log 2>&1 &
python3 lib/rover.py rover4 ${hostname} 7004 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 1000,1000,1999,1999 20 1500 0,1,2,3,5,6,7,8 1> /tmp/p3/logs/rover4.log 2>&1 &
python3 lib/rover.py rover5 ${hostname} 7005 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 1000,2000,1999,2999 20 1500 0,1,2,3,4,6,7,8 1> /tmp/p3/logs/rover5.log 2>&1 &
python3 lib/rover.py rover6 ${hostname} 7006 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7007,${hostname}:7008,${hostname}:7100 2000,0,2999,999 20 1500 0,1,2,3,4,5,7,8 1> /tmp/p3/logs/rover6.log 2>&1 &
python3 lib/rover.py rover7 ${hostname} 7007 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7008,${hostname}:7100 2000,1000,2999,1999 20 1500 0,1,2,3,4,5,6,8 1> /tmp/p3/logs/rover7.log 2>&1 &
python3 lib/rover.py rover8 ${hostname} 7008 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7100 2000,2000,2999,2999 20 1500 0,1,2,3,4,5,6,7 1> /tmp/p3/logs/rover8.log 2>&1 &

python3 lib/networkVisualizer.py network-visualizer Swagats-MacBook-Air.local 7100 0 0 1> /tmp/p3/logs/network-visualizer.log 2>&1 &
