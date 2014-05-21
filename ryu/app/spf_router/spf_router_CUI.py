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
from sys import stdin
import urllib2
import time

LOG = logging.getLogger("spf_router_cui")
LOG.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
LOG.addHandler(ch)

REST_SERVER_ADDR = 'http://localhost:8080'
LINK_CAPACITY = 100  # count Bps
DEFAULT_ACCESS_PORT = "3"
MAX_PORTS_NUM = 10
WAIT_TIME_WAIT_PORTS_ADD = 1


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

    def __eq__(self, other):
        return True \
            if self.dpid == other.dpid and \
               self.port_no == other.port_no and \
               self.hw_addr == other.hw_addr \
            else \
            False

    def __str__(self):
        return "dpid:" + str(self.dpid) + " port:" + str(self.port_no)


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
        if self.src_port == other.src_port and self.dst_port == other.dst_port:
            return True
        else:
            return False

    def __str__(self):
        return "(" + str(self.src_port) + ")" + "   --------------->   " + "(" + str(self.dst_port) + ")" + "  Load:" + str(
            int(float(self.attr) * 8)) + " (Bps)"


class Topology(list):
    def __init__(self):
        """
            Save Link Object in list

        """
        super(Topology, self).__init__()

    def __get_dps_conn(self):
        dps_conn = list()

        for link in self:
            src_port = link.src_port
            dst_port = link.dst_port
            dps_conn.append((src_port.dpid, dst_port.dpid, link.attr))

        return dps_conn

    def __get_peer_port_no(self, dpid, peer_dpid):
        try:
            for link in self:
                src_port = link.src_port
                dst_port = link.dst_port
                if src_port.dpid == dpid and dst_port.dpid == peer_dpid:
                    return dst_port.port_no
            LOG.error("ERROR to find the link")
            return None

        except Exception, e:
            LOG.error(e)
            return None

    def get_spf_path(self, src_dpid, dst_dpid, req_bandwidth):

        """
        generate the shortest path from src to dst switch.

        :param src_dpid: int
        :param dst_dpid: int
        :param req_bandwidth: float
        :return a list from src_dpid to dst_dpid, element in list is a int.
        """
        dp_conn = self.__get_dps_conn()
        adj_list = self.__conv_adj_list(dp_conn)
        # add dp_conn to get weight from the data structure.
        dist, prev_list = self.__shortest_path(adj_list, src_dpid, dp_conn)
        path = self.__get_path_from_prev(prev_list, src_dpid, dst_dpid)
        return path

    def get_flow_entries_rest(self, match, optimal_path):
        flow_entries_json = list()

        for i in range(0, len(optimal_path) - 1):
            link_ports_peers = (optimal_path[i], optimal_path[i + 1])
            match_field = match
            out_port = self.__get_peer_port_no(link_ports_peers[0], link_ports_peers[1])
            flow_entry = FlowEntry(optimal_path[i], match_field, out_port)
            flow_entries_json.append(flow_entry.convert_to_json())

        # for the destination access switch.
        match_field = match
        out_port = DEFAULT_ACCESS_PORT
        flow_entry = FlowEntry(optimal_path[len(optimal_path) - 1], match_field, out_port)
        flow_entries_json.append(flow_entry.convert_to_json())

        return flow_entries_json

    @staticmethod
    def __conv_adj_list(dp_conn):
        """
        convert a bi-direction link list to a adj_list
        :param dp_conn: list(int:src_dpid, int:dst_dpid, str:attr) bi-direction
        :return just like {"001":["002","003"]}
        """
        adj_list = dict()
        for link in dp_conn:
            src_node = link[0]
            dst_node = link[1]
            ava_bandwidth = float(link[2])

            if not adj_list.has_key(src_node):
                adj_list[src_node] = list()
            adj_list[src_node].append(dst_node)
        return adj_list

    @staticmethod
    def __shortest_path(adj_list, src_dpid, dp_conn):
        def __get_all_nodes_from_adj_list(_adj_l):
            return adj_list.keys()

        def __get_neighbor(_adj_l, _node):
            return _adj_l[_node] if _adj_l.has_key(_node) else None

        def __get_weight(_u, _v, _weight):
            """

            :param _u:
            :param _v:
            :param _weight: list(int:src_dpid, int:dst_dpid, str:attr)
            """
            try:
                for dp_conn in _weight:
                    if dp_conn[0] == _u and dp_conn[1] == _v:
                        return float(dp_conn[2])
            except Exception, e:
                LOG.error(e)
                return None

        dist = {src_dpid: 0}
        previous = {}
        queue = __get_all_nodes_from_adj_list(adj_list)

        try:
            while queue:
                # find vertex u in Queue with smallest distance in dist[]
                u = queue[0]
                for node in queue[1:]:
                    if (   (not dist.has_key(u))
                           or (dist.has_key(node) and dist[node] < dist[u]) ):
                        u = node
                queue.remove(u)

                # Process reachable, remaining nodes from u
                for v in __get_neighbor(adj_list, u):
                    if v in queue:
                        alt = dist[u] + __get_weight(u, v, dp_conn)
                        if (not dist.has_key(v)) or (alt < dist[v]):
                            dist[v] = alt
                            previous[v] = u
            return dist, previous
        except Exception, e:
            LOG.error(e)
            return None, None

    @staticmethod
    def __get_path_from_prev(prev, src_dpid, dst_dpid):
        path = list()
        path.append(dst_dpid)
        curr = dst_dpid
        while curr != src_dpid:
            path.append(prev[curr])
            curr = prev[curr]
        return [node for node in reversed(path)]

    def update(self):
        connector = RyuConnector()
        links_json = connector.get_topo()
        if links_json is None:
            LOG.error("cannot get links_json from connector.")
            return

        old_len = len(self)

        exist_flags = list()
        # Add some links
        for i in range(0, len(links_json)):
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
            if l not in self:
                self.append(l)
            else:
                exist_flags.append(i)

        # delete some disconnected links.
        for i in set(range(0, old_len)).difference(exist_flags):
            self.remove(self[i])

        # update the link usage.
        self.__update_link_util()

    def __update_link_util(self):
        connector = RyuConnector()

        # First time to get bytes count.
        bytes_count_first = {}
        time_first = time.time()
        for link in self:
            tx_bytes, rx_bytes = connector.get_port_status(link.src_port.dpid, link.src_port.port_no)
            bytes_count_first[link] = tx_bytes + rx_bytes

        # Second time to get bytes count.
        time.sleep(WAIT_TIME_WAIT_PORTS_ADD)
        bytes_count_second = {}
        time_second = time.time()
        for link in self:
            tx_bytes, rx_bytes = connector.get_port_status(link.src_port.dpid, link.src_port.port_no)
            bytes_count_second[link] = tx_bytes + rx_bytes

        # compute the link usage at this time.
        duration = time_second - time_first  # count in second.
        for link in self:
            link.attr = ((bytes_count_second[link] - bytes_count_first[link]) / float(duration))
            link.attr = str(link.attr)

    def show(self):
        for link in self:
            print link


