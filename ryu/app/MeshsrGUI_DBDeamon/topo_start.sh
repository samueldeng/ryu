#!/bin/bash
bash cleanup_db.sh
ryu-manager --verbose --observe-links ryu.topology.switches ryu.app.ofctl_rest ryu.app.rest_topology ryu/app/diesi_test.py
