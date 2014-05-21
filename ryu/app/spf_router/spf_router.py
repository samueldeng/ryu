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
import json
import logging
import urllib2

LOG = logging.getLogger("SPF_Router_App")
REST_SERVER_ADDR = 'http://localhost:8080'
LINK_CAPACITY = 100  # count Bps

ap_dpids = {
    '0003': "192.168.1.0/24",
    '0004': "192.168.2.0/24",
    '0005': "192.168.3.0/24",
}
all_to_all_flow_entry = {
    ('0003', '0004'): [],
    ('0004', '0003'): [],
    ('0003', '0005'): [],
    ('0005', '0003'): [],
    ('0004', '0005'): [],
    ('0005', '0004'): [],
}

MAX_PORTS_NUM = 4
ALL_PORTS = "*"


class Port(object):
    def __init__(self, dpid=0, port_no=0, hw_addr='F'):
        """

        :param dpid: int
        :param port_no: int
        :param hw_addr: str
        """
        super(Port, self).__init__()
        self.dpid = int(dpid)
        self.port_no = int(port_no)
        self.hw_addr = str(hw_addr)


class Link(object):
    def __init__(self, src, dst, attr=None):
        """

        :param src: Port()
        :param dst: Port()
        :param attr: str
        """
        super(Link, self).__init__()
        self.src_port = src
        self.dst_port = dst
        self.attr = attr

    def __eq__(self, other):
        if self.src_port == other.src_port and self.dst_port == other.dst_port and self.attr == other.attr:
            return True
        else:
            return False


class Links(list):
    def __init__(self):
        """
            Save Link in Links

        """
        super(Links, self).__init__()

    def get_dps_conn(self):
        dps_conn = list(tuple(int, int, str))

        for link in self:
            src_port = link.src_port
            dst_port = link.dst_port
            dps_conn.append(src_port.dpid, dst_port.dpid, link.attr)

        return dps_conn

    def get_peer_port_no(self, dpid, peer_dpid):
        for link in self:
            src_port = link.src_port
            dst_port = link.dst_port
            if src_port.dpid == dpid and dst_port.dpid == dst_port:
                return dst_port.port_no
        LOG.error("ERROR to find the link")
        return None


def update_link_util(links):
    try:
        for link in links:
            response_ports = urllib2.urlopen(REST_SERVER_ADDR + '/stats/port/' + link.src_port.dpid).read()
            ports_json = json.loads(response_ports)[link.src_port.dpid]

            for port_info in ports_json:
                port_no = port_info["port_no"]
                if port_no == link.src_port.port_no:
                    tx_bytes = port_info["tx_bytes"]
                    rx_bytes = port_info["rx_packets"]
                    link.attr = str((tx_bytes + rx_bytes) / float(LINK_CAPACITY))
                    break
    except Exception, e:
        LOG.error(e)


def update_topo(prev_links):
    try:
        response_links = urllib2.urlopen(REST_SERVER_ADDR + '/v1.0/topology/links').read()
        links_json = json.loads(response_links)

        exist_flags = list()
        # Add some links
        for i in range(0, len(links_json) - 1):
            src = links_json[i]['src']
            dst = links_json[i]['dst']

            src_dpid = src['dpid'].encode()
            src_port_no = src['port_no'].encode()
            src_hw_addr = src['hw_addr'].encode()
            dst_dpid = dst['dpid'].encode()
            dst_port_no = dst['port_no'].encode()
            dst_hw_addr = dst['hw_addr'].encode()

            src_port = Port(src_dpid, src_port_no, src_hw_addr)
            dst_port = Port(dst_dpid, dst_port_no, dst_hw_addr)

            l = Link(src_port, dst_port)
            # TODO override equal method. or it compare the ref.
            if l not in prev_links:
                prev_links.append(l)
            else:
                exist_flags.append(i)

        # delete some disconnected links.
        for i in exist_flags:
            prev_links.remove(prev_links[i])

        # update the link usage.
        update_link_util(prev_links)

    except Exception, e:
        LOG.error(e)


class FlowEntry(object):
    def __init__(self, dpid, match, action):
        super(FlowEntry, self).__init__()
        self.dpid = dpid
        self.match = match
        self.action = action

    def convert_to_json(self):
        if self.is_port_num(self.match):
            match = {"in_port": self.match}
            action = {"port": self.action, "type": "OUTPUT"}
            dpid = self.dpid

            flow_entry = {
                "dpid": dpid,
                "cookie": "0",
                "priority": "1111",
                "match": match,
                "actions": action,
            }
            return json.dumps(flow_entry)

        elif self.is_nw_addr(self.match):
            match = {"dl_type": 2048, "nw_src": self.match}
            action = {"port": self.action, "type": "OUTPUT"}
            dpid = self.dpid

            flow_entry = {
                "dpid": dpid,
                "cookie": "0",
                "priority": "1111",
                "match": match,
                "actions": action,
            }
            return json.dumps(flow_entry)
        else:
            LOG.error("Fatal Bug, wrong match format")
            return None

    @staticmethod
    def is_nw_addr():
        # TODO validate self.match as a network field match like 192.168.1.0/24
        return True

    def is_port_num(self):
        if str(self.match).isdigit() and int(self.match) <= MAX_PORTS_NUM:
            return True
        else:
            LOG.error("EXCEED MAX_PORTS_NUM In DP")
            return False


