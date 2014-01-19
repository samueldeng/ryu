# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#attention that it should be run under "ryu" e.g., run@run-HP-Pro-3380-MT:~/Documents/ryu/ryu-3.5/ryu$ ryu-manager --verbose --observe-links topology/switches.py app/try_router8.py

import os
import string
import json
import logging

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.controller import Datapath
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.lib import ofctl_v1_3
from ryu.ofproto import ofproto_v1_3
#from ryu.lib import ofctl_v1_0
#from ryu.ofproto import ofproto_v1_0
from ryu.topology.switches import get_switch, get_link, Switch

LOG = logging.getLogger("DCRouter_Logger")
__author__ = 'Samuel'
blueprint = open('app/blueprint', 'w')
devicegraph = open('app/devicegraph', 'w')
#TODO after get dpid_to_label first configure the ip of servers, then add flow entries to switches
k = 4#the parameter of FatTree
half = 0#the parameter of whether the FatTree is only a half


def etac(blueprint, devicegraph):
    etacresult = os.popen('./app/mysaucy app/blueprint app/devicegraph app/result')
    while 1:
        line = etacresult.readline()
        if '' == line:
            break
        print line


def fattree(k, half, dic_label_to_port):
    if half == 0:
        print '\n{(src_label,dst_label):(src_port,dst_port)}\n'
        #edges betweem edge switches and aggregation switches
        print>> blueprint, str((k * k / 2) * 2 + (k * k / 4)) + ' ' + str(
            (k / 2) * (k / 2) * k + (k * k / 4 * k)) + ' 1'
        for i in xrange(k * k / 2):
            for p in xrange(k / 2):
                j = i / (k / 2) * (k / 2) + (k * k / 2) + p
                print>> blueprint, str(i) + ' ' + str(j)
                dic_label_to_port[(i, j)] = (k - 1 - p, i % (k / 2))
                print str(i) + ',' + str(j) + ':' + str(dic_label_to_port[(i, j)])
            #edges between aggregation switches and core switches
        for i in range(k * k / 2, (k * k / 2) * 2):
            for p in xrange(k / 2):
                j = (i - k * k / 2) % (k / 2) * (k / 2) + 2 * (k * k / 2) + p
                print>> blueprint, str(i) + ' ' + str(j)
                dic_label_to_port[(i, j)] = (k - 1 - p, (i - k * k / 2) / (k / 2))
                print str(i) + ',' + str(j) + ':' + str(dic_label_to_port[(i, j)])
            #print '\n{(src_label,dst_label):(src_port,dst_port)}\n'
            #print dic_label_to_port
    else:
        print str((k * k / 2) + (k * k / 8)) + ' ' + str((k / 2) * (k / 2) * (k / 2) + (k * k / 8 * k / 2)) + ' 1'
        for i in xrange(k / 2 * k / 2):
            for p in xrange(k / 2):
                j = i / (k / 2) * (k / 2) + (k / 2 * k / 2) + p
                print>> blueprint, str(i) + ' ' + str(j)
            # edges between half aggregation switches and half core switches
        for i in range(k / 2 * k / 2, (k / 2 * k / 2) * 2):
            if (i - k * k / 4) % (k / 2) >= k / 4:
                continue
            for p in xrange(k / 2):
                j = (i - k * k / 4) % (k / 2) * (k / 2) + 2 * (k * k / 4) + p
                print>> blueprint, str(i) + ' ' + str(j)