class RyuConnector(object):
    @staticmethod
    def get_topo():
        try:
            response_links = urllib2.urlopen(REST_SERVER_ADDR + '/v1.0/topology/links').read()
            links_json = json.loads(response_links)
            return links_json
        except:
            return None

    @staticmethod
    def get_port_status(dpid, port_no):

        """

        :param dpid:
        :param port_no:
        :return: return (tx_bytes, rx_bytes)
        """
        try:
            response_ports = urllib2.urlopen(REST_SERVER_ADDR + '/stats/port/' + str(dpid)).read()
            ports_json = json.loads(response_ports)
            port_json = ports_json[str(dpid)]

            for port_info in port_json:
                _port_no = port_info["port_no"]
                if _port_no == port_no:
                    tx_bytes = port_info["tx_bytes"]
                    rx_bytes = port_info["rx_packets"]
                    return tx_bytes, rx_bytes
        except Exception, e:
            LOG.error(e)
            return None, None

    @staticmethod
    def add_flow(flow_entry):
        try:
            req = urllib2.Request(REST_SERVER_ADDR + '/stats/flowentry/add')
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, flow_entry)
            LOG.info(response)
            return True
        except Exception, e:
            LOG.error(e)
            return False


class FlowEntry(object):
    def __init__(self, dpid, match, action):
        super(FlowEntry, self).__init__()
        self.dpid = dpid
        self.match = match
        self.action = action

    def convert_to_json(self):
        if self.is_port_num():
            match = {"in_port": self.match}
            action = [{"port": self.action, "type": "OUTPUT"}]
            dpid = self.dpid

            flow_entry = {
                "dpid": str(dpid),
                # "cookie": "0",
                "priority": "1111",
                "match": match,
                "actions": action,
            }
            return json.dumps(flow_entry)

        elif self.is_nw_addr():
            match = {"dl_type": 2048, "nw_src": self.match}
            action = [{"port": self.action, "type": "OUTPUT"}]
            dpid = self.dpid

            flow_entry = {
                "dpid": str(dpid),
                # "cookie": "0",
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
            return False


def read_ctrl_cmd():
    """
        read the std_in to read the control command.
        just like 192.168.1.0/24 1 4 90

    :return 1st, string: a match_field only support for ip like "192.168.1.10/24"
    :return 2nd, int: source datapath id.
    :return 3st. int. destination datapath id
    :return 4rd. float. required bandwidth.
    """
    try:
        cmds = stdin.readline().split(" ")
        match = cmds[0]
        src_dpid = int(cmds[1])
        dst_dpid = int(cmds[2])
        req_bandwidth = float(cmds[3])
        return match, src_dpid, dst_dpid, req_bandwidth
    # TODO to check if the src_dpid and dst_dpid is among dpsets.
    except ValueError, ve:
        LOG.error("wrong file format" + str(ve))
        return None, None, None, None
    except IOError, io_e:
        LOG.error(io_e)
        return None, None, None, None
    except:
        return None, None, None, None


def main():
    topo = Topology()
    connector = RyuConnector()

    while True:
        print "****************************TOPOLOGY*******************************"
        topo.update()
        topo.show()
        print "*******************************************************************"

        print "Input the command (match_field, source_dpid, dst_dpid, required_bandwidth), like 192.168.0.0/24 3 5 1.0"
        match, src_dpid, dst_dpid, req_bandwidth = read_ctrl_cmd()
        if match is None or src_dpid is None or dst_dpid is None or req_bandwidth is None:
            LOG.error("wrong cmds.")
            continue

        spf_path = topo.get_spf_path(src_dpid, dst_dpid, req_bandwidth)
        flow_entries = topo.get_flow_entries_rest(match, spf_path)

        for flow_entry in flow_entries:
            if connector.add_flow(flow_entry):
                LOG.info("push flow successfully")
            else:
                LOG.info("push flow error.")

        print "push shortest path  " + str(spf_path) + "  successfully."


if __name__ == '__main__':
    main()