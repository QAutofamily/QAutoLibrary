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