def blueprint_label_to_ip(k, dic_label_ip):#use switch ip to calculate the flow entries quickly
    for i in xrange(k):
        for j in xrange(k / 2):
            label = i * k / 2 + j
            ip = '10.' + str(i) + '.' + str(j) + '.1'
            dic_label_ip[
                label] = ip#the label to ip of edge switch (Attention:the servers ip = 10.pod.switch.ID,where ID is the host's position in that subnet (in [2,k/2+1],starting from left to right) so when we know the edge switch ip then we know the ip of servers connected with that edge switch)

            label = k * k / 2 + i * k / 2 + j
            agg = j + k / 2
            ip = '10.' + str(i) + '.' + str(agg) + '.1'
            dic_label_ip[label] = ip#the label to ip of aggregation switch
    for i in xrange(k / 2):
        for j in xrange(k / 2):
            label = k * k + i * k / 2 + j
            ip = '10.' + str(k) + '.' + str(i + 1) + '.' + str(j + 1)
            dic_label_ip[label] = ip#the label to ip of core switch
    print '\nlabel of switches in blueprint : ip of switches in blueprint\n'
    print dic_label_ip


def blueprint_ports_to_devicegraph_ports(bports_to_dports, label_to_port, dpid_to_port, dpid_to_label):
    for i in dpid_to_port:
        dsrc = i[0]
        ddst = i[1]
        dport = dpid_to_port[i]
        bsrc = dpid_to_label[dsrc]
        bdst = dpid_to_label[ddst]
        bport = label_to_port[(bsrc, bdst)]
        bports_to_dports[(bsrc, bport[0])] = (dsrc, dport[0])
        bports_to_dports[(bdst, bport[1])] = (ddst, dport[1])
    print '{(blueprint_switch_label,port):(dpid,port)}'
    print bports_to_dports


