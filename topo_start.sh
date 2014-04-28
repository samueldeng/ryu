#!/bin/python
ryu-manager  --verbose --observe-links \
ryu.topology.switches  \
ryu/app/rest_topology.py  \
ryu/app/ofctl_rest.py \
ryu/topology/hosts_discovery.py \
ryu/app/rest_hosts_discovery.py
