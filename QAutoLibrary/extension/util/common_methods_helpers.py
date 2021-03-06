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

import unittest
from datetime import datetime
from robot.api import logger

from selenium.common.exceptions import StaleElementReferenceException, ElementNotVisibleException, \
    ElementNotSelectableException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from QAutoLibrary.extension.config import get_config_value


class CommonMethodsHelpers(object):

    @classmethod
    def webdriver_wait(cls, function, driver, msg='', timeout=None, fallback=False):
        """
        Wait until function returns True
        Executes passed function until it returns True
        or time exceeds DEFAULT_TIMEOUT
        if time exceeds DEFAULT_TIMEOUT throws exception

        :param function: Function which should return True
        :param driver:
        :param msg: Exception message
        :param timeout:
        :return:
        """
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        TimeOutError = AssertionError
        try:
            WebDriverWait(driver, timeout, ignored_exceptions=[ElementNotVisibleException, StaleElementReferenceException,
                                                               ElementNotSelectableException]).until(function, msg)
        except TimeoutException as e:
            if not fallback:
                raise TimeOutError("%s %s" % (DebugLog.get_timestamp(), msg))
        except Exception as e:
            raise e

    @classmethod
    def assert_equal(cls, expected, actual, msgpass='', msg=''):
        """
        Assertion with printing
        On fail prints out expected and actual values

        :param expected: Expected value
        :param actual: Actual value
        :param msgpass: Message to print if pass
        :param msg: Message to print if fail
        :return:
        """
        info = "%s %s\nexpected: '%s', actual '%s'" % (DebugLog.get_timestamp(), msg, expected, actual)
        unittest.TestCase("assertEqual").assertEqual(expected, actual, info)

    @classmethod
    def escape_xpath_text(cls, text):
        text = str(text)
        if '"' in text and '\'' in text:
            parts = text.split('\'')
            return "concat('%s')" % "', \"'\", '".join(parts)
        if '\'' in text:
            return "\"%s\"" % text
        return "'%s'" % text


class DebugLog(object):

    @staticmethod
    def get_timestamp():
        (tm, micro) = datetime.now().strftime('%H:%M:%S.%f').split('.')
        return "%s.%03d" % (tm, int(micro) / 1000)

    @staticmethod
    def log(msg):
        logger.info(msg, html=True)
