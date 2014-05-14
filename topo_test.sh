#!/bin/python
ryu-manager  --verbose --observe-links \
ryu.topology.switches  \
ryu/app/rest_topology.py  \
ryu/app/ofctl_rest.py
