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

LOG = logging.getLogger("SPF_Router")


class Graph:
    graph = dict()

    def __init__(self, graph):
        # graph = {str:[str,str...]})
        self.graph = graph

    def get_all_nodes(self):
        return self.graph.keys()

    def get_neighbor(self, node):
        assert isinstance(node, str)
        if not self.graph.has_key(node):
            return None
        else:
            return self.graph[node]

    @staticmethod
    def get_weight(u, v):
        return 1


def shortest_path(graph, source_node):
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
                alt = dist[u] + graph.get_weight(u, v)
                if (not dist.has_key(v)) or (alt < dist[v]):
                    dist[v] = alt
                    previous[v] = u
    return dist, previous


def conv_adj_matrix(links, request_bandwidth):
    graph = dict()
    for link in links:
        node = link[0]
        peer_node = link[1]
        ava_bandwidth = link[2]
        if ava_bandwidth < request_bandwidth:
            continue
        if not graph.has_key(node):
            graph[node] = list()
        if not graph.has_key(peer_node):
            graph[peer_node] = list()
        graph[node].append(peer_node)
        graph[peer_node].append(node)
    return graph


def gen_path_from_prev(prev, begin, end):
    path = list()
    path.append(end)
    curr = end
    while curr != begin:
        path.append(prev[curr])
        curr = prev[curr]
    return [node for node in reversed(path)]


def main():
    links = [
        ('1', '3', 100),
        ('1', '4', 100),
        ('2', '3', 100),
        ('2', '4', 100),
        ('3', '4', 100),
        ('3', '5', 10),
        ('3', '6', 100),
        ('4', '5', 30),
        ('4', '6', 100),
        ('5', '6', 100),
        ('5', '7', 100),
        ('5', '8', 100),
        ('6', '7', 100),
        ('6', '8', 100),
    ]
    begin_end = ('1', '7', 90)
    begin_node = begin_end[0]
    end_node = begin_end[1]
    required_bandwidth = begin_end[2]

    graph = conv_adj_matrix(links, required_bandwidth)
    my_g = Graph(graph)
    dist, prev = shortest_path(my_g, begin_node)
    path = gen_path_from_prev(prev, begin_node, end_node)
    print path


if __name__ == main():
    main()
