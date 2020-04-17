from robot.api import SuiteVisitor, TestSuite
from QAutoLibrary.QAutoRobot import QAutoRobot


class RemoveTasksByTags(SuiteVisitor):

    def __init__(self, runid, robotname, mongodb="localhost", mongoport="27017", username="", password=""):
        self.runid=runid
        self.robotname=robotname
        # Get tags based on RPA status (executed in other robot run)
        qr = QAutoRobot("")
        qr.rpa_logger_init(robotname=robotname, runid=runid, mongodbIPPort=mongodb+":"+mongoport, username=username, password=password)
        self.state_tags = qr.get_rpa_executed_tasks(runid, robotname)
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
