import os
import sys
import imp
import inspect
from types import FunctionType

from QAutoLibrary import FileOperations
from QAutoLibrary.QAutoSelenium import CommonUtils

from QAutoLibrary.extension.screencast.vlc_recorder import VlcRecorder
from QAutoLibrary.extension.testdata.testdata import get_global_testdata, TestData
from QAutoLibrary.extension.parsers.parameter_parser import set_parameter_file
from QAutoLibrary.extension.util.GlobalUtils import Singleton

DefaultDirectory = ["pagemodel", "common_lib"]
TestReportFolder = "test_reports"

WarningNoTestData = "QautoRobot: Not using TestData"
WarningDirectoryNotFound = "QautoRobot: Method directory could not be found: "

LibraryScope = 'TEST SUITE'
LibraryAttributeName = "QAutoRobot"


class QAutoRobot(CommonUtils):
    """
    Robot library for dynamically adding all qautorobot methods to robot runnable state or in robot project libraries
    """
    __metaclass__ = Singleton
    ROBOT_LIBRARY_SCOPE = LibraryScope
    KEYWORDS = {}

    def __init__(self, testdata=None, *shared_directory):
        """
        During initilization adds dynamically all library methods to library
        """
        super(QAutoRobot, self).__init__()

        # Test data file to use in library
        self.test_data_file = testdata

        # Set directory's to add
        self.default_directory = DefaultDirectory
        self.shared_directory = [x for x in shared_directory]
        self.directory = self.default_directory + self.shared_directory

        # Set all dynamic imports
        self.dynamically_import_librarys()

    def update_project_modules(self):
        """
        Update project modules

        :return: None
        """
        for directory in self.directory:
            library_files = self.get_library_files_in_directory(directory)

            for _file in library_files:
                module = ".".join([directory, _file.replace(".py", "")])
                if module in sys.modules:
                    try:
                        full_path = os.path.join(os.getcwd(), directory, _file)
                        imp.load_source(module, full_path)
                    except Exception, e:
                        print "Failed to reload module: %s\n%s" % (module, repr(e))

        for directory in self.directory:
            self.remove_module_methods(directory)

        self.dynamically_import_librarys()

    def dynamically_import_librarys(self):
        """
        Dynamically add all library methods to library

        :return: None
        """
        sys.modules[LibraryAttributeName] = self

        # Set test data methods to library if test data file set
        if self.test_data_file:
            set_parameter_file(self.test_data_file)
            self.set_testdata_methods()
        else:
            self.warning(WarningNoTestData)

        # Set all methods that are used in file operations
        self.set_file_operation_methods()

        sys.path.append(os.getcwd())
        # Set directory methods into library
        for directory in self.directory:
            # Append path to 1 up in directory
            sys.path.append(os.path.join(directory, ".."))
            self.set_module_methods(directory)

    def set_file_operation_methods(self):
        """
        Set testdata methods from global testdata to class

        :return: None
        """
        method_names = self.get_class_method_names(FileOperations)
        for _method_name in method_names:
            # Get method
            _method = getattr(FileOperations, _method_name)
            # Set testdata method into library
            self.set_attribute(self, _method_name, _method)

    def set_testdata_methods(self):
        """
        Set testdata methods from global testdata to class

        :return: None
        """
        # Get global testdata for adding method into library
        testdata = get_global_testdata()

        method_names = self.get_class_method_names(TestData)
        for _method_name in method_names:
            # Get method
            _method = getattr(testdata, _method_name)
            # Set testdata method into library
            self.set_attribute(self, _method_name, _method)

    def remove_module_methods(self, directory):
        """
        Remove methods and libary's in given directory from class

        :param directory: Directory where library files are
        :return: None
        """
        library_files = self.get_library_files_in_directory(directory)

        for library in library_files:
            try:
                # Make library name from
                library = os.path.basename(library).replace(".py", "")
                # Import library module
                _import = "{}.{}".format(os.path.basename(directory), library)
                # Import keyword module
                _module = reload(__import__(_import, fromlist=['']))
                # Find library name from module
                library_name = self.find_library_class_name_from_module(_module, library)
                if not library_name:
                    break
                # Get keyword library from module
                _class = getattr(_module, library_name)
                self.remove_library_module_methods(library, _class)
            except Exception as e:
                pass

    def set_module_methods(self, directory):
        """
        Set all module methods from path to class

        :param dir: Path to directory
        :return: None
        """
        # Find all library files from the directory
        # If folder does not exist abort setting modules
        library_files = self.get_library_files_in_directory(directory)

        for library in library_files:
            try:
                # Make library name from
                library = os.path.basename(library).replace(".py", "")
                # Import library module
                _import = "{}.{}".format(os.path.basename(directory), library)
                # Import keyword module
                _module = reload(__import__(_import, fromlist=['']))
                # Find library name from module
                library_name = self.find_library_class_name_from_module(_module, library)
                if not library_name:
                    break
                # Get keyword library from module
                _class = getattr(_module, library_name)
                self.set_library_module_methods(library, _class)
            except Exception as e:
                self.warning(library + ": " + str(e))

    def find_library_class_name_from_module(self, _module, library):
        """
        Find class name to use from module

        :param _module: Python module to find classes from
        :param library: Library class name
        :return: Class name or None
        """
        clsmembers = inspect.getmembers(_module, inspect.isclass)
        clsmembers = [x[0] for x in clsmembers if library.lower() in x[0].lower()]
        clsmembers = [x for x in clsmembers if library.lower() == x.lower()]
        try:
            return clsmembers[0]
        except IndexError:
            return None

    def remove_library_module_methods(self, library, _class):
        """
        Remove library module_methods from class

        :param library: Library class name
        :param _class: Library class object
        :return: None
        """
        # List of method names in python lib object (ignore private methods)
        method_names = self.get_class_method_names(_class)
        for _method_name in method_names:
            # Set python library object
            self.remove_attribute(self, library)
            # Set method with library name + . + method name
            self.remove_attribute(self, library + "." + _method_name)
            # Set method with method name
            self.remove_attribute(self, _method_name)

    def set_library_module_methods(self, library, _class):
        """
        Set library methods to qautorobot

        :param library: Library class name
        :param _class: Library class object
        :return: None
        """
        # Library class for python lib object
        library_class = _class()
        # List of method names in python lib object (ignore private methods)
        method_names = self.get_class_method_names(_class)
        for _method_name in method_names:
            # Get method
            _method = getattr(library_class, _method_name)
            # Set python library object
            self.set_attribute(self, library, library_class, rename_duplicate=False)
            # Set method with library name + . + method name
            self.set_attribute(self, library + "." + _method_name, _method, rename_duplicate=True)
            # Set method with method name
            self.set_attribute(self, _method_name, _method, rename_duplicate=True)

    @staticmethod
    def remove_attribute(_class, _name):
        """
        Remove attribute

        :param _class: Class to add attribute into
        :param _name: Name for given attribute
        :return: None
        """
        delattr(_class, _name)

    def set_attribute(self, _class, _name, _attr, rename_duplicate=True, depth=0):
        """
        Checks that attribute does not exist. If id does not add it to class

        :param _class: Class to add attribute into
        :param _name: Name for given attribute
        :param _attr: Attribute to add
        :param rename_duplicate: Add attribute with rename if True
        :param depth: Keeps count of recursion depth
        :return: None
        """
        try:
            # Tries to get the attribute to check that it does not exist
            # If it does exist call function again with different name
            _attr = getattr(_class, _name)
            if rename_duplicate:
                depth += 1
                duplicate_name = self.generate_duplicate_name(_name, depth)
                self.set_attribute(_class, duplicate_name, _attr, depth=depth)
        except AttributeError:
            setattr(_class, _name, _attr)
        self.KEYWORDS[_name] = _attr

    def generate_duplicate_name(self, _name, depth):
        """
        Generate name for duplicate method

        :param _name: Current method name
        :param _count: Recursion depth
        :return:
        """
        # If depth is deeper than 1 remove old duplicate count number
        if depth >= 1:
            _name = _name[:-1]
        return _name + str(depth)

    @staticmethod
    def get_class_methods(_class):
        """
        Get all class methods

        :param _class: Class to add attribute into
        :return: List of class methods
        """
        return [x for x, y in _class.__dict__.items() if type(y) == FunctionType]

    @classmethod
    def get_class_method_names(cls, _class):
        """
        Get class methods list from class

        :param _class: Python class
        :return: None
        """
        return [_name for _name in cls.get_class_methods(_class) if not _name.startswith("_")]

    def get_library_files_in_directory(self, directory):
        """
        Get all library files in directory

        :return: Library files list
        """
        try:
            return [_file for _file in os.listdir(directory) if _file.endswith(".py") and not _file.startswith("__")]
        except OSError as e:
            self.warning(WarningDirectoryNotFound + str(e))
            return []

    @staticmethod
    def get_testdata():
        """
        Get global test data object

        :return: Global testdata object
        """
        return get_global_testdata()

    @staticmethod
    def get_failure_image_path(test_case):
        """
        Get image path to failure image

        :param test_case: Test case name
        :return: image_path
        """
        image_path = os.path.join(os.getcwd(), TestReportFolder, test_case.replace(" ", "_") + ".png")
        return image_path

    @staticmethod
    def generate_failure_documentation(documentation, test_case):
        """
        Get image path to failure image

        :param documentation: Documentation string
        :param test_case: Test case name
        :return: image_path
        """
        test_case = test_case.replace(" ", "_")
        documentation = "{}\n\nRecording: [{}.ogg|recording]\n\n[{}.png|image]".format(documentation,
                                                                                       test_case, test_case)
        return documentation

    def run_keyword(self, method_name, args):
        """
        Run QAutoRobot project keywords

        :param method_name: String method name
        :param args: String arguments
        :return: Method return
        """
        _method = self.KEYWORDS[method_name]

        if args:
            _return = _method(eval(args))
        else:
            _return = _method()

        return _return

    def start_recording(self, test_case):
        """
        Start screencast recording

        :return: None
        """
        record_path = os.path.join(os.getcwd(), TestReportFolder, test_case.replace(" ", "_") + ".ogg")
        self.recorder = VlcRecorder(record_path)
        self.recorder.start()

    def stop_recording(self):
        """
        Stop screencast recording

        :return: Path to recording file
        """
        self.recorder.stop()
        return self.recorder.get_file()