class DataCenterRouter(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(DataCenterRouter, self).__init__(*args, **kwargs)
        self.switches = []
        self.links = {}
        #add a list to save the number (0,1,...) of dpids
        self.nums_to_dpids = {}
        self.dpids_to_nums = {}
        self.label_to_ip = {}# {the label of switch in bluprint(fattree) : the ip of switch in blueprint}
        self.dpid_to_port = {}# {(src_dpid,dst_dpid):(src_port,dst_port)}use src dpid and dst dpid to check their connecting ports number
        self.label_to_port = {}# {(src_label,dst_label):(src_port,dst_port)}
        self.dpid_to_label = {}# {dpid,label} use the induced subgraph isomorphic algorithm (ETAC,program with c) to get the corresponding nodes between devicegraph(dpid) and blueprint(label)
        self.label_to_dpid = {}
        self.bports_to_dports = {}#{(blueprint_switch_label,port):(dpid,port)}
        # self.switches = get_switch(self)
        # self.links = get_link(self)

        LOG.debug("intitial switches of topology")
        LOG.debug(self.switches)
        LOG.debug("initial links of topology")
        LOG.debug(self.links)
        fattree(k, half, self.label_to_port)
        blueprint_label_to_ip(k, self.label_to_ip)
        blueprint.flush()

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def topology_change_handler(self, ev):
        self.switches = get_switch(self)
        self.links = get_link(self)
        #convert the links (src,dst) to the graph (with 0,1,.. label of switches)
        graph = []
        n = len(self.switches)
        m = len(self.links)
        print str(n) + ' ' + str(m / 2) + ' 1'
        print>> devicegraph, str(n) + ' ' + str(
            m / 2) + ' 1'#TODO self.links seems two-way e.g.,(1,0),(0,1) , but if it may have the possible of only (1,0) ????
        for i in xrange(n):
            graph.append([])
            for j in xrange(n):
                graph[i].append(0)
        startnum = 0
        print 'dpids nums:'
        for switch in self.switches:
            # make the dpid to 0,1,...the number of switch, then print the links use 0,1,... without repeated edges
            self.nums_to_dpids[startnum] = switch.dp.id
            self.dpids_to_nums[switch.dp.id] = startnum
            print str(switch.dp.id) + ' ' + str(startnum)
            #print>>devicegraph,str(switch.dp.id)+' '+str(startnum)
            startnum = startnum + 1
        print 'edges:'
        for link in self.links:
            srcnum = self.dpids_to_nums[link.src.dpid]
            dstnum = self.dpids_to_nums[link.dst.dpid]
            if graph[srcnum][dstnum] == 0 and graph[dstnum][srcnum] == 0:
                print str(srcnum) + ' ' + str(dstnum)
                #print 'ports:'+str(link.src.port_no)+' '+str(link.dst.port_no)
                self.dpid_to_port[(link.src.dpid, link.dst.dpid)] = (
                link.src.port_no, link.dst.port_no)#TODO may we can get the port_no use self.links directly ???
                #print 'src:'+str(link.src.dpid)+'dst:'+str(link.dst.dpid)+'->ports:'+str(self.dpid_to_port[(link.src.dpid,link.dst.dpid)])
                print>> devicegraph, str(srcnum) + ' ' + str(dstnum)
                graph[srcnum][dstnum] = 1
        devicegraph.flush()
        print '{(src_dpid,dst_dpid):(src_port,dst_port)}'
        print self.dpid_to_port
        #end convert
        #use the induced subgraph isomorphic algorithm (ETAC,program with c) to get the corresponding nodes between devicegraph(dpid) and blueprint(label)
        etac(blueprint, devicegraph)
        result = open('app/result', 'r')
        line = result.readline()
        print line
        while 1:
            line = result.readline()
            if '' == line:
                break
            numline = line.split()
            #print numline[0]
            #print str(self.nums_to_dpids[int(numline[0])])
            self.dpid_to_label[self.nums_to_dpids[int(numline[0])]] = int(numline[1])
            self.label_to_dpid[int(numline[1])] = self.nums_to_dpids[int(numline[0])]
            #print str(self.nums_to_dpids[int(numline[0])])+' '+str(self.dpid_to_label[self.nums_to_dpids[int(numline[0])]])
            print line
        print 'dpid:label'
        print self.dpid_to_label
        print 'label:dpid'
        print self.label_to_dpid
        blueprint_ports_to_devicegraph_ports(self.bports_to_dports, self.label_to_port, self.dpid_to_port,
                                             self.dpid_to_label)
        #end etac
        LOG.debug('show switches of topology')
        LOG.debug(self.switches)
        LOG.debug('\n\n\n\n\n\n')
        LOG.debug('show links of topology')
        links_json = json.dumps([link.to_dict() for link in self.links])
        LOG.debug(links_json)

        # compute the shorthes path and add flow entry to dp.
        # eg, there should be add a new flow entry.

        eg_switch = Switch(self.switches.pop())
        print type(eg_switch.dp)
        flow = {
            # default value.
            'cookie': 0,
            'cookie_mask': 0,
            'table_id': 0,
            'idle_timeout': 0,
            'hard_timeout': 0,
            'priority': 0,
            'buffer_id': ofproto_v1_3.OFP_NO_BUFFER,
            'out_port': ofproto_v1_3.OFPP_ANY,
            'out_group': ofproto_v1_3.OFPG_ANY,
            'flags': 0,
            'match': {},
            'action': [],
        }
        cmds = {
            'add': ofproto_v1_3.OFPFC_ADD,
            'modif': ofproto_v1_3.OFPFC_MODIFY,
            'del': ofproto_v1_3.OFPFC_DELETE,
            'modif_s': ofproto_v1_3.OFPFC_MODIFY_STRICT,
            'del_s': ofproto_v1_3.OFPFC_DELETE_STRICT,
        }
        ofctl_v1_3.mod_flow_entry(eg_switch.dp, flow, cmds['add'])

        # Another Method to modify the flow..
        # Datapath(eg_switch.dp).ofproto_parser.OFPFlowMod(eg_switch.dp, cookie, cookie_mask,
        #                                 table_id, ofp.OFPFC_ADD,
        #                                 idle_timeout, hard_timeout,
        #                                 priority, buffer_id,
        #                                 ofp.OFPP_ANY, ofp.OFPG_ANY,
        #                                 ofp.OFPFF_SEND_FLOW_REM,
        #                                 match, inst)

        # TODO add meter table entry.
