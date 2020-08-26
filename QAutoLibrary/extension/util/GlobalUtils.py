"""
#    QAutomate Ltd 2018. All rights reserved.
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
import os
import re
import sys
import traceback
from sys import platform as _platform


def throw_error(error_msg):
    """
    Raise own exception

    :param error_msg: error_msg message as String
    :return: Exception and message
    """
    print("_____________________________________________________")
    print(traceback.print_exc())
    print("_____________________________________________________")
    info = "".join(traceback.format_tb(sys.exc_info()[2]))
    linenumber = ""
    for m in re.finditer(r"\\(.*)line(.*),", info):
        linenumber = info[m.start() - 2:m.end() - 1]
        break
    raise Exception('\n'.join(["\n", linenumber, error_msg]))


class Singleton(type):
    """
    Singleton class for making singleton classes
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):  # @NoSelf
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GlobalUtils(object):

    # extensions
    PY = ".py"
    XML = ".xml"
    PNG = ".png"
    ROBOT = ".robot"

    # Testing script TESTDATA variable
    TESTDATA = "TESTDATA"

    LINUX = "linux"
    WINDOWS = "windows"

    # QAutoLibrary project directory paths
    SITE_PACKAGES_QAUTOLIBRARY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    WEBDRIVERS_PATH = os.path.join(SITE_PACKAGES_QAUTOLIBRARY_PATH, "webdrivers")

    QAUTOLIBRARY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    CONFIG_PATH = os.path.join(QAUTOLIBRARY_PATH, "config")
    EXTENSION_PATH = os.path.join(QAUTOLIBRARY_PATH, "extension")
    JS_HELPERS_PATH = os.path.join(EXTENSION_PATH, "js_helpers")

    # Webdriver paths
    RESOURCES_GECKO32_PATH = os.path.join(WEBDRIVERS_PATH, "geckodriver_win32")
    RESOURCES_GECKO64_PATH = os.path.join(WEBDRIVERS_PATH, "geckodriver_win64")
    RESOURCES_LINUX_GECKO64_PATH = os.path.join(WEBDRIVERS_PATH, "geckodriver_linux64")
    RESOURCES_LINUX_CHROME64_PATH = os.path.join(WEBDRIVERS_PATH, "chromedriver_linux64")
    RESOURCES_CHROME32_PATH = os.path.join(WEBDRIVERS_PATH, "chromedriver_win32")
    RESOURCES_EDGE_PATH = os.path.join(WEBDRIVERS_PATH, "msedgedriver")
    RESOURCES_IE_PATH = os.path.join(WEBDRIVERS_PATH, "ie_win")

    BROWSER_CONFIG_FILE_FRAMEWORK = os.path.join(CONFIG_PATH, "browser_config.xml")
    SPINNER_LOCATOR_FILE = "spinner_locators.txt"
    FRAMEWORK_SPINNER_LOCATORS_FILE = os.path.join(CONFIG_PATH, SPINNER_LOCATOR_FILE)

    # JS helpers used in QAutoSelenium methods
    DRAG_DROP_HELPER = os.path.join(JS_HELPERS_PATH, "drag_and_drop_helper.js")
    JQUERY_LOADER_HELPER = os.path.join(JS_HELPERS_PATH, "jquery_load_helper.js")

    SCREENSHOTS_XML_FILE = "screenshots.xml"

    # QAutoLibrary testing project directory's
    PM_FOLDER_NAME = "pagemodel"
    TESTS_FOLDER_NAME = "tests"
    PYTHON_VAR_FOLDER_NAME = "variables"
    SCRIPTS_FOLDER_NAME = "scripts"
    DATA_FOLDER_NAME = "data"
    MEASUREMENTS_FOLDER_NAME = "measurements"
    COMMON_LIB_FOLDER_NAME = "common_lib"

    TOOL_CACHE = "tool_cache"
    GECKODRIVER_LOG = os.path.join(TOOL_CACHE, "geckodriver.log")
    COMPARE_SCREENSHOT = os.path.join(TOOL_CACHE, "compare_screenshot.png")
    CURRENT_SCREENSHOT = os.path.join(TOOL_CACHE, "current_screenshot.png")

    # Config file folder structure
    CONFIG_DIR = "config"
    # Folders inside config folder
    PROJECT_CONFIG_DIR = os.path.join(CONFIG_DIR, "project_config")
    COMMENT_CONFIG_DIR = os.path.join(CONFIG_DIR, "comment_config")
    DOCUMENT_CONFIG_DIR = os.path.join(CONFIG_DIR, "document_config")
    REPORT_CONFIG_DIR = os.path.join(CONFIG_DIR, "report_config")
    # Project configs
    BROWSER_CONFIG_FILE = os.path.join(PROJECT_CONFIG_DIR, "browser_settings.xml")
    PROJECT_SETTINGS_FILE = os.path.join(PROJECT_CONFIG_DIR, "project_settings.xml")
    PROJECT_SPINNER_LOCATORS_FILE = os.path.join(PROJECT_CONFIG_DIR, SPINNER_LOCATOR_FILE)

    COMMON_PARAMETERS_FOLDER_NAME = os.path.join(DATA_FOLDER_NAME, "common_parameters")
    SCREENSHOTS_FOLDER_NAME = os.path.join(DATA_FOLDER_NAME, "screenshots")
    LOGIN_FOLDER_NAME = os.path.join(DATA_FOLDER_NAME, "login")

    XML_FOLDER_NAME = os.path.join(DATA_FOLDER_NAME, "xml")
    XML_REQUEST_FOLDER_NAME = os.path.join(XML_FOLDER_NAME, "requests")
    XML_RESPONSE_FOLDER_NAME = os.path.join(XML_FOLDER_NAME, "response")
    XML_DEBUG_FOLDER_NAME = os.path.join(XML_FOLDER_NAME, "debug")

    JSON_FOLDER_NAME = os.path.join(DATA_FOLDER_NAME, "json")
    JSON_REQUEST_FOLDER_NAME = os.path.join(JSON_FOLDER_NAME, "requests")
    JSON_RESPONSE_FOLDER_NAME = os.path.join(JSON_FOLDER_NAME, "response")
    JSON_DEBUG_FOLDER_NAME = os.path.join(JSON_FOLDER_NAME, "debug")

    SOAP_FOLDER_NAME = os.path.join(DATA_FOLDER_NAME, "soap")
    SOAP_REQUEST_FOLDER_NAME = os.path.join(SOAP_FOLDER_NAME, "requests")
    SOAP_RESPONSE_FOLDER_NAME = os.path.join(SOAP_FOLDER_NAME, "response")
    SOAP_DEBUG_FOLDER_NAME = os.path.join(SOAP_FOLDER_NAME, "debug")

    NAVIGATION_DATA_PREFIX = "navigation_"
    RESOURCE_DATA_PREFIX = "resource_"
    MEMORY_DATA_PREFIX = "memory_"

    # Browser names for selenium
    BROWSER_NAME = "browser_name"
    BROWSER_NAMES = ["ie", "ff", "gc", "me", "sf", "op", "aa"]
    BROWSER_FULL_NAMES = {
        "ie": "Internet Explorer",
        "ff": "Firefox",
        "gc": "Chrome",
        "me": "MicrosoftEdge",
        "sf": "Safari",
        "op": "Opera"
    }

    IE = "ie"

    @classmethod
    def is_linux(cls):
        return cls.LINUX in _platform
