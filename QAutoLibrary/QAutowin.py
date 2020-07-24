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

import pywinauto
from pywinauto.keyboard import send_keys
from robot.api.deco import keyword
from robot.api import logger
import time
import os
from PIL import ImageGrab
import subprocess
import pygetwindow as gw
import win32api


class QAutowin(object):
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    def __init__(self, backend="uia"):
        self.app = pywinauto.application.Application(backend=backend)
        self.backend = backend

    @keyword(name='Open Application')
    def Open_Application(self, appname, **kwargs):  # arg=application, arg2=backend Win32 API or MS UI Automation
        # timeout=None, retry_interval=None, create_new_console=False, wait_for_idle=True, work_dir=None
        """
        **Opens application**

        :Example:
            | Open application  notepad.exe
        """
        print(kwargs)
        if appname != "":
            self.app.start(appname, **kwargs)
            logger.info('Opening application %s.' % appname)

    @keyword(name='Connect Application')
    def Connect_Application(self, **kwargs):  # arg=application, arg2=backend Win32 API or MS UI Automation
        """
        **Connects to application**

        :Example:
            | Connect application  best_match=Untitled - Notepad
        """
        if "process" in kwargs.keys():
            self.app.application_process = kwargs["process"]
            for i in range(3):
                try:
                    self.app.connect(process=int(self.app.application_process))
                    break
                except:
                    if i == 2:
                        logger.error("Failed to connect to application: %s " % self.app.application_process)
                    else:
                        logger.warn("App connection failed. Attempt: %d" % i)
                        time.sleep(5)
        else:
            self.app.connect(**kwargs)

        return self.app.process

    @keyword(name='Print identifiers')
    def print_identifiers(self):
        """
        **Returns print control identifiers**

        --------------
        :Example:
            | Print identifiers
        """

        window = self.find_connected_app_window()
        print(window.print_control_identifiers())

    def find_connected_app_window(self):
        """
        **Returns window of connected app with using hwnd**

        --------------
        :Example:
            | ${window}=  Find app window
        """
        window_count = len(self.app.windows())
        window = self.app.window(found_index=(window_count - 1))
        return window

    def find_connected_app_windows(self):
        """
        **Returns window of connected app with using hwnd**

        --------------
        :Example:
            | ${window}=  Find app window
        """
        windows = []
        window_count = len(self.app.windows())
        for x in range(window_count):
            window = self.app.window(found_index=(window_count - x+1))
            windows.append(window)

        windows.append(self.app.top_window())
        windows.reverse()

        return windows

    @keyword(name='Click Element')
    def Click_Element(self, **kwargs):
        """
        **Clicks at element**

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | Click element  title=File
        """
        windows = self.find_connected_app_windows()
        error = None
        for window in windows:
            try:
                if "text" in kwargs:
                    logger.info('Clicking element %s.' % kwargs)
                    for kwarg in kwargs.keys():
                        if kwarg == "text":
                            window[(kwargs["text"])].wait('visible', timeout=10)
                            window[(kwargs["text"])].click_input()
                            break
                elif 'x' in kwargs and 'y' in kwargs:
                    logger.info('Clicking at coordinates %s.' % kwargs)
                    self.Click_Coordinates(**kwargs)
                else:
                    logger.info('Clicking element %s.' % kwargs)
                    window.child_window(**kwargs).wait('visible', timeout=10)
                    window.child_window(**kwargs).click_input()
                return True
            except Exception as e:
                error = e
                logger.info(str(e))
        raise error

    @keyword(name='Send Keywords')  # Send input data. Useful for text fields, that "Input text" does not recognize. Also, you can send keyboard actions, for example like ~ for Enter
    # https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html
    def Send_Keywords(self, user_input):
        """
        **Send key presses**

        --------------
        :Example:
            | Send_Keywords  x
        """
        logger.info('Send keywords %s.' % user_input)
        send_keys(user_input)

    @keyword(name='Input Text')
    def Input_Text(self, user_input, **kwargs):
        """
        **Input text to element**

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | Input Text  text  title=File
        """
        window = self.find_connected_app_window()
        # Input text by: auto_id, class_name, class_name_re, title, title_re, control_type
        if "text" in kwargs:
            logger.info('Input text %s element %s.' % (user_input, kwargs))
            for kwarg in kwargs.keys():
                if kwarg == "text":
                    window[(kwargs["text"])].wait('visible', timeout=10)
                    window[(kwargs["text"])].type_keys(user_input, with_spaces=True, with_tabs=True)
                    break
        else:
            logger.info('Input text %s element %s.' % (user_input, kwargs))
            window.child_window(**kwargs).wait('visible', timeout=10)
            window.child_window(**kwargs).set_text("")
            window.child_window(**kwargs).type_keys(user_input, with_spaces=True, with_tabs=True)

    @keyword(name='Click Coordinates')
    def Click_Coordinates(self, **kwargs):
        """
        **Clicks at element using coordinates**

        :Example:
            | Click element  x=500    y=300
        """
        window = self.find_connected_app_window()
        for kwarg in kwargs.keys():
            # application_title = (apptitle)
            # "File"
            if kwarg == "x":
                x = kwargs["x"]
            if kwarg == "y":
                y = kwargs["y"]

        window.maximize()
        time.sleep(1)
        window.click_input(coords=((int(x)), (int(y))))


    @keyword(name="Verify Text")
    def Verify_text(self, user_input, **kwargs):
        """
        **Verify element text**

        :param:  text
        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | Verify text  asserted_text  title=File
        """
        text = self.Get_text(**kwargs)
        if text == user_input:
            logger.info("%s is equal to %s" % (text, user_input))
            pass
        else:
            self.fail("%s is not equal to %s" % (text, user_input))


    @keyword(name="Verify Text Contains")
    def Verify_text_contains(self, user_input, **kwargs):
        """
        **Verify element containing text **

        :param:  text
        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | Verify text contains  asserted_text  title=File
        """
        text = self.Get_text(**kwargs)
        print("Get_text:", text)
        if user_input in text:
            logger.info("%s contains %s" % (text, user_input))
            pass
        else:
            self.fail("%s does not contain %s" % (text, user_input))


    @keyword(name="Get Text")
    def Get_text(self, **kwargs):
        """
        **Get text of element**

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | {text}=  Get text  title=File
        """
        window = self.find_connected_app_window()
        if "text" in kwargs:
            for kwarg in kwargs.keys():
                if kwarg == "text":
                    text = window[(kwargs["text"])].iface_value.CurrentValue
                    return text
        else:
            text = window.child_window(**kwargs).iface_value.CurrentValue
            return text


    @keyword(name='Right click element')
    def Right_click_element(self, **kwargs):
        """
        **Right-clicks at element**

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | Right click element  title=File
        """
        window = self.find_connected_app_window()
        if "text" in kwargs:
            logger.info('Clicking element %s.' % kwargs)
            for kwarg in kwargs.keys():
                if kwarg == "text":
                    window[(kwargs["text"])].wait('visible', timeout=10)
                    window[(kwargs["text"])].right_click_input()
                    break
        else:
            logger.info('Clicking element %s.' % kwargs)
            window.window(**kwargs).wait('visible', timeout=10)
            window.window(**kwargs).right_click_input()


    @keyword(name='Close application')
    def Close_application(self):
        """
        **Closes previously opened application**

        :Example:
            | Close application
        """
        self.app.kill()


    @keyword(name='Take screenshot')
    def Take_screenshot(self, error_image_folder):
        """
        **Take screenshot**

        --------------
        :Example:
            | Take screenshot  screenshot_name
        """
        image = ImageGrab.grab()
        image.save(error_image_folder)
        logger.error('Something went wrong. Screenshot taken')


    def Close_cmd_process(self, cmd_process):
        """
        **Close cmd process**

        --------------
        :Example:
            | Close cmd process  cmd_process_title
        """
        result = subprocess.run(['tasklist', '/fi', 'imagename eq cmd.exe', '/v', '/fo:csv', '/nh'], stdout=subprocess.PIPE)
        results = str(result).split('cmd.exe",')
        pid = ""
        for proc in results:
            if cmd_process in proc:
                print(proc)
                pid = proc.split(",")[0].replace('"', '')
                result_kill = subprocess.run(['taskkill', '/PID', pid], stdout=subprocess.PIPE)
                print(result_kill)

        if pid == "":
            print("No process found: ", cmd_process)


    @keyword(name='Launch bat')
    def Launch_bat(self, directory, bat_name):
        """
        **Run bat file**

        --------------
        :Example:
            | Launch bat  directory  file_name
        """
        dir = os.getcwd()
        os.chdir(directory)
        try:
            subprocess.call('start ' + bat_name, shell=True)
            os.chdir(dir)
        except Exception as e:
            os.chdir(dir)
            print(e)
        time.sleep(3)

