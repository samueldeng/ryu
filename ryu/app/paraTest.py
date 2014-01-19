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


class DataCenterRouter(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(DataCenterRouter, self).__init__(*args, **kwargs)
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

        eg_switch = Switch(self.switches.pop())

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
        ofctl_v1_3.mod_flow_entry(eg_switch.dp, cmds['add'])