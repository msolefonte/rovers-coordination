#!/usr/bin/env bash

mkdir -p /tmp/p3/logs

python3 src/rover.py rover0 rasp-011 33000 rasp-011:33001,rasp-011:33002,rasp-011:33003,rasp-012:33004,rasp-012:33005,rasp-012:33006,rasp-012:33007,rasp-012:33008,rasp-011:33100 0,0,999,999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover0.log 2>&1 &
python3 src/rover.py rover1 rasp-011 33001 rasp-011:33000,rasp-011:33002,rasp-011:33003,rasp-012:33004,rasp-012:33005,rasp-012:33006,rasp-012:33007,rasp-012:33008,rasp-011:33100 0,1000,999,1999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover1.log 2>&1 &
python3 src/rover.py rover2 rasp-011 33002 rasp-011:33000,rasp-011:33001,rasp-011:33003,rasp-012:33004,rasp-012:33005,rasp-012:33006,rasp-012:33007,rasp-012:33008,rasp-011:33100 0,2000,999,2999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover2.log 2>&1 &
python3 src/rover.py rover3 rasp-011 33003 rasp-011:33000,rasp-011:33001,rasp-011:33002,rasp-012:33004,rasp-012:33005,rasp-012:33006,rasp-012:33007,rasp-012:33008,rasp-011:33100 1000,0,1999,999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover3.log 2>&1 &

python3 src/networkVisualizer.py network-visualizer rasp-011 33100 0 0 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/network-visualizer.log 2>&1 &
