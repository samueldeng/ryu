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
from ryu.controller import event

LOG = logging.getLogger(__name__)


class EventHostsRequest(event.EventRequestBase):
    def __init__(self):
        super(EventHostsRequest, self).__init__()
        self.dst = 'HostDiscovery'

    def __str__(self):
        return 'EventHostRequest<src=%s><dst=%s>' % (self.src, self.dst)


class EventHostsReply(event.EventReplyBase):
    def __init__(self, dst, hosts):
        super(EventHostsReply, self).__init__(dst)
        self.hosts = hosts