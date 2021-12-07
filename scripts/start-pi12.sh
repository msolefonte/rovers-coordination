#!/usr/bin/env bash

mkdir -p /tmp/p3/logs

python3 src/rover.py rover4 rasp-012 33004 rasp-011:33000,rasp-011:33001,rasp-011:33002,rasp-011:33003,rasp-012:33005,rasp-012:33006,rasp-012:33007,rasp-012:33008,rasp-011:33100 1000,1000,1999,1999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover4.log 2>&1 &
python3 src/rover.py rover5 rasp-012 33005 rasp-011:33000,rasp-011:33001,rasp-011:33002,rasp-011:33003,rasp-012:33004,rasp-012:33006,rasp-012:33007,rasp-012:33008,rasp-011:33100 1000,2000,1999,2999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover5.log 2>&1 &
python3 src/rover.py rover6 rasp-012 33006 rasp-011:33000,rasp-011:33001,rasp-011:33002,rasp-011:33003,rasp-012:33004,rasp-012:33005,rasp-012:33007,rasp-012:33008,rasp-011:33100 2000,0,2999,999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover6.log 2>&1 &
python3 src/rover.py rover7 rasp-012 33007 rasp-011:33000,rasp-011:33001,rasp-011:33002,rasp-011:33003,rasp-012:33004,rasp-012:33005,rasp-012:33006,rasp-012:33008,rasp-011:33100 2000,1000,2999,1999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover7.log 2>&1 &
python3 src/rover.py rover8 rasp-012 33008 rasp-011:33000,rasp-011:33001,rasp-011:33002,rasp-011:33003,rasp-012:33004,rasp-012:33005,rasp-012:33006,rasp-012:33007,rasp-011:33100 2000,2000,2999,2999 20 1500 yuNfEw1IK2DrZTLL8-TJVSG6sLhF0olzo_UZkwgSxQk= 1> /tmp/p3/logs/rover8.log 2>&1 &
