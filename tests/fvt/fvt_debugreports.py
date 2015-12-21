import time
from tests.lib.base_api_test import TestBase
from tests.lib.restapilib import APIRequestError
from tests.lib.restapilib import Validator


class Debugreports(TestBase):

    """
    Represents test case that could help in testing the REST API supported for Debug Reports.

    Attributes:
    \param TestBase
    config file which contains all configuration information with sections
    """
    default_debugreport_schema = {"type": "object",
                                  "properties": {"name": {"type": "string"},
                                                 "time": {"type": "string"},
                                                 "name": {"type": "string"},
                                                 "uri": {"type": "string"}
                                                 }
                                  }

    default_task_schema = {"type": "object",
                           "properties": {"status": {"type": "string"},
                                          "message": {"type": "string"},
                                          "id": {"type": "string"},
                                          "target_uri": {"type": "string"},
                                          }
                           }

    new_debug_report = {"name": 'test1'}
    debugreport_uri = '/plugins/gingerbase/debugreports'
    rename_reportname = {"name": 'test1_rename'}
    task_uri = '/plugins/gingerbase/tasks'

    @classmethod
    def setUpClass(self):
        super(Debugreports, self).setUpClass()
        self.validator = Validator()

    def test_S001_create_debug_report(self):
        """
        Create new debug report
        """
        self.logging.info('--> Debugreports.test_S001_create_debug_report()')
        try:
            resp_report = self.session.request_post_json(
                Debugreports.debugreport_uri, Debugreports.new_debug_report)
            if resp_report is not None:
                self.logging.debug(
                    'Addition of new repository is successful: %s' % (resp_report))
                self.validator.validate_json(
                    resp_report, Debugreports.default_task_schema)
                self.logging.debug(
                    "**********Debug Report status: \"%s\"" % (resp_report["status"]))
                task_status = resp_report["status"]
                task_id = resp_report["id"]
                while task_status == "running":
                    time.sleep(5)
                    task_resp = self.session.request_get_json(
                        Debugreports.task_uri + '/' + task_id)
                    task_status = task_resp["status"]
                    print "Status: %s" % (task_status)
                    continue
                if task_status == "finished":
                    self.logging.debug('Creation of a debug report is successful: %s' % (
                        Debugreports.new_debug_report["name"]))
                else:
                    self.logging.error('Creation of a debug report is failed')
        except Exception, err:
            self.logging.error(
                'Debugreports.test_S001_create_debug_report(): ERROR: %s\n' % str(err))
            raise Exception(str(err))
        finally:
            self.logging.info(
                '<-- Debugreports.test_S001_create_debug_report()')

    def test_S002_retrieve_alldebugreports(self):
        """
         Retrieve a summarized list of all available Debug Reports
        """
        self.logging.info(
            '--> Debugreports.test_S002_retrieve_alldebugreports()')
        try:
            self.logging.debug(
                'Retrieve a summarized list of all available Debug Reports')
            resp_json = self.session.request_get_json(
                Debugreports.debugreport_uri)
            self.logging.debug('Debug Reports found : %s' % (resp_json))
            if resp_json is not None:
                for dr_json in resp_json:
                    self.validator.validate_json(
                        dr_json, Debugreports.default_debugreport_schema)
                    self.logging.debug(
                        "Debug Report Name: \"%s\"" % (dr_json["name"]))
            else:
                self.logging.debug('No Debug Report found : %s' % (resp_json))
        except APIRequestError as error:
            self.logging.error(error.__str__())
        finally:
            self.logging.info(
                '<-- Debugreports.test_S002_retrieve_alldebugreports()')

    def test_S003_retrieve_alldebugreports_description(self):
        """
         Retrieve a description of all debug reports
        """
        self.logging.info(
            '--> Debugreports.test_S003_retrieve_alldebugreports_description()')
        try:
            self.logging.debug('Retrieve the description of all debug reports')
            resp_json = self.session.request_get_json(
                Debugreports.debugreport_uri)
            if resp_json is not None:
                for dr_json in resp_json:
                    self.validator.validate_json(
                        dr_json, Debugreports.default_debugreport_schema)
                    self.logging.debug(
                        "Debug Report name: \"%s\"" % (dr_json["name"]))
                    debug_report_name = dr_json["name"]
                    details_json = self.session.request_get_json(
                        Debugreports.debugreport_uri + '/' + debug_report_name)
                    self.validator.validate_json(
                        details_json, Debugreports.default_debugreport_schema)
                    self.logging.debug(
                        'Debug Report description is : %s' % (details_json))
            else:
                self.logging.debug('No Debug Report found : %s' % (resp_json))
        except APIRequestError as error:
            self.logging.error(error.__str__())
        finally:
            self.logging.info(
                '<-- Debugreports.test_S003_retrieve_alldebugreports_description()')

    def test_S004_rename_report(self):
        """
        Rename Debug Report name
        """
        rename_uri = Debugreports.debugreport_uri + \
            '/' + Debugreports.new_debug_report["name"]
        self.logging.info('--> Debugreports.test_S004_rename_report()')
        resp = self.session.request_get(
            rename_uri, expected_status_values=[200])
        try:
            if resp is not None:
                resp_repo = self.session.request_put_json(
                    rename_uri, Debugreports.rename_reportname, expected_status_values=[200])
                if resp_repo is not None:
                    self.logging.debug(
                        'Renaming debug report is successful: %s' % (resp_repo))
                    renamed_report_json = self.session.request_get_json(
                        Debugreports.debugreport_uri + '/' + Debugreports.rename_reportname["name"])
                    self.logging.debug(
                        'After rename debug report description is : %s' % (renamed_report_json))
                    self.logging.debug(
                        'Renaming back to original debug report name')
                    self.session.request_put_json(
                        Debugreports.debugreport_uri + '/' + Debugreports.rename_reportname["name"], Debugreports.new_debug_report, expected_status_values=[200])
        except Exception, err:
            self.logging.error(
                'Debugreports.test_S004_rename_report(): ERROR: %s\n' % str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- Debugreports.test_S004_rename_report()')

    def test_S005_delete_debug_report(self):
        """
        Delete an existing debug report
        """
        del_uri = Debugreports.debugreport_uri + '/' + \
            Debugreports.new_debug_report["name"]
        self.logging.info('--> Debugreports.test_S005_rdelete_debug_report()')
        resp = self.session.request_get(
            del_uri, expected_status_values=[200])
        try:
            if resp is not None:
                del_resp = self.session.request_delete(del_uri)
                self.assertEquals(
                    204, del_resp.status_code, "Debug report has been deleted")
        except Exception, err:
            self.logging.error(
                'Debugreports.test_S005_rdelete_debug_report(): ERROR: %s\n' % str(err))
            raise Exception(str(err))
        finally:
            self.logging.info(
                '<-- Debugreports.test_S005_rdelete_debug_report()')
