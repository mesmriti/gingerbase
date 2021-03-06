#
# Project Ginger Base
#
# Copyright IBM, Corp. 2013-2015
#
# Code derived from Project Kimchi
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

from wok.control.base import AsyncResource, Collection
from wok.control.base import Resource
from wok.control.utils import UrlSubNode

from wok.plugins.gingerbase.control.cpuinfo import CPUInfo


@UrlSubNode('host', True)
class Host(Resource):
    def __init__(self, model, id=None):
        super(Host, self).__init__(model, id)
        self.role_key = 'dashboard'
        self.admin_methods = ['GET', 'POST']
        self.uri_fmt = '/host/%s'
        self.reboot = self.generate_action_handler('reboot')
        self.shutdown = self.generate_action_handler('shutdown')
        self.stats = HostStats(self.model)
        self.packagesupdate = PackagesUpdate(self.model)
        self.repositories = Repositories(self.model)
        self.swupdate = self.generate_action_handler_task('swupdate')
        self.swupdateprogress = SoftwareUpdateProgress(self.model)
        self.cpuinfo = CPUInfo(self.model)
        self.capabilities = Capabilities(self.model)

    @property
    def data(self):
        return self.info


class SoftwareUpdateProgress(AsyncResource):
    def __init__(self, model, id=None):
        super(SoftwareUpdateProgress, self).__init__(model, id)
        self.role_key = 'updates'
        self.admin_methods = ['GET']

    @property
    def data(self):
        return self.info


class HostStats(Resource):
    def __init__(self, model, id=None):
        super(HostStats, self).__init__(model, id)
        self.role_key = 'dashboard'
        self.admin_methods = ['GET']
        self.history = HostStatsHistory(self.model)

    @property
    def data(self):
        return self.info


class HostStatsHistory(Resource):
    @property
    def data(self):
        return self.info


class Capabilities(Resource):
    def __init__(self, model, id=None):
        super(Capabilities, self).__init__(model, id)

    @property
    def data(self):
        return self.info


class PackagesUpdate(Collection):
    def __init__(self, model):
        super(PackagesUpdate, self).__init__(model)
        self.role_key = 'updates'
        self.admin_methods = ['GET']
        self.resource = PackageUpdate


class PackageUpdate(Resource):
    def __init__(self, model, id=None):
        super(PackageUpdate, self).__init__(model, id)
        self.role_key = 'updates'
        self.admin_methods = ['GET']

    @property
    def data(self):
        return self.info


class Repositories(Collection):
    def __init__(self, model):
        super(Repositories, self).__init__(model)
        self.role_key = 'updates'
        self.admin_methods = ['GET', 'POST']
        self.resource = Repository


class Repository(Resource):
    def __init__(self, model, id):
        super(Repository, self).__init__(model, id)
        self.role_key = 'updates'
        self.admin_methods = ['GET', 'PUT', 'POST', 'DELETE']
        self.uri_fmt = "/host/repositories/%s"
        self.enable = self.generate_action_handler('enable')
        self.disable = self.generate_action_handler('disable')

    @property
    def data(self):
        return self.info
