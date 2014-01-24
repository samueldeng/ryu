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
from ryu.lib import ofctl_v1_3
from ryu.lib import ofctl_v1_0
import ryu

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER, HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.topology.switches import get_switch, get_link, Switch
from ryu.controller import dpset

LOG = logging.getLogger("DCRouter_Logger")
__author__ = 'Samuel'


class DataCenterRouter(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(DataCenterRouter, self).__init__(*args, **kwargs)
        self.switches = []
        self.links = {}
        self.dpset = {}

        LOG.debug("intitial switches of topology")
        LOG.debug(self.switches)
        LOG.debug("initial links of topology")
        LOG.debug(self.links)
        LOG.debug("initial dpset")
        LOG.debug(self.dpset)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def topology_change_handler(self, ev):
        self.switches = get_switch(self)
        self.links = get_link(self)

        LOG.debug('\n\n\n')
        LOG.debug('show switches of topology')
        LOG.debug(self.switches)
        LOG.debug('\n\n\n')
        LOG.debug('show links of topology')
        links_json = json.dumps([link.to_dict() for link in self.links])
        LOG.debug(links_json)
        LOG.debug('\n\n\n')

        LOG.debug('show switch_foo')
        switch_foo = Switch(self.switches.pop())
        LOG.debug(switch_foo.dp)
        LOG.debug('\n\n\n')

        LOG.debug('show switch_foo.getDPID')
        LOG.debug(type(switch_foo.dp.getDPID()))
        switch_foo_dpid = switch_foo.dp.getDPID()
        LOG.debug(switch_foo_dpid)
        LOG.debug('\n\n\n')

        LOG.debug('show dpset')
        LOG.debug(self.dpset)
        LOG.debug('\n\n\n')

        flow = {
            'table_id': 0,
            'priority': 32768,
            'match': {
                "ipv4_src": '10.0.0.1' #FIXME in ofctl_v1_3 is ipv4_src
            },
            'out_port': 1,
            'actions': [
                {
                    "port": 1,
                    "type": "OUTPUT"
                },
            ],
        }
        cmds = {
            'add': ofproto_v1_3.OFPFC_ADD,
            'modif': ofproto_v1_3.OFPFC_MODIFY,
            'del': ofproto_v1_3.OFPFC_DELETE,
        }
        ofctl_v1_3.mod_flow_entry(self.dpset[switch_foo_dpid], flow ,cmds['add'])

        LOG.debug("succefully execute the mod_flow_entry\n\n\n")

    @set_ev_cls(ryu.controller.dpset.EventDP, HANDSHAKE_DISPATCHER)
    def dpset_maintainer(self, ev):
        dp = ev.dp      #<class 'ryu.controller.controller.Datapath'>
        if ev.enter:
            self.dpset[str(dp.id)] = dp #<class dp.id :int>
        else:
            del self.dpset[str(dp.id)]