def generate_flow_entry(optimal_path, topo):
    flow_entries_json = list()

    # for the source access switch.
    match_field = ap_dpids[optimal_path[0]]
    out_port = topo.__get_peer_port_no(optimal_path[0], optimal_path[1])
    flow_entry = FlowEntry(optimal_path[0], match_field, out_port)
    flow_entries_json.append(flow_entry.convert_to_json())

    # for the core switch.
    for i in range(1, len(optimal_path) - 2):
        link = tuple(optimal_path[i], optimal_path[i + 1])
        match_filed = topo.__get_peer_port_no(tuple[0], optimal_path[i - 1])
        out_port = topo.__get_peer_port_no(link[0], link[1])
        flow_entry = FlowEntry(optimal_path[i], match_field, out_port)
        flow_entries_json.append(flow_entry.convert_to_json())

    # for the destination access switch.
    match_field = topo.__get_peer_port_no(optimal_path[len(optimal_path) - 2], optimal_path[len(optimal_path) - 1])
    out_port = ALL_PORTS
    flow_entry = FlowEntry(optimal_path[len(optimal_path) - 1], match_field, out_port)
    flow_entries_json.append(flow_entry.convert_to_json())

    return flow_entries_json


def push_to_switch(flow_entry):
    LOG.debug(flow_entry)
    try:
        req = urllib2.Request(REST_SERVER_ADDR + '/stats/flowentry/add')
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, flow_entry)
        LOG.debug(response)
    except Exception, e:
        LOG.error(e)


def conv_adj_list(links):
    """
    convert a bi-direction link list to a adj_list
    :param links: list(int:src_dpid, int:dst_dpid, str:attr) bi-direction
    """
    graph = dict()
    for link in links:
        src_node = link[0]
        dst_node = link[1]
        ava_bandwidth = float(link[2])

        if not graph.has_key(src_node):
            graph[src_node] = list()
        graph[src_node].append(dst_node)
    return graph


def gen_path_from_prev(prev, src_ap, dst_ap):
    path = list()
    path.append(dst_ap)
    curr = dst_ap
    while curr != src_ap:
        path.append(prev[curr])
        curr = prev[curr]
    return [node for node in reversed(path)]


def spf_path(dp_conn, src_ap, dst_ap):
    """

    :param dp_conn: list(int:src_dpid, int:dst_dpid, str:attr)
    :param src_ap: int
    :param dst_ap: int
    """
    graph = conv_adj_list(dp_conn)
    dist, prev = shortest_path(graph, src_ap, dp_conn)
    path = gen_path_from_prev(prev, src_ap, dst_ap)
    return path


def get_weight(u, v, weight):
    """

    :param u:
    :param v:
    :param weight: list(int:src_dpid, int:dst_dpid, str:attr)
    """
    try:
        for dp_conn in weight:
            if dp_conn[0] == u and dp_conn[1] == v:
                return dp_conn[2]
    except Exception, e:
        LOG.error("***********FUCK*********")
        LOG.error("***********FUCK*********")
        LOG.error("***********FUCK*********")
        LOG.error("***********FUCK*********")


def shortest_path(graph, source_node, weight):
    dist = {source_node: 0}
    previous = {}
    queue = graph.get_all_nodes()  # queue could be a list.

    while queue:
        # find vertex u in Queue with smallest distance in dist[]
        u = queue[0]
        for node in queue[1:]:
            if (   (not dist.has_key(u))
                   or (dist.has_key(node) and dist[node] < dist[u]) ):
                u = node
        queue.remove(u)

        # Process reachable, remaining nodes from u
        for v in graph.get_neighbor(u):
            if v in queue:
                alt = dist[u] + get_weight(u, v, weight)
                if (not dist.has_key(v)) or (alt < dist[v]):
                    dist[v] = alt
                    previous[v] = u
    return dist, previous


def main():
    links = Links()

    while True:
        update_topo(links)
        dp_conn = links.get_dps_conn()
        for (src_ap, dst_ap), flow_entries_on_wire in all_to_all_flow_entry:
            optimized_path = spf_path(dp_conn, src_ap, dst_ap)
            curr_flow_entries = generate_flow_entry(optimized_path, links)

            if curr_flow_entries.__eq__(flow_entries_on_wire):
                continue
            for flow_entry in curr_flow_entries:
                all_to_all_flow_entry[(src_ap, dst_ap)] = curr_flow_entries
                # TODO delete previous flow entry.
                # push_to_switch(flow_entry)


if __name__ == main():
    main()
