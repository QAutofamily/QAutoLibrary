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
from pathlib import Path
from sys import platform as _platform


# TODO: Pathlib. This is the way. -The Mandalorian, 2020
from QAutoLibrary.FileOperations import get_file_lines_without_newlines, save_content_to_file


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
    CSV = ".csv"
    PYC = ".pyc"
    JSON = ".json"
    JSON_ENC = ".json.enc"
    ROBOT = ".robot"
    EXTENSION_LIST = [PY, PNG]


    # Testing script TESTDATA variable
    TESTDATA = "TESTDATA"

    LINUX = "linux"
    WINDOWS = "windows"

    # QAutoLibrary project directory paths
    SITE_PACKAGES_QAUTOLIBRARY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    WEBDRIVERS_PATH = os.path.join(Path.home(), "webdrivers") #os.path.join(SITE_PACKAGES_QAUTOLIBRARY_PATH, "webdrivers")

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

    # QAutoLibrary testing project directory's
    PM_FOLDER_NAME = "pagemodel"
    TESTS_FOLDER_NAME = "tests"
    PYTHON_VAR_FOLDER_NAME = "variables"
    SCRIPTS_FOLDER_NAME = "scripts"
    DATA_FOLDER_NAME = "data"
    MEASUREMENTS_FOLDER_NAME = "measurements"
    COMMON_LIB_FOLDER_NAME = "common_lib"

    if getattr(sys, 'frozen', False):
        TOOL_CACHE_PATH = os.path.abspath(os.path.join(sys._MEIPASS, "tool_cache"))
        TOOL_CACHE = os.path.abspath(os.path.join(sys._MEIPASS, "tool_cache"))
    else:
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


    # TODO: QUADRUPLE CHECK THE GLOBALS BEFORE MAIN
    ############################
    # QAutoRobot functionality #
    ############################
    COMMON_RESOURCES_FILENAME = "common_resources.robot"
    COMMON_RESOURCES_PATH = Path(os.getcwd()) / "resources" / COMMON_RESOURCES_FILENAME
    if getattr(sys, 'frozen', False):
        QAUTOROBOT_PATH = os.getcwd()
        WEBFRAMEWORK_PATH = os.path.abspath(os.path.join(QAUTOROBOT_PATH, 'resources'))
        RESOURCES_PATH = WEBFRAMEWORK_PATH
    else:
        QAUTOROBOT_PATH = os.getcwd()
        WEBFRAMEWORK_PATH = os.path.abspath(os.path.join(QAUTOROBOT_PATH, 'resources'))
        RESOURCES_PATH = WEBFRAMEWORK_PATH


    USED_DIRS_FILE = "working_dir.cfg"

    GLOBAL_SETTINGS_FILE = "global_settings.xml"
    SCREENSHOTS_XML_FILE = "screenshots.xml"
    CANVAS_ELEMENTS_FILE = "canvas_elements.xml"
    AUTOGEN_PARAMETERS = "autogen_parameters.xml"

    URLS_FILE = "saved_urls.txt"
    TEST_SET_SETUP_AND_TEARDOWN_METHODS = ["setUp", "tearDown", "tearDownTestSet", "setUpTestSet"]

    home_dir = os.path.expanduser("~")
    if os.path.isdir(os.path.join(home_dir, "qautomate")):
        home_dir = os.path.join(home_dir, "qautomate")

    TECHILA_SETTINGS_FILE = os.path.join(home_dir, "techila.json")

    GLOBAL_SETTINGS_FILE = "global_settings.xml"



    SUPPORT_EMAIL = "support@qautomate.fi"
    TERMS_PAGE_URL = "https://qautomate.fi/qautomate-privacy-policy"
    LICENSE_PAGE_URL = "https://qautomate.fi/qautomate-license"
    SUPPORT_PAGE_URL = "http://www.qautomate.fi/"
    LICENSE_SERVER_URL = "https://customer.qautomate.fi/"
    TEAM_LICENSE_PAGE = "teamLicense.html"
    UPDATE_INFO_PAGE = "getLatestQautorobotUpdate.html"
    PURCHASE_PAGE_URL = "https://qautomate.fi/purchase/"

    _ICON16 = os.path.join(RESOURCES_PATH, "icons", "icon_16x16.png")
    _ICON32 = os.path.join(RESOURCES_PATH, "icons", "icon_32x32.png")
    _ICON48 = os.path.join(RESOURCES_PATH, "icons", "icon_48x48.png")
    _ICON128 = os.path.join(RESOURCES_PATH, "icons", "icon_128x128.png")
    _ICON256 = os.path.join(RESOURCES_PATH, "icons", "icon_256x256.png")

    TOOL_FRAMEWORK_FOLDER_NAME = "webframework"
    ROBOT_FOLDER_NAME = "robot"
    RESOURCES_FOLDER_NAME = "resources"

    DOCUMENTATION_TEMPLATE_PATH = os.path.join(RESOURCES_PATH, "templates", "documentation_template.md")

    PAGEMODEL_IMAGE_FOLDER = "images"

    GIT_IGNORE_FOLDER_NAME = ".gitignore"
    GIT_IGNORE_TEMPLATE = """*.py[co]
    .pyc
    test_reports
    tool_cache
    """
    # TODO: These are not the only ones that need to be changed.
    # Will take a while to find them all, since they are a bit rare.
    if getattr(sys, 'frozen', False):
        FLOW_EXTENSION_PATH = os.path.abspath(os.path.join(sys._MEIPASS, "src", "extension"))
        _BROWSER_CONFIG_FILE_FRAMEWORK = os.path.join(os.getcwd(), "config", "browser_config.xml")
        _EDITOR_FONT_SETTINGS = os.path.join(os.getcwd(), "config", "editor_font_settings.ini")
        _LICENSE_TEAM_FILE = os.path.join(os.getcwd(), "alive_host")
        TOOL_HOME_PAGE = "file:///" + os.path.join(RESOURCES_PATH, "startpage", "start.html")
        TOOL_CACHE_PATH = os.path.abspath(os.path.join(sys._MEIPASS, "tool_cache"))
        TOOL_CACHE = os.path.abspath(os.path.join(sys._MEIPASS, "tool_cache"))
    else:
        FLOW_EXTENSION_PATH = os.path.abspath(os.path.join(QAUTOROBOT_PATH, 'src', 'extension'))
        _BROWSER_CONFIG_FILE_FRAMEWORK = os.path.join(WEBFRAMEWORK_PATH, "config", "browser_config.xml")
        _EDITOR_FONT_SETTINGS = os.path.join(WEBFRAMEWORK_PATH, "config", "editor_font_settings.ini")
        _LICENSE_TEAM_FILE = os.path.join(RESOURCES_PATH, "alive_host")
        TOOL_CACHE_PATH = os.path.abspath(os.path.join(QAUTOROBOT_PATH, 'tool_cache'))
        TOOL_HOME_PAGE = "file:///" + os.path.join(RESOURCES_PATH, "startpage", "start.html")

    REPORT_DOCUMENTATION_INDEX = os.path.join("test_reports", "report.html")

    COMPARE_SCREENSHOT = os.path.join(TOOL_CACHE, "compare_screenshot.png")
    CURRENT_SCREENSHOT = os.path.join(TOOL_CACHE, "current_screenshot.png")
    SCREENSHOT = os.path.join(TOOL_CACHE, "screenshot.png")
    TEMP_FRAME_SCREENSHOT = os.path.join(TOOL_CACHE, "temp_frame_screenshot.png")

    _BY_TYPES = ['id', 'link_text', 'class_name', 'css_selector', 'xpath']

    USED_TEST_SET_FILES = os.path.join(TOOL_CACHE, "test_set.txt")
    USED_TEST_FLOW_FILES = os.path.join(TOOL_CACHE, "test_flow.txt")
    USED_PAGEMODEL_FILES = os.path.join(TOOL_CACHE, "pagemodel.txt")
    TRACEBACK_FILE = os.path.join(TOOL_CACHE, "traceback.txt")
    LATEST_WORKING_DIR = os.path.join(TOOL_CACHE, "latest_working_dir.zip")
    GECKODRIVER_LOG = os.path.join(TOOL_CACHE, "geckodriver.log")
    # data
    _DATA_FOLDER_NAME = "data"
    _COMMON_PARAMETERS_FOLDER_NAME = os.path.join(_DATA_FOLDER_NAME, "common_parameters")
    _SCREENSHOTS_FOLDER_NAME = os.path.join(_DATA_FOLDER_NAME, "screenshots")
    _IMAGE_FOLDER_NAME = "images"
    _MEASUREMENTS_FOLDER_NAME = "measurements"

    RESOURCES_FOLDER_NAME = "resources"
    _STRUCTURE_XML_FILENAME = "structure.xml"
    _STRUCTURE_GV_FILENAME = "structure.gv"

    _NAVIGATION_DATA_PREFIX = "navigation_"
    _RESOURCE_DATA_PREFIX = "resource_"
    _MEMORY_DATA_PREFIX = "memory_"

    _ROOT_MODEL_NAME = "open_application"
    _ROOT_MODEL_METHOD_NAME = "open_application_url"
    _ROOT_NODE_INDEX = "1."
    _ROOT_NODE_FULL_TEXT = "1. " + _ROOT_MODEL_NAME
    _EXIT_NODE_INDEX = "2."
    _PARAMETERS = "parameters"

    _HTTP_PROTOCOL = "http://"
    _HTTPS_PROTOCOL = "https://"

    _BUILD_TYPE_STABLE = "stable"
    _BUILD_TYPE_DAILY = "daily"

    _WINDOWS_LONG_FILENAME_PRFIX = "\\\\?\\"

    _BROWSER_NAME = "browser_name"
    _BROWSER_NAMES = ["ie", "ff", "gc", "me", "aa"]
    _BROWSER_FULL_NAMES = {"ie": "Internet Explorer",
                           "ff": "Firefox",
                           "gc": "Chrome",
                           "me": "MicrosoftEdge"}
    _SCREENSHOT_NAMES = ["sh1", "sh2", "sh3"]
    _SCREENSHOT_FULL_NAMES = {"sh1": "Screenshot1", "sh2": "Screenshot2", "sh3": "Screenshot3"}

    _SH1 = "sh1"
    _SH2 = "sh2"
    _SH3 = "sh3"
    _FIREFOX = "ff"
    _CHROME = "gc"
    _IE = "ie"

    _PM_TESTCASE_MAX_LENGTH = 50

    _ACCEPTABLE_WEB_ELEMENTS = ['a', 'abbr', 'acronym', 'address', 'area',
                                'article', 'aside', 'audio', 'b', 'big', 'blockquote', 'br', 'button',
                                'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup',
                                'command', 'datagrid', 'datalist', 'dd', 'del', 'details', 'dfn',
                                'dialog', 'dir', 'div', 'dl', 'dt', 'em', 'event-source', 'fieldset',
                                'figcaption', 'figure', 'footer', 'font', 'form', 'frame', 'header', 'h1',
                                'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'iframe', 'img', 'input', 'ins',
                                'keygen', 'kbd', 'label', 'legend', 'li', 'm', 'map', 'menu', 'meter',
                                'multicol', 'nav', 'nextid', 'ol', 'output', 'optgroup', 'option',
                                'p', 'pre', 'progress', 'q', 's', 'samp', 'section', 'select',
                                'small', 'sound', 'source', 'spacer', 'span', 'strike', 'strong',
                                'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'time', 'tfoot',
                                'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var', 'video']

    _PYTHON = "Python"
    _JAVA = "Java"

    _PERF_INITIAL_NODE_NAME = "b"
    _PERF_INITIAL_ACTION_NAME = "action_b"

    _BY_TYPES = ['id', 'link_text', 'class_name', 'css_selector', 'xpath']

    _NOT_SUPPORTED_INPUT_TYPES = ["image", "button", "hidden", "submit"]

    _FORM_TAG_LIST = ["input", "select", "textarea"]

    _USE_ID_INPUT_TYPES = ['checkbox', 'radio']

    _PREFERRED_ATTRIBUTES = ['id', 'name', 'value', 'type', 'alt']

    _ID_BLOCK_LIST = ["ember"]

    _DESIGNER_SELENIUM_TIMEOUT = 10
    _VIEWER_TEST_EXECUTOR_TIMEOUT = 20
    _MAX_GENERATOR_URLS_SHOWN = 10
    _TEST_DATA_COLUMN_WIDTH_SMALL = 200
    _TEST_DATA_COLUMN_WIDTH_BIG = 500

    _DEFAULT_SCREENSHOT_SIMILARITY_LEVEL = 98

    _UPDATED_PAGEMODEL_SUFFIX = "_temp_updated"

    # proxy options
    _PERF_CONTROL_PACKET_URL = "http://ixonos.visualtest/visualtest"
    _PERF_PROXY_ADDR = "127.0.0.1"
    _PERF_PROXY_PORT = "3128"

    _CSV_HEADERS = ["OBJECT_NAME", "LOCATOR", "VALUE", "X_COORD", "Y_COORD", "WIDTH", "HEIGHT"]
    _CSV_COMMA_CHAR = "@@@"

    _ONLINE_TEST_REPORT_FILE = "LOG_model_execution.txt"

    _METHOD_TYPE_INPUT = "input"
    _METHOD_TYPE_VERIFICATION = "verification"
    _METHOD_TYPE_PRECONDITION = "precondition"
    _METHOD_TYPE_LIST = [_METHOD_TYPE_INPUT, _METHOD_TYPE_VERIFICATION, _METHOD_TYPE_PRECONDITION]

    _CANVAS_TMPL = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head></head>
    <body>
    <canvas align="left" id="myCanvas" width="1920" height="5200"></canvas>
        <script>
          var canvas = document.getElementById('myCanvas');
          var context = canvas.getContext('2d');
          var imageObj = new Image();
          var urlVars = getUrlVars();

        function resize_canvas() {
        canvas.width  = imageObj.width;
        canvas.height = imageObj.height;
        }

        function getUrlVars() {
        var vars = {};
        var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi,
        function(m,key,value) {
          vars[key] = value;
        });
        return vars;
        }
          imageObj.onload = function() {
            console.log(imageObj.width, imageObj.height);
            resize_canvas();
            context.drawImage(imageObj, 0, 0);
            context.beginPath();
            context.lineWidth="2";
            context.strokeStyle=urlVars["border"];

            context.globalAlpha=0.5;
            context.rect(urlVars["x"],urlVars["y"],urlVars["w"],urlVars["h"]);
            context.fillStyle=urlVars["fill"];
            context.fill();
            context.stroke();


          };
          imageObj.src = urlVars["png"];
          // Red rectangle

        </script>
    </body>
    </html>"""

    @classmethod
    def reload_paths(cls):
        """
        Reloads resource paths based on valued set in RESOURCES_PATH and WEBFRAMEWORK_PATH

        Required when running utilities in non frozen state.
        """
        cls._ICON16 = str(Path(cls.RESOURCES_PATH) / "icons" / "icon_16x16.png")
        cls._ICON32 = str(Path(cls.RESOURCES_PATH) / "icons" / "icon_32x32.png")
        cls._ICON48 = str(Path(cls.RESOURCES_PATH) / "icons" / "icon_48x48.png")
        cls._ICON128 = str(Path(cls.RESOURCES_PATH) / "icons" / "icon_128x128.png")
        cls._ICON256 = str(Path(cls.RESOURCES_PATH) / "icons" / "icon_256x256.png")
        cls._BROWSER_CONFIG_FILE_FRAMEWORK = str(Path(cls.WEBFRAMEWORK_PATH) / "config" / "browser_config.xml")
        cls._EDITOR_FONT_SETTINGS = str(Path(cls.WEBFRAMEWORK_PATH) / "config" / "editor_font_settings.ini")
        cls._LICENSE_TEAM_FILE = str(Path(cls.RESOURCES_PATH) / "alive_host")
        cls.TOOL_HOME_PAGE = "file:///" + str(Path(cls.RESOURCES_PATH) / "startpage" / "start.html")
        cls.DOCUMENTATION_TEMPLATE_PATH = str(Path(cls.RESOURCES_PATH) / "templates" / "documentation_template.md")


    # Returns path to license file (user directory)
    # @return: Path to license file
    @classmethod
    def get_license_path(cls):
        home_dir = os.path.expanduser("~")
        ixo_dir = os.path.join(home_dir, "qautomate")
        if os.path.isdir(ixo_dir):
            return ixo_dir
        else:
            return home_dir

    @classmethod
    def get_root_model_name(cls):
        return cls._ROOT_MODEL_NAME

    @classmethod
    def get_root_model_method_name(cls):
        return cls._ROOT_MODEL_METHOD_NAME

    @classmethod
    def update_used_working_dir(cls, used_dir_file, used_dir):
        # save_content_to_file(used_dir, used_dir_file)
        remembered_dirs = 10
        dir_list = []
        update_needed = True
        try:
            dir_list = [x for x in get_file_lines_without_newlines(used_dir_file)
                        if os.path.isdir(os.path.join(x, cls.PM_FOLDER_NAME))]
            if used_dir in dir_list:
                if dir_list.index(used_dir) > 0:
                    dir_list.remove(used_dir)
                    dir_list.insert(0, used_dir)
                else:
                    update_needed = False
            elif len(dir_list) == remembered_dirs:
                dir_list.pop()
                dir_list.insert(0, used_dir)
            else:
                dir_list.insert(0, used_dir)
        except:
            dir_list.insert(0, used_dir)

        if update_needed:
            save_content_to_file("\n".join(dir_list), used_dir_file)

    @staticmethod
    def event_is_ctrl(event):
        return event.ControlDown()

    @staticmethod
    def event_is_ctrl_shift(event):
        return event.ControlDown() and event.ShiftDown()

    @staticmethod
    def event_is_ctrl_w(event):
        return ((event.ControlDown() or event.CmdDown()) and event.GetUnicodeKey() == 87)

    @staticmethod
    def event_is_ctrl_space(event):
        return ((event.ControlDown() or event.CmdDown()) and event.GetUnicodeKey() == 32)

    @staticmethod
    def event_is_ctrl_f(event):
        return ((event.ControlDown() or event.CmdDown()) and event.GetUnicodeKey() == 70)

    @staticmethod
    def event_is_ctrl_q(event):
        return ((event.ControlDown() or event.CmdDown()) and event.GetUnicodeKey() == 81)

    @staticmethod
    def event_is_ctrl_e(event):
        return ((event.ControlDown() or event.CmdDown()) and event.GetUnicodeKey() == 69)

    @staticmethod
    def event_is_ctrl_r(event):
        return ((event.ControlDown() or event.CmdDown()) and event.GetUnicodeKey() == 82)

    @staticmethod
    def event_is_ctrl_s(event):
        return ((event.ControlDown() or event.CmdDown()) and event.GetUnicodeKey() == 83)

    @classmethod
    def is_id_in_bloclist(cls, _id):
        for id_block in cls._ID_BLOCK_LIST:
            if id_block in _id:
                # id is in blocklist
                return True
        return False
    ###############
    # /QAutoRobot #
    ###############

