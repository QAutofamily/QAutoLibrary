from robot.api import SuiteVisitor, TestSuite
from QAutoLibrary.RpaLogger import RpaLogger


class RemoveTasksByTags(SuiteVisitor):

    def __init__(self, runid, robotname, mongodb="localhost", mongoport="27017S", username="", password=""):
        self.runid=runid
        self.robotname=robotname
        # Get tags based on RPA status (executed in other robot run)
        rl = RpaLogger()
        rl.rpa_logger_init(robotname=robotname, runid=runid, mongodbIPPort=mongodb+":"+mongoport, username=username, password=password)
        self.state_tags = rl.get_rpa_executed_tasks(runid, robotname)
        print("State tags: ", self.state_tags)

    def start_suite(self, suite):
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
        tc_rpa_data = rpa_suite.tests.create("Add rpa data")
        tc_rpa_data.keywords.create('Setup rpa data', args=[self.runid, self.robotname])
        suite.tests.insert(0, tc_rpa_data)
