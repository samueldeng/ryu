# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
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


import logging
import time
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.topology import eventHosts
from ryu.lib import hub
from ryu.topology.api import get_all_switch, get_all_link

LOG = logging.getLogger(__name__)


class HostDiscovery(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _EVENTS = []

    MAX_TIMEOUT = 60
    CLEAN_PERIOD = 60
    UPDATE_TOPO_PERIOD = 3

    def __init__(self, *args, **kwargs):
        super(HostDiscovery, self).__init__(*args, **kwargs)
        self.name = 'HostDiscovery'
        self.all_dps_mac_addr = []
        # {(int$dpid,int$in_port):(str$mac_addr_src,float$host_lastest_conn)}
        self.hosts_loc = {}

        self.topo_dps_mac = []
        self.topo_links = []

        # TODO the hosts_loc is a shared variable.
        self.timeout_event = hub.Event()
        self.get_topology_event = hub.Event()
        self.threads.append(hub.spawn(self.host_conn_timeout_loop))
        self.threads.append(hub.spawn(self.topology_loop))

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    @staticmethod
    def add_flow(datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath

        dpid = datapath.id  # int
        in_port_no = msg.match['in_port']  # int

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        mac_addr_src = eth.src  # str
        mac_addr_dst = eth.dst  # str

        LOG.debug("packet in dpid=%s in_port=%s FROM:%s TO:%s", dpid, in_port_no, mac_addr_src, mac_addr_dst)

        # TODO abstract the algorithm using strategy design pattern.
        if self.topo_dps_mac == [] or self.topo_links == []:
            return

        if mac_addr_src not in self.topo_dps_mac:
            LOG.debug(mac_addr_src)
            if self.is_direct_from_host(dpid, in_port_no):
                time_now = time.time()
                self.hosts_loc[(dpid, in_port_no)] = (mac_addr_src, time_now)

                LOG.debug(self.hosts_loc)


    def host_conn_timeout_loop(self):
        while True:
            host_expire = []
            for (key, value) in self.hosts_loc.items():
                time_latest_conn = value[1]
                now = time.time()
                # LOG.debug(str(key) + ':' + str(now - time_latest_conn))
                if now - time_latest_conn > self.MAX_TIMEOUT:
                    host_expire.append(key)
            for host in host_expire:
                self.hosts_loc.pop(host)

            self.timeout_event.wait(self.CLEAN_PERIOD)

    def topology_loop(self):
        while True:
            switches = get_all_switch(self)  # [switches.Switch obj,]
            # LOG.debug(switches)
            all_switches_mac_addr = []
            for switch in switches:
                ports = switch.ports  # list
                for port in ports:
                    # LOG.debug(port.hw_addr)  # switches.Port
                    all_switches_mac_addr.append(port.hw_addr)

            self.topo_dps_mac = all_switches_mac_addr
            # LOG.debug(self.topo_dps_mac)
            self.topo_links = get_all_link(self)
            # LOG.debug(self.topo_links)

            self.get_topology_event.wait(self.UPDATE_TOPO_PERIOD)

    def is_direct_from_host(self, dpid, in_port_no):
        links = self.topo_links  # {switches.Link obj:timestamp}
        if self.is_in_links((dpid, in_port_no), links):
            return False
        else:
            return True

    @staticmethod
    def is_in_links(port, all_links):
        for link in all_links:
            # LOG.debug(type(link))
            link_src = link.src  # switches.Port
            link_dst = link.dst  # switches.Port

            src_port = (link_src.dpid, link_src.port_no)  # (int, int)
            dst_port = (link_dst.dpid, link_dst.port_no)

            if port == src_port or port == dst_port:
                return True
        return False


    @set_ev_cls(eventHosts.EventHostsRequest)
    def hosts_request_handler(self, req):
        # LOG.debug(req)
        hosts = []
        # {(int$dpid,int$in_port):(str$mac_addr_src,float$time_incoming)}
        # to
        # { "(" dpid ":" port ")" :str$nic_mac_addr}
        for (key, value) in self.hosts_loc.items():
            dpid = str(key[0])
            in_port_num = str(key[1])
            peer_mac_addr = str(value[0])
            hosts.append(dict(dpid=dpid, port_no=in_port_num, peer_mac=peer_mac_addr))

        rep = eventHosts.EventHostsReply(req.src, hosts)
        self.reply_to_request(req, rep)


def get_hosts(app):
    request = eventHosts.EventHostsRequest()
    # LOG.debug(request)
    rep = app.send_request(request)
    return rep.hosts