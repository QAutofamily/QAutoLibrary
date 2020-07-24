"""
#    QAutomate Ltd 2020. All rights reserved.
#
#    Copyright and all other rights including without limitation all intellectual property rights and title in or
#    pertaining to this material, all information contained herein, related documentation and their modifications and
#    new versions and other amendments (QAutomate Material) vest in QAutomate Ltd or its licensor's.
#    Any reproduction, transfer, distribution or storage or any other use or disclosure of QAutomate Material or part
#    thereof without the express prior written consent of QAutomate Ltd is strictly prohibited.
#
#    Distributed with QAutomate license.
#    All rights reserved, see LICENSE for details.
"""

from robot.api import SuiteVisitor, TestSuite
from QAutoLibrary.QAutoRobot import QAutoRobot


class RemoveTasksByTags(SuiteVisitor):

    def __init__(self, runid, robotname, *args):
        self.runid=runid
        self.robotname=robotname
        self.state_tags = None
        mongodb = "localhost"
        mongoport = "27017"
        username = ""
        password = ""
        # Get passed arguments
        for arg in args:
            try:
                key, value = arg.split("=")
            except ValueError as e:
                print ("WARNING: Invalid argument: %s" % arg)
                continue
            if key == "mongodb":
                mongodb = value
            elif key == "mongoport":
                mongoport = value
            elif key == "username":
                username = value
            elif key == "password":
                password = value
            elif key == "states":
                # User defined states (tags)
                self.state_tags = [state.strip() for state in value.split(",")]
            else:
                print ("WARNING: Unknown key argument: %s" % key)
                print ("WARNING: Valid key arguments are: [mongodb, mongoport, username, password, states]")

        if not self.state_tags:
            # Get tags based on RPA status from database (executed in other robot run)
            self.qr = QAutoRobot("")
            self.qr.rpa_logger_init(robotname=robotname, runid=runid, mongodbIPPort=mongodb+":"+mongoport, username=username, password=password)
            self.state_tags = self.qr.get_rpa_executed_tasks(runid, robotname)
        print("State tags: ", self.state_tags)

    def start_suite(self, suite):
        if self.state_tags is None:
            # We don't have Mongo db connection do fatal error
            fail_suite = TestSuite(name='Fatal error')
            tc_fatal_error = fail_suite.tests.create("Fatal MongoDB error")
            tc_fatal_error.keywords.create('Fatal error', args=["RPA Mongodb Server not available or authentication failed. Please check connection parameters."])
            suite.tests.insert(0, tc_fatal_error)
        else:
            # Remove tasks from suite based on RPA status (which was already executed in other robot run)
            filtered_tests = []
            for test in suite.tests:
                remove_test = False
                for tag in self.state_tags:
                    if tag in test.tags:
                        remove_test = True
                        break
                if not remove_test:
                    filtered_tests.append(test)
            suite.tests = filtered_tests
            # Add task to setup robot data in begin of suite
            rpa_suite = TestSuite(name='Rpa data')
            tc_rpa_data = rpa_suite.tests.create("Get data from database")
            tc_rpa_data.keywords.create('Setup data', args=[self.runid, self.robotname])
            suite.tests.insert(0, tc_rpa_data)
