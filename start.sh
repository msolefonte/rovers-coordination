#!/usr/bin/env bash
#mkdir -p /tmp/p3/logs
hostname=$(hostname -I | awk '{print $1}')
#hostname='LAPTOP-C2621QF2'
python3 lib/Srover.py rover0 ${hostname} 7000 ${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 0,0,999,999 20 1500  &
python3 lib/Srover.py rover1 ${hostname} 7001 ${hostname}:7000,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 0,1000,999,1999 20 1500 1 &
python3 lib/Srover.py rover2 ${hostname} 7002 ${hostname}:7000,${hostname}:7001,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 0,2000,999,2999 20 1500 1 &
python3 lib/Srover.py rover3 ${hostname} 7003 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 1000,0,1999,999 20 1500 1 &
python3 lib/Srover.py rover4 ${hostname} 7004 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 1000,1000,1999,1999 20 1500 1 &
python3 lib/Srover.py rover5 ${hostname} 7005 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7006,${hostname}:7007,${hostname}:7008,${hostname}:7100 1000,2000,1999,2999 20 1500 1 &
python3 lib/Srover.py rover6 ${hostname} 7006 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7007,${hostname}:7008,${hostname}:7100 2000,0,2999,999 20 1500 1 &
python3 lib/Srover.py rover7 ${hostname} 7007 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7008,${hostname}:7100 2000,1000,2999,1999 20 1500 1 &
python3 lib/Srover.py rover8 ${hostname} 7008 ${hostname}:7000,${hostname}:7001,${hostname}:7002,${hostname}:7003,${hostname}:7004,${hostname}:7005,${hostname}:7006,${hostname}:7007,${hostname}:7100 2000,2000,2999,2999 20 1500 1 &

python3 lib/SnetworkVisualizer.py network-visualizer ${hostname} 7100 0 0 1 &
