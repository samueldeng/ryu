from ryu.base import app_manager
from ryu.topology import event
from ryu.controller.controller import Datapath
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import ofctl_v1_3
from ryu.ofproto import ofproto_v1_3
from ryu.lib import ofctl_v1_0
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.mac import haddr_to_bin
from ryu.lib.ip import ipv4_to_str
from ryu.lib.ip import ipv4_to_bin
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.topology.switches import Switch
from ryu.topology.api import get_switch


class SendPkt(app_manager.RyuApp):
    OFP_VERSIONS = {ofproto_v1_3.OFP_VERSION}

    def __init__(self, *args, **kwargs):
        super(SendPkt, self).__init__(*args, **kwargs)

    def pkt_out(self, datapath, pkt, port=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        data = pkt.data
        if port != None:
            out_port = port
        else:
            out_port = ofproto.OFPP_FLOOD
        actions = [parser.OFPActionOutput(out_port)]
        print "pkt-out!"
        print "port:", out_port
        print "pkt:", data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        print 'switch entrying'
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        # print 'add flow!!!!!!!!!!!!!!!'
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        idle_timeout = 600
        hard_timeout = 10
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    def sendpkt(self, dpid, pkt, port=None):
        srcip = pkt['srcip']
        dstip = pkt['dstip']
        srcport = pkt['srcport']
        dstport = pkt['dstport']
        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(ethertype=2048))
        # pkt.add_protocol(ethernet.ethernet(ethertype=2048,src='11:22:33:44:55:66',dst='11:22:33:44:55:66'))
        # proto=6  tcp; proto=17  udp
        pkt.add_protocol(ipv4.ipv4(proto=6, src=srcip, dst=dstip))
        #pkt.add_protocol(udp.udp(src_port=srcport,dst_port=dstport))
        pkt.add_protocol(tcp.tcp(src_port=srcport, dst_port=dstport))
        datapath = get_switch(self, dpid)[0].dp
        self.pkt_out(datapath, pkt, port)

    # Main
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def pkt_in(self, ev):
        pkt = {}
        pkt['srcip'] = '10.0.0.1'
        pkt['dstip'] = '10.0.0.2'
        pkt['srcport'] = 1234
        pkt['dstport'] = 2345
        self.sendpkt(1, pkt)
