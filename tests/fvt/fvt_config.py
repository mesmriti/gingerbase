#
# Project Kimchi
#
# Copyright IBM, Corp. 2015
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301USA

from tests.lib.base_api_test import TestBase
from tests.lib.restapilib import APIRequestError


class TestConfig(TestBase):
    """
    Represents test case that could help in testing the REST API support for retrieving configuration and capabilities
    information.

    Attributes:
        \param TestBase
         config file which contains all configuration information with sections
    """

    # Response json for configuration looks like
    # {"display_proxy_port":"64667","version":"1.4.0-86.git30cf319"}

    config_schema = {"type": "object",
                     "properties": {"display_proxy_port": {"type": "string"},
                                    "version": {"type": "string"}
                                    }
                     }

    # Response json for capabilities information looks like
    # {"federation":"off", "repo_mngt_tool":"yum", "system_report_tool":true,
    #  "libvirt_stream_protocols":["http","https","ftp","ftps","tftp"],
    # "auth":"pam", "nm_running":false, "qemu_stream":true, "screenshot":null,
    #  "update_tool":true, "kernel_vfio":true, "qemu_spice":true}

# TODO: capabilities_schema is yet to be tested for boolean values which might be obtained for screenshot.
    capabilities_schema = {"type": "object",
                           "properties": {"federation": {"enum" : ["on", "off"]},
                                          "repo_mngt_tool": {"enum" : ["deb", "yum", "null"]},
                                          "system_report_tool": {"type": "boolean"},
                                          "libvirt_stream_protocols": {"type": "array",
                                                                       "items": {"type": "string"}
                                                                       },
                                          "auth": {"enum" : ["pam", "ldap"]},
                                          "nm_running": {"type": "boolean"},
                                          "qemu_stream": {"type": "boolean"},
                                          "screenshot": {"type": ["boolean", "null"]},
                                          "update_tool": {"type": "boolean"},
                                          "kernel_vfio": {"type": "boolean"},
                                          "qemu_spice": {"type": "boolean"},
                                          "mem_hotplug_support" : {"type" : "boolean"}
                                          }
                           }

    distros_schema = {"type": "array",
                      "properties": {"os_distro": {"type": "string"},
                                     "os_version": {"type": "string"},
                                     "name": {"type": "string"},
                                     "os_arch": {"type": "string"},
                                     "path": {"type": "string"},
                                     }
                      }

    distros_fedora_schema = {"type": "object",
                             "properties": {"os_distro": {"type": "string"},
                                            "os_version": {"type": "string"},
                                            "name": {"type": "string"},
                                            "os_arch": {"type": "string"},
                                            "path": {"type": "string"},
                                            }
                             }

    uri_config = '/plugins/gingerbase/config'
    uri_distros = '/plugins/gingerbase/config/distros'

    def setUp(self):
        pass

    def test_S000_list_config_info(self):
        """
        Retrieve configuration information
        """

        self.logging.info('--> TestConfig.test_list_config_info() ')
        try:
            self.logging.debug('Retrieve configuration information ')
            resp_json = self.session.request_get_json(TestConfig.uri_config, [200])
            if resp_json is not None:
                self.logging.debug(resp_json)
                self.validator.validate_json(resp_json, TestConfig.config_schema)
            else:
                self.logging.debug('No Configuration information found')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            self.logging.error('<-- TestConfig.test_list_config_info() ')
        finally:
            self.logging.info('<-- TestConfig.test_list_config_info()')

    def test_S001_list_capabilities(self):
        """
        Retrieve capabilities information
        """
        self.logging.info('--> TestConfig.test_list_capabilities() ')
        try:
            self.logging.debug('Retrieve host capabilities information ')
            uri_capabilities = TestConfig.uri_config + '/' + 'capabilities'
            resp_json = self.session.request_get_json(uri_capabilities, [200])
            if resp_json is not None:
                self.logging.debug(resp_json)
                self.validator.validate_json(resp_json, TestConfig.capabilities_schema)
            else:
                self.logging.debug('No host capabilities information found')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            self.logging.error('<-- TestConfig.test_list_capabilities() ')
        finally:
            self.logging.info('<-- TestConfig.test_list_capabilities()')
