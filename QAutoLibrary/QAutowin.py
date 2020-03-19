import pywinauto
from pywinauto.keyboard import send_keys
from robot.api.deco import keyword
from robot.api import logger
import time
import os
from PIL import ImageGrab
import subprocess

# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#testing-libraries
# https://github.com/robotframework/robotframework/blob/master/doc/userguide/src/ExtendingRobotFramework/CreatingTestLibraries.rst

class QAutowin(object):
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    def __init__(self, backend="uia"):
        self.app = pywinauto.application.Application(backend=backend)
        pass

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
        for kwarg in kwargs.keys():
            print(kwarg)
            if kwarg == "process":
                self.app.application_process = kwargs["process"]
                self.app.connect(process=int(self.app.application_process))
            else:
                self.app.application_title = kwargs[list(kwargs.keys())[-1]]
                self.app.connect(**kwargs)
            logger.info(self.app.process)
            return self.app.process

    @keyword(name='Click Element')
    def Click_Element(self, **kwargs):
        """
        **Clicks at element**

        :kwargs: auto_id, class_name, class_name_re, title, title_re, control_type
        --------------
        :Example:
            | Click element  title=File
        """
        if "text" in kwargs:
            logger.info('Clicking element %s.' % kwargs)
            for kwarg in kwargs.keys():
                if kwarg == "text":
                    self.app.window(title_re=self.app.application_title)[(kwargs["text"])].wait('visible', timeout=10)
                    self.app.window(title_re=self.app.application_title)[(kwargs["text"])].click_input()
                    break
        elif 'x' in kwargs and 'y' in kwargs:
            logger.info('Clicking at coordinates %s.' % kwargs)
            self.Click_Coordinates(**kwargs)
        else:
            logger.info('Clicking element %s.' % kwargs)
            self.app.window(title_re=self.app.application_title).child_window(**kwargs).wait('visible', timeout=10)
            self.app.window(title_re=self.app.application_title).child_window(**kwargs).click_input()

    @keyword(name='Send Keywords')  # Send input data. Useful for text fields, that "Input text" does not recognize. Also, you can send keyboard actions, for example like ~ for Enter
    # https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html
    def Send_Keywords(self, user_input):
        logger.info('Send keywords %s.' % user_input)
        send_keys(user_input)

    @keyword(name='Input Text')
    def Input_Text(self, user_input, **kwargs):
        # Input text by: auto_id, class_name, class_name_re, title, title_re, control_type
        if "text" in kwargs:
            logger.info('Input text %s element %s.' % (user_input, kwargs))
            for kwarg in kwargs.keys():
                if kwarg == "text":
                    self.app.window(title_re=self.app.application_title)[(kwargs["text"])].wait('visible', timeout=10)
                    self.app.window(title_re=self.app.application_title)[(kwargs["text"])].type_keys(user_input,
                                                                                                     with_spaces=True,
                                                                                                     with_tabs=True)
                    break
        else:
            logger.info('Input text %s element %s.' % (user_input, kwargs))
            self.app.window(title_re=self.app.application_title).child_window(**kwargs).wait('visible', timeout=10)
            self.app.window(title_re=self.app.application_title).child_window(**kwargs).set_text("")
            self.app.window(title_re=self.app.application_title).child_window(**kwargs).type_keys(user_input,
                                                                                                  with_spaces=True,
                                                                                                  with_tabs=True)

    @keyword(name='Click Coordinates')
    def Click_Coordinates(self, **kwargs):
        """
        **Clicks at element using coordinates**

        :Example:
            | Click element  x=500    y=300
        """
        for kwarg in kwargs.keys():
            #application_title = (apptitle)
            # "File"
            if kwarg == "x":
                x = kwargs["x"]
            if kwarg == "y":
                y = kwargs["y"]

        self.app.window(title_re=self.app.application_title).maximize()
        time.sleep(1)
        self.app.window(title_re=self.app.application_title).click_input(coords=((int(x)), (int(y))))

    @keyword(name="Verify Text")
    def Verify_text(self, user_input, **kwargs):
        text = self.Get_text(**kwargs)
        print("Get_text:", text)
        if text == user_input:
            logger.info("%s is equal to %s" % (text, user_input))
            pass
        else:
            self.fail("%s is not equal to %s" % (text, user_input))

    @keyword(name="Get Text")
    def Get_text(self, **kwargs):
        if "text" in kwargs:
            for kwarg in kwargs.keys():
                if kwarg == "text":
                    text = self.app.window(title_re=".*"+self.app.application_title)[(kwargs["text"])].iface_value.CurrentValue
                    return text
        else:
            text = self.app.window(title_re=".*"+self.app.application_title).child_window(**kwargs).iface_value.CurrentValue
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
        if "text" in kwargs:
            logger.info('Clicking element %s.' % kwargs)
            for kwarg in kwargs.keys():
                if kwarg == "text":
                    self.app.window(title_re=self.app.application_title)[(kwargs["text"])].wait('visible', timeout=10)
                    self.app.window(title_re=self.app.application_title)[(kwargs["text"])].right_click_input()
                    break
        else:
            logger.info('Clicking element %s.' % kwargs)
            self.app.window(title_re=self.app.title).window(**kwargs).wait('visible', timeout=10)
            self.app.window(title_re=self.app.title).window(**kwargs).right_click_input()

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
        image = ImageGrab.grab()
        image.save(error_image_folder)
        logger.error('Something went wrong. Screenshot taken')

    @keyword(name='Close all cmds')
    def Close_all_cmds(self):
        os.system("TASKKILL /F /IM cmd.exe")

    @keyword(name='Launch bat')
    def Launch_bat(self, directory, bat_name):
        os.chdir(directory) # D:\\QAutomate\\QAutomate\\
        subprocess.call('start"' + bat_name + '"', shell=True)
        time.sleep(3)


