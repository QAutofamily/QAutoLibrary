import csv
import os
import random
import subprocess
import sys
import time
import traceback
import unittest
import requests
from PIL import Image  # @UnresolvedImport
from collections import OrderedDict
from datetime import datetime
from functools import wraps
from lxml import etree, html
from re import search
from urllib.error import URLError, HTTPError
from sys import platform as _platform

from logging import warn, log
from robot.libraries.BuiltIn import BuiltIn
from QAutoLibrary.Cryptomodule import AESCipher

from requests.auth import HTTPBasicAuth
from selenium.common.exceptions import WebDriverException, NoAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

from time import sleep
from simplejson import loads, dumps
from urllib3.exceptions import ConnectionError

from QAutoLibrary.extension.util.common_methods_helpers import CommonMethodsHelpers, DebugLog
from QAutoLibrary.extension.webdriver_cache.webdriver_cache import DriverCache
from QAutoLibrary.extension.util.GlobalUtils import GlobalUtils
from QAutoLibrary.extension.webdriver_cache.browser import create_driver
from QAutoLibrary.extension.config import get_config_value
from QAutoLibrary.extension.util.webtimings import get_measurements as webtimings_get_measurements
from QAutoLibrary.FileOperations import open_file, get_file_lines, save_content_to_file, get_file_content
from QAutoLibrary.extension.util.xml_screenshot_parser import XmlScreenshotParser

from QAutoLibrary.QAutoElement import QAutoElement

# TODO decide how to fix this
try:
    from QAutoLibrary.extension import XmlScreenshotParser
except:
    pass

ERROR_UNSUPPORTED_ELEMENT_TYPE = "Element type is unsupported"

JS_GET_XPATH_POSITION = """
function getNodeNumber(current) {
    var childNodes = current.parentNode.childNodes;
    var total = 0;
    var index = -1;
    for (var i = 0; i < childNodes.length; i++) {
        var child = childNodes[i];
        if (child.nodeName == current.nodeName) {
            if (child == current) {
              index = total;
            }
            total++;
        }
    }
    return index;
}

function getTestabilityPath(nodeName, testAttr, testAttrValue){
    return '/' + nodeName + '[@' + testAttr + '="' + testAttrValue + '"]';
}

function getRelativeXpath(current, testAttr){
    if (testAttr){
        var testAttrValue = current.getAttribute(testAttr);
        if (testAttrValue){
            return getTestabilityPath(current.nodeName.toLowerCase(), testAttr, testAttrValue);
        }
    }
    if (current.parentNode == null){
        return '/' + current.nodeName.toLowerCase();
    }
    var index = getNodeNumber(current);
    var currentPath = '/' + current.nodeName.toLowerCase();
    if (index >= 0) {
        currentPath += '[' + (index + 1) + ']';
    }
    return currentPath;
}

return getRelativeXpath(arguments[0], arguments[1]);
"""


