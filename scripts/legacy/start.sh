#!/usr/bin/env bash

mkdir -p /tmp/p3/logs

python3 lib/coordinator.py localhost 7000 localhost:7001,localhost:7002 > /tmp/p3/logs/c0.log &
python3 lib/coordinator.py localhost 7001 localhost:7002,localhost:7000 > /tmp/p3/logs/c1.log &
python3 lib/coordinator.py localhost 7002 localhost:7000,localhost:7001 > /tmp/p3/logs/c2.log &
python3 lib/peer.py node0 localhost 9000 localhost:7000,localhost:7001,localhost:7002 node1,node2 > /tmp/p3/logs/p0.log &
python3 lib/peer.py node1 localhost 9001 localhost:7000,localhost:7001,localhost:7002 node2,node3 > /tmp/p3/logs/p1.log &
python3 lib/peer.py node2 localhost 9002 localhost:7000,localhost:7001,localhost:7002 node3,node4 > /tmp/p3/logs/p2.log &
python3 lib/peer.py node3 localhost 9003 localhost:7000,localhost:7001,localhost:7002 node4,node5 > /tmp/p3/logs/p3.log &
python3 lib/peer.py node4 localhost 9004 localhost:7000,localhost:7001,localhost:7002 node5,node6 > /tmp/p3/logs/p4.log &
python3 lib/peer.py node5 localhost 9005 localhost:7000,localhost:7001,localhost:7002 node6,node7 > /tmp/p3/logs/p5.log &
python3 lib/peer.py node6 localhost 9006 localhost:7000,localhost:7001,localhost:7002 node7,node0 > /tmp/p3/logs/p6.log &
python3 lib/peer.py node7 localhost 9006 localhost:7000,localhost:7001,localhost:7002 node0,node1 > /tmp/p3/logs/p7.log &
