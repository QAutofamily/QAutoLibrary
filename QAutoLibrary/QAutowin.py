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
import time
import os
import subprocess
import re
import sys

from pywinauto.keyboard import send_keys
from robot.api.deco import keyword
from robot.api import logger
from PIL import ImageGrab
from QAutoLibrary.QAutoRPAImage import QAutoRPAImage

class QAutowin(object):
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    def __init__(self, backend="uia"):
        self.app = pywinauto.application.Application(backend=backend)
        self.backend = backend

    def __find_application__(self, application):
        """
        **Finds directories containing a specified application**
        Searches the application in C:/Users/<USER>/AppData/Roaming/, C:/Users/<USER>/AppData/Local/,
        and in C:/Program Files/, C:/Program Files (x86)/.

        :param application: Name of the specified application. Can contain file ending.
        :type application: str

        :return: List of the found file paths for the application.
        :rtype: list
        """
        environments_to_search = ['APPDATA', 'LOCALAPPDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)']
        results = []

        environments_to_search = [os.getenv(environment) for environment in environments_to_search
                                  if os.getenv(environment)]
        for environment in environments_to_search:
            logger.info(f"Searching application '{application}' in environment '{environment}'...")
            for root, dirs, files in os.walk(environment):
                if application in files:
                    results.append(os.path.join(root, application))
                    logger.info(f"Application '{application}' found in '{environment}'!")
        return results

    @keyword(name='Open Application')
    def Open_Application(self, appname, **kwargs):  # arg=application, arg2=backend Win32 API or MS UI Automation
        # timeout=None, retry_interval=None, create_new_console=False, wait_for_idle=True, work_dir=None
        """
        **Opens application**
        Attempts to open a specified application by the provided name or command. If unable to start
        the application directly, attempts to search for the application's location and start it by
        the found file path.

        Searches the application in AppData, Program Files, and Program Files (x86) directories
        if necessary. Providing file ending may help in finding the correct file, such as '.exe' file.
        Providing command line parameters may hinder the search.

        Optional parameters:
          timeout=None - Time in seconds before Application.Start() quits.
          retry_interval=None - Interval in seconds between Application.Start() retries.
          work_dir=None - Provide working directory for the application.
        Optional parameters are used for Pywinauto.Application.Start() function. See pywinauto
        module for further details: https://pypi.org/project/pywinauto/

        :param appname: Application name, or console command, to start it. Can include file path and file ending.
        :type appname: str

        -------------
        :Example:
            | Open application  |  notepad.exe
            | Open application  |  C:\\Program Files\\Spotify\\Spotify.exe
            | Open application  |  C:\\Program Files\\Notepad++\\notepad++.exe --help
            | Open application  |  git-bash.exe  |  timeout=10  |  retry_interval=2  |  work_dir=C:\\MyProject
        """
        print(kwargs)
        try:
            self.app.start(appname, **kwargs)
            logger.info(f"Application '{appname}' started directly.")
        except:
            logger.info(f"Could not start application '{appname}' directly. Searching for the application...")
            found_applications = []
            found_applications.extend(self.__find_application__(appname))
            if len(found_applications) >= 1:
                self.app.start(found_applications[0], **kwargs)
                if len(found_applications) > 1:
                    logger.warn(f"Found application in {len(found_applications)} locations: {found_applications}")

        if not self.app.is_process_running():
            raise Exception(f"Could not open application '{appname}'!")
        logger.info(f"Opened application '{appname}'.")

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

    @keyword(name='Find Window')
    def Find_Window(self, **kwargs):
        """
        **Finds pywinauto window**

        :param kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | ${window}=  Find window  title=File
            | ${var}=   Call Method    ${window}    click_input
        """
        windows = self.find_connected_app_windows()
        timeout = 10
        if "timeout" in kwargs:
            timeout = kwargs["timeout"]
            del(kwargs["timeout"])

        for window in windows:
            try:
                if "parent" in kwargs:
                    if type(kwargs["parent"]) == list:
                        for parent in kwargs["parent"]:
                            if "text" in parent:
                                logger.info('Finding window %s.' % parent)
                                window = window[(parent["text"])]
                                window.wait('exists', timeout=timeout)
                                pass
                            else:
                                logger.info('Finding window %s.' % parent)
                                window = window.window(**parent)
                                window.wait('exists', timeout=timeout)
                    else:
                        logger.info('Finding window %s.' % kwargs["parent"])
                        window = window.window(**kwargs["parent"])
                        window.wait('exists', timeout=timeout)
                    del (kwargs["parent"])

                if "text" in kwargs:
                    logger.info('Finding window %s.' % kwargs["text"])
                    window = window[kwargs["text"]]
                    window.wait('exists', timeout=timeout)
                else:
                    logger.info('Finding window %s.' % kwargs)
                    window = window.window(**kwargs)
                    window.wait('exists', timeout=timeout)

                window.wait('ready', timeout=timeout)
                window.wait('active', timeout=timeout)
                return window
            except Exception as e:
                error = e
                logger.info(str(e))

        raise error

    @staticmethod
    def __get_click_positions(rectangle):
        """
        Helper function for GetElementInfoFromCoords

        :param rectangle: Element rectangle
        :return:  app_x, app_y, app_x2, app_y2, size
        """
        app_x = str(rectangle).split(",")[0].strip()[2:]
        app_y = str(rectangle).split(",")[1].strip()[1:]
        app_x2 = str(rectangle).split(",")[2].strip()[1:]
        app_y2 = str(rectangle).split(",")[3].strip()[1:].replace(")","")

        app_width = int(str(rectangle).split(",")[2].strip()[1:])-int(app_x)
        app_height = int(str(rectangle).split(",")[3].strip()[1:].replace(")",""))-int(app_y)
        app_middle_x = int(app_width)/2
        app_middle_y = int(app_height)/2
        size = app_width * app_height

        return app_x, app_y, app_x2, app_y2, size

    @staticmethod
    def __check_if_inside_rectangle(x1, y1, x2, y2, x, y):
        """
        Helper function for GetElementInfoFromCoords

        :param x1: Rectangle x1
        :param y1: Rectangle y1
        :param x2: Rectangle x2
        :param y2: Rectangle y2
        :param x: x coordinate to confirm
        :param y: y coordinate to confirm
        :return: True or False
        """
        if (x > x1 and x < x2 and y > y1 and y < y2):
            return True
        else:
            return False

    @keyword(name='Get Element Info From Coords')
    def GetElementInfoFromCoords(self, x, y):
        """
        **Gets information from element at coordinates**

        :kwargs: x, y
        --------------
        :Example:
            | Click element  image=rpa_images//test.png
        """
        windows_and_descendants = []
        for x in range(5):
            window_count = len(self.app.windows())
            if window_count > x + 1:
                window = self.app.window(found_index=(window_count - x + 1))
                descendants = window.descendants()
                windows_and_descendants.append((descendants, window))

        window = self.app.top_window()
        descendants = window.descendants()
        windows_and_descendants.append((descendants, window))

        clist = []
        elements = ""
        windows = []
        for win_and_dec in windows_and_descendants:
            for ctrl in win_and_dec[0]:
                elements += str(ctrl.rectangle())
                clist.append((str(ctrl.rectangle()), ctrl))
                windows.append(win_and_dec[1])

        match_list = re.findall(r'[L,T,R,B]-?\d*\.{0,1}\d+(?=[,)])', elements)
        rectangle_table = []
        k = 0
        for i in range(0, len(match_list), 4):
            rectangle_table.append(
                "(" + match_list[i] + ", " + match_list[i + 1] + ", " + match_list[i + 2] + ", " + match_list[
                    i + 3] + ")")
            k = k + 1

        best_match = ""
        sizeorig = sys.maxsize
        for s in rectangle_table:
            x1, y1, x2, y2, size = self.__get_click_positions(str(s))
            if x == "" or y == "":
                pass
            elif self.__check_if_inside_rectangle(int(x1), int(y1), int(x2), int(y2), int(x), int(y)):
                if size < sizeorig:
                    sizeorig = size
                    best_match = "(L" + x + ", T" + y + ", R" + str(x2) + ", B" + str(y2) + ")"

        ctrl_match = [ctrl for (rect, ctrl) in clist if best_match in str(rect)]
        if ctrl_match:
            ctrl = ctrl_match[-1]
            ctrllist = {}
            ctrllist['rectangle'] = str(ctrl.rectangle())
            ctrllist['name'] = str(ctrl.element_info.name)
            ctrllist['auto_id'] = str(ctrl.element_info.automation_id)
            ctrllist['control_id'] = str(ctrl.element_info.control_id)
            ctrllist['control_type'] = str(ctrl.element_info.control_type)
            ctrllist['rich_text'] = str(ctrl.element_info.rich_text)
            ctrllist['class_name'] = str(ctrl.friendly_class_name())
            ctrllist['coord'] = (x, y)
            try:
                ctrllist['value'] = str(ctrl.legacy_properties()['Value'])
            except:
                ctrllist['value'] = ""
            try:
                ctrllist['input_field_text'] = ctrl.window_text()
            except:
                ctrllist['input_field_text'] = ""
            ctrllist['title'] = str(ctrl.element_info.name)
            ctrllist['ctrl'] = type(ctrl)
            print("ctrl_list", ctrllist)
            return ctrllist
        else:
            raise Exception(f"Element not found from coords: x={x}, y={y}")

    @keyword(name='Click Element')
    def Click_Element(self, **kwargs):
        """
        **Clicks at element**

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type, image, timeout
        --------------
        :Example:
            | Click element  title=File
            | Click element  image=rpa_images//test.png
        """
        if "image" in kwargs:
            logger.info('Clicking element with image' % kwargs)
            self.Click_element_with_image(**kwargs)
        elif 'x' in kwargs and 'y' in kwargs:
            logger.info('Clicking at coordinates %s.' % kwargs)
            self.Click_Coordinates(**kwargs)
        else:
            window = self.Find_Window(**kwargs)
            logger.info('Clicking element %s.' % kwargs)
            window.click_input()

    @keyword(name='Click element with image')
    def Click_element_with_image(self, **kwargs):
        """
        **Click with image**

        :kwargs: image, timeout, right, double
        --------------
        :Example:
            | Click element with image  image=rpa_images//image.png
            | Click element with image  image=rpa_images//image.png  timeout=30
            | Click element with image  image=rpa_images//image.png  timeout=30  right=True
            | Click element with image  image=rpa_images//image.png  timeout=30  double=True
        """
        timeout = 30
        if "timeout" in kwargs:
            timeout = kwargs["timeout"]
        image_path = kwargs["image"]
        if "double" in kwargs:
            QAutoRPAImage.double_click_image(image_path, timeout)
        if "right" in kwargs:
            QAutoRPAImage.right_click_image(image_path, timeout)
        else:
            QAutoRPAImage.click_image(image_path, timeout)

    @keyword(name='Input element with image')
    def Input_element_with_image(self, text, **kwargs):
        """
        **Inputs text with image**

        :args: text
        :kwargs: image, timeout
        --------------
        :Example:
            | Input element with image  text  image=rpa_images//image.png
            | Input element with image  text  image=rpa_images//image.png  timeout=30
        """
        timeout = 30
        if "timeout" in kwargs:
            timeout = kwargs["timeout"]
        image_path = kwargs["image"]
        QAutoRPAImage.click_image(image_path, timeout)
        time.sleep(0.5)
        self.Send_Keywords(text)

    @keyword(name='Double Click Element')
    def Double_Click_Element(self, **kwargs):
        """
        **Clicks at element**

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | Double click element  title=File
        """
        if "image" in kwargs:
            logger.info('Clicking element with image' % kwargs)
            kwargs["double"] = True
            self.Click_element_with_image(**kwargs)
        elif 'x' in kwargs and 'y' in kwargs:
            logger.info('Double clicking at coordinates %s.' % kwargs)
            self.Double_Click_Coordinates(**kwargs)
        else:
            window = self.Find_Window(**kwargs)
            logger.info('Double clicking element %s.' % kwargs)
            window.click_input(double=True)

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

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type, image, timeout
        --------------
        :Example:
            | Input Text  text  title=File
            | Input Text  text  image=rpa_images//test.png
        """
        if "image" in kwargs:
            logger.info('Input text %s element %s.' % (user_input, kwargs))
            self.Input_element_with_image(user_input, **kwargs)
        else:
            window = self.Find_Window(**kwargs)
            logger.info('Input text %s element %s.' % (user_input, kwargs))
            window.set_text("")
            window.type_keys(user_input, with_spaces=True, with_tabs=True)

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

    @keyword(name='Double Click Coordinates')
    def Double_Click_Coordinates(self, **kwargs):
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
        window.click_input(double=True, coords=((int(x)), (int(y))))

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
            logger.info(f'Element value: "{text}" is equal to "{user_input}" for {kwargs}')
        else:
            raise Exception(f'Element value: "{text}" is not equal to "{user_input}" for {kwargs}')

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
            logger.info(f'Element value: "{text}" contains "{user_input}" for {kwargs}')
        else:
            raise Exception(f'Element value: "{text}" does not contain "{user_input}" for {kwargs}')

    @keyword(name="Get Text")
    def Get_text(self, **kwargs):
        """
        **Get text of element**

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | {text}=  Get text  title=File
        """
        if "image" in kwargs:
            timeout = 30
            if "timeout" in kwargs:
                timeout = kwargs["timeout"]
            image_path = kwargs["image"]
            x, y = QAutoRPAImage.get_image_coords(image_path, timeout)
            ctrl_list = self.GetElementInfoFromCoords(x, y)
            text = ctrl_list["value"]
        else:
            window = self.Find_Window(**kwargs)
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
        logger.info('Right clicking element %s.' % kwargs)
        if "image" in kwargs:
            kwargs["right"] = True
            self.Click_element_with_image(**kwargs)
        else:
            window = self.Find_Window(**kwargs)
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

