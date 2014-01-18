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

import json
import logging

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.controller import Datapath
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER
from ryu.lib import ofctl_v1_3
from ryu.ofproto import ofproto_v1_3
from ryu.topology.switches import get_switch, get_link, Switch

LOG = logging.getLogger("DCRouter_Logger")
__author__ = 'Samuel'


DPid_IP = {'1':'10.0.0.1',
           '2':'10.0.1.1',
           '3':'10.1.0.1',
           '4':'10.1.1.1',
           '5':'10.0.2.1',
           '6':'10.0.3.1',
           '7':'10.1.2.1',
           '8':'10.1.3.1',
           '9':'10.2.1.1',
           '10':'10.2.1.2'}
  
    
    
class DataCenterRouter(app_manager.RyuApp):
 
    def __init__(self, * args, ** kwargs):
        super(DataCenterRouter, self).__init__(* args, ** kwargs)
        self.switches = []
        self.links = {}

        # self.switches = get_switch(self)
        # self.links = get_link(self)

        LOG.debug("intitial switches of topology")
        LOG.debug(self.switches)
        LOG.debug("initial links of topology")
        LOG.debug(self.links)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def topology_change_handler(self, ev):
        self.switches = get_switch(self)
        self.links = get_link(self)

        LOG.debug('show switches of topology')
        LOG.debug(self.switches)
        LOG.debug('\n\n\n\n\n\n')
        LOG.debug('show links of topology')
        links_json = json.dumps([link.to_dict() for link in self.links])
        LOG.debug(links_json)

        # compute the shorthes path and add flow entry to dp.
        # eg, there should be add a new flow entry.
    def Switch_routing(self,DPid_IP):
        while len(self.switches)>0:
            eg_switch = Switch(self.switches.pop())
            eg_switch_dpid = eg_switch.id
            eg_switch_dpno = hex2dec(str(eg_switch_dpid))
            eg_switch_IP = DPid_IP.get(eg_switch_dpno)
            IP_seg = eg_switch_IP.split('.')
            pod_x = IP_seg[1]
            switch_z = IP_seg[2]
            if pod_x in range(0,1) and switch_z in range(2,3):
                '''Aggregate'''
                Aggregation_switch_routing(eg_switch,pod_x,switch_z)
            elif pod_x == 2 :
                '''core'''
                Core_switch_routing(eg_switch)
            else:
                '''edge'''
                Edge_switch_routing(eg_switch,pod_x,switch_z)
            
        
    def Add_Flow(self,eg_switch,forward_IP,next_hop):
        
        flow = {
            # FIXME must modif the default value or the flow entry will be useless.
            'cookie': 0,
            'cookie_mask': 0,
            'table_id': 0,
            'idle_timeout':0,
            'hard_timeout':0,
            'priority':0,
            'buffer_id':ofproto_v1_3.OFP_NO_BUFFER,
            'out_port':ofproto_v1_3.OFPP_ANY,
            'out_group':ofproto_v1_3.OFPG_ANY,
            'flags':0,
            'match': {
                "ipv4_src":forward_IP
            },
            'action':[
                {
                    "port": 2,
                    ## FIXME here must be used the port but the next hop
                    "type": "OUTPUT"
                },
                {
                    "table_id": 1,
                    "type": "GOTO_TABLE"
                }
            ],
        }
        cmds={
            'add':ofproto_v1_3.OFPFC_ADD,
            'modif':ofproto_v1_3.OFPFC_MODIFY,
            'del':ofproto_v1_3.OFPFC_DELETE,
            'modif_s':ofproto_v1_3.OFPFC_MODIFY_STRICT,
            'del_s':ofproto_v1_3.OFPFC_DELETE_STRICT,
        }
        ofctl_v1_3.mod_flow_entry(eg_switch.dp,flow,cmds['add'])

def Aggregation_switch_routing(eg_switch, pod_x, switch_z):
    for subnet_i in range(0,1):
        '''
        switch_IP = '10.'+ str(pod_x) +'.' + str(switch_z) + '.' '1'
        switch_dp = [i for i in DPid_IP.keys() if DPid_IP[i] == switch_IP]
        switch_dpno = switch_dp[0]
        '''
        forward_IP = '10.' + str(pod_x) + '.' + str(subnet_i) + '.0/24'
        next_hop = str(subnet_i)
        DataCenterRouter.Add_Flow(eg_switch, forward_IP, next_hop)
    for hostID_i in range(2,3):
        forward_IP = '0.0.0.'+ str(hostID_i) +'/8'
        next_hop = str((hostID_i-2+switch_z)%2 + 2)
        DataCenterRouter.Add_Flow(eg_switch, forward_IP, next_hop)
        
def Core_switch_routing(eg_switch):
    for destination_pod_x in range(0,1):
        forward_IP = '10.' + str(destination_pod_x) + '.0.0/16'
        next_hop = str(destination_pod_x)
        DataCenterRouter.Add_Flow(eg_switch, forward_IP, next_hop)
        
def Edge_switch_routing(eg_switch,pod_x, switch_z):
    for server_i in range(2,3):
        forward_IP = '10.' + str(pod_x) + '.' + str(switch_z) + '.' + str(server_i)
        next_hop = str(server_i - 2)
        DataCenterRouter.Add_Flow(eg_switch, forward_IP, next_hop)
    for server_j in range(2,3):
        forward_IP = '10.' + str(pod_x) + '.' + str((switch_z+1)%2) + '.'+ str(server_j)
        if (switch_z+1)%2 == 1:
            next_hop = str(2)
        else:
            next_hop = str(3)
        DataCenterRouter.Add_Flow(eg_switch, forward_IP, next_hop)
    for server_k in range(2,3 ):
        forward_IP = '0.0.0.'+ str(server_k) +'/8'
        if switch_z == 0:
            next_hop = 3
        elif switch_z ==1:
            next_hop = 2
        DataCenterRouter.Add_Flow(eg_switch, forward_IP, next_hop)                
# hex2dec
# 16  to 10
def hex2dec(string_num):
    return str(int(string_num.upper(), 16))