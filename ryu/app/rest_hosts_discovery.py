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
from webob import Response

from ryu.app.wsgi import ControllerBase, WSGIApplication
from ryu.base import app_manager
from ryu.topology.HostDiscovery import get_hosts

LOG = logging.getLogger("RestHosts_Logger")


class HostsDiscoveryController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(HostsDiscoveryController, self).__init__(req, link, data,
                                                       **config)
        self.host_discovery_api_app = data['host_discovery_api_app']

    def list_hosts(self, req, **kwargs):
        LOG.info(self.host_discovery_api_app)
        hosts = get_hosts(self.host_discovery_api_app)
        LOG.debug(hosts)  # { "(" dpid ":" port ")" :str$nic_mac_addr}
        body = json.dumps(hosts)
        return Response(content_type='application/json', body=body)


class HostsAPI(app_manager.RyuApp):
    _CONTEXTS = {
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(HostsAPI, self).__init__(*args, **kwargs)
        self.name = "HostsAPI"
        wsgi = kwargs['wsgi']
        mapper = wsgi.mapper

        controller = HostsDiscoveryController
        wsgi.registory[controller.__name__] = {'host_discovery_api_app': self}
        route_name = 'host_discovery'

        uri = '/hosts'
        mapper.connect(route_name, uri, controller=controller,
                       action='list_hosts',
                       conditions=dict(method=['GET']))