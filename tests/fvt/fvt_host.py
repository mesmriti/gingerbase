#!/usr/bin/python
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

import time
import unittest

#from tests.lib.base_api_test import TestBase
#from tests.lib.restapilib import APIRequestError
#from tests.lib.restapilib import Validator
from requests.exceptions import ConnectionError
#from tests.lib.utils import vm_utils
from tests.fvt.utils import vm_utils
from tests.fvt.restapilib import Validator
from tests.fvt.fvt_base import TestBase, APIRequestError


class TestHostInfo(TestBase):
    """
    Represents test case that could help in testing the REST API supported for host static information.

    Attributes:
        \param TestBase  
         config file which contains all configuration information with sections
    """
    # Response json of host static information looks like
    # {"os_distro":"Fedora", "os_version":"21", "os_codename":"Twenty One", "cpu_model":"QEMU Virtual CPU version (cpu64-rhel6)", 
    # "cpus":1, "memory":2073870336}
    default_schema = {"type" : "object",
                      "properties" : {"os_distro": {"type" : "string"},
                                      "os_version" :{"type" : "string"},
                                      "os_codename" : {"type" : "string"},
                                      "cpu_model" : {"type" : "string"},
                                      "cpus" : {"type" : "number"},
                                      "memory" : {"type" : "number"},
                                      }
                      }
    #swupdate api returns a task resource
    default_task_schema = {"type" : "object",
                           "properties": {"status": {"type": "string"},
                                          "message": {"type": "string"},
                                          "id": {"type": "string"},
                                          "target_uri": {"type": "string"},
                                          }
                           }
    uri_host = '/plugins/gingerbase/host'
    uri_task = '/plugins/gingerbase/tasks'
    
    def setUp(self):
        pass
        
    def test_S001_hostinfo(self):
        """
        Retrieve host static information
        """
        self.logging.info('--> TestHostInfo.test_hostinfo()')
        try:
            self.logging.debug('Retrieve host static information')
            resp = self.session.request_get_json(TestHostInfo.uri_host, [200])
            if resp is not None:
                self.logging.debug('Host static information found : %s' % (resp))
                self.validator.validate_json(resp, TestHostInfo.default_schema)
            else:
                self.logging.info('Host static information is not found')
                
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info('<-- TestHostInfo.test_hostinfo()')
    
    def test_S002_host_swupdate(self):
        """
        Start the update of packages in background and return a Task resource
        skip test case for exception : "KCHPKGUPD0001E": "No packages marked for update"
        """
        
        self.logging.info('--> TestHostInfo.test_host_swupdate()')
        self.errormsg='KCHPKGUPD0001E: No packages marked for update'
        try:
            self.logging.debug('starting software update...!!!')
            resp = self.session.request_post_json(TestHostInfo.uri_host+"/swupdate")
            #swupdate returns a task resource
            if resp is not None:
                self.validator.validate_json(resp, TestHostInfo.default_task_schema)
                self.logging.debug('host software update response json: %s' % (resp))
                self.logging.debug(
                    "**********software update status: \"%s\"" % (resp["status"]))
                task_status = resp["status"]
                task_id = resp["id"]
                while task_status == "running":
                    time.sleep(5)
                    task_resp = self.session.request_get_json(
                        TestHostInfo.uri_task + '/' + task_id, [200])
                    task_status = task_resp["status"]
                    self.logging.debug('Status: %s' % (task_status))
                    continue
                if task_status == "finished":
                    self.logging.debug('Software update is successful')
                else:
                    self.logging.error("software update task message: %s " % (task_resp['message']))
                    self.logging.error('Software update is failed')
                    self.assertFalse(True, task_resp['message'])
                 
        except APIRequestError as error:
            if self.errormsg in error:
                self.logging.info('Skipping start swupdate test: %s' %(self.errormsg))
                raise unittest.SkipTest('Skipping start swupdate test: no packages marked for update')
            else :
                self.logging.error(error.__str__())
                raise Exception(error)
        finally:
            self.logging.info('<-- TestHostInfo.test_host_swupdate()')


class TestHostShutdownWithoutVms(TestBase):
    """
    Test case to test host shutdown when no VM is in running state    
    """
    @classmethod 
    def setUpClass(self):
        super(TestHostShutdownWithoutVms, self).setUpClass()
        self.logging.info('--> TestHostShutdownWithoutVms.setUpClass()')
        resp = vm_utils.list_vms(self.session, expected_status=[200])
        is_any_running_vm = False
        if resp is not None:
            for vm in resp:
                if vm['state'] == 'running':
                    is_any_running_vm = True
                    break
            if is_any_running_vm:
                raise unittest.SkipTest('TestHostShutdownWithoutVms: Skipping host shutdown since one or more VM(s) are in running state')
        self.logging.info("No VM is in running state")
        self.logging.info('<-- TestHostShutdownWithoutVms.setUpClass()')
    
    @unittest.skip("Skip test_S001_host_shutdown() as this will shutdown host")
    def test_S001_host_shutdown(self):
        """
        Power off the host machine
        """
        self.logging.info('--> TestHostShutdownWithoutVms.test_S001_host_shutdown()')
        try:
            self.logging.debug('power off the host machine')
            self.session.request_post(TestHostInfo.uri_host+"/shutdown", [200])
        except ConnectionError as error:
            self.logging.debug('host shutdown successful')            
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info('<-- TestHostShutdownWithoutVms.test_S001_host_shutdown()')
        
class TestHostShutdownWithRunningVms(TestBase):
    """
    Test case to test host shutdown having a vm in running state 
    """
    @classmethod 
    def setUpClass(self):
        super(TestHostShutdownWithRunningVms, self).setUpClass()
        self.logging.info('--> TestHostShutdownWithRunningVms.setUpClass()')
        self.vm_name="test_vm_4_host"
        vm_utils.create_vm(self.session, self.vm_name)
        vm_utils.start_vm(self.session, self.vm_name)
            
    def test_S001_host_shutdown(self):
        """
        Power off the host machine
        """
        self.logging.info('--> TestHostShutdownWithRunningVms.test_S001_host_shutdown()')
        shutdown_error = "KCHHOST0001E: Unable to shutdown host machine as there are running virtual machines"
        try:
            self.logging.debug('power off the host machine')
            self.session.request_post(TestHostInfo.uri_host+"/shutdown", [200])            
        except APIRequestError as error:
            if shutdown_error in error:
                self.logging.debug('Successful : Unable to shutdown host machine as there are running virtual machines')
            else:
                raise Exception(error.__str__())
        finally:
            self.logging.info('<-- TestHostShutdownWithRunningVms.test_S001_host_shutdown()')
    
    @classmethod
    def tearDownClass(self):
        self.logging.info('--> TestHostShutdownWithRunningVms.tearDownClass()')
        vm_utils.poweroff_vm(self.session, self.vm_name)
        vm_utils.delete_vm(self.session, self.vm_name)
        self.logging.info('<-- TestHostShutdownWithRunningVms.tearDownClass()')
    
class TestHostRebootWithoutVms(TestBase):
    """
    Test case to test host reboot when no VM is in running state    
    """
    @classmethod 
    def setUpClass(self):
        super(TestHostRebootWithoutVms, self).setUpClass()
        self.logging.info('--> TestHostRebootWithoutVms.setUpClass()')
        resp = vm_utils.list_vms(self.session, expected_status=[200])
        is_any_running_vm = False
        if resp is not None:
            for vm in resp:
                if vm['state'] == 'running':
                    is_any_running_vm = True
                    break
            if is_any_running_vm:
                raise unittest.SkipTest('TestHostRebootWithoutVms: Skipping host reboot since one or more VM(s) are in running state')
        self.logging.info("No VM is in running state")
        self.logging.info('<-- TestHostRebootWithoutVms.setUpClass()')
    
    @unittest.skip("Skip test_S001_host_reboot() as this will reboot host")        
    def test_S001_host_reboot(self):
        """
        Reboot the host machine
        """
        self.logging.info('--> TestHostRebootWithoutVms.test_S001_host_reboot()')
        try:
            self.logging.debug('reboot the host machine')
            self.session.request_post(TestHostInfo.uri_host+"/reboot")
        
        except ConnectionError as error:
            self.logging.debug('host reboot successful')            
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info('<-- TestHostRebootWithoutVms.test_S001_host_reboot()')

class TestHostRebootWithRunningVms(TestBase):
    """
    Test case to test host reboot having a vm in running state 
    """
    @classmethod 
    def setUpClass(self):
        super(TestHostRebootWithRunningVms, self).setUpClass()
        self.logging.info('--> TestHostRebootWithRunningVms.setUpClass()')
        self.vm_name="test_vm_4_host"
        vm_utils.create_vm(self.session, self.vm_name)
        vm_utils.start_vm(self.session, self.vm_name)
        self.logging.info('<-- TestHostRebootWithRunningVms.setUpClass()')
            
    def test_S001_host_reboot(self):
        """
        Reboot the host machine
        """
        self.logging.info('--> TestHostRebootWithRunningVms.test_S001_host_reboot()')
        reboot_error = "KCHHOST0002E: Unable to reboot host machine as there are running virtual machines"
        try:
            self.logging.debug('reboot the host machine')
            self.session.request_post(TestHostInfo.uri_host+"/reboot")
        except APIRequestError as error:
            if reboot_error in error:
                self.logging.debug('Successful : Unable to reboot host machine as there are running virtual machines')
            else:
                raise Exception(error.__str__())
        finally:
            self.logging.info('<-- TestHostRebootWithRunningVms.test_S001_host_reboot()')
    
    @classmethod
    def tearDownClass(self):
        self.logging.info('--> TestHostRebootWithRunningVms.tearDownClass()')
        vm_utils.poweroff_vm(self.session, self.vm_name)
        vm_utils.delete_vm(self.session, self.vm_name)
        self.logging.info('<-- TestHostRebootWithRunningVms.tearDownClass()')

class TestHostStats(TestBase):
    """
    Represents test case that could help in testing the REST API supported for host sample data.
 
    Attributes:
        \param TestBase  
         config file which contains all configuration information with sections    
    """
    #Response json of host stats looks like
    #{"cpu_utilization":4.1, "disk_write_rate":0, "net_sent_rate":153, "memory":{ "cached":536342528, "avail":1154670592, "total":2073870336,
    #"buffers":92864512, "free":525463552}, "net_recv_rate":94, "disk_read_rate":0}
    default_schema={"type" : "object",
                   "properties" : {"cpu_utilization": {"type" : "number"},
                                   "disk_write_rate": {"type" : "number"},
                                   "net_sent_rate" : {"type" : "number"},
                                   "memory" : {"type" : "object",
                                               "properties" : {"cached" : {"type" : "number"},
                                                               "avail": {"type" : "number"},
                                                               "total": {"type" : "number"},
                                                               "buffers":{"type" : "number"},
                                                               "free":{"type" : "number"},
                                                               }
                                               },
                                   "net_recv_rate": {"type" : "number"},
                                   "disk_read_rate": {"type" : "number"}                                   
                                   }
                    }
    uri_hoststats='/plugins/gingerbase/host/stats'
    
    def setUp(self):
        pass
    
    def test_S001_hoststats(self):
        """
        Retrieve host sample data
        """
        self.logging.info('--> TestHostStats.test_hoststats()')
        try:
            self.logging.debug('Retrieve host sample data')
            resp = self.session.request_get_json(TestHostStats.uri_hoststats, [200])
            if resp is not None:
                self.logging.debug('Host sample data found : %s' % (resp))
                self.validator.validate_json(resp, TestHostStats.default_schema)
            else:
                self.logging.info('Host sample data is not found')
                
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info('<-- TestHostStats.test_hoststats()')
            
class TestCpuInfo(TestBase):
    """
    Represents test case that could help in testing the REST API supported for cpuinfo to
    retrieve the sockets, cores, and threads values
 
    Attributes:
        \param TestBase  
         config file which contains all configuration information with sections    
    """
    #Response json of cpuinfo looks like
    #{"cores":1, "threading_enabled":true, "sockets":1, "threads_per_core":1}
    default_schema={"type" : "object",
                    "properties" : {"cores": {"type" : "number"},
                                    "threading_enabled": {"type" : "boolean"},
                                    "sockets": {"type" : "number"},
                                    "threads_per_core" : {"type" : "number"}
                                    }
                    }
    uri_host_cpuinfo='/plugins/gingerbase/host/cpuinfo'
    def setUp(self):
        pass
    
    def test_S001_host_cpuinfo(self):
        """
        Retrieve cpuinfo - sockets, cores, and threads values
        """
        self.logging.info('--> TestCpuInfo.test_host_cpuinfo()')
        try:
            self.logging.debug('Retrieve cpuinfo - sockets, cores, and threads values')
            resp = self.session.request_get_json(TestCpuInfo.uri_host_cpuinfo, [200])
            if resp is not None:
                self.logging.debug('cpu information found : %s' % (resp))
                self.validator.validate_json(resp, TestCpuInfo.default_schema)
            else:
                self.logging.info('cpu information is not found')
                
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info('<-- TestCpuInfo.test_host_cpuinfo()')
        
class TestHostStatsHistory(TestBase):
    """
    Represents test case that could help in testing the REST API supported for HostStatsHistory.

    Attributes:
        \param TestBase
         config file which contains all configuration information with sections
    """
    default_schema = {"type":"object",
                      "properties": {"cpu_utilization" : {"type": "array",
                                                          "items": {"type": "number"}
                                                        },
                                     "disk_write_rate" : {"type": "array",
                                                          "items": {"type": "number"}
                                                        },
                                     "net_sent_rate" : {"type": "array",
                                                        "items": {"type": "number"}
                                                        },
                                     "memory" : {"type": "array",
                                                 "items": {"type":"object",
                                                           "properties": {"cached" : {"type" : "number"},
                                                                       "avail" : {"type" : "number"},
                                                                       "total" : {"type" : "number"},
                                                                       "buffers" : {"type" : "number"},
                                                                       "free" : {"type" : "number"}
                                                                       }
                                                        }
                                                 },
                                     "net_recv_rate" : {"type": "array",
                                                        "items": {"type": "number"}
                                                        },
                                     "disk_read_rate" : {"type": "array",
                                                        "items": {"type": "number"}
                                                        }
                                     }
                      }

    uri_history = '/plugins/gingerbase/host/stats/history'

    def setUp(self):
        pass

    def test_S001_host_stats_history(self):
        """
        Retrieve host stats history
        """

        self.logging.info('--> TestHostStatsHistory.test_host_stats_history() ')
        try:
            self.logging.debug('Retrieve host stats history ')
            resp_json = self.session.request_get_json(TestHostStatsHistory.uri_history, [200])
            if resp_json is not None:
                self.logging.debug(resp_json)
                self.validator.validate_json(resp_json, TestHostStatsHistory.default_schema)
            else:
                self.logging.debug('No History found')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info('<-- TestHostStatsHistory.test_host_stats_history()')