class CommonMethods(object):
    """
    **Class that contains common methods**
    """

    def __init__(self, driver_cache=None):
        self.driver_cache = driver_cache and driver_cache or DriverCache()
        self.screenshot_parser = None
        self.last_element = None
        self.selenium_speed = 0

    def set_speed(self, timeout):
        """
        **Set selenium speed**

        :param timeout: timeout in seconds
        """
        self.selenium_speed = float(timeout)

    def find_element_if_not_webelement(self, element):
        """
        **Find element if its not selenium web element**

        :param element: element to find
        :return: Web element
        """
        # Set selenium speed
        sleep(self.selenium_speed)
        element_type = type(element)
        if element_type in [QAutoElement, tuple]:
            return self.find_element(element)
        elif element_type == WebElement:
            return element
        else:
            self.fail(ERROR_UNSUPPORTED_ELEMENT_TYPE)

    def fail(self, message):
        """
        **Message to print in report as a String**

        :param message: Message to print as a string.
        --------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.fail("My message")``

        """
        raise AssertionError(message)

    def warning(self, message):
        """
        **Adds warning to test report**

        :param message: Message to print as a String
        -----------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.warning("My message")``

        """
        message = "**WARN**Warning: %s*WARN*" % message
        warn(message)

    def measure_async_screen_response_time(self, measurement_name, timeout, reference_picture, element=None):
        """
        **Return page loading time based on screenshot verification**

        :param measurement_name: String represents name of measure point
        :param timeout: Int represents how long (in seconds) to take screenshots
        :param reference_picture: String represents name of the reference picture
        :param element: Tuple represents element: (By, 'value')

        :return:    return Time in seconds how long takes to find correct screenshot
                    or if no match found return False
        -------------
        :Example:
            | *Page model level*
            | ``QAutoRobot.measure_async_screen_response_time("trial", 10, "trial_perf_pic")``

        """
        driver = self.driver_cache._get_current_driver()
        perf_png_data_dict = OrderedDict()

        start = time.time()
        loop_time = start + int(timeout)
        while (loop_time > time.time()):
            png_data = driver.get_screenshot_as_png()
            elapsed = time.time() - start
            perf_png_data_dict[elapsed] = png_data
            del png_data

        # get reference screenshot metadata
        if not self.screenshot_parser:
            self.screenshot_parser = XmlScreenshotParser()
        xml_meta_data, ref_scr_file_name_path = CommonUtils._check_screenshot_file_name(self.screenshot_parser,
                                                                                        reference_picture)
        if xml_meta_data['area'] is True:
            ref_scr_x = int(xml_meta_data['x'])
            ref_scr_y = int(xml_meta_data['y'])
            ref_scr_w = int(xml_meta_data['w'])
            ref_scr_h = int(xml_meta_data['h'])
        else:
            if not element:
                print("Web element must be given, if using element screenshot")
                return False
            element = self.find_element_if_not_webelement(element)

            element_loc = element.location
            element_size = element.size
            ref_scr_x = int(element_loc['x'])
            ref_scr_y = int(element_loc['y'])
            ref_scr_w = int(element_size['width'])
            ref_scr_h = int(element_size['height'])

        if get_config_value("runtime_similarity") != '':
            similarity = get_config_value("runtime_similarity")
        else:
            similarity = int(xml_meta_data['similarity'])

        ref_scr_file_name = os.path.basename(ref_scr_file_name_path)
        scr_ref = Image.open(ref_scr_file_name_path)
        scr_ref_list = list(scr_ref.getdata())

        # save png data and compare to reference image
        save_dir = os.path.join(os.getcwd(), get_config_value("reporting_folder_run"), "perf_screenshots")
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        for elapsed, perf_png_data in perf_png_data_dict.items():
            perf_png = os.path.join(save_dir, "%s_%s.png" % (measurement_name, elapsed))
            try:
                with open(perf_png, 'wb') as f:
                    f.write(perf_png_data)
            except IOError:
                print("Failed to save screenshot: %s" % perf_png)
                continue

            scr_curr = Image.open(perf_png)
            scr_curr_subim = scr_curr.crop((ref_scr_x, ref_scr_y, ref_scr_x + ref_scr_w, ref_scr_y + ref_scr_h))

            scr_curr_list = list(scr_curr_subim.getdata())
            actual_screenshot = os.path.splitext(perf_png)[0] + "_actual.png"
            scr_curr_subim.save(actual_screenshot)

            unittest.TestCase("assertTrue").assertTrue(
                len(scr_curr_list) == len(scr_ref_list),
                "Screenshots size does not match. Reference screenshot: %s." % ref_scr_file_name
            )

            diff = 0
            for i in range(len(scr_curr_list)):
                diff = (diff + abs(int(scr_ref_list[i][0]) - int(scr_curr_list[i][0])) +
                        abs(int(scr_ref_list[i][1]) - int(scr_curr_list[i][1])) +
                        abs(int(scr_ref_list[i][2]) - int(scr_curr_list[i][2])))

            difference = round(100 * float(diff) / float(len(scr_curr_list) * 3 * 255), 2)
            is_similar = (100 - difference) >= similarity

            if is_similar:
                print("Comparing screenshots...  Screenshots match. Reference screenshot: %s. " +
                      "Similarity level is %s.") % (ref_scr_file_name, str(100 - difference) + "%")
                print("Match found and time was: %s" % elapsed)
                return elapsed
            else:
                print("Comparing screenshots... Screenshots do not match. Current screenshot: %s. " +
                      "Similarity level is %s.") % (os.path.basename(actual_screenshot), str(100 - difference) + "%")

        return False

    def _save_screen_element(self, x, y, w, h, image_name):
        driver = self.driver_cache._get_current_driver()
        driver.save_screenshot(os.getcwd() + os.sep + "test_reports" + os.sep + image_name);

        x = x
        y = y
        width = x + w
        height = y + h

        im = Image.open(os.getcwd() + os.sep + "test_reports" + os.sep + image_name)
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save(os.getcwd() + os.sep + "test_reports" + os.sep + image_name)

    def get_xpath(self, element):
        if element != None:
            xpath = ""
            driver = self.driver_cache._get_current_driver()
            try:
                current = element
                path = ''
                while current.tag_name.lower() != "html":
                    current_path = driver.execute_script(JS_GET_XPATH_POSITION, current)
                    path = current_path + path
                    xpath = '/' + path
                    elements = driver.find_elements_by_xpath(xpath)
                    if len(elements) == 1 and element == elements[0]:
                        break
                    current = driver.execute_script("return arguments[0].parentNode", current)

                return xpath
            except WebDriverException as e:
                print(str(e))
                return None
        else:
            return None

    def find_last_searched_element_details(self, element=None):
        """
        **Find element with last searched elements information**

        :return: Element details or none
        """
        if element == None:
            element = self.last_element_details()

        else:
            print("Element not found")
            return None

    def find_element_with_coordinates(self, x, y):
        """
        **Finds web element with coordinates**

        :param x: x position
        :param y: y position
        :return: Web element
        """
        driver = self.driver_cache._get_current_driver()
        elem_str = "return document.elementFromPoint(" + str(x) + ", " + str(y) + ")"
        return driver.execute_script(elem_str)

    def find_element(self, element):
        """
        **Return found WebElement**

        :param element: Element representation (By, value) or WebElement
        :return:   WebElement
        -------------
        :Example:
            | *Page model level*
            | ``element = QAutoRobot.find_element((By.LINK_TEXT, u'Trial'))``

        """
        self.last_element = element
        driver = self.driver_cache._get_current_driver()
        by = element[0]
        value = element[1]
        return driver.find_element(by, value)

    def find_elements(self, element):
        """
        **Return found list of WebElement's**

        :param element: Element representation (By, value) or WebElement
        :return:    List of WebElement's
        -------------
        :Example:
            | *Page model level*
            | ``all_elements = QAutoRobot.find_elements((By.CSS_SELECTOR, u"img"))``

        """
        self.last_element = element
        driver = self.driver_cache._get_current_driver()
        by = element[0]
        value = element[1]

        return driver.find_elements(by, value)

    def fallback_element(self, element, action, value=""):
        locator_by = element[0]
        locator_value = element[1]
        last_elem = self.last_element_details(True, action)

        if last_elem == None:
            msg = "Failed to click %s '%s, %s' after %s seconds" % (action,
                                                                    locator_by.upper(), locator_value,
                                                                    get_config_value("default_timeout"))
            self.fail(msg)
            return False

        if last_elem[0] == None and last_elem[1] == None:
            msg = "Failed to %s element '%s, %s' after %s seconds" % (action,
                                                                      locator_by.upper(), locator_value,
                                                                      get_config_value("default_timeout"))
            self.fail(msg)
            return False
        elif last_elem[1] != None:
            if action == "input":
                self.input_text_element_at_coordinates(last_elem[0], last_elem[1], last_elem[2], value)
                sleep(1)
            else:
                self.click_element_at_coordinates(last_elem[0], last_elem[1], last_elem[2])
                sleep(1)
            return True
        elif last_elem[0] != None:
            msg = "UI layout changed. Failed to %s element '%s, %s' after %s seconds" % (action,
                                                                                         locator_by.upper(),
                                                                                         locator_value,
                                                                                         get_config_value(
                                                                                             "default_timeout"))
            self.fail(msg)
            raise

    def last_element_details(self, fallback=False, action=""):
        self.print_keywords()
        try:
            x = self.last_element.coordinates[0]
            y = self.last_element.coordinates[1]
            w = self.last_element.size[0]
            h = self.last_element.size[1]

            driver = self.driver_cache._get_current_driver()
            dimensions = driver.get_window_size()
            BuiltIn().log("Searched element coordinates and size: x: " + str(x) + " y: " + str(y) + " w: " + str(
                w) + " h: " + str(h))
            # check if coordinates are empty or outside current screen
            if x and y and w and h and dimensions.get("height") > int(y) and dimensions.get("width") > int(x):
                test_name = BuiltIn().get_variable_value("${TEST NAME}")
                elem_middle_x = int(w) / 2
                elem_middle_y = int(h) / 2
                click_x = int(x) + elem_middle_x
                click_y = int(y) + elem_middle_y
                element = self.find_element_with_coordinates(click_x, click_y)
                element_size = element.size
                element_location = element.location

                locator_id = element.get_attribute('id')
                locator_class = element.get_attribute('class')
                element_tag_name = element.tag_name
                element_text = element.text
                element_size = element.size
                print("Found element id: " + locator_id)
                print("Found element class: " + locator_class)
                print("Found element tag name: " + element_tag_name)
                print("Found element text: " + element_text.replace("\n", " "))
                try:
                    htmldoc = element.find_element_by_xpath("parent::*").find_element_by_xpath(
                        "parent::*").get_attribute("innerHTML")
                except:
                    htmldoc = element.get_attribute("outerHTML")
                print("")

                document_root = html.fromstring(htmldoc)
                print(etree.tostring(document_root, encoding='unicode', pretty_print=True))
                self._save_screen_element(x, y, w, h, "Searched_" + test_name + "_" + action + "_element.png")
                BuiltIn().log("<img src='" + "Searched_" + test_name + "_" + action + "_element.png" + "'>", "HTML")
                BuiltIn().log("Current element coordinates and size:  x: " + str(element_location['x']) + " y: " + str(
                    element_location['y']) + " w: " + str(element_size['width']) + " h: " + str(element_size['height']))
                if fallback:
                    self._save_screen_element(element_location['x'], element_location['y'], element_size['width'],
                                              element_size['height'],
                                              "Current_" + test_name + "_" + action + "_element.png")
                    BuiltIn().log("<img src='" + "Current_" + test_name + "_" + action + "_element.png" + "'>", "HTML")

                if h == element_size['height'] and w == element_size['width']:
                    if fallback:
                        self.warning(
                            "#Fallback at coordinates ---> Testcase: " + test_name + " ---> Searched element locator is changed: " + str(
                                self.last_element.locator) + " .Element locator needs to be updated. ")
                    else:
                        self.warning("#Testcase: " + test_name + " ---> Searched element locator is changed: " + str(
                            self.last_element.locator) + " .Element locator needs to be updated. ")

                    return (element, str(int(elem_middle_x)), str(int(elem_middle_y)))
                else:
                    return (element, None, None)
        except Exception as e:
            return (None, None, None)

    def click_element(self, element, to_print=True):
        """
        **Click at element**

        :param element: Element representation (By, value) or WebElement
        :param to_print: Flag, if True prints action message
        --------------
        :Example:
            | *Page model level*
            | using web element
            | ``QAutoRobot.click_element(self.TRIAL)``
            | using representation
            | ``QAutoRobot.click_element((By.LINK_TEXT, u'Trial'))``
        """

        start = time.time()
        self.wait_until_element_is_visible(element, get_config_value("default_timeout"), "", True)
        self.wait_until_element_is_enabled(element, 1, "", True)
        end = time.time()
        duration = end - start
        click_timeout = get_config_value("default_timeout")
        if duration > 20:
            click_timeout = 3
        msg = "Failed to click element after %s seconds" % get_config_value("default_timeout")
        try:
            CommonMethodsHelpers.webdriver_wait(lambda driver: self._click_element(element, to_print),
                                                self.driver_cache._get_current_driver(), msg, click_timeout, False)
        except:
            self.fallback_element(element, "click")

    def _click_element(self, element, to_print=True):
        printout = ""
        locator_by = element[0]
        locator_value = element[1]

        web_element = self.find_element_if_not_webelement(element)
        element_loc = web_element.location
        try:
            if web_element.text != "":
                printout = "* Clicking at '%s' '%s:%s' in %s" % (
                web_element.text, locator_by, locator_value, str(element_loc))
            else:
                try:
                    printout = "* Clicking at '%s:%s' in %s" % (locator_by, locator_value, str(element_loc))
                except:
                    printout = "* Clicking at Unknown button"
        except:
            print("* Clicking at Unknown button")
        try:
            web_element.click()
        except WebDriverException as e:
            if "is not clickable at point" in e.msg:
                DebugLog.log("Retry click after exception: " + e.msg)
                return False
            else:
                DebugLog.log("Stopped running on WebDriverException: " + e.msg)
                raise

        if to_print:
            DebugLog.log(printout)
        return True

    def double_click_element(self, element, to_print=True):
        """
        **Double click at element**

        :param element: Element representation (By, value) or WebElement
        :param to_print: Flag, if True prints action message
        -------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.double_click_element(self.TRIAL)``
            | using representation
            | ``QAutoRobot.double_click_element((By.LINK_TEXT, u'Trial'))``

        """
        locator_by = element[0]
        locator_value = element[1]
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        web_element = self.find_element_if_not_webelement(element)
        if to_print:
            try:
                if web_element.text != "":
                    DebugLog.log("Double clicking at '%s' '%s:%s' in %s" % (
                    web_element.text, locator_by, locator_value, str(element_loc)))
                else:
                    try:
                        element_loc = web_element.location
                        DebugLog.log("Double clicking at '%s:%s' in %s" % (locator_by, locator_value, str(element_loc)))
                    except:
                        DebugLog.log("Double clicking at UNKNOWN BUTTON")
            except:
                DebugLog.log("Double clicking at UNKNOWN BUTTON")

        actions.double_click(web_element).perform()

    def triple_click_element(self, element, to_print=True):
        """
        **Triple click at element**

        :param element: Element representation (By, value) or WebElement
        :param to_print: Flag, if True prints action message
        -------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.triple_click_element(self.TRIAL)``
            | using representation
            | ``QAutoRobot.triple_click_element((By.LINK_TEXT, u'Trial'))``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        web_element = self.find_element_if_not_webelement(element)
        if to_print:
            try:
                if web_element.text != "":
                    DebugLog.log("* Triple clicking at '%s'" % web_element.text)
                else:
                    try:
                        element_information = repr(element)
                        element_loc = web_element.location
                        DebugLog.log("* Triple clicking at '%s'" % str(element_information) + str(element_loc))
                    except:
                        DebugLog.log("* Triple clicking at UNKNOWN BUTTON")
            except:
                DebugLog.log("* Triple clicking at UNKNOWN BUTTON")

        actions.click(web_element)
        actions.double_click(web_element)
        actions.perform()

    def click_element_at_coordinates(self, element, x, y, to_print=True):
        """
        **Clicks at the specified coordinates at element**

        :param element: Element representation (By, value) or WebElement
        :param x: x-coordinate
        :param y: y-coordinate
        :param to_print: Flag, if True prints action message
        --------------
        :Example:
            | *Page model level*
            | using web element
            | ``QAutoRobot.click_element_at_coordinates(self.TRIAL, 1, 1)``
            | using representation
            | ``QAutoRobot.click_element_at_coordinates((By.LINK_TEXT, u'Trial'), 1, 1)``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        web_element = self.find_element_if_not_webelement(element)
        if to_print:
            try:
                if web_element.text != "":
                    print("* Clicking at element (%s, %s, %s)" % (
                        web_element.text + " ", x + ",", y + " ") + " coordinates")
                else:
                    try:
                        element_information = repr(element)
                        element_loc = web_element.location
                        DebugLog.log("* Clicking at element (%s, %s, %s)" % (
                            str(element_information) + str(element_loc) + " " + x + ",", y + " ") + " coordinates")
                    except:
                        DebugLog.log("* Clicking at element (%s, %s, %s)" % (
                            "Unknown button" + " ", x + ",", y + " ") + " coordinates")
            except:
                DebugLog.log(
                    "* Clicking at element (%s, %s, %s)" % ("Unknown button" + " ", x + ",", y + " ") + " coordinates")
        actions.move_to_element(web_element).move_by_offset(x, y).click().perform()

    def input_text_element_at_coordinates(self, element, x, y, text, to_print=True):
        """
        **Clicks at the specified coordinates at element**

        :param element: Element representation (By, value) or WebElement
        :param x: x-coordinate
        :param y: y-coordinate
        :param to_print: Flag, if True prints action message
        --------------
        :Example:
            | *Page model level*
            | using web element
            | ``self.input_text_element_at_coordinates(self.TRIAL, 1, 1)``
            | using representation
            | ``self.input_text_element_at_coordinates((By.LINK_TEXT, u'Trial'), 1, 1)``
            |

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        web_element = self.find_element_if_not_webelement(element)
        if to_print:
            try:
                if web_element.text != "":
                    print("* Input text at element (%s, %s, %s)" % (
                        web_element.text + " ", x + ",", y + " ") + " coordinates")
                else:
                    try:
                        element_information = repr(element)
                        element_loc = web_element.location
                        DebugLog.log("* Input text at element (%s, %s, %s)" % (
                            str(element_information) + str(element_loc) + " " + x + ",", y + " ") + " coordinates")
                    except:
                        DebugLog.log("* Input text at element (%s, %s, %s)" % (
                            "Unknown button" + " ", x + ",", y + " ") + " coordinates")
            except:
                DebugLog.log(
                    "* Input at element (%s, %s, %s)" % ("Unknown button" + " ", x + ",", y + " ") + " coordinates")
        # actions.move_to_element(web_element).move_by_offset(x, y).send_keys_to_element(web_element, text).perform()
        actions.send_keys_to_element(web_element, text).perform()

    def input_text(self, element, value, to_print=True, encrypt=False):
        """
        **Clear and types text to input element**

        :param element: Element representation (By, value) or WebElement
        :param value: String to type in
        :param to_print: Flag, if True prints action message
        -------------
        :Example:
            | *Page model level*
            | using web element
            | ``QAutoRobot.input_text(self.ID_CONTACT_FIRST_NAME, "this is value")``
            | using representation
            | ``QAutoRobot.input_text((By.ID, u'contact_first_name'), "this is value")``

        """

        start = time.time()
        self.wait_until_element_is_visible(element, get_config_value("default_timeout"), "", True)
        end = time.time()
        duration = end - start
        input_timeout = get_config_value("default_timeout")
        if duration > 20:
            input_timeout = 3

        msg = "Failed to input text after %s seconds" % get_config_value("default_timeout")
        try:
            CommonMethodsHelpers.webdriver_wait(lambda driver: self._input_text(element, value, to_print, encrypt),
                                                self.driver_cache._get_current_driver(), msg, input_timeout, False)
        except:
            self.fallback_element(element, "input", value)

    def _input_text(self, element, value, to_print=True, encrypt=False):
        try:
            if encrypt:
                project_folder = os.getcwd()
                DebugLog.log("Encrypted password")
                _key = ""
                _key = get_file_content(project_folder + os.sep + "key.txt")

                cipher = AESCipher(_key)
                plain_password = cipher.decrypt(value)
                value = plain_password
        except Exception as e:
            DebugLog.log(e)

        locator_by = element[0]
        locator_value = element[1]
        web_element = self.find_element_if_not_webelement(element)
        valuelog = value
        try:
            elementtype = web_element.get_attribute("type")
            if elementtype == "password":
                valuelog = "***********"
        except Exception as e:
            print(e)

        if to_print:
            try:
                element_loc = web_element.location
                DebugLog.log("* Clear and Typing text '%s' into element field '%s:%s' in %s" % (
                    valuelog, locator_by, locator_value, element_loc))
            except:
                try:
                    DebugLog.log("* Clear and Typing text '%s' into element field 'Unknown element'" % valuelog)
                except:
                    DebugLog.log(
                        "* Clear and Typing text '%s' into element field 'Unknown element'" % valuelog.encode(
                            'ascii',
                            'ignore'))
        web_element.clear()
        value = CommonMethodsHelpers.contains_nonascii(value)
        web_element.send_keys(value)
        return True

    def send_keys(self, element, value, to_print=True):
        """
        **Type value to element**

        :param element: Element representation (By, value) or WebElement
        :param value: Value to type in to the element
        :param to_print: Flag, if True prints action message
        --------------
        :Example:
            | *Page model level*
            | using web element
            | ``QAutoRobot.send_keys(self.ID_CONTACT_FIRST_NAME, "this is value")``
            | using representation
            | ``QAutoRobot.send_keys((By.ID, u'contact_first_name'), "this is value")``

        """
        self.wait_until_element_is_visible(element)
        web_element = self.find_element_if_not_webelement(element)
        if to_print:
            try:
                element_information = repr(element)
                element_loc = web_element.location
                DebugLog.log(
                    "* Typing text '%s' into element field '%s'" % (value, str(element_information) + str(element_loc)))
            except:
                try:
                    DebugLog.log("* Typing text '%s' into element field '%s'" % (value, "Unknown button"))
                except:
                    DebugLog.log("* Typing text '%s' into element field '%s'" % (value.encode('ascii', 'ignore'),
                                                                                 "Unknown button"))
        value = CommonMethodsHelpers.contains_nonascii(value)
        web_element.send_keys(value)

    def wait_until_element_is_visible(self, element, timeout=None, msg=None, fallback=False):
        """
        **Wait until element specified is visible**

        :param element: Element representation (By, value) or WebElement object.
        :param timeout: Uses default timeout, unless custom value provided.
        :param msg: Message if element is not visible
        :exception:  If time exceeds DEFAULT_TIMEOUT, then rise exception.
        -------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_is_visible(self.TRIAL)``
            | using representation
            | ``QAutoRobot.common_utils.wait_until_element_is_visible((By.LINK_TEXT, u'Trial'))``
            | using timeout
            | ``QAutoRobot.wait_until_element_is_visible(self.TRIAL, 10)``
            | ``QAutoRobot.wait_until_element_is_visible((By.LINK_TEXT, u'Trial'), 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        if not msg:
            if type(element) in [tuple, QAutoElement]:
                msg = "Element '%s' is not visible for %s seconds" % (element[1], timeout)
            else:
                msg = "Element '%s' is not visible for %s seconds" % (element.text, timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_visible(element),
                                            self.driver_cache._get_current_driver(), msg, timeout, fallback)

    def wait_until_element_is_not_visible(self, element, timeout=None, msg=None):
        """
        **Wait until element specified is not visible**

        :param element: Element representation (By, value) or WebElement object.
        :param timeout: Uses default timeout, unless custom value provided.
        :param msg: Message if element is visible
        :exception:  If time exceeds DEFAULT_TIMEOUT, then rise exception.
        ------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_is_not_visible(self.TRIAL)``
            | using representation
            | ``QAutoRobot.common_utils.wait_until_element_is_not_visible((By.LINK_TEXT, u'Trial'))``
            | using timeout
            | ``QAutoRobot.wait_until_element_is_not_visible(self.TRIAL, 10)``
            | ``QAutoRobot.wait_until_element_is_not_visible((By.LINK_TEXT, u'Trial'), 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        if not msg:
            if type(element) in [tuple, QAutoElement]:
                msg = "Element '%s' is visible for %s seconds" % (element[1], timeout)
            else:
                msg = "Element '%s' is visible for %s seconds" % (element.text, timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: not self.is_visible(element),
                                            self.driver_cache._get_current_driver(), msg, timeout)
        print("Element (" + element[0] + ":" + element[1] + ") not visible in " + str(timeout) + " seconds")

    def wait_until_element_is_disabled(self, element, timeout=None, msg=None):
        """
        **Wait until element is disabled.**

        :param element: Element representation (By, value) or WebElement object.
        :param timeout: Uses default timeout, unless custom value provided.
        :param msg: Message if element is not disabled
        :exception:  If time exceeds DEFAULT_TIMEOUT, then rise exception.
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_is_disabled(self.TRIAL)``
            | using representation
            | ``QAutoRobot.common_utils.wait_until_element_is_disabled((By.LINK_TEXT, u'Trial'))``
            | using timeout
            | ``QAutoRobot.wait_until_element_is_disabled(self.TRIAL, 10)``
            | ``QAutoRobot.wait_until_element_is_disabled((By.LINK_TEXT, u'Trial'), 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        if not msg:
            if type(element) in [tuple, QAutoElement]:
                msg = "Element '%s' is not disabled after %s seconds" % (element[1], timeout)
            else:
                msg = "Element '%s' is not disabled after %s seconds" % (element.text, timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_disabled(element),
                                            self.driver_cache._get_current_driver(), msg, timeout)

    def wait_until_element_is_enabled(self, element, timeout=None, msg=None, fallback=False):
        """
        **Wait until element is enabled.**

        :param element: Element representation (By, value) or WebElement object.
        :param timeout: Uses default timeout, unless custom value provided.
        :param msg: Message if element is not enabled.
        :exception: If time exceeds DEFAULT_TIMEOUT, then rise exception.
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_is_enabled(self.TRIAL)``
            | using representation
            | ``QAutoRobot.common_utils.wait_until_element_is_enabled((By.LINK_TEXT, u'Trial'))``
            | using timeout
            | ``QAutoRobot.wait_until_element_is_enabled(self.TRIAL, 10)``
            | ``QAutoRobot.wait_until_element_is_enabled((By.LINK_TEXT, u'Trial'), 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        if not msg:
            if type(element) in [tuple, QAutoElement]:
                msg = "Element '%s' is not enabled after %s seconds" % (element[1], timeout)
            else:
                msg = "Element '%s' is not enabled after %s seconds" % (element.text, timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_enabled(element),
                                            self.driver_cache._get_current_driver(), msg, timeout, fallback)

    def get_download_time(self, downloads_folder="", max_download_time=120):
        """
                **Return file download time in Chrome**

                :param downloads_folder: Chrome download folder
                :param max_download_time: Max timeout to download
                :return: time
                ---------------
                :Example:
                    | *Page model level example*
                    | ``value = QAutoRobot.get_download_time()``

        """
        downloadtime = None
        path_to_downloads = ""
        if downloads_folder != "":
            path_to_downloads = downloads_folder
        else:
            if "win" in _platform:
                path_to_downloads = os.path.join(os.environ['USERPROFILE'], "Downloads")
            else:
                path_to_downloads = os.path.join("/home", os.environ['USER'], "Downloads")

        search_start = datetime.now()

        while (1):
            # Searching .crdownload file
            time.sleep(0.1)
            currenttime = datetime.now() - search_start
            if int(round(currenttime.total_seconds(), 1)) > 8:  # Search timeout 8 seconds
                print(".crdownload not found after: " + "8" + " seconds")
                return None

            # Go through files in path_to_downloads
            for filename in os.listdir(path_to_downloads):
                if filename.endswith('.crdownload'):
                    print("File found")
                    # File found! start tracking download time
                    DL_start_time = datetime.now()
                    print(path_to_downloads + os.sep + filename)
                    while (os.path.isfile(path_to_downloads + os.sep + filename) == True):
                        currentdownloadtime = datetime.now() - DL_start_time  # Tracking download time
                        if int(round(currentdownloadtime.total_seconds(), 1)) > int(max_download_time):
                            print("Download max timeout exceeded: " + str(max_download_time) + " seconds")
                            return None
                        time.sleep(0.05)
                    downloadtime = datetime.now() - DL_start_time
                    BuiltIn().set_test_documentation(filename[:-11] + " downloaded in " + str(downloadtime) + "\n",
                                                     append=True)
                    return downloadtime

    def get_browser_console_log(self):
        """
                **Return browser console log**

                :return: console log
                ---------------
                :Example:
                    | *Page model level example*
                    | ``value = QAutoRobot.get_browser_console_log()``

        """
        console_log = self.driver_cache._get_current_driver().get_log("browser")
        print(console_log)
        return console_log

    @classmethod
    def get_timestamp(self):
        """
        **Return timestamp**

        :Format: 'yyyyMMddhhmmss'
        :return: String which represents current time
        ---------------
        :Example:
            | *Page model level example*
            | ``value = QAutoRobot.get_timestamp()``

        """
        t = datetime.now().timetuple()
        timestamp = "%d%02d%02d%02d%02d%02d" % (t[0], t[1], t[2], t[3], t[4], t[5])
        return timestamp

    def add_dynamic_content_to_parameters(self, parameters, name, value, section=None):
        """
        **Add dynamic content to parameters dictionary**

        *dynamic content is available in current test run*

        :param parameters: Parameters dictionary
        :param name: Name for added parameter as string
        :param value: Value for added parameter as string
        :param section: Optional section where parameter is added as string
        -------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.add_dynamic_content_to_parameters(TESTDATA, "param_name", "my_value")``
            | ``QAutoRobot.add_dynamic_content_to_parameters(TESTDATA, "param_name", "my_value", "my_section")``
            | Using dynamic value
            | ``QAutoRobot.add_dynamic_content_to_parameters(self.ELEMENT_NAME, parameters["param_name"])``

        """
        if not section:
            parameters.update({name: value})
            try:
                print("* Dynamic parameter '%s'='%s' added to parameters dictionary" % (name, value))
            except:
                print("* Dynamic parameter added to parameters dictionary")
        else:
            if section in list(parameters.keys()):
                parameters[section].update({name: value})
            else:
                parameters.update({section: {name: value}})
            try:
                print("* Dynamic parameter ('%s'='%s') added to '%s' section of parameters dictionary" % (name, value,
                                                                                                          section))
            except:
                print("* Dynamic parameter added to parameters dictionary")

    def get_measurements(self, measurement_name):
        """
        **Return measurements**

        :param measurement_name: String represents name of measurement point
        :return:    Measured time in specific point
        ------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.get_measurements("trial")``

        """
        driver = self.driver_cache._get_current_driver()
        return webtimings_get_measurements(measurement_name, driver, "total", "load", "latency")

    ## Return resource timings
    # @param measurement_name    String represents name of measurement point
    # @return Measured time in specific resource
    #
    # Example:
    # @code
    #   # Page model level example
    #   QAutoRobot.get_resource_timings("trial")
    # @endcode
    def get_resource_timings(self, measurement_name):
        """
        **Return resource timings**

        :param measurement_name: String represents name of measurement point
        :return:    Measured time in specific resource
        ------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.get_resource_timings("trial")``

        """
        try:
            resource_timings = self.execute_javascript("return window.performance.getEntriesByType('resource');",
                                                       log=False)
            if resource_timings:

                measurement_folder = os.path.join(get_config_value("reporting_folder"),
                                                  GlobalUtils.MEASUREMENTS_FOLDER_NAME)
                if not os.path.exists(measurement_folder):
                    os.mkdir(measurement_folder)
                js_file = os.path.join(measurement_folder, GlobalUtils.RESOURCE_DATA_PREFIX + measurement_name + ".js")
                jtl_file = os.path.join(measurement_folder,
                                        GlobalUtils.RESOURCE_DATA_PREFIX + measurement_name + ".jtl")

                ts = int(time.time()) * 1000
                timings_string = "'%s': [" % ts
                jtl_timings_string = ""

                max_respond_end = 0
                min_start_time = None
                for resource_dict in resource_timings:
                    if 'responseEnd' in resource_dict and resource_dict['responseEnd'] > max_respond_end:
                        max_respond_end = resource_dict['responseEnd']
                    if 'startTime' in resource_dict and (
                            not min_start_time or resource_dict['startTime'] < min_start_time):
                        min_start_time = resource_dict['startTime']
                    timings_string += "{"
                    for key, value in resource_dict.items():
                        # temporary fix for firefox timings
                        if key == "toJSON":
                            continue
                        timings_string += "'%s': '%s', " % (key, value)
                    timings_string = timings_string.rstrip(", ") + "},\n"
                # add total duration
                total_duration = max_respond_end - min_start_time
                timings_string += "{'%s': '%s', '%s': '%s'}],\n" % ("name", "All", "duration", total_duration)
                jtl_timings_string += "\t<sample ts='%s' t='%s' lb='%s'/>\n" % (
                    ts, str(int(total_duration)), measurement_name)

                if (os.path.isfile(js_file)):
                    read_lines = get_file_lines(js_file)
                    new_lines = read_lines[:-1] + [timings_string] + [read_lines[-1]]
                    content = "".join(new_lines)
                else:
                    heading = "var resource_js_data = {\n"
                    ending = "};"
                    content = heading + timings_string + ending

                if (os.path.isfile(jtl_file)):
                    read_lines = get_file_lines(jtl_file)
                    new_lines = read_lines[:-1] + [jtl_timings_string] + [read_lines[-1]]
                    content_jtl = "".join(new_lines)
                else:
                    heading = "<?xml version='1.0' encoding='UTF-8'?>\n<testResults version='1.2'>\n"
                    ending = "</testResults>"
                    content_jtl = heading + jtl_timings_string + ending

                save_content_to_file(content, js_file)
                save_content_to_file(content_jtl, jtl_file)
                print("Total loading time: " + str(round(total_duration)) + " ms")
                self.execute_javascript("return window.performance.clearResourceTimings();", log=False)
                BuiltIn().set_test_documentation(
                    "*Webpage loading times:*\n\n*" + measurement_name.capitalize() + "* total loading time: *" + str(
                        round(total_duration)) + "* ms\n\n", append=True)
                return resource_timings
            else:
                print("%s: No resource timings to measure!!" % measurement_name)
                return []
        except Exception as e:
            print("Failed to get resource timings:\n%s" % str(e))
            return None

    def get_dom_element_count(self, log=True):
        """
        **Counting DOM-elements**

        :return:  Returns number of DOM-elements on web page.
        -------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.get_dom_element_count()``

        """
        dom_count = self.execute_javascript("return document.getElementsByTagName('*').length;", log)
        return dom_count

    def open_browser(self, browser_name=None, url=None, alias=None, size=None):
        """
        **Open specified browser with url**

        :param browser_name: Browser to open
        :param url: Url to open
        :param alias: save driver with alias
        :param size: Browser window size. Fullscreen if none.
        :return:    id
        -------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.open_browser("ff", http://qautomate.fi/")``

        """

        browser_name = browser_name and browser_name or get_config_value("browser_name")
        if alias:
            DebugLog.log("* Opening browser '%s' with alias '%s'" % (browser_name, alias))
        else:
            DebugLog.log("* Opening browser '%s'" % browser_name)
        driver = create_driver(browser_name)

        # register driver and get id
        _id = self.driver_cache.register(driver, browser_name, alias)

        if not size:
            driver.maximize_window()

        if url:
            DebugLog.log("* Opening base url '%s'" % url)
            driver.get(url)

        return _id

    def switch_browser(self, id_or_alias):
        """
        **Switch between active browsers using id or alias**

        :param id_or_alias: Identify new active browser
        --------------
        :Example:
            | *Page model level example with id*
            | ``id = QAutoRobot.open_browser("ff", "http://qautomate.fi/")``
            | ``id2 = QAutoRobot.open_browser("ff", "http://qautomate.fi/")``
            | run some steps
            | ``QAutoRobot.switch_browser(id)``

        """

        DebugLog.log("* Switching browser with id or alias '%s'" % id_or_alias)
        self.driver_cache.switch_driver(id_or_alias)

    def close_browser(self):
        """
        **Closes current active browser**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.close_browser()``

        """

        DebugLog.log("* Closing browser '%s' with id or alias '%s'" % (self.driver_cache._get_current_browser(),
                                                                       self.driver_cache.get_current_id_or_alias()))
        self.driver_cache.close()

    def close_all_browsers(self):
        """
        **Closes all opened browsers**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.close_all_browsers()``

        """

        DebugLog.log("* Closing all browsers")
        self.driver_cache.close_all()

    def go_to(self, url, log=True):
        """
        **Open specified url**

        :param url: Url to open
        :param log: Flag, if True prints action message
        -----------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.go_to("http://qautomate.fi/")``

        """
        driver = self.driver_cache._get_current_driver()
        if log:
            try:
                DebugLog.log("* Opening: '%s'" % url)
            except:
                DebugLog.log("* Opening url")

        driver.get(url)

    def open_url(self, url, log=True):
        """
        **Open specified url**

        :param url: Url to open
        :param log: Flag, if True prints action message
        --------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.open_url("http://qautomate.fi/")``

        """
        self.go_to(url, log)

    def is_visible(self, element, timeout=None):
        """
        **Return visibility of element.**

        :param element: Element representation (By, value) or WebElement.
        :param timeout: No timeout used, unless custom value provided.
        :return: visibility of element. True or False.
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.is_visible(self.TRIAL)``
            | using representation
            | ``QAutoRobot.is_visible((By.LINK_TEXT, u'Trial'))``
            | using timeout
            | ``QAutoRobot.is_visible(self.TRIAL, 10)``
            | ``QAutoRobot.is_visible((By.LINK_TEXT, u'Trial'), 10)``

        """
        self.last_element = element
        if not timeout:
            try:
                if type(element) in [tuple, QAutoElement]:
                    elements = self.find_elements(element)
                    return len(elements) > 0 and elements[0].is_displayed()
                else:
                    return element.is_displayed()
            except WebDriverException:
                return False
        else:
            try:
                CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_visible(element),
                                                    self.driver_cache._get_current_driver(), '', timeout)
                return True
            except:
                return False

    def is_disabled(self, element, timeout=None):
        """
        **Return disability of element.**

        :param element: Element representation (By, value) or WebElement.
        :param timeout: No timeout used, unless custom value provided.
        :return: True if element disabled, else - False.
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.is_disabled(self.TRIAL)``
            | using representation
            | ``QAutoRobot.is_disabled((By.LINK_TEXT, u'Trial'))``
            | using timeout
            | ``QAutoRobot.is_disabled(self.TRIAL, 10)``
            | ``QAutoRobot.is_disabled((By.LINK_TEXT, u'Trial'), 10)``

        """
        self.last_element = element
        if not timeout:
            try:
                if type(element) in [tuple, QAutoElement]:
                    elements = self.find_elements(element)
                    return len(elements) > 0 and not (elements[0].is_enabled())
                else:
                    return not (element.is_enabled())
            except WebDriverException:
                return False
        else:
            try:
                CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_disabled(element),
                                                    self.driver_cache._get_current_driver(), '', timeout)
                return True
            except:
                return False

    def is_enabled(self, element, timeout=None):
        """
        **Return enablity of element.**

        :param element: Element representation (By, value) or WebElement.
        :param timeout: No timeout used, unless custom value provided.
        :return: True if element enabled, else - False.
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.is_enabled(self.TRIAL)``
            | using representation
            | ``QAutoRobot.is_enabled((By.LINK_TEXT, u'Trial'))``
            | using timeout
            | ``QAutoRobot.is_enabled(self.TRIAL, 10)``
            | ``QAutoRobot.is_enabled((By.LINK_TEXT, u'Trial'), 10)``

        """
        self.last_element = element
        if not timeout:
            try:
                if type(element) in [tuple, QAutoElement]:
                    elements = self.find_elements(element)
                    return len(elements) > 0 and elements[0].is_enabled()
                else:
                    return element.is_enabled()
            except WebDriverException:
                return False
        else:
            try:
                CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_enabled(element),
                                                    self.driver_cache._get_current_driver(), '', timeout)
                return True
            except:
                return False

    def get_text(self, element):
        """
        **Return element's text**

        :param element: Element representation (By, value) or WebElement
        :return: Text of element
        -------------
        :Example:
            | *Page model level example*
            | using web element
            | ``value = QAutoRobot.get_text(self.TRIAL)``
            | using representation
            | ``value = QAutoRobot.get_text((By.LINK_TEXT, u'Trial'))``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        return element.text

    def get_value(self, element):
        """
        **Return element's value**

        :param element: Element representation (By, value) or WebElement
        :return: Value of element
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``value = QAutoRobot.get_value(self.TRIAL)``
            | using representation
            | ``value = QAutoRobot.get_value((By.LINK_TEXT, u'Trial'))``

        """
        return self.get_attribute(element, "value")

    def compare_screenshots(self, ref_scr_name):
        """
        **Compares screenshots or part of screenshots**

        :param ref_scr_name: Screenshot name in string format
        --------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.compare_screenshots("ref_scr_name")``

        """

        if not self.screenshot_parser:
            self.screenshot_parser = XmlScreenshotParser()

        xml_meta_data, ref_scr_file_name_path = CommonUtils._check_screenshot_file_name(self.screenshot_parser,
                                                                                        ref_scr_name)

        ref_scr_x = int(xml_meta_data['x'])
        ref_scr_y = int(xml_meta_data['y'])
        ref_scr_w = int(xml_meta_data['w'])
        ref_scr_h = int(xml_meta_data['h'])
        if get_config_value("runtime_similarity") != '':
            similarity = get_config_value("runtime_similarity")
        else:
            similarity = int(xml_meta_data['similarity'])

        CommonUtils()._handle_screenshot_comparison(ref_scr_file_name_path, ref_scr_x, ref_scr_y,
                                                    ref_scr_w, ref_scr_h, similarity)

    def compare_element_screenshots(self, element, ref_scr_name):
        """
        **Compares screenshots of elements**

        :param element: Element representation (By, value) or WebElement
        :param ref_scr_name: Screenshot name in string format
        -------------
        :Example:
            *Page model level example*
            ``QAutoRobot.compare_element_screenshots(self.TRIAL,"ref_scr_name")``

        """

        if not self.screenshot_parser:
            self.screenshot_parser = XmlScreenshotParser()

        self.wait_until_element_is_visible(element)

        xml_meta_data, ref_scr_file_name_path = CommonUtils._check_screenshot_file_name(self.screenshot_parser,
                                                                                        ref_scr_name)

        if get_config_value("runtime_similarity") != '':
            similarity = get_config_value("runtime_similarity")
        else:
            similarity = int(xml_meta_data['similarity'])

        element = self.find_element_if_not_webelement(element)

        element_loc = element.location
        element_size = element.size
        ref_scr_x = int(element_loc['x'])
        ref_scr_y = int(element_loc['y'])
        ref_scr_w = int(element_size['width'])
        ref_scr_h = int(element_size['height'])

        CommonUtils()._handle_screenshot_comparison(ref_scr_file_name_path, ref_scr_x,
                                                    ref_scr_y, ref_scr_w, ref_scr_h, similarity)

    def execute_javascript(self, js_script, log=True):
        """
        **Execute JavaScript code**

        :param js_script: String represents JavaScript code
        :param log: Flag, if True prints action message
        :return: Object return by JavaScript code else None
        ---------------
        :Example:
            | *age model level example*
            | ``value = QAutoRobot.execute_javascript("run_function(variable)")``

        """
        driver = self.driver_cache._get_current_driver()
        if log:
            DebugLog.log("* Execute javascript: " + str(js_script))
        return driver.execute_script(js_script)

    def execute_async_javascript(self, js_script, log=True):
        """
        **Execute async JavaScript code**

        :param js_script: String represents JavaScript code
        :param log: Flag, if True prints action message
        :return: Object return by JavaScript code else None
        ---------------

        """
        driver = self.driver_cache._get_current_driver()
        if log:
            DebugLog.log("* Execute javascript: " + str(js_script))
        return driver.execute_async_script(js_script)

    def get_web_response(self, url, method, auth_file, data):
        """
        **Return response from web service**

        :param url: Web service url
        :param method: Rest-api method. Get, post, put or delete.
        :param auth_file: Optional name of the auth_file. Blank if not needed.
        :param data: Optional data for request as string.
        :return: Web response from server
        --------------
        :Example:
            | *Page model level example*
            | ``value = QAutoRobot.get_web_response(u'http://api.openweathermap.org/data/2.5/weather?q=London&mode=xml', u'get', u'auth_file.txt', u'')``

        """
        username = None
        password = None

        if auth_file:
            _file = get_file_lines(os.path.abspath(os.path.join(os.getcwd(), GlobalUtils.LOGIN_FOLDER_NAME, auth_file)))
            for line in _file:
                (username, password) = line.split()
        try:
            if method.lower() == "get":
                return requests.get(url, auth=HTTPBasicAuth(username, password))
            elif method.lower() == "post":
                if data[-4:] == ".txt":
                    return requests.post(url, json=dumps(data), auth=HTTPBasicAuth(username, password))
                else:
                    return requests.post(url, data=open(data), auth=HTTPBasicAuth(username, password))
            elif method.lower() == "put":
                if data[-4:] == ".txt":
                    return requests.put(url, json=dumps(data), auth=HTTPBasicAuth(username, password))
                else:
                    return requests.put(url, data=open(data), auth=HTTPBasicAuth(username, password))
            elif method.lower() == "delete":
                if data[-4:] == ".txt":
                    return requests.delete(url, json=dumps(data), auth=HTTPBasicAuth(username, password))
                else:
                    return requests.delete(url, data=open(data), auth=HTTPBasicAuth(username, password))
            else:
                print("Method not recognized")
        except HTTPError as e:
            print('Error code: ', e.code, e.read())
        except URLError as e:
            print(e.reason)

    def get_soap_response(self, url, request_file_xml):
        """
        **Gets SOAP response from web service to be used in verify_soap_api**

        :param url: Web service url
        :param request_file_xml: Request xml file in ../data/soap/requests/
        --------------
        :Example:
            | *Page model level example*
            | ``value = QAutoRobot.get_soap_response(u'http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', u'soap_xml.xml')``

        """
        headers = {'content-type': 'text/xml'}
        body = get_file_content(os.path.abspath(os.path.join(os.getcwd(), GlobalUtils.SOAP_REQUEST_FOLDER_NAME,
                                                             request_file_xml)))
        try:
            response = requests.post(url, data=body, headers=headers)
            root = etree.fromstring(response.content)
            fault_msg = ''.join(root.xpath("//*[local-name() = 'faultstring'][position()=1]/text()"))
            if fault_msg is not "":
                self.fail(fault_msg)
            else:
                return response.content
        except ConnectionError as e:
            print(e)

    def get_text_length(self, element):
        """
        **Return element text length. Spaces are also counted.**

        :param element: Element representation (By, value) or WebElement
        :return: WebElement text length as integer
        -------------
        :Example:
            | *Page model level example*
            | using web element
            | ``value = QAutoRobot.get_text_length(self.TRIAL)``
            | using representation
            | ``value = QAutoRobot.get_text_length((By.LINK_TEXT, u'Trial'))``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        print("Element text length: ", len(element.text))
        return len(element.text)

    def start_zapproxy_daemon(self, installation_dir):
        """
        **Start Zap proxy daemon**

        .. note::
            Zapproxy UI and python client must be installed

        :param installation_dir: Zapproxy installation folder
        :return: Zap daemon object, zap session name
        ------------------
        :Example:
            | *Page model level example*
            | ``zap, zap_session = QAutoRobot.start_zapproxy_daemon('C:\\ZedAttackProxy\\zap.bat')``

        """
        try:
            from zapv2 import ZAPv2
        except Exception as e:
            print("ZAP installation does not found or missing!" + str(e))
        print('Starting ZAP ...')
        try:
            zap_test_measurement_folder = os.getcwd() + os.sep + "test_reports"
            if not os.path.exists(zap_test_measurement_folder):
                os.mkdir(zap_test_measurement_folder)
        except Exception as e:
            print("Could not create zap measurements folder:\n%s" % str(e))

        session_name = "qautorobot_zap_session_" + self.get_timestamp()
        try:
            newsession = zap_test_measurement_folder + os.sep + session_name
            print(newsession)
            subprocess.Popen(installation_dir + " -daemon -newsession " + newsession)
            print('Waiting for ZAP to load ...')
            zap = ZAPv2(proxies={'http': 'http://127.0.0.1:8092', 'https': 'http://127.0.0.1:8092'})
            for _ in range(25):
                try:
                    _ = requests.head("http://127.0.0.1:8092")
                    print("ZAPproxy running")
                    time.sleep(5)
                    return zap, session_name
                except requests.ConnectionError:
                    pass
                time.sleep(3)

        except Exception as e:
            print("Failed to start zap proxy and session! Please check installation path and settings." + str(e))

    def stop_zapproxy_daemon(self, zap):
        """
        **Stop Zap proxy daemon**

        .. note::
            Zapproxy UI and python client must be installed

        :param zap: Zap proxy object
        -------------
        :Example:
            | *Pagemodel level example*
            | ``zap, zap_session = QAutoRobot.start_zapproxy_daemon('C:\\ZedAttackProxy\\zap.bat')``
            | ``QAutoRobot.stop_zapproxy_daemon(zap)``

        """
        try:
            # To close ZAP:
            zap.core.shutdown()
        except Exception as e:
            print("Zap " + str(e))
        time.sleep(4)

    def generate_zap_test_report(self, installation_dir, session_name, report_name="qautorobot_zap_report.html"):
        """
        **Generate zap test report html**

        .. note::
            Zapproxy UI and python client must be installed

        :param installation_dir: Zap installation dir
        :param session_name: Zap session name
        :param report_name: Zap report name
        --------------
        :Example:
            | Pagemodel level example
            |
            | ``QAutoRobot.generate_zap_test_report('C:\\ZedAttackProxy\\zap.bat', zap_session)``
            | ``or QAutoRobot.generate_zap_test_report('C:\\ZedAttackProxy\\zap.bat', zap_session, "qautorobot_zap.html")``
        """
        try:
            zap_test_report_folder = os.getcwd() + os.sep + "test_reports"
            print("Generating zap report")
            subprocess.Popen(
                installation_dir + " -last_scan_report " + zap_test_report_folder + os.path.sep + report_name + " -session " + zap_test_report_folder + os.path.sep + session_name + " -cmd")
        except Exception as e:
            print("Failed to generate zap test report" + str(e))
        time.sleep(1)


class WebMethods(CommonMethods):
    """
    **Class that contains methods for web**
    """

    def __init__(self, driver_cache=None):
        self.driver_cache = driver_cache and driver_cache or DriverCache()
        CommonMethods.__init__(self, self.driver_cache)
        # print "WebMethods"

    def get_selected_list_value(self, element):
        """
        **Return selected option value from dropdown list**

        :param element: Element representation (By, value) or WebElement
        :return: String value of selected option
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_selected_list_value(self.ID_DROPDOWN)``
            | using representation
            | ``QAutoRobot.get_selected_list_value((By.ID, u'dropdown'))``

        """
        element = self.find_element_if_not_webelement(element)
        return Select(element).first_selected_option.get_attribute('value')

    def get_selected_list_label(self, element):
        """
        **Return selected option text from dropdown list**

        :param element: Element representation (By, value) or WebElement
        :return: String text of selected option
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_selected_list_label(self.ID_DROPDOWN)``
            | using representation
            | ``QAutoRobot.get_selected_list_label((By.ID, u'dropdown'))``

        """
        element = self.find_element_if_not_webelement(element)
        return Select(element).first_selected_option.text

    def select_from_list_by_value(self, element, value):
        """
        **Select option from dropdown list by value**

        :param element: Element representation (By, value) or WebElement
        :param value: Dropdown option value
        -------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.select_from_list_by_value(self.ID_DROPDOWN, 10)``
            | using representation
            | ``QAutoRobot.select_from_list_by_value((By.ID, u'dropdown'), 10)``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        element = Select(element)
        try:
            DebugLog.log("* Selecting '%s' from dropdown list" % value)
        except:
            DebugLog.log("* Selecting from dropdown list")
        element.select_by_value(value)

    def select_from_list_by_label(self, element, text):
        """
        **Select option from dropdown list by text**

        :param element: Element representation (By, value) or WebElement
        :param text: Dropdown option visible text
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.select_from_list_by_label(self.ID_DROPDOWN, "value")``
            | using representation
            | ``QAutoRobot.select_from_list_by_label((By.ID, u'dropdown'), "value")``

        """
        self.wait_until_element_is_visible(element)
        msg = "Failed to select from list after %s seconds" % get_config_value("default_timeout")
        CommonMethodsHelpers.webdriver_wait(lambda driver: self._select_from_list_by_label(element, text),
                                            self.driver_cache._get_current_driver(), msg)

    def _select_from_list_by_label(self, element, text):
        element = self.find_element_if_not_webelement(element)
        element = Select(element)
        try:
            DebugLog.log("* Selecting '%s' from dropdown list" % text)
        except:
            DebugLog.log("* Selecting from dropdown list")
        element.select_by_visible_text(text)
        return True

    def select_from_list_by_random_option(self, element, *val_to_skip):
        """
        **Select random option from dropdown list**

        :param element: Element representation (By, value) or WebElement
        :param val_to_skip: Values to skip
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.select_from_list_by_random_option(self.ID_DROPDOWN)``
            | using representation
            | ``QAutoRobot.select_from_list_by_random_option((By.ID, u'dropdown'))``

        """
        self.wait_until_element_is_visible(element)
        options = self.get_selected_list_labels(element)
        option_to_select = self._get_random_value(options, *val_to_skip)
        self.select_from_list_by_label(element, option_to_select)

    def unselect_checkbox(self, element, status="unchecked"):
        """
        **Unchecks the checkbox**

        :param element: checkbox element
        :param status: final state of the checkbox "checked" or "unchecked"
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.unselect_checkbox(self.ID_CHECKBOX1)``
            | using representation
            | ``QAutoRobot.unselect_checkbox((By.ID, u'checkbox1'))``

        """
        if self.get_attribute(element, "type") == "checkbox":
            if status == "unchecked":
                if self.get_attribute(element, "checked") == "true" or self.get_attribute(element,
                                                                                          "checked") == "checked":
                    DebugLog.log("* Unchecking the checkbox")
                    self.click_element(element)
                else:
                    DebugLog.log("* Checkbox is already unchecked")
        else:
            DebugLog.log("Element might be not a checkbox")

    def select_checkbox(self, element, status="checked"):
        """
        **Checks the checkbox**

        :param element: checkbox element
        :param status: final state of the checkbox "checked" or "unchecked"
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.select_checkbox(self.ID_CHECKBOX1)``
            | ``QAutoRobot.select_checkbox(self.ID_CHECKBOX1, "unchecked")``
            | using representation
            | ``QAutoRobot.select_checkbox((By.ID, u'checkbox1'))``
            | ``QAutoRobot.select_checkbox((By.ID, u'checkbox1'), "unchecked")``

        """
        self.wait_until_element_is_visible(element)
        msg = "Failed to select checkbox after %s seconds" % get_config_value("default_timeout")
        CommonMethodsHelpers.webdriver_wait(lambda driver: self._select_checkbox(element, status),
                                            self.driver_cache._get_current_driver(), msg)

    def _select_checkbox(self, element, status="checked"):
        if self.get_attribute(element, "type") in ["checkbox", "radio"]:
            if status == "checked":
                if self.get_attribute(element, "checked") is None:
                    DebugLog.log("* Checking the checkbox")
                    self.click_element(element)
                else:
                    DebugLog.log("* Checkbox is already checked")
            elif status == "unchecked":
                if self.get_attribute(element, "checked") == "true" or self.get_attribute(element,
                                                                                          "checked") == "checked":
                    DebugLog.log("* Unchecking the checkbox")
                    self.click_element(element)
                else:
                    DebugLog.log("* Checkbox is already unchecked")
        else:
            DebugLog.log("Element might be not a checkbox or radio button")
        return True

    def get_selected_list_labels(self, element):
        """
        **Return texts of list dropdown options**

        :param element: Element representation (By, value) or WebElement
        :return: List strings, which represent dropdown options texts
        ------------------
        :Example:
            | *Page model level example*
            | using web element
            | ``text_list = QAutoRobot.get_selected_list_labels(self.ID_DROPDOWN)``
            | using representation
            | ``text_list = QAutoRobot.get_selected_list_labels((By.ID, u'dropdown'))``

        """
        self.wait_until_element_is_visible(element)
        values = []
        element = self.find_element_if_not_webelement(element)
        for value in Select(element).options:
            values.append(self.get_text(value))
        return values

    def get_selected_list_values(self, element):
        """
        **Return values of list dropdown options**

        :param element: Element representation (By, value) or WebElement
        :return: List strings, which represent dropdown options texts
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``text_list = QAutoRobot.get_selected_list_values(self.ID_DROPDOWN)``
            | using representation
            | ``text_list = QAutoRobot.get_selected_list_values((By.ID, u'dropdown'))``

        """
        self.wait_until_element_is_visible(element)
        values = []
        element = self.find_element_if_not_webelement(element)
        for value in Select(element).options:
            values.append(self.get_attribute(value, "value"))
        return values

    def get_attribute(self, element, attr):
        """
        **Return element's attribute**

        :param element: Element representation (By, value) or WebElement
        :param attr: Attribute of an element
        :return: element's attribute
        -----------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_attribute(self.ID_DROPDOWN, "name")``
            | using representation
            | ``QAutoRobot.get_attribute((By.ID, u'dropdown'), "name")``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        return element.get_attribute(attr)

    def wait_until_element_is_present(self, element, timeout=None):
        """
        **Wait for element is present in source code.**

        :exception Exception: if time exceeds DEFAULT_TIMEOUT, then rise exception.
        :param element: Element representation (By, value).
        :param timeout: Uses default timeout, unless custom value provided.
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_is_present(self.ID_TESTINPUT)``
            | using representation
            | ``QAutoRobot.wait_until_element_is_present((By.ID, u'testInput'))``
            | using timeout
            | ``QAutoRobot.wait_until_element_is_present(self.ID_TESTINPUT, 10)``
            | ``QAutoRobot.wait_until_element_is_present((By.ID, u'testInput'), 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        message = "Element {By: '%s', value: '%s'} is not presented for %s seconds" % (element[0], element[1], timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_present(element),
                                            self.driver_cache._get_current_driver(), message, timeout)

    def wait_until_element_is_not_present(self, element, timeout=None):
        """
        **Wait for element is not present in source code.**

        :exception Exception: if time exceeds DEFAULT_TIMEOUT, then rise exception.
        :param element: Element representation (By, value).
        :param timeout: Uses default timeout, unless custom value provided.
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_is_not_present(self.ID_TESTINPUT)``
            | using representation
            | ``QAutoRobot.wait_until_element_is_not_present((By.ID, u'testInput'))``
            | using timeout
            | ``QAutoRobot.wait_until_element_is_not_present(self.ID_TESTINPUT, 10)``
            | ``QAutoRobot.wait_until_element_is_not_present((By.ID, u'testInput'), 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        message = "Element {By: '%s', value: '%s'} is presented for %s seconds" % (element[0], element[1], timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: not self.is_present(element),
                                            self.driver_cache._get_current_driver(), message, timeout)

    def wait_until_table_size_changes(self, element, timeout=None, msg=None):
        """
        **Wait until table size changes**

        :exception Exception: if time exceeds DEFAULT_TIMEOUT, then rise exception.
        :param element: Element representation (By, value) or WebElement object.
        :param timeout: Uses default timeout, unless custom value provided.
        :param msg: Message
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_table_size_changes(self.ID_TABLETEST)``
            | using representation
            | ``QAutoRobot.wait_until_table_size_changes((By.ID, u'tableTest'))``
            | using timeout
            | ``QAutoRobot.wait_until_table_size_changes(self.ID_TABLETEST, 10)``
            | ``QAutoRobot.wait_until_table_size_changes((By.ID, u'tableTest'), 10)``

        """
        size = self.get_table_size(element)
        if not timeout:
            timeout = get_config_value("default_timeout")
        if not msg:
            if type(element) in [tuple, QAutoElement]:
                msg = "Element '%s' size is not changed after %s seconds" % (element[1], timeout)
            else:
                msg = "Element '%s' size is not changed after %s seconds" % (element.text, timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.get_table_size(element)[0] != size[0],
                                            self.driver_cache._get_current_driver(), msg, timeout)

    def mouse_over(self, element):
        """
        **Mouse over\hover element**

        :param element: Element representation (By, value) or WebElement object.
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.mouse_over(self.TRIAL)``
            | using representation
            | ``QAutoRobot.mouse_over((By.LINK_TEXT, u'Trial'))``

        """
        self.mouse_over_by_offset(element, 0, 0)

    def mouse_over_by_offset(self, element, xoffset, yoffset):
        """
        **Mouse over\hover element by offset**

        :param element: Element representation (By, value) or WebElement object.
        :param xoffset: X coordinate offset
        :param yoffset: coordinate offset
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.mouse_over_by_offset(self.TRIAL, 0, 0)``
            | using representation
            | ``QAutoRobot.mouse_over_by_offset((By.LINK_TEXT, u'Trial'), 0, 0)``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        try:
            DebugLog.log("* Mouse over '%s' by offset(%s,%s)" % (element.text, xoffset, yoffset))
        except:
            DebugLog.log("* Mouse over")
        actions.move_to_element(element).move_by_offset(xoffset, yoffset).perform()

    def open_context_menu(self, element):
        """
        **Mouse right click at element opening context menu**

        :param element: Element representation (By, value) or WebElement object.
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.open_context_menu(self.TRIAL)``
            | using representation
            | ``QAutoRobot.open_context_menu((By.LINK_TEXT, u'Trial'))``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        try:
            DebugLog.log("* Right click at '%s'" % element.text)
        except:
            DebugLog.log("* Right click")
        actions.context_click(element).perform()

    def mouse_right_click_by_offset(self, element, xoffset, yoffset):
        """
        **Mouse right click at element by offset**

        :param element: Element representation (By, value) or WebElement object.
        :param xoffset: X coordinate offset
        :param yoffset: Y coordinate offset
        -------------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.mouse_right_click_by_offset(self.TRIAL, 0, 0)``
            | using representation
            | ``QAutoRobot.mouse_right_click_by_offset((By.LINK_TEXT, u'Trial'), 0, 0)``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        try:
            DebugLog.log("* Right click at '%s' by offset(%s,%s)" % (element.text, xoffset, yoffset))
        except:
            DebugLog.log("* Right click")
        actions.move_to_element(element).move_by_offset(xoffset, yoffset).context_click().perform()

    def mouse_down(self, element):
        """
        **Click and hold mouse left button at element. Element is pressed without releasing button**

        :param element: Element representation (By, value) or WebElement object.
        -------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.mouse_down(self.TRIAL)``
            | using representation
            | ``QAutoRobot.mouse_down((By.LINK_TEXT, u'Trial'))``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        try:
            DebugLog.log("* Mouse click down '%s'" % element.text)
        except:
            DebugLog.log("* Mouse click down")
        actions.click_and_hold(element).perform()

    def mouse_up(self, element):
        """
        **Releases mouse left button at element. Element**

        :param element: Element representation (By, value) or WebElement object.
        -------------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.mouse_up(self.TRIAL)``
            | using representation
            | ``QAutoRobot.mouse_up((By.LINK_TEXT, u'Trial'))``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)
        try:
            DebugLog.log("* Mouse click up '%s'" % element.text)
        except:
            DebugLog.log("* Mouse click up")
        actions.release(element).perform()

    def drag_and_drop_by_offset(self, element, xoffset, yoffset):
        """
        **Drags draggable element onto x,y offset**

        :param element: Element to drag
        :param xoffset: Drag element from current position to xoffset
        :param yoffset: Drag element from current position to yoffset
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.drag_and_drop_by_offset(self.ID_DRAG1, 0, 0)``
            | using representation
            | ``QAutoRobot.drag_and_drop_by_offset((By.CSS_SELECTOR, u'div>p'), 0, 0)``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(element)
        draggable = self.find_element_if_not_webelement(element)
        try:
            DebugLog.log("* Drag and drop '%s' by offset(%s,%s)" % (draggable.text, xoffset, yoffset))
        except:
            DebugLog.log("* Drag and drop by offset")
        actions.drag_and_drop_by_offset(draggable, xoffset, yoffset).perform()

    def is_present(self, element, timeout=None):
        """
        **Return True if element presents in source code, else - False**

        :param element: Element representation (By, value).
        :param timeout: No timeout used, unless custom value provided.
        :return: True if element presents in source code, else -  False.
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.is_present(self.ID_TESTINPUT)``
            | using representation
            | ``QAutoRobot.is_present((By.ID, u'testInput'))``
            | using timeout
            | ``QAutoRobot.is_present(self.ID_TESTINPUT, 10)``
            | ``QAutoRobot.is_present(By.ID, u'testInput'), 10)``

        """
        if not timeout:
            elements = self.find_elements(element)
            return len(elements) > 0
        else:
            try:
                CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_present(element),
                                                    self.driver_cache._get_current_driver(), '', timeout)
                return True
            except:
                return False

    def get_elements_count(self, element):
        """
        **Return number of found elements**

        :param element: Element representation
        :return: Number of found elements
        --------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.get_elements_count((By.CSS_SELECTOR, u"img"))``

        """
        return len(self.find_elements(element))

    ## Internal return random value from list
    # @endcode
    def _get_random_value(self, _list, *val_to_skip):
        _tmp = list(_list)
        for skipped in val_to_skip:
            _tmp.remove(CommonMethodsHelpers.contains_nonascii(skipped))
        value = random.choice(_tmp)
        try:
            print("* Random value is '%s'" % value)
        except:
            print("* Random value")

        return value

    def wait_until_page_contains(self, text, timeout=None):
        """
        **Wait until page's contains text**

        :param text: Element's text which should be
        :param timeout: Uses default timeout, unless custom value provided.
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_page_contains(u'Cell text is this')``
            | using representation
            | ``QAutoRobot.wait_until_page_contains((u'Cell text is this')``
            | using timeout
            | ``QAutoRobot.wait_until_page_contains(u'Cell text is this', 10)``
            | ``QAutoRobot.wait_until_page_contains(u'Cell text is this', 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        element = (By.XPATH, "//*[contains(., %s)]" % CommonMethodsHelpers.escape_xpath_text(text))
        msg = "Text '%s' did not appear in %s seconds" % (text, timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.is_present(element),
                                            self.driver_cache._get_current_driver(), msg, timeout)
        try:
            DebugLog.log("* Page contains text: '%s'" % text)
        except:
            DebugLog.log("* Page contains text")

    def wait_until_page_does_not_contain(self, text, timeout=None):
        """
        **Wait until page's does not contain text**

        :param text: Element's text which should be
        :param timeout: Uses default timeout, unless custom value provided.
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_page_contain(u'Cell text is this')``
            | using representation
            | ``QAutoRobot.wait_until_page_contain((u'Cell text is this')``
            | using timeout
            | ``QAutoRobot.wait_until_page_contain(u'Cell text is this', 10)``
            | ``QAutoRobot.wait_until_page_contain(u'Cell text is this', 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        element = (By.XPATH, "//*[contains(., %s)]" % CommonMethodsHelpers.escape_xpath_text(text))
        msg = "Text '%s' did not appear in %s seconds" % (text, timeout)
        CommonMethodsHelpers.webdriver_wait(lambda driver: not self.is_present(element),
                                            self.driver_cache._get_current_driver(), msg, timeout)
        try:
            DebugLog.log("* Page does not contain text: '%s'" % text)
        except:
            DebugLog.log("* Page does not contain text")

    def wait_until_element_does_not_contain(self, element, text, timeout=None):
        """
        **Wait until element's does not contains text**

        :param element: Element representation (By, value) or WebElement.
        :param text: Element's text which should not be
        :param timeout: Uses default timeout, unless custom value provided.
        ---------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_does_not_contain(self.TEST, u'Cell text changed')``
            | using representation
            | ``QAutoRobot.wait_until_element_does_not_contain((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), u'Cell text changed')``
            | using timeout
            | ``QAutoRobot.wait_until_element_does_not_contain(self.TEST, u'Cell text changed', 10)``
            | ``QAutoRobot.wait_until_element_does_not_contain((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), u'Cell text changed', 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        msg = "Text '%s' did not disappear in '%s' seconds from element" % (text, timeout)
        text = CommonMethodsHelpers.contains_nonascii(text)
        CommonMethodsHelpers.webdriver_wait(lambda driver: text not in self.get_text(element), msg, timeout)

    def wait_until_element_contains(self, element, text, timeout=None):
        """
        **Wait until element's contains text**

        :param element: Element representation (By, value) or WebElement.
        :param text: Element's text which should be
        :param timeout: Uses default timeout, unless custom value provided.
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.common_utils.wait_until_element_contains(self.elements.TEST, u'Cell text is this')``
            | ``QAutoRobot.wait_until_element_contains((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), u'Cell text is this'1', 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        msg = "Text '%s' did not appear in '%s' seconds from element" % (text, timeout)
        text = CommonMethodsHelpers.contains_nonascii(text)
        CommonMethodsHelpers.webdriver_wait(lambda driver: text in self.get_text(element), msg, timeout)

    def wait_until_element_should_not_be(self, element, text, timeout=None):
        """
        **Wait until element's text is not equal**

        :param element: Element representation (By, value) or WebElement.
        :param text: Element's text which should not be
        :param timeout: Uses default timeout, unless custom value provided.
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_should_not_be(self.TEST, u'Cell text changed')``
            | using representation
            | ``QAutoRobot.wait_until_element_should_not_be((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), u'Cell text changed')``
            | using timeout
            | ``QAutoRobot.wait_until_element_should_not_be(self.TEST, u'Cell text changed', 10)``
            | ``QAutoRobot.wait_until_element_should_not_be((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), u'Cell text changed', 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        msg = "Text equals '%s' did not disappear in '%s' seconds from element" % (text, timeout)
        text = CommonMethodsHelpers.contains_nonascii(text)
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.get_text(element) != text, msg, timeout)

    def wait_until_element_should_be(self, element, text, timeout=None):
        """
        **Wait until element's text is equal**

        :param element: Element representation (By, value) or WebElement.
        :param text: Element's text which should be
        :param timeout: Uses default timeout, unless custom value provided.
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_should_be(self.TEST, u'Cell text is this')``
            | using representation
            | ``QAutoRobot.wait_until_element_should_be((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), u'Cell text is this')``
            | using timeout
            | ``QAutoRobot.wait_until_element_should_be(self.TEST, u'Cell text is this', 10)``
            | ``QAutoRobot.wait_until_element_should_be((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), u'Cell text is this'1', 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        msg = "Text equals '%s' did not appear in '%s' seconds from element" % (text, timeout)
        text = CommonMethodsHelpers.contains_nonascii(text)
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.get_text(element) == text, msg, timeout)
        print("Element locator " + element[0] + ":" + element[1])

    def wait_until_element_attribute_contains(self, element, attr, expected_value, timeout=None):
        """
        **Wait until element's attribute contains value**

        :param element: Element representation (By, value) or WebElement.
        :param attr: Element's attribute
        :param expected_value: Element's attribute value which should be
        :param timeout: Uses default timeout, unless custom value provided.
        ----------------
         :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.wait_until_element_attribute_contains(self.ID_DROPDOWN, "name", "dropdown")``
            | using representation
            | ``QAutoRobot.wait_until_element_attribute_contains((By.ID, u'dropdown'), "name", "dropdown")``
            | using timeout
            | ``QAutoRobot.wait_until_element_attribute_contains(self.ID_DROPDOWN, "name", "dropdown", 10)``
            | ``QAutoRobot.wait_until_element_attribute_contains((By.ID, u'dropdown'), "name", "dropdown", 10)``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        expected_value = CommonMethodsHelpers.contains_nonascii(expected_value)
        msg = "Webelement's attribute '%s' doesn't contains '%s'" % (attr, expected_value)
        CommonMethodsHelpers.webdriver_wait(lambda driver: expected_value in self.get_attribute(element, attr), msg,
                                            timeout)

    def wait_until_document_ready(self):
        """
        **Wait until browser finish loading webpage**

        Execute JS to check readyState of DOM page object.

        :Example:
            | *Page model level example*
            | ``QAutoRobot.wait_until_document_ready()``

        """
        self.wait_for_condition("return document.readyState", "complete")
        DebugLog.log("* Browser loaded webpage")

    def wait_for_condition(self, js_script, value, msg=None):
        """
        **Wait for condition JavaScript returns value**

        :param js_script: Executable JavaScript
        :param value: Expected value which should be returned by JavaScript
        :param msg: Message
        --------------------
        :Example:
            | ``wait_for_condition("document.title", "javascript - hide index.html in the URL - Stack Overflow")``
        """
        if not msg:
            msg = "'%s' not equal to '%s'" % (js_script, value)
        CommonMethodsHelpers.webdriver_wait(lambda driver:
                                            CommonMethodsHelpers.contains_nonascii(driver.execute_script(js_script)) ==
                                            CommonMethodsHelpers.contains_nonascii(value),
                                            self.driver_cache._get_current_driver(), msg)

    def wait_until_jquery_ajax_loaded(self, timeout=None):
        """
        **Wait until browser is finished loading jQuery**

        Execute JS to check is jQuery active.

        :param timeout: Uses default timeout, unless custom value provided.
        ----------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.wait_until_jquery_ajax_loaded()``

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        msg = "jQuery not found from the page. wait_for_jquery_ajax_loaded method needs jQuery to work!"
        CommonMethodsHelpers.webdriver_wait(lambda driver: self.execute_javascript("return typeof jQuery;",
                                                                                   log=False) != "undefined",
                                            self.driver_cache._get_current_driver(), msg, timeout)
        msg = "Ajax jQuery is not loaded for %s seconds" % timeout
        CommonMethodsHelpers.webdriver_wait(
            lambda driver: self.execute_javascript("return jQuery.active;", log=False) == 0,
            self.driver_cache._get_current_driver(), msg, timeout)
        DebugLog.log("* jQuery loaded on webpage")

    def select_frame(self, element):
        """
        **Switch focus to frame**

        :param element: Element representation (By, value), WebElement or frame name.
        ------------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.select_frame(self.IFRAME)``
            | using representation
            | ``QAutoRobot.select_frame((By.CSS_SELECTOR, u'iframe'))``

        """
        driver = self.driver_cache._get_current_driver()
        element = self.find_element_if_not_webelement(element)
        DebugLog.log("* Switching frame to")
        driver.switch_to_frame(element)

    def select_frame_default_content(self):
        """
        **Switch focus to default content**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.select_frame_default_content()``

        """
        DebugLog.log("* Switching to default content")
        self.driver_cache._get_current_driver().switch_to_default_content()

    def close_window_and_focus_to_previous(self):
        """
        **Close current window and focus to previous one**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.close_window_and_focus_to_previous()``

        """
        driver = self.driver_cache._get_current_driver()
        handles = driver.window_handles
        # check if it the last window --- it is not closed then
        if len(handles) > 1:
            DebugLog.log("* Closing current window and focus to previous window")
            driver.close()
            driver.switch_to_window(handles[-2])
        else:
            DebugLog.log("* The only browser window cannot be closed.")

    def close_window(self):
        """
        **Close current window**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.close_window()``

        """
        driver = self.driver_cache._get_current_driver()
        handles = driver.window_handles
        # check if it the last window --- it is not closed then
        if len(handles) > 1:
            DebugLog.log("* Closing current window")
            driver.close()
        else:
            DebugLog.log("* The only browser window cannot be closed.")

    def get_window_size(self):
        """
        **Returns current window size width, height**

        :return width, height
        -----------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.get_window_size()``

        """
        driver = self.driver_cache._get_current_driver()
        size = driver.get_window_size()
        return size['width'], size['height']

    def set_window_size(self, width, height):
        """
        **Set current window size width, height**

        :param width: window width
        :param height: window height
        -------------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.set_window_size(800, 600)``

        """
        driver = self.driver_cache._get_current_driver()
        driver.set_window_size(width, height)

    def get_table_size(self, element):
        """
        **Get table size**

        :param element: Table element representation (By, value) or WebElement object.
        :return: table_size, table_rows, table_columns
        ---------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_size(self.TABLE)``
            | ``element_rowtable = QAutoRobot.get_table_size(self.ID_TABLE)``
            | using representation
            | ``QAutoRobot.get_table_size((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'))``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        row = "TBODY/TR"
        cell = "TD"
        table_rows, table_columns = 0, 0
        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            element_column = elem.find_elements(By.XPATH, cell)
            for elem_c in element_column:
                if self.is_visible(elem_c):
                    table_columns = element_column.index(elem_c) + 1
                    table_rows = element_rows.index(elem) + 1
        cells = table_rows * table_columns
        return cells, table_rows, table_columns

    def table_contains_text(self, element, value):
        """
        **Checks if table contains text**

        :param element: Table element representation (By, value) or WebElement object.
        :param value: String
        :return: Boolean value
        --------------
        :Example:
            | using web element
            | ``QAutoRobot.table_contains_text(self.TABLE, u'in_table')``
            | using representation
            | ``QAutoRobot.table_contains_text((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), u'in_table')``

        """
        if value in self.find_element(element).text:
            return True
        else:
            return False

    def get_table_column_and_row_by_text_contains(self, element, text, row="TBODY/TR", cell="TD"):
        """
        **Find table column and row number by contains text**

        :param element: Table element representation (By, value) or WebElement object.
        :param text: Element's text should contains
        :param row: Xpath to element where text should be default id 'TBODY/TR'
        :param cell: Xpath to element where text should be default id 'TD'
        :return: element_row, element_col, text_row, text_col
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_column_and_row_by_text_contains(self.TABLE, "text_to_find")``
            | ``element_rowtable = QAutoRobot.get_table_column_and_row_by_text_contains(self.ID_TABLE, parameters[u'member_id'],"TBODY/TR","TD/SPAN")``
            | ``element_rowtable[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_table_column_and_row_by_text_contains((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "text_to_find_contains")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row == "" or row is None:
            row = "TBODY/TR"

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            element_column = elem.find_elements(By.XPATH, cell)
            for elem_c in element_column:
                if self.is_visible(elem_c) and text in self.get_text(elem_c):
                    # return "real" row and column numbers
                    column = element_column.index(elem_c) + 1
                    row = element_rows.index(elem) + 1
                    print("* Found text contains '%s' from column '%s' and row '%s'" % (text, column, row))
                    return elem, elem_c, row, column

        self.fail("* Text '%s' contains not found from table" % text)

    def get_table_column_and_row_by_text(self, element, text, row="TBODY/TR", cell="TD"):
        """
        **Find table column and row number by text**

        :param element: Table element representation (By, value) or WebElement object.
        :param text:    Element's text which should be
        :param row:     Xpath to element where text should be default id 'TBODY/TR'
        :param cell:    Xpath to element where text should be default i:d 'TD'
        :return:        element_row, element_col, text_row, text_col
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_column_and_row_by_text(self.TABLE, "text_to_find")``
            | ``element_rowtable = QAutoRobot.get_table_column_and_row_by_text(self.ID_TABLE, parameters[u'member_id'],"TBODY/TR","TD/SPAN")``
            | ``element_rowtable[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_table_column_and_row_by_text((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "text_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row == "" or row is None:
            row = "TBODY/TR"

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            element_column = elem.find_elements(By.XPATH, cell)
            for elem_c in element_column:
                if self.is_visible(elem_c) and self.get_text(elem_c) == text:
                    # return "real" row and column numbers
                    column = element_column.index(elem_c) + 1
                    row = element_rows.index(elem) + 1
                    print("* Found text '%s' from column '%s' and row '%s'" % (text, column, row))
                    return elem, elem_c, row, column

        self.fail("* Text '%s' not found from table" % text)

    def get_table_column_and_row_by_value_contains(self, element, value, row="TBODY/TR", cell="TD"):
        """
        **Find table column and row number by contains value**

        :param element: Table element representation (By, value) or WebElement object.
        :param value: Element's value should contains
        :param row: Xpath to element where text should be default id 'TBODY/TR'
        :param cell: Xpath to element where text should be default id 'TD'
        :return: element_row, element_col, text_row, text_col
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_column_and_row_by_value_contains(self.TABLE, "text_to_find")``
            | ``element_rowtable = QAutoRobot.get_table_column_and_row_by_value_contains(self.ID_TABLE, parameters[u'member_id'],"TBODY/TR","TD/SPAN")``
            | ``element_rowtable[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_table_column_and_row_by_value_contains((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "text_to_find_contains")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row == "" or row is None:
            row = "TBODY/TR"

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            element_column = elem.find_elements(By.XPATH, cell)
            for elem_c in element_column:
                if self.is_visible(elem_c) and value in self.get_value(elem_c):
                    # return "real" row and column numbers
                    column = element_column.index(elem_c) + 1
                    row = element_rows.index(elem) + 1
                    print("* Found value contains '%s' from column '%s' and row '%s'" % (value, column, row))
                    return elem, elem_c, row, column

        self.fail("* Value '%s' contains not found from table" % value)

    def get_table_column_and_row_by_value(self, element, value, row="TBODY/TR", cell="TD"):
        """
        **Find table column and row number by value**

        :param element: Table element representation (By, value) or WebElement object.
        :param value: Element's value which should be
        :param row: Xpath to element where text should be default id 'TBODY/TR'
        :param cell: Xpath to element where text should be default id 'TD'
        :return: element_row, element_col, text_row, text_col
        -------------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_column_and_row_by_value(self.TABLE, "text_to_find")``
            | ``element_rowtable = QAutoRobot.get_table_column_and_row_by_value(self.ID_TABLE, parameters[u'member_id'],"TBODY/TR","TD/SPAN")``
            | ``element_rowtable[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_table_column_and_row_by_value((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "text_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row == "" or row is None:
            row = "TBODY/TR"

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            element_column = elem.find_elements(By.XPATH, cell)
            for elem_c in element_column:
                if self.is_visible(elem_c) and self.get_value(elem_c) == value:
                    # return "real" row and column numbers
                    column = element_column.index(elem_c) + 1
                    row = element_rows.index(elem) + 1
                    print("* Value text '%s' from column '%s' and row '%s'" % (value, column, row))
                    return elem, elem_c, row, column

        self.fail("* Value '%s' not found from table" % value)

    def get_table_column_and_row_by_attribute_value(self, element, attribute, value, row="TBODY/TR", cell="TD"):
        """
        **Find table column and row number by attribute value**

        :param element: Table element representation (By, value) or WebElement object.
        :param attribute: Element's attribute
        :param value: Element's attribute value should contains
        :param row: Xpath to element where text should be default id 'TBODY/TR'
        :param cell: Xpath to element where text should be default id 'TD'
        :return: element_row, element_col, text_row, text_col
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_column_and_row_by_attribute_value(self.TABLE, "name", "attribute_to_find")``
            | ``element_rowtable = QAutoRobot.get_table_column_and_row_by_attribute_value(self.ID_TABLE, "name", parameters[u'member_id'],"TBODY/TR","TD/SPAN")``
            | ``element_rowtable[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_table_column_and_row_by_attribute_value((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "name", "attribute_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row == "" or row is None:
            row = "TBODY/TR"

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            element_column = elem.find_elements(By.XPATH, cell)
            for elem_c in element_column:
                if self.is_visible(elem_c) and self.get_attribute(elem_c, attribute) == value:
                    # return "real" row and column numbers
                    column = element_column.index(elem_c) + 1
                    row = element_rows.index(elem) + 1
                    print("* Found attribute with value '%s' from column '%s' and row '%s'" % (value, column, row))
                    return elem, elem_c, row, column

        self.fail("* Attribute with value '%s' not found from table" % value)

    def get_table_column_and_row_by_attribute_value_contains(self, element, attribute, value, row="TBODY/TR",
                                                             cell="TD"):
        """
        **Find table column and row number by attribute value contains**

        :param element: Table element representation (By, value) or WebElement object.
        :param attribute: Element's attribute
        :param value: Element's attribute value should contains
        :param row: Xpath to element where text should be default id 'TBODY/TR'
        :param cell: Xpath to element where text should be default id 'TD'
        :return: element_row, element_col, text_row, text_col
        ---------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_column_and_row_by_attribute_value_contains(self.TABLE, "name", "attribute_to_find")``
            | ``element_rowtable = QAutoRobot.get_table_column_and_row_by_attribute_value_contains(self.ID_TABLE, "name", parameters[u'member_id'],"TBODY/TR","TD/SPAN")``
            | ``element_rowtable[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_table_column_and_row_by_attribute_value_contains((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "name", "attribute_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row == "" or row is None:
            row = "TBODY/TR"

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            element_column = elem.find_elements(By.XPATH, cell)
            for elem_c in element_column:
                if self.is_visible(elem_c) and value in self.get_attribute(elem_c, attribute):
                    # return "real" row and column numbers
                    column = element_column.index(elem_c) + 1
                    row = element_rows.index(elem) + 1
                    print("* Found attribute contains value '%s' from column '%s' and row '%s'" % (value, column, row))
                    return elem, elem_c, row, column

        self.fail("* Attribute with value '%s' not found from table" % value)

    def get_table_column_and_row_by_multiple_text(self, element, text1, text2, row="TBODY/TR", cell="TD"):
        """
        **Find table column and row number by text**

        :param element: Table element representation (By, value) or WebElement object.
        :param text1: Element's text1 which should be (match text1 and text2)
        :param text2: Element's text2 which should be (match text1 and text2)
        :param row: Xpath to element where text should be default id 'TBODY/TR'
        :param cell: Xpath to element where text should be default id 'TD'
        :return: element1_row, element1_col, text1_row, text1_column, element2_row, element2_col, text2_row, text2_column
        ------------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_column_and_row_by_multiple_text(self.TABLE, "text_to_find1", "text_to_find2")``
            | ``element_rowtable = QAutoRobot.get_table_column_and_row_by_multiple_text(self.ID_TABLE, parameters[u'member_id'], parameters[u'group_id'],"TBODY/TR","TD/SPAN")``
            | ``element_rowtable[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_table_column_and_row_by_multiple_text((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "text_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row == "" or row is None:
            row = "TBODY/TR"

        temp_row = -1
        temp_elem = None
        temp_column = None

        element_rows = element.find_elements(By.XPATH, row)

        for elem in element_rows:
            element_column = elem.find_elements(By.XPATH, cell)
            for elem_c in element_column:
                if self.is_visible(elem_c) and self.get_text(elem_c) == text1:
                    temp_row = element_rows.index(elem)
                    temp_column = element_column.index(elem_c)
                    temp_elem = elem
                    temp_elem_c = elem_c
                if self.is_visible(elem_c) and self.get_text(elem_c) == text2 and element_rows.index(elem) == temp_row:
                    # return "real" row and column numbers
                    column = element_column.index(elem_c) + 1
                    row = element_rows.index(elem) + 1
                    print("* Found text1 '%s' from column '%s' and row '%s'" % (text1, temp_column + 1, temp_row + 1))
                    print("* Found text2 '%s' from column '%s' and row '%s'" % (text2, column, row))
                    return temp_elem, temp_elem_c, temp_row + 1, temp_column + 1, elem, elem_c, row, column

        self.fail("* Texts '%s' and '%s' not found from table in same row" % (text1, text2))

    def get_table_cell_text_by_column_and_row(self, element, column, row, cell="TD"):
        """
        **get table cell text by given column and row.**

        :param element: Table element representation (By, value) or WebElement object.
        :param column: Table column where to click
        :param row: Table row where to click
        :param cell: Xpath to element which should be clicked, default is 'TD'
        :return: Xpath to element which should be clicked, default is 'TD'
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_table_cell_text_by_column_and_row(self.TABLE, 1, 1)``
            | using representation
            | ``QAutoRobot.get_table_cell_text_by_column_and_row((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), 1, 1)``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        element_row = element.find_elements(By.XPATH, "TBODY/TR")[int(row) - 1]
        table_text = element_row.find_elements(By.XPATH, cell)[int(column) - 1].text
        print("* Found text '%s' from column '%s' and row '%s'" % (table_text, str(column), str(row)))
        return table_text

    def click_table_cell_by_column_and_row(self, element, column, row, cell="TD"):
        """
        **Click table cell by given column and row.**

        :param element: Table element representation (By, value) or WebElement object.
        :param column: Table column where to click
        :param row: Table row where to click
        :param cell: Xpath to element which should be clicked, default is 'TD'
        --------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.click_table_cell_by_column_and_row(self.TABLE, 1, 1)``
            | using representation
            | ``QAutoRobot.click_table_cell_by_column_and_row((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), 1, 1)``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        element_row = element.find_elements(By.XPATH, "TBODY/TR")[int(row) - 1]
        self.click_element(element_row.find_elements(By.XPATH, cell)[int(column) - 1])

    def click_element_from_table_row(self, element, row, element_path):
        """
        **Click table cell by given row.**

        :param element: Table element representation (By, value) or WebElement object.
        :param row: Table row where is link or button to click
        :param element_path: Path to element which should be clicked
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.click_table_cell_by_column_and_row(self.TABLE, 1, "TD/DIV/H4/A")``
            | using representation
            | ``QAutoRobot.click_table_cell_by_column_and_row((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), 1, "TD/DIV/H4/A")``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        element_row = element.find_elements(By.XPATH, "TBODY/TR")[int(row) - 1]
        self.click_element(element_row.find_element(By.XPATH, element_path))

    def get_list_row_by_text_contains(self, element, text, row="LI", cell=""):
        """
        **Find list item row number by contains text from UL list**

        :param element: List element representation (By, value) or WebElement object.
        :param text: Element's text should contains
        :param row: Xpath to element where text should be default id 'LI'
        :param cell: Xpath to element where text should be default id ''
        :return: element_row, text_row
        -----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_list_row_by_text_contains(self.LIST, "text_to_find")``
            | ``element_rowlist = QAutoRobot.get_list_row_by_text_contains(self.ID_LIST, parameters[u'member_id'],"LI")``
            | ``element_rowlist[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_list_row_by_text_contains((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "text_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row is None or row == "":
            row = "LI"
        if cell is None:
            cell = ""

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            if cell == "" and self.is_visible(elem) and text in self.get_text(elem):
                row = element_rows.index(elem) + 1
                print("* Found text '%s' from row '%s'" % (text, row))
                return elem, row
            elif cell:
                cell_elements = elem.find_elements(By.XPATH, cell)
                for cell_elem in cell_elements:
                    if self.is_visible(cell_elem) and text in self.get_text(cell_elem):
                        row = element_rows.index(elem) + 1
                        print("* Found text '%s' from row '%s'" % (text, row))
                        return cell_elem, row

        print("* Text '%s' not found from list" % text)
        return None, None

    def get_list_row_by_text(self, element, text, row="LI", cell=""):
        """
        **Find list item row number by text from UL list**

        :param element: List element representation (By, value) or WebElement object.
        :param text: Element's text which should be
        :param row: Xpath to element where text should be default id 'LI'
        :param cell: Xpath to element where text should be default id ''
        :return: element_row, text_row
        -------------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_list_row_by_text(self.LIST, "text_to_find")``
            | ``element_rowlist = QAutoRobot.get_list_row_by_text(self.LIST, parameters[u'member_id'],"LI")``
            | ``element_rowlist[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_list_row_by_text((By.CSS_SELECTOR, u'#tableTest>tbody>tr>td'), "text_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row is None or row == "":
            row = "LI"
        if cell is None:
            cell = ""

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            if cell == "" and self.is_visible(elem) and text == self.get_text(elem):
                # return "real" row and column numbers
                row = element_rows.index(elem) + 1
                print("* Found text '%s' from row '%s'" % (text, row))
                return elem, row
            elif cell:
                cell_elements = elem.find_elements(By.XPATH, cell)
                for cell_elem in cell_elements:
                    if self.is_visible(cell_elem) and text == self.get_text(cell_elem):
                        row = element_rows.index(elem) + 1
                        print("* Found text '%s' from row '%s'" % (text, row))
                        return cell_elem, row

        print("* Text '%s' not found from list" % text)
        return None, None

    def get_list_row_by_value(self, element, value, row="LI", cell=""):
        """
        **Find list item row number by value from UL list**

        :param element: List element representation (By, value) or WebElement object.
        :param value: Element's value which should be
        :param row: Xpath to element where text should be default id 'LI'
        :param cell: Xpath to element where text should be default id ''
        :return: element_row, value_row
        ----------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_list_row_by_value(self.LIST, "value_to_find")``
            | ``element_rowlist = QAutoRobot.get_list_row_by_value(self.LIST, parameters[u'member_id'],"LI")``
            | ``element_rowlist[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_list_row_by_value((By.CSS_SELECTOR, u'#list'), "value_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row is None or row == "":
            row = "LI"
        if cell is None:
            cell = ""

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            if cell == "" and self.is_visible(elem) and self.get_value(elem) == value:
                # return "real" row and column numbers
                row = element_rows.index(elem) + 1
                print("* Found value '%s' from row '%s'" % (value, row))
                return elem, row
            elif cell:
                cell_elements = elem.find_elements(By.XPATH, cell)
                for cell_elem in cell_elements:
                    if self.is_visible(cell_elem) and self.get_value(cell_elem) == value:
                        row = element_rows.index(elem) + 1
                        print("* Found value '%s' from row '%s'" % (value, row))
                        return cell_elem, row

        print("* Value '%s' not found from list" % value)
        return None, None

    def get_list_row_by_value_contains(self, element, value, row="LI", cell=""):
        """
        **Find list item row number by value contains from UL list**

        :param element: List element representation (By, value) or WebElement object.
        :param value: Element's value should contains
        :param row: Xpath to element where text should be default id 'LI'
        :param cell: Xpath to element where text should be default id ''
        :return: element_row, value_row
        ---------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_list_row_by_value_contains(self.LIST, "value_to_find")``
            | ``element_rowlist = QAutoRobot.get_list_row_by_value_contains(self.LIST, parameters[u'member_id'],"LI","span")``
            | ``element_rowlist[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_list_row_by_value_contains((By.CSS_SELECTOR, u'#list'), "value_to_find")``

        """

        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row is None or row == "":
            row = "LI"
        if cell is None:
            cell = ""

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            if cell == "" and self.is_visible(elem) and value in self.get_value(elem):
                row = element_rows.index(elem) + 1
                print("* Found value contains '%s' from row '%s'" % (value, row))
                return elem, row
            elif cell:
                cell_elements = elem.find_elements(By.XPATH, cell)
                for cell_elem in cell_elements:
                    if self.is_visible(cell_elem) and value in self.get_value(cell_elem):
                        row = element_rows.index(elem) + 1
                        print("* Found value contains '%s' from row '%s'" % (value, row))
                        return cell_elem, row

        print("* Value '%s' contains not found from list" % value)
        return None, None

    def get_list_row_by_attribute_value(self, element, attribute, value, row="LI", cell=""):
        """
        **Find list item row number by attribute value contains from UL list**

        :param element: List element representation (By, value) or WebElement object.
        :param attribute: Element's attribute
        :param value: Element's attribute value should contains
        :param row: Xpath to element where text should be default id 'LI'
        :param cell: Xpath to element where text should be default id ''
        :return: element_row, value_row
        ---------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_list_row_by_attribute_value(self.LIST, "name", "value_to_find")``
            | ``element_rowlist = QAutoRobot.get_list_row_by_attribute_value(self.LIST, "name", parameters[u'member_id'], "LI","span")``
            | ``element_rowlist[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_list_row_by_attribute_value((By.CSS_SELECTOR, u'#list'), "name", "value_to_find")``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row is None or row == "":
            row = "LI"
        if cell is None:
            cell = ""

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            if cell == "" and self.is_visible(elem) and self.get_attribute(elem, attribute) == value:
                row = element_rows.index(elem) + 1
                print("* Found attribute with value '%s' from row '%s'" % (value, row))
                return elem, row
            elif cell:
                cell_elements = elem.find_elements(By.XPATH, cell)
                for cell_elem in cell_elements:
                    if self.is_visible(cell_elem) and self.get_attribute(cell_elem, attribute) == value:
                        row = element_rows.index(elem) + 1
                        print("* Found attribute with value '%s' from row '%s'" % (value, row))
                        return cell_elem, row

        print("* Attribute with value '%s' contains not found from list" % value)
        return None, None

    def get_list_row_by_attribute_value_contains(self, element, attribute, value, row="LI", cell=""):
        """
        **Find list item row number by attribute value contains from UL list**

        :param element: List element representation (By, value) or WebElement object.
        :param attribute: Element's attribute
        :param value: Element's attribute value should contains
        :param row: Xpath to element where text should be default id 'LI'
        :param cell: Xpath to element where text should be default id ''
        :return: element_row, value_row
        ---------------
        :Example:
            | *Page model level example*
            | using web element
            | ``QAutoRobot.get_list_row_by_attribute_value_contains(self.LIST, "name", "value_to_find","span")``
            | ``element_rowlist = QAutoRobot.get_list_row_by_attribute_value_contains(self.LIST, "name", parameters[u'member_id'],"LI")``
            | ``element_rowlist[0].find_element(By.CSS_SELECTOR, '.fa-wrench').click()``
            | using representation
            | ``QAutoRobot.get_list_row_by_attribute_value_contains((By.CSS_SELECTOR, u'#list'), "name", "value_to_find")``

        """
        self.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        if row is None or row == "":
            row = "LI"
        if cell is None:
            cell = ""

        element_rows = element.find_elements(By.XPATH, row)
        for elem in element_rows:
            if cell == "" and self.is_visible(elem) and value in self.get_attribute(elem, attribute):
                row = element_rows.index(elem) + 1
                print("* Found attribute contains value '%s' from row '%s'" % (value, row))
                return elem, row
            elif cell:
                cell_elements = elem.find_elements(By.XPATH, cell)
                for cell_elem in cell_elements:
                    if self.is_visible(cell_elem) and value in self.get_attribute(cell_elem, attribute):
                        row = element_rows.index(elem) + 1
                        print("* Found attribute contains value '%s' from row '%s'" % (value, row))
                        return cell_elem, row

        print("* Attribute with value '%s' contains not found from list" % value)
        return None, None

    def go_back(self):
        """
        **Simulates pressing Back button in browser window**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.go_back()``

        """
        driver = self.driver_cache._get_current_driver()
        DebugLog.log("* Go back in browser")
        driver.back()

    def delete_all_cookies(self):
        """
        **Deletes all cookies from current session**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.delete_all_cookies()``

        """
        driver = self.driver_cache._get_current_driver()
        DebugLog.log("* Delete all cookies")
        driver.delete_all_cookies()

    def alert_is_present(self):
        """
        **Check if alert is present**

        :return: Alert as webdriver element alert if alert not found returns false
        --------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.alert_is_present()``

        """
        driver = self.driver_cache._get_current_driver()
        try:
            driver.switch_to.alert
            DebugLog.log("* Alsert is present")
            return True
        except NoAlertPresentException:
            return False

    def alert_should_be_present(self):
        """
        **Check if alert is present**

        :return: Alert as webdriver element alert if alert not found returns false
        ---------------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.alert_is_present()``

        """
        driver = self.driver_cache._get_current_driver()
        try:
            driver.switch_to.alert.dismiss()
        except NoAlertPresentException:
            return False

    def accept_alert(self):
        """
        **Accepts current alert window**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.accept_alert()``

        """
        driver = self.driver_cache._get_current_driver()
        driver.switch_to_alert().accept()
        DebugLog.log("* Click Accept/OK in alert box")

    def dismiss_alert(self):
        """
        **Dismisses current alert window**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.dismiss_alert()``

        """
        driver = self.driver_cache._get_current_driver()
        driver.switch_to_alert().dismiss()
        DebugLog.log("* Click Dismiss/Cancel in alert box")

    def reload_page(self):
        """
        **Refreshes page**

        :Example:
            | *Page model level example*
            | ``QAutoRobot.refresh_page()``

        """
        driver = self.driver_cache._get_current_driver()
        DebugLog.log("* Reload weg page")
        driver.refresh()

    def get_js_memory_heap(self, measurement_name):
        """
        **Returns memory heap**

        :param measurement_name: String represents name of measurement point
        -------------------
        :Example:
            | *Page model level example*
            | ``QAutoRobot.get_js_memory_heap(measurement_name)``

        """
        if not self.driver_cache._is_gc():
            print("get_js_memory_heap is currently supported only by the Google Chrome browser.")
            return

        memory_data = self.execute_javascript("return performance.memory;", log=False)
        if memory_data and 'usedJSHeapSize' in memory_data:

            ts = int(time.time()) * 1000

            try:
                measurement_folder = os.path.join(get_config_value("reporting_folder"),
                                                  GlobalUtils.MEASUREMENTS_FOLDER_NAME)
                if not os.path.exists(measurement_folder):
                    os.mkdir(measurement_folder)
            except Exception as e:
                print("Could not create measurements folder:\n%s" % str(e))

            js_file = os.path.join(measurement_folder, GlobalUtils.MEMORY_DATA_PREFIX + str(measurement_name) + ".js")

            # javascript file
            try:
                if (os.path.isfile(js_file)):
                    read_lines = get_file_lines(js_file)
                    str_to_insert = "{'memoryHeap': '" + str(memory_data['usedJSHeapSize']) + "', 'timestamp': '" + str(
                        ts) + \
                                    "', 'label': '" + str(measurement_name) + "'},\n"
                    new_lines = read_lines[:-1] + [str_to_insert] + [read_lines[-1]]
                    content = "".join(new_lines)
                    save_content_to_file(content, js_file)
                else:
                    heading = "var memory_js_data = ["
                    lines = "\n{'memoryHeap': '" + str(memory_data['usedJSHeapSize']) + "', 'timestamp': '" + str(ts) + \
                            "', 'label': '" + str(measurement_name) + "'},"
                    ending = "\n];"
                    new_lines = heading + lines + ending
                    content = "".join(new_lines)
                    save_content_to_file(content, js_file)
                return memory_data['usedJSHeapSize']
            except Exception as e:
                print("Could not generate js file:\n%s" % str(e))
                return None
        else:
            print("%s: No memory heap to measure!!" % measurement_name)
            return None


class CanvasMethods(object):
    """
    **Class that contains methods for Canvas based areas**
    """

    def __init__(self, driver_cache=None):
        self.driver_cache = driver_cache and driver_cache or DriverCache()

    def click_canvas(self, element):
        """
        **Click at element**

        :param element: Element representation (By, value) or WebElement

        """
        html5_element = self.find_element_canvas(element)
        # print "html5 element: ", html5_element.text
        driver = self.driver_cache._get_current_driver()

        if html5_element:
            value = element[1]
            canvas_id = ""
            canvas_id = value.split("'")[1].split("_")[1]

            all_canvases = driver.find_elements_by_tag_name("canvas")

            if all_canvases:
                correct_canvas = None
                if len(all_canvases) == 1 and (
                        all_canvases[0].size['width'] == 0 or all_canvases[0].size['height'] == 0):
                    unittest.TestCase("assertTrue").assertTrue(False, "No canvas elements found")
                else:
                    for canvas in all_canvases:
                        if canvas.get_attribute("id") == canvas_id:
                            correct_canvas = canvas
                            break

                    if correct_canvas:
                        element_loc_x = html5_element.canvas_location['xCanvas']
                        element_loc_y = html5_element.canvas_location['yCanvas']
                        element_size_width = html5_element.size['width']
                        element_size_height = html5_element.size['height']
                        element_center_x = element_loc_x + int(element_size_width / 2)
                        element_center_y = element_loc_y + int(element_size_height / 2)

                        ActionChains(driver).move_to_element_with_offset(correct_canvas,
                                                                         element_center_x,
                                                                         element_center_y).click().perform()
                        time.sleep(2)
                    else:
                        unittest.TestCase("assertTrue").assertTrue(False, "No correct canvas element found")

            else:
                unittest.TestCase("assertTrue").assertTrue(False, "No canvas elements found")

        else:
            unittest.TestCase("assertTrue").assertTrue(False, "Correct object inside canvas element not found")

    def compare_screenshots_canvas(self, ref_scr_name):
        """
        **Compares screenshots or part of screenshots**

        :param ref_scr_name: Screenshot name in string format

        """

        if not self.screenshot_parser:
            self.screenshot_parser = XmlScreenshotParser()

        xml_meta_data, ref_scr_file_name_path = CommonUtils._check_screenshot_file_name(self.screenshot_parser,
                                                                                        ref_scr_name)

        ref_scr_x = int(xml_meta_data['x'])
        ref_scr_y = int(xml_meta_data['y'])
        ref_scr_w = int(xml_meta_data['w'])
        ref_scr_h = int(xml_meta_data['h'])
        if get_config_value("runtime_similarity") != '':
            similarity = get_config_value("runtime_similarity")
        else:
            similarity = int(xml_meta_data['similarity'])

        CommonUtils()._handle_screenshot_comparison(ref_scr_file_name_path, ref_scr_x, ref_scr_y,
                                                    ref_scr_w, ref_scr_h, similarity)

    def compare_element_screenshots_canvas(self, element, ref_scr_name):
        """
        **Compares screenshots of elements**

        :param element: Element representation (By, value)
        :param ref_scr_name: Screenshot name in string format

        """
        self.compare_screenshots_canvas(ref_scr_name)

    def _is_visible_canvas(self, element):
        try:
            if type(element) in [tuple, QAutoElement]:
                # only canvas element visibility is checked at the moment
                value = element[1]
                canvas_id = ""
                canvas_id = value.split("'")[1].split("_")[1]

                driver = self.driver_cache._get_current_driver()
                all_canvases = driver.find_elements_by_tag_name("canvas")

                if all_canvases:
                    correct_canvas = None
                    if len(all_canvases) == 1 and all_canvases[0].size['width'] == 0 and all_canvases[0].size[
                        'height'] == 0:
                        return False
                    else:
                        for canvas in all_canvases:
                            if canvas.get_attribute("id") == canvas_id:
                                correct_canvas = canvas
                                break

                        if correct_canvas:
                            return correct_canvas.is_displayed()
                        else:
                            return False
                else:
                    return False
            else:
                # base canvas element
                return element.is_displayed()

        except WebDriverException:
            return False

    def wait_until_element_is_visible_canvas(self, element, msg=None, timeout=None):
        """
        **Wait until visible**

        :param element: element: (By, 'value')
        :param msg: Message
        :param timeout: Using default timeout

        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        if not msg:
            if type(element) in [tuple, QAutoElement]:
                msg = "Element '%s' is not visible for %s seconds" % (element[1], timeout)
            else:
                msg = "Element '%s' is not visible for %s seconds" % (element.text, timeout)

        CommonMethodsHelpers.webdriver_wait(lambda driver: self._is_visible_canvas(element),
                                            self.driver_cache._get_current_driver(), msg, timeout)


class Asserts(object):
    """
    **Class that contains methods for making verifications**
    """

    def __init__(self, driver_cache=None):
        self.driver_cache = driver_cache and driver_cache or DriverCache()
        self._wm = WebMethods(self.driver_cache)

    def element_text_should_be(self, element, text):
        """
        **Verifies if text in element corresponds to expected one**

        :param element: Element representation (By, value).
        :param text: String text
        ---------------
        :Example:
            | ``QAutoRobot.element_text_should_be(self.element, text)``
        """
        CommonMethodsHelpers.assert_equal(text, self._wm.get_text(element))
        print("Element locator " + element[0] + ":" + element[1])

    def element_value_should_be(self, element, value):
        """
        **Verifies if value of element corresponds to expected one**

        :param element: Element representation (By, value).
        :param value: String
        ------------
        :Example:
            | ``QAutoRobot.element_text_should_be(self.element, value)``
        """
        CommonMethodsHelpers.assert_equal(value, self._wm.get_value(element))
        print("Element locator " + element[0] + ":" + element[1])

    def list_value_should_be(self, element, value):
        """
        **Verifies if value of selected item in drop-down list corresponds to expected one**

        :param element: Element representation (By, value).
        :param value: Value of the item
        -------------------
        :Example:
            | ``QAutoRobot.list_value_should_be(self.element, value)``

        """
        CommonMethodsHelpers.assert_equal(value, self._wm.get_selected_list_value(element))
        print("Element locator " + element[0] + ":" + element[1])

    def list_label_should_be(self, element, text):
        """
        **Verifies if text of selected item in drop-down list corresponds  to expected one**

        :param element: Element representation (By, value).
        :param text: String text
        --------------
        :Example:
            | ``QAutoRobot.list_label_should_be(self.element, text)``
        """
        CommonMethodsHelpers.assert_equal(text, self._wm.get_selected_list_label(element))
        print("Element locator " + element[0] + ":" + element[1])

    def element_attribute_should_be(self, element, attribute, value):
        """
        **Verifies if attribute of element corresponds  to expected one**

        :param element: Element representation (By, value).
        :param attribute: Attribute of an element
        :param value: String text
        ---------------
        :Example:
            | ``QAutoRobot.wait_until_element_should_not_be(self.element, attribute, value)``
        """
        CommonMethodsHelpers.assert_equal(value, self._wm.get_attribute(element, attribute))
        print("Element locator " + element[0] + ":" + element[1])

    def element_attribute_should_contains(self, element, attr, expected_value):
        """
        **Verify if attribute contains expected value**

        :param element: Element representation (By, value) or WebElement.
        :param attr: Element's attribute
        :param expected_value: Element's attribute value which should be contained
        -------------
        :Example:
            | ``QAutoRobot.element_attribute_should_contains(self.CONTACT_QAUTOMATE_FI, u'href', u'mailto')``
        """
        atr_text = self._wm.get_attribute(element, attr)
        print("Element locator " + element[0] + ":" + element[1])
        try:
            msg = "Element attribute '%s' doesn't contain text '%s'" % (attr, expected_value)
        except:
            msg = "Element attribute doesn't contain correct text"
        unittest.TestCase("assertTrue").assertTrue(expected_value in atr_text, msg)
        try:
            print("Element attribute '%s' contains text '%s'" % (attr, expected_value))
        except:
            pass

    def elements_count_should_be(self, element, value_int):
        """
        **Verifies if count of elements corresponds to expected one**

        :param element: Element representation (By, value).
        :param value_int: Integer number
        -----------------
        :Example:
            | ``QAutoRobot.elements_count_should_be(self.element, value_int)``
        """
        CommonMethodsHelpers.assert_equal(int(value_int), self._wm.get_elements_count(element))
        print("Element locator " + element[0] + ":" + element[1])

    def element_should_contain(self, element, text):
        """
        **Verifies if text in element contains given text**

        :param element: Element representation (By, value).
        :param text: String text
        ------------------
        :Example:
            | ``QAutoRobot.element_should_contain(self.CLASS_MAIN_HEADER, text)``
        """
        el_text = self._wm.get_text(element)
        print("Element locator " + element[0] + ":" + element[1])
        try:
            msg = "Element text '%s' doesn't contain text '%s'" % (el_text, text)
        except:
            msg = "Element text doesn't contain correct text"
        unittest.TestCase("assertTrue").assertTrue(text in el_text, msg)

    def element_should_be_visible(self, element):
        """
        **Verify that element is visible.**

        Use ``unittest.assertTrue()`` to verify that element is visible.

        :param element: Element representation (By, value).
        --------------
        :Example:
            | ``rcm = (By.ID, "map-player-rcMenu")``
            | ``element_should_be_visible(self, rcm)``
        """
        by = element[0]
        value = element[1]
        visible = self._wm.is_visible(element)
        unittest.TestCase("assertTrue").assertTrue(visible,
                                                   "Element {By: '%s', value: '%s'} is not visible" % (by, value))
        try:
            DebugLog.log("* Element 'By: %s, value: %s' is visible" % (by, value))
        except:
            DebugLog.log("* Element is visible")

    def element_should_be_present(self, element):
        """
        **Verify that element is present.**

        Use ``unittest.assertTrue()`` to verify that element is present.

        :param element: Element representation (By, value).
        --------------
        :Example:
            | ``rcm = (By.ID, "map-player-rcMenu")``
            | ``element_should_be_present(self, rcm)``
        """
        by = element[0]
        value = element[1]
        present = self._wm.is_present(element)
        unittest.TestCase("assertTrue").assertTrue(present,
                                                   "Element {By: '%s', value: '%s'} is not present" % (by, value))
        try:
            DebugLog.log("* Element 'By: %s, value: %s' is present" % (by, value))
        except:
            DebugLog.log("* Element is present")

    def element_should_be_disabled(self, element):
        """
        **Verify that element is disabled.**

        Use ``unittest.assertTrue()`` to verify that element is disabled.

        :param element: Element representation (By, value).
        -----------------
        :Example:
            | ``rcm = (By.ID, "map-player-rcMenu")``
            | ``element_should_be_disabled(self, rcm)``
        """
        by = element[0]
        value = element[1]
        present = self._wm.is_disabled(element)
        unittest.TestCase("assertTrue").assertTrue(present,
                                                   "Element {By: '%s', value: '%s'} is not disabled" % (by, value))
        try:
            DebugLog.log("* Element 'By: %s, value: %s' is disabled" % (by, value))
        except:
            DebugLog.log("* Element is disabled")

    def element_should_be_enabled(self, element):
        """
        **Verify that element is enabled.**

        Use ``unittest.assertTrue()`` to verify that element is disabled.

        :param element: Element representation (By, value).
        -----------------
        :Example:
            | ``rcm = (By.ID, "map-player-rcMenu")``
            | ``element_should_be_enabled(self, rcm)``

        """
        by = element[0]
        value = element[1]
        present = self._wm.is_enabled(element)
        unittest.TestCase("assertTrue").assertTrue(present,
                                                   "Element {By: '%s', value: '%s'} is not enabled" % (by, value))
        try:
            DebugLog.log("* Element 'By: %s, value: %s' is enabled" % (by, value))
        except:
            DebugLog.log("* Element is enabled")

    def title_should_be(self, string):
        """
        **Verifies if page title corresponds to expected one**

        :param string: expected page title

        """
        driver = self.driver_cache._get_current_driver()
        title = driver.title
        msgpass = "Page title: %s" % title
        msg = "Wrong page title"
        CommonMethodsHelpers.assert_equal(string, title, msgpass, msg)

    def element_should_be_table_column_and_row(self, element, text, column, row, cell="TD"):
        """
        **Verify that text from selected table column and row.**

        Use ``unittest.assert_equal()`` to verify that text is correct.

        :param element: Table element representation (By, value) or WebElement object.
        :param text: Element's text which should be
        :param column: Table column where to verify text
        :param row: Table row where to verify text
        :param cell: Xpath to element where text should be, default is 'TD'
        --------------
        :Example:
            | ``TABLE = (By.ID, "my-table")``
            | ``element_should_be_table_column_and_row(self, TABLE, "text_to_verify", 2, 1)``

        """
        self._wm.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        element_row = element.find_elements(By.XPATH, "TBODY/TR")[int(row) - 1]
        msgpass = "* Text found from table: %s" % text
        msg = "Wrong text in table:"
        CommonMethodsHelpers.assert_equal(text,
                                          self._wm.get_text(element_row.find_elements(By.XPATH, cell)[int(column) - 1]),
                                          msgpass, msg)

    def verify_rest_api_xml_value(self, url, method, expected_file, auth_file, request_file_xml):
        """
        **Verifies if REST-API values are equal to expected ones. Supports get, post, put and delete methods. Only XML format.**

        Xpath examples: ``"//city[1]/country[1]/text()"``, ``"//city[1]/coord[1]/@lat"``

        :param url: Web request url
        :param method: get, post, put or delete
        :param expected_file: Text file which includes xpaths and expected values to verify. One verification per line: xpath expected_value
        :param auth_file: Optional login credentials text file. Only one line: username password. Leave blank if not needed.
        :param request_file_xml: Name of the request xml file. Leave blank if not needed.
        ----------------
        :Example:
            | ``url = u'http://api.openweathermap.org/data/2.5/weather?q=London,uk&appid=2de143494c0b295cca9337e1e96b00e0&mode=xml'``
            | ``QAutoRobot.verify_rest_api_xml_value(url, u'get', u'expected.txt', u'', u'')``
            |
            | ``QAutoRobot.verify_rest_api_xml_value(u'http://exampleurl.com', u'post', u'expected_response.txt', u'auth.txt', u'request.xml')``
        """
        if method.lower() not in ('get', 'post', 'put', 'delete'):
            self._wm.fail("Rest method not recognized")
        if method.lower() == 'get':
            root = etree.fromstring(self._wm.get_web_response(url, "get", auth_file, data=None).text)
        else:
            request_file = os.path.abspath(
                os.path.join(os.getcwd(), GlobalUtils.XML_REQUEST_FOLDER_NAME, request_file_xml))
            root = etree.fromstring(self._wm.get_web_response(url, method, auth_file, request_file).text)
        try:
            response = etree.tostring(root, pretty_print=True)
        except:
            response = etree.tostring(root)
        save_content_to_file(str(response.strip('\r\n')), os.path.abspath(os.path.join(os.getcwd(),
                                                                                       GlobalUtils.XML_DEBUG_FOLDER_NAME,
                                                                                       "response_file.xml")))

        expected_response_file = get_file_lines(
            os.path.abspath(os.path.join(os.getcwd(), GlobalUtils.XML_RESPONSE_FOLDER_NAME,
                                         expected_file)))
        msgpass = "* Values are equal"
        msg = "Values are not equal"
        for line in expected_response_file:
            (xpath, expected_value) = line.split()
            CommonMethodsHelpers.assert_equal(expected_value, ''.join(root.xpath(xpath)), msgpass, msg)

    def verify_rest_api_json_value(self, url, method, expected_file, auth_file, request_file_json):
        """
        **Verifies if REST-API values are equal to expected ones. Supports get, post, put and delete methods. Only JSON format.**

        Directories for request, response and login files are in your working directory ``../data/..`` Key example: coord.lat

        :param url: Web request url
        :param method: Rest-api method. Get, post, put or delete.
        :param expected_file: Text file which includes key/value pairs to verify. One verification per line: key expected_value.
        :param auth_file: Optional login credentials text file. Only one line: username password. Leave blank if not needed.
        :param request_file_json: Name of the request file. Leave blank if not needed.
        -----------------
        :Example:
            | ``url = u'http://api.openweathermap.org/data/2.5/weather?q=London,uk&appid=2de143494c0b295cca9337e1e96b00e0'``
            | ``QAutoRobot.verify_rest_api_json_value(url, u'get', u'expected.txt', u'', u'')``
            |
            | ``QAutoRobot.verify_rest_api_json_value(u'http://exampleurl.com', u'post', u'expected_response.txt', u'auth.txt', u'request.txt')``
        """
        if method.lower() not in ('get', 'post', 'put', 'delete'):
            self._wm.fail("Rest method not recognized")
        if method.lower() == 'get':
            response = loads(self._wm.get_web_response(url, method, auth_file, data=None).text)
        else:
            request_file = os.path.abspath(
                os.path.join(os.getcwd(), GlobalUtils.JSON_REQUEST_FOLDER_NAME, request_file_json))
            response = loads(self._wm.get_web_response(url, method, auth_file, get_file_content(request_file)).text)

        response_to_file = dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
        save_content_to_file(str(response_to_file.strip('\r\n')),
                             os.path.abspath(
                                 os.path.join(os.getcwd(), GlobalUtils.JSON_DEBUG_FOLDER_NAME, "response_file.txt")))

        expected_response_file = get_file_lines(
            os.path.abspath(os.path.join(os.getcwd(), GlobalUtils.JSON_RESPONSE_FOLDER_NAME,
                                         expected_file)))
        msgpass = "* Values are equal"
        msg = "Values are not equal"
        for line in expected_response_file:
            (key, expected_value) = line.split()
            CommonMethodsHelpers.assert_equal(expected_value, str(reduce(dict.get, key.split("."), response)), msgpass,
                                              msg)

    def verify_soap_api_value(self, url, request_file_xml, response_file, full_file=True):
        """
        **Verifies if SOAP-API values are equal to expected ones.**

        Place for request and response files: ``../data/soap/..``

        If verifying single values: One verification per line in response file. xpath expected_value

        :param url: Web service url
        :param request_file_xml: Request xml filename
        :param response_file: File which includes expectes response or key/value pairs
        :param full_file: Boolean: If true verify full reponse, if false verify single values
        ---------------
        :Example:
            | ``QAutoRobot.verify_soap_api(u'http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', u'soap_xml.xml', response_file.txt)``
        """
        response = self._wm.get_soap_response(url, request_file_xml)
        if full_file:
            expected = get_file_content(os.path.abspath(os.path.join(os.getcwd(), GlobalUtils.SOAP_RESPONSE_FOLDER_NAME,
                                                                     response_file)))
            try:  # Pretty print doesn't work if there is tag mismatch
                tree = etree.XML(expected.decode('utf-8').encode('ascii'))
                expected = etree.tostring(tree, pretty_print=True)
                root = etree.fromstring(response)
                response = etree.tostring(root, pretty_print=True)
            except:
                pass

            save_content_to_file(str(expected.strip('\r\n')), os.path.abspath(os.path.join(os.getcwd(),
                                                                                           GlobalUtils.SOAP_DEBUG_FOLDER_NAME,
                                                                                           "expected_file.xml")))
            save_content_to_file(str(response.strip('\r\n')), os.path.abspath(os.path.join(os.getcwd(),
                                                                                           GlobalUtils.SOAP_DEBUG_FOLDER_NAME,
                                                                                           "response_file.xml")))
            if str(expected) == str(response):
                DebugLog.log("* Files are equal")
            else:
                DebugLog.log("Files are not equal")
                msg = "\n\nExpected:\n'%s' \n\nActual:\n'%s'" % (expected, response)
                self._wm.fail(msg)
        else:
            root = etree.fromstring(response)
            msgpass = "* Values are equal"
            msg = "Values are not equal"
            expected_response_file = get_file_lines(os.path.abspath(os.path.join(os.getcwd(),
                                                                                 GlobalUtils.SOAP_RESPONSE_FOLDER_NAME,
                                                                                 response_file)))
            for line in expected_response_file:
                (xpath, expected_value) = line.split()
                CommonMethodsHelpers.assert_equal(expected_value, ''.join(root.xpath(xpath)), msgpass, msg)

    def element_text_length_should_be(self, element, expected_length):
        """
        **Verifies if element text length is equal to expected. Spaces are also counted.**

        :param element: Element representation (By, value) or WebElement
        :param expected_length: User provided expected length
        -----------------
        :Example:
            | ``QAutoRobot.verify_text_length(self.FEATURELIST_FEATURE, u'13')``
        """
        self._wm.wait_until_element_is_visible(element)
        element = self.find_element_if_not_webelement(element)

        msgpass = "* Text length is same as expected"
        msg = "Text length is different than expected"
        CommonMethodsHelpers.assert_equal(str(expected_length), str(len(element.text)), msgpass, msg)

    def checkbox_should_be_selected(self, element):
        """
        **Check radiobutton is selected.**

        :param element: Radiobutton element
        :Example:
            | ``QAutoRobot.checkbox_should_be_selected(self.CLASS_RADIO)``
        """
        if self._wm.get_attribute(element, "type") == "checkbox":
            msg = "%s checkbox should have been selected" % self._wm.get_attribute(element, "name")
            unittest.TestCase("assertTrue").assertTrue(self._wm.get_attribute(element, "checked"), msg)
            try:
                DebugLog.log("%s checkbox is selected" % self._wm.get_attribute(element, "name"))
            except:
                pass
        else:
            print("Element might be not a radiobutton")

    def checkbox_should_not_be_selected(self, element):
        """
        **Check radiobutton is not selected.**

        :param element: Radiobutton element
        ------------------
        :Example:
            | ``QAutoRobot.checkbox_should_not_be_selected(self.CLASS_RADIO)``
        """
        if self._wm.get_attribute(element, "type") == "checkbox":
            msg = "%s checkbox should not have been selected" % self._wm.get_attribute(element, "name")
            unittest.TestCase("assertTrue").assertTrue(self._wm.get_attribute(element, "checked") is None, msg)
            try:
                DebugLog.log("%s checkbox is not selected" % self._wm.get_attribute(element, "name"))
            except:
                pass
        else:
            print("Element might be not a checkbox")


class CommonWrappers(object):
    def __init__(self, driver_cache=None):
        self.driver_cache = driver_cache and driver_cache or DriverCache()
        self._wm = WebMethods(self.driver_cache)

    def click_element(self, element):
        self._wm.click_element(element)

    def click_element_at_coordinates(self, x, y):
        self._wm.click_element_at_coordinates(x, y)

    def input_text(self, element, parameters):
        self._wm.input_text(element, parameters)

    def fail(self, message):
        self._wm.fail(message)

    def send_keys(self, element, parameters):
        self._wm.send_keys(element, parameters)

    def wait_until_element_is_visible(self, element):
        self._wm.wait_until_element_is_visible(element)

    def compare_screenshots(self, parameters):
        self._wm.compare_screenshots(parameters)

    def compare_element_screenshots(self, element, parameters):
        self._wm.compare_element_screenshots(element, parameters)

    def element_should_be(self, element, parameters):
        self._wm.wait_until_element_is_visible(element)
        CommonMethodsHelpers.assert_equal(parameters, self._wm.get_text(element))

    def element_value_should_be(self, element, parameters):
        self._wm.wait_until_element_is_visible(element)
        CommonMethodsHelpers.assert_equal(parameters, self._wm.get_value(element))


class Wrappers(CommonWrappers):
    def __init__(self, driver_cache=None):
        self.driver_cache = driver_cache and driver_cache or DriverCache()
        CommonWrappers.__init__(self, self.driver_cache)

    def select_from_list_by_value(self, element, parameters):
        self._wm.select_from_list_by_value(element, parameters)

    def select_from_list_by_label(self, element, parameters):
        self._wm.select_from_list_by_label(element, parameters)

    def select_frame(self, element):
        self._wm.select_frame(element)

    def select_frame_default_content(self):
        self._wm.select_frame_default_content()

    def get_measurements(self, parameters):
        return self._wm.get_measurements(parameters)

    def get_js_memory_heap(self, measurement_name):
        return self._wm.get_js_memory_heap(measurement_name)

    def get_resource_timings(self, measurement_name):
        return self._wm.get_resource_timings(measurement_name)

    def wait_until_document_ready(self):
        self._wm.wait_until_document_ready()

    def wait_until_jquery_ajax_loaded(self, timeout=None):
        self._wm.wait_until_jquery_ajax_loaded(timeout)

    def go_to(self, parameters):
        self._wm.go_to(parameters)


class CanvasWrappers(object):
    def __init__(self, driver_cache=None):
        self.driver_cache = driver_cache and driver_cache or DriverCache()
        self._cam = CanvasMethods(self.driver_cache)

    def click_canvas(self, element):
        self._cam.click_canvas(element)

    def compare_screenshots_canvas(self, parameters):
        self._cam.compare_screenshots_canvas(parameters)

    def compare_element_screenshots_canvas(self, element, parameters):
        self._cam.compare_element_screenshots_canvas(element, parameters)

    def wait_until_element_is_visible_canvas(self, element):
        self._cam.wait_until_element_is_visible_canvas(element)


## Main class for all available methods
class CommonUtils(WebMethods, Asserts, Wrappers, CanvasMethods, CanvasWrappers):
    """
    **Main class for all available methods**
    """

    DATA_TEST_CASES_AND_DATA_FILES = {}

    def __init__(self):
        self.driver_cache = DriverCache()
        WebMethods.__init__(self, self.driver_cache)
        CanvasMethods.__init__(self, self.driver_cache)
        Asserts.__init__(self, self.driver_cache)

        Wrappers.__init__(self, self.driver_cache)
        CanvasWrappers.__init__(self, self.driver_cache)

    def __generate_tests(self, path_to_file, method):
        """
        **Creates string which contains Python code for**

        tests with values from data file.

        :param path_to_file: path to data file
        :param method: method name
        :return: string containing Python code with all tests
        ---------------
        :Example:
            | `` __generate_tests("data.csv", "search") -> ""``
            | ``def test_search_data_row_1(self):``
            | ``QAutoRobot.search('value from first row')``
            | ``def test_search_data_row_2(self):``
            | ``QAutoRobot.search('value from second row')``

        """
        template = """def test_{0}_data_row_{1}(self):
        self.{0}({2})"""

        l = []
        with open_file(path_to_file) as f:
            c = csv.reader(f)
            i = 0
            for row in c:
                if i != 0:
                    row = ['u"%s"' % v for v in row]
                    l.append(template.format(method, i, ','.join(row)))
                i += 1

        return ''.join(l)

    def __add_tests_to_class(self, classs, path_to_file, method):
        """
        **Adds tests to class object**

        :param classs: class object
        :param path_to_file: path to data file
        :param method: method name

        """
        compiled = compile(self.__generate_tests(path_to_file, method), '<string>', 'exec')
        exec(compiled)

        funcs = [v for k, v in list(locals().items()) if k.startswith('test')]

        for f in funcs:
            setattr(classs, f.__name__, f)

    def data_test_class(self, test_class):
        """
        **Python decorator for test classes**

        Decorator adds data tests to test class object

        :param test_class: test class object
        :return: test class object
        """
        for test_case in self.DATA_TEST_CASES_AND_DATA_FILES:
            self.__add_tests_to_class(test_class, self.DATA_TEST_CASES_AND_DATA_FILES[test_case], test_case.__name__)
        self.DATA_TEST_CASES_AND_DATA_FILES = {}
        return test_class

    def data_test(self, data_file):
        """
        **Python decorator for test methods**

        Decorator sets information about method which will be used for creating tests with arguments from data file.

        :param data_file: path to data file

        """
        if not os.path.isabs(data_file) and not os.path.exists(data_file):
            import inspect
            test_file = inspect.stack()[1][1]
            data_file = os.path.join(os.path.dirname(test_file), data_file)
            data_file = os.path.abspath(data_file)

        def wrapper(func):
            self.DATA_TEST_CASES_AND_DATA_FILES[func] = data_file
            return func

        return wrapper

    @classmethod
    def catch_exc(cls, message, *args, **kwargs):
        """
        **Python decorator should catch exceptions**

        :param message: Message to print on fail
        :param args: Function agruments
        :param kwargs: Function keyword arguments
        :return: wrapped function
        ------------------
        :Example:
            | ``catch_exc("Fail to open url")``
            |   ``def open_url(url):``

        """

        def out_wrapper(func, *args, **kwargs):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    func(*args, **kwargs)
                except:
                    etype, value, tb = sys.exc_info()
                    traceback.print_exception(etype, value, tb)
                    print(message)

            return wrapper

        return out_wrapper

    def measure_exc_time(self, func, *args, **kwargs):
        """
        **Python decorator**

        Use it for measuring function elapsed time

        Usage: simply add "@measure_exc_time" before measuring function

        :param func: Function which will be executed
        :param args: Function agruments
        :param kwargs: Function keyword arguments
        :return: wrapped Function
        -----------------
        :Example:
            | ``@measure_exc_time``
            | ``def go_to(url):``
        """

        def wrapper(*args, **kwargs):
            t1 = time.clock()
            res = func(*args, **kwargs)
            t2 = time.clock()
            try:
                print("MEASURE: %s(), %s" % (func.__name__, t2 - t1))
            except:
                print("MEASURE")
            return res

        return wrapper

    def _get_actions(self):
        """
        **MOUSE ACTIONS**
        **Get ActionChains object**

        With this object complex action can be created

        :Example:
            | ``actions = _get_actions()``

        """
        driver = self.get_current_driver()
        return ActionChains(driver)

    def execute_javascript_with_args(self, js_script, *args):
        """
        **Execute JavaScript code with arguments**

        :param js_script: String represents JavaScript code
        :param args: Arguments
        :return: Object return by JavaScript code else None
        """
        driver = self.get_current_driver()
        return driver.execute_script(js_script, *args)

    def save_screenshot(self, saving_dir=None, action=''):
        """
        **Take browser view screenshot.**

        .. note::
            Default place of screenshots is temp directory.

        :param saving_dir: Directory where screenshot is placed
        :param action: String which is added to file name
        ---------------
        :Example:
            | ``save_screenshot(os.path.join(os.pardir, "test_results"), 'clicking')``

        """
        if not saving_dir:
            saving_dir = os.getenv('Temp') + "/"
        path_to_file = os.path.abspath(saving_dir + CommonUtils.get_timestamp() + action + ".png")
        try:
            print("* Saving screenshot to '%s'" % path_to_file)
        except:
            print("* Saving screenshot")
        self.get_current_driver().save_screenshot(path_to_file)

    def get_random_value(self, _list, *val_to_skip):
        """
        **Return random value from list**

        :param _list: List of objects
        :param val_to_skip: Values to skip
        :return: Random value from list
        -----------------
        :Example:
            | ``val_to skip = ["chart_months_6"]``
            | ``RADIO_BTNS = (By.NAME, "chart_months")``
            | ``get_random_value(RADI, val_to skip)``

        """
        _tmp = list(_list)
        for skipped in val_to_skip:
            _tmp.remove(CommonMethodsHelpers.contains_nonascii(skipped))
        value = random.choice(_tmp)
        try:
            print("* Random value is '%s'" % value)
        except:
            print("* Random value")

        return value

    def select_window(self, function, *args):
        """
        **Switch focus to new window**

        :param function: Function which opens new window
        :param args: list of arguments for function
        -------------------
        :Example:
            | ``terms_of_use = (By.CLASS_NAME, 'MCCopyrightTerms')``
            | ``function = find_element(terms_of_use).click``
            | ``select_window(function)``
            | ``select_window(self.click, terms_of_use)``

        """
        driver = self.get_current_driver()
        initial_handles = driver.window_handles
        function(*args)
        WebDriverWait(driver, 20).until(lambda driver: len(initial_handles) < len(driver.window_handles))
        new_handles = driver.window_handles
        for handle in initial_handles:
            new_handles.remove(handle)
        driver.switch_to_window(new_handles[0])
        try:
            DebugLog.log("* Switching to '%s' window" % driver.title)
        except:
            DebugLog.log("* Switching window")

    def get_number_from_string(self, pattern, text):
        """
        **Gets integer from string using regex**

        :param pattern: String, represents regex, can be used to get specific number from string if it contains many numbers
        :param text: String, which contains numbers
        :return: Number from string
        ---------------------
        :Example:
            | ``getNumberFromString("\\d+ mins", "From to 11 stops left and time 36 mins") #returns 36``
            | ``getNumberFromString("\\d+", "From to 11 stops left and time 36 mins") #returns 11``
            | ``getNumberFromString(":\\d+", "11:56)  #returns 56``

        """
        first_text = search(pattern, text).group()
        return search("\\d+", first_text).group()

    def get_page_source(self):
        """
        **Returns page source**

        :return: page source
        --------------------
        :Example:
            | ``QAutoRobot.go_to("http://www.maps.nokia.com")``
            | ``html_source = QAutoRobot.get_page_source()``
            | ``if "City and Country Maps" in html_source:``
            |   ``do something``
            | ``else:``
            |   ``do something else``

        """
        driver = self.get_current_driver()
        return driver.page_source

    def save_page_source(self, testname):
        """
        **Writes page source to file in test reports folder, used in teardown**

        :return: page source
        --------------------
        :Example:
            | ``QAutoRobot.go_to("http://www.maps.nokia.com")``
            | ``html_source = QAutoRobot.save_page_source()``
            | ``if "City and Country Maps" in html_source:``
            |   ``do something``
            | ``else:``
            |   ``do something else``

        """
        driver = self.get_current_driver()
        with open(os.path.join("test_reports", testname + "_source.html"), 'w') as file:
            file.write(driver.page_source)

    def drag_and_drop(self, draggable, droppable):
        """
        **Drags draggable element onto droppable**

        :param draggable: Element to drag
        :param droppable: Element to drop onto
        -------------------
        :Example:
            | ``QAutoRobot.drag_and_drop(self.ID_DRAG1, self.ID_DRAGDIV2)``

        """
        actions = self._get_actions()
        self.wait_until_element_is_visible(draggable)

        draggable = self.find_element_if_not_webelement(draggable)
        droppable = self.find_element_if_not_webelement(droppable)

        actions.drag_and_drop(draggable, droppable).perform()

    def drag_and_drop_html5(self, draggable, droppable):
        """
        **Drags draggable element onto droppable (HTML5)**

        :param draggable: Element to drag
        :param droppable: Element to drop onto
        -----------------
        :Example:
            | ``QAutoRobot.drag_and_drop_html5(self.ID_DRAG1, self.ID_DRAGDIV2)``

        """
        self.wait_until_element_is_visible(draggable)
        draggable = self.find_element_if_not_webelement(draggable)
        droppable = self.find_element_if_not_webelement(droppable)

        # load jquery helper
        jquery_helper = get_file_content(GlobalUtils.JQUERY_LOADER_HELPER)
        driver = self.get_current_driver()
        driver.set_script_timeout(get_config_value("default_timeout"))
        driver.execute_async_script(jquery_helper)

        # load drag and drop helper
        drag_and_drop_helper = get_file_content(GlobalUtils.DRAG_DROP_HELPER)
        drag_and_drop_js = "$(arguments[0]).simulateDragDrop({dropTarget: arguments[1]});"
        DebugLog.log("* Executing drag and drop element onto droppable")
        self.execute_javascript_with_args(drag_and_drop_helper + drag_and_drop_js, draggable, droppable)

    @classmethod
    def write_value_jtl_file(self, measurement_name, sample):
        """
        **Writes given value to file in jtl format**

        :param measurement_name: label of the measurement (also file name) as a String
        :param sample: value to save in the file as Int (seconds)
        """

        sample = float(sample)
        ts = int(time.time()) * 1000
        t = int(round(sample * 1000))

        try:
            measurement_folder = os.path.join(get_config_value("reporting_folder"),
                                              GlobalUtils.MEASUREMENTS_FOLDER_NAME)
            if not os.path.exists(measurement_folder):
                os.mkdir(measurement_folder)
        except Exception as e:
            print("Could not create measurements folder:\n%s" % str(e))

        jtl_file = os.path.join(measurement_folder, GlobalUtils.NAVIGATION_DATA_PREFIX + str(measurement_name) + ".jtl")
        js_file = os.path.join(measurement_folder, GlobalUtils.NAVIGATION_DATA_PREFIX + str(measurement_name) + ".js")

        # jtl file
        try:
            if (os.path.isfile(jtl_file)):
                read_lines = get_file_lines(jtl_file)
                str_to_insert = "<sample t='" + str(t) + "'" + " ts='" + str(ts) + "'" + " lb='" \
                                + str(measurement_name) + "' s='true' rc='200' rm='OK'/>\n"
                new_lines = read_lines[:-1] + [str_to_insert] + [read_lines[-1]]
                content = "".join(new_lines)
                save_content_to_file(content, jtl_file)
            else:
                heading = "<?xml version='1.0' encoding='UTF-8'?>\n<testResults version='1.2'>"
                lines = "\n<sample t='" + str(t) + "'" + " ts='" + str(ts) + "'" + " lb='" \
                        + str(measurement_name) + "' s='true' rc='200' rm='OK'/>"
                ending = "\n</testResults>"
                new_lines = heading + lines + ending
                content = "".join(new_lines)
                save_content_to_file(content, jtl_file)
        except Exception as e:
            print("Could not generate jtl file" + str(e))

        # javascript file
        try:
            if (os.path.isfile(js_file)):
                read_lines = get_file_lines(js_file)
                str_to_insert = "{'load': '" + str(t) + "', 'timestamp': '" + str(ts) + "', 'succes': true, 'label': '" \
                                + str(measurement_name) + "', 'response_code': '200', 'response_msg': 'OK'},\n"
                new_lines = read_lines[:-1] + [str_to_insert] + [read_lines[-1]]
                content = "".join(new_lines)
                save_content_to_file(content, js_file)
            else:
                heading = "var timings_js_data = ["
                lines = "\n{'load': '" + str(t) + "', 'timestamp': '" + str(ts) + "', 'succes': true, 'label': '" \
                        + str(measurement_name) + "', 'response_code': '200', 'response_msg': 'OK'},"
                ending = "\n];"
                new_lines = heading + lines + ending
                content = "".join(new_lines)
                save_content_to_file(content, js_file)
        except Exception as e:
            print("Could not generate js file:\n%s" % str(e))

    def create_ref_screenshot(self, ref_scr_name, ref_scr_x, ref_scr_y, ref_scr_w, ref_scr_h):
        """
        **Creates refernece screenshot of an area**

        :param ref_scr_name: Reference screenshot file image name
        :param ref_scr_x: Area's x-coordination
        :param ref_scr_y: Area's y-coordination
        :param ref_scr_w: Area's width
        :param ref_scr_h: Area's height
        :return: created screenshot
        """
        scr_created = True
        try:

            self.take_full_screenshot(GlobalUtils.COMPARE_SCREENSHOT)

            ref_scr_im = Image.open(GlobalUtils.COMPARE_SCREENSHOT)
            ref_scr_subim = ref_scr_im.crop((int(ref_scr_x), int(ref_scr_y), int(ref_scr_x) + int(ref_scr_w),
                                             int(ref_scr_y) + int(ref_scr_h)))
            current_dir = os.getcwd()
            if os.path.split(current_dir)[1] == "tests" or os.path.split(current_dir)[1] == "suites":
                current_dir = os.path.abspath(os.path.join(current_dir, ".."))

            ref_scr_subim.save(os.path.join(current_dir, GlobalUtils.SCREENSHOTS_FOLDER_NAME, ref_scr_name))
        except Exception as ex:
            print("Failed to create reference screenshot:\n", str(ex))
            scr_created = False

        return scr_created

    def create_element_ref_screenshot(self, element, ref_scr_name):
        """
        **Creates refernece screenshot of an element**

        :param element: Element representation (By, value) or WebElement
        :param ref_scr_name: Reference screenshot image file name
        :return: element_found Boolen
        """

        element_found = True
        try:
            self.wait_until_element_is_visible(element)

            element = self.find_element_if_not_webelement(element)

            element_loc = element.location
            element_size = element.size

            ref_scr_x = int(element_loc['x'])
            ref_scr_y = int(element_loc['y'])
            ref_scr_w = int(element_size['width'])
            ref_scr_h = int(element_size['height'])

            self.take_full_screenshot(GlobalUtils.COMPARE_SCREENSHOT)

            ref_scr_im = Image.open(GlobalUtils.COMPARE_SCREENSHOT)
            ref_scr_subim = ref_scr_im.crop((ref_scr_x, ref_scr_y, ref_scr_x + ref_scr_w, ref_scr_y + ref_scr_h))
            current_dir = os.getcwd()
            if os.path.split(current_dir)[1] == "tests" or os.path.split(current_dir)[1] == "suites":
                current_dir = os.path.abspath(os.path.join(current_dir, ".."))

            ref_scr_subim.save(os.path.join(current_dir, GlobalUtils.SCREENSHOTS_FOLDER_NAME, ref_scr_name))

        except:
            element_found = False

        return element_found

    def create_ref_screenshot_canvas(self, ref_scr_name, x_coord, y_coord, width, height):
        """
        **Creates reference screenshot of an element**

        :param ref_scr_name: Reference screenshot image file name
        :param x_coord: Element's x coordination
        :param y_coord: Element's y coordination
        :param width: Element's width
        :param height: Element's height
        :return: scr_created ref_scr_name Boolean Updated screenshot file name
        """
        scr_created = True
        try:
            ref_scr_name = ref_scr_name.split(".png")[0] + "_%s_%s_%s_%s.png" % (
                str(x_coord).strip(), str(y_coord).strip(),
                str(width).strip(), str(height).strip())

            self.take_full_screenshot(GlobalUtils.COMPARE_SCREENSHOT)

            ref_scr_im = Image.open(GlobalUtils.COMPARE_SCREENSHOT)
            ref_scr_subim = ref_scr_im.crop((x_coord, y_coord, x_coord + width, y_coord + height))
            current_dir = os.getcwd()
            if os.path.split(current_dir)[1] == "tests" or os.path.split(current_dir)[1] == "suites":
                current_dir = os.path.abspath(os.path.join(current_dir, ".."))

            ref_scr_subim.save(os.path.join(current_dir, GlobalUtils.SCREENSHOTS_FOLDER_NAME, ref_scr_name))
        except Exception as ex:
            print("Create reference screenshot of object inside canvas exception: ", str(ex))
            scr_created = False

        return scr_created, ref_scr_name

    @classmethod
    def _check_screenshot_file_name(cls, screenshot_parser, ref_scr_name):
        """

        :param screenshot_parser:
        :param ref_scr_name:
        :return:
        """
        current_dir = os.getcwd()

        browser, screenres = cls._get_browser_and_resolution()
        ref_scr_file_name = ref_scr_name + "_" + browser + "-" + screenres + ".png"
        ref_scr_file_name_path = os.path.join(current_dir, GlobalUtils.SCREENSHOTS_FOLDER_NAME, ref_scr_file_name)

        xml_meta_data = screenshot_parser._get_screenshot_metadata(ref_scr_name, browser, screenres)
        if xml_meta_data:
            unittest.TestCase("assertTrue").assertTrue(os.path.isfile(ref_scr_file_name_path),
                                                       ("Reference screenshots file does not exists. " +
                                                        "Reference screenshot: %s.") % ref_scr_file_name)
        else:
            # screenshot not found in xml, try to find best match
            found, xml_meta_data, new_file_name, msg = screenshot_parser._find_best_match(ref_scr_name, browser,
                                                                                          screenres)
            unittest.TestCase("assertTrue").assertTrue(found is True,
                                                       "%s Reference screenshot: %s." % (msg, new_file_name))
            # found screenshot with different browser
            print("WARNING: Reference screenshot (%s) not found. Using screenshot (%s), " +
                  "which was created different browser (%s).") % (
                ref_scr_file_name, new_file_name, xml_meta_data['browser'])
            ref_scr_file_name = new_file_name
            ref_scr_file_name_path = os.path.join(current_dir, GlobalUtils.SCREENSHOTS_FOLDER_NAME, ref_scr_file_name)

        return xml_meta_data, ref_scr_file_name_path

    def _handle_screenshot_comparison(self, ref_scr_file_name_path, ref_scr_x, ref_scr_y, ref_scr_w, ref_scr_h,
                                      similarity):
        current_dir = os.getcwd()
        ref_scr_file_name = os.path.basename(ref_scr_file_name_path)
        scr_ref = Image.open(ref_scr_file_name_path)
        scr_ref_list = list(scr_ref.getdata())

        self.take_full_screenshot(GlobalUtils.CURRENT_SCREENSHOT)
        scr_curr = Image.open(GlobalUtils.CURRENT_SCREENSHOT)
        scr_curr_subim = scr_curr.crop((ref_scr_x, ref_scr_y, ref_scr_x + ref_scr_w, ref_scr_y + ref_scr_h))

        scr_curr_list = list(scr_curr_subim.getdata())

        scr_ref.save(current_dir + "/reference_scr.png")
        scr_curr_subim.save(current_dir + "/actual_scr.png")

        # save screenshot name to temp file
        cur_ref_scr_filename = "cur_ref_scr_filename.txt"
        cur_ref_src_full_filename = os.path.join(current_dir, cur_ref_scr_filename)
        with open(cur_ref_src_full_filename, "wb") as cur_ref_scr_file:
            cur_ref_scr_file.write(ref_scr_file_name)

        unittest.TestCase("assertTrue").assertTrue(len(scr_curr_list) == len(scr_ref_list),
                                                   ("Screenshots size does not match. " +
                                                    "Reference screenshot: %s.") % ref_scr_file_name)

        diff = 0
        for i in range(len(scr_curr_list)):
            diff = (diff + abs(int(scr_ref_list[i][0]) - int(scr_curr_list[i][0])) +
                    abs(int(scr_ref_list[i][1]) - int(scr_curr_list[i][1])) +
                    abs(int(scr_ref_list[i][2]) - int(scr_curr_list[i][2])))

        # difference = int(round(100 * float(diff) / float(len(scr_curr_list) * 3 * 255)))
        difference = round(100 * float(diff) / float(len(scr_curr_list) * 3 * 255), 2)
        is_similar = (100 - difference) >= similarity

        unittest.TestCase("assertTrue").assertTrue(is_similar,
                                                   (
                                                           "Screenshots do not match. Reference screenshot: %s. Similarity level " +
                                                           "is '%s' percent") % (
                                                       ref_scr_file_name, str(100 - difference)))

        print("Comparing screenshots... Screenshots match. Reference screenshot: %s. "
              "Similarity level is %s.") % (ref_scr_file_name, str(100 - difference) + "%")

    @classmethod
    def _get_browser_and_resolution(cls):
        # Get screen resolution and browser name
        browser_name = get_config_value(GlobalUtils.BROWSER_NAME)
        import wx
        display_size = wx.DisplaySize()
        screen_res = str(display_size[0]) + "x" + str(display_size[1])
        return browser_name, screen_res

    def get_current_url(self):
        """
        **Get current active browsers url as a String.**
         :return: Current active browser url as a String.
        """
        return self.get_current_driver().current_url

    def get_current_driver(self):
        """
        **Get current active webdriver object.**

        :return: Current active webdriver object.
        """
        return self.driver_cache._get_current_driver()

    def get_current_browser(self):
        """
        **Get current active webdriver object.**

        :return: Current active webdriver object.
        """
        return self.driver_cache._get_current_browser()

    def is_current_driver(self):
        """
        **Is there current active webdriver object.**

        :return: True or False
        """
        return self.driver_cache._is_current_driver()

    def is_ie(self):
        """
        **Returns True is browser is Internet Explorer, else - False.**

        :return: True is browser is Internet Explorer, else - False.
        """
        return self.driver_cache._is_ie()

    def is_ff(self):
        """
        **Returns True is browser is Firefox, else - False.**

        :return: True is browser is Firefox, else - False.
        """
        return self.driver_cache._is_ff()

    def is_gc(self):
        """
        **Returns True is browser is Google Chrome, else - False.**

        :return: True is browser is Google Chrome, else - False.
        """
        return self.driver_cache._is_gc()

    def get_browser_version(self):
        """
        **Returns browser version**

        :return: version as String
        """
        driver = self.get_current_driver()

        # TODO: how to get version info from new firefox versions
        if "version" in driver.desired_capabilities:
            return driver.desired_capabilities["version"]
        return ""

    def take_full_screenshot(self, pic_name, height_override=None):
        """
        Take full screenshot of the page

        :param pic_name: Name for the screenshot
        :param height_override: Override height
        :return: None
        """
        driver = self.get_current_driver()

        # start from the top
        driver.execute_script("window.scrollTo(0, 0);")

        if self.is_gc():
            margin = 17
            viewport_width = driver.execute_script("return window.innerWidth") - margin
        elif self.is_ff():
            margin = 17
            viewport_width = driver.execute_script("return window.innerWidth") - margin
        else:
            driver.save_screenshot(pic_name)
            return

        doc_width = driver.execute_script("return document.body.offsetWidth")

        if viewport_width > doc_width:
            doc_width = viewport_width

        viewport_height = driver.execute_script("return window.innerHeight")
        doc_height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.body.clientHeight);")

        if height_override is not None:
            doc_height = height_override

        if viewport_height >= doc_height:
            driver.save_screenshot(pic_name)
            return

        rectangles = []

        i = 0
        while i < doc_height:
            ii = 0
            top_height = i + viewport_height

            if top_height > doc_height:
                top_height = doc_height

            while ii < doc_width:
                top_width = ii + viewport_width

                if top_width > doc_width:
                    top_width = doc_width

                rectangles.append((ii, i, top_width, top_height))

                ii += viewport_width

            i = i + viewport_height

        stitched_image = Image.new('RGB', (doc_width, doc_height))
        previous = None
        part = 0
        for rectangle in rectangles:
            if previous is not None:
                driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
                time.sleep(0.2)

            file_name = "scroll_part_{0}.png".format(part)
            driver.get_screenshot_as_file(file_name)

            screenshot = Image.open(file_name)

            if rectangle[1] + viewport_height > doc_height:
                offset = (rectangle[0], doc_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])

            stitched_image.paste(screenshot, offset)

            del screenshot
            os.remove(file_name)

            part += 1
            previous = rectangle

        stitched_image.save(pic_name)


## Class allows to measure time
class Timer:
    """
    **Class allows to measure time**
    """

    def start(self):
        """
        **Start timer**

        """
        self.__start_time = time.time()
        self.__running = True

    ## Stop timer
    def stop(self):
        """
        **Stop timer**

        """
        self.__stop_time = time.time()

    def get_elapsed_time(self):
        """
        **Get elapsed time**

        :return: Time difference between start and stop
        """
        if self.__running:
            self.stop()
        return self.__stop_time - self.__start_time


if __name__ == "__main__":
    pm = CommonUtils()
