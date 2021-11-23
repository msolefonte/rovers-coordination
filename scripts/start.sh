#!/usr/bin/env bash

mkdir -p /tmp/p3/logs

hostname=$(hostname -I | awk '{print $1}')

python3 lib/rover.py rover0 ${hostname} 7000 ${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008 0,0,999,999 20 1500 > /tmp/p3/logs/rover0.log &
python3 lib/rover.py rover1 ${hostname} 7001 ${hostname}:7000,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008 0,1000,999,1999 20 1500 > /tmp/p3/logs/rover1.log &
python3 lib/rover.py rover2 ${hostname} 7002 ${hostname}:7000,${hostname}:7001,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008 0,2000,999,2999 20 1500 > /tmp/p3/logs/rover2.log &
python3 lib/rover.py rover3 ${hostname} 7003 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008 1000,0,1999,999 20 1500 > /tmp/p3/logs/rover3.log &
python3 lib/rover.py rover4 ${hostname} 7004 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008 1000,1000,1999,1999 20 1500 > /tmp/p3/logs/rover4.log &
python3 lib/rover.py rover5 ${hostname} 7005 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7006,${hostname}:7007,${hostname}:7008 1000,2000,1999,2999 20 1500 > /tmp/p3/logs/rover5.log &
python3 lib/rover.py rover6 ${hostname} 7006 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7007,${hostname}:7008 2000,0,2999,999 20 1500 > /tmp/p3/logs/rover6.log &
python3 lib/rover.py rover7 ${hostname} 7007 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7008 2000,1000,2999,1999 20 1500 > /tmp/p3/logs/rover7.log &
python3 lib/rover.py rover8 ${hostname} 7008 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007 2000,2000,2999,2999 20 1500 > /tmp/p3/logs/rover8.log &
