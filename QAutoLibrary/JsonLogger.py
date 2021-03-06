# encoding: utf-8+
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
from QAutoLibrary.QAutoElement import QAutoElement
from time import sleep
import datetime
import os, errno
import json
import io
import re
import platform


class JsonLogger():

    def __init__(self):
        """
        Class initialization

        """
        pass

    def json_logger_init(self, filename=None, robotname=None):
        """
        :param filename: Path to the .json file where the information will be saved.
        :param robotname: Name of the robot that generated the message to be saved
        :param time: Current timestamp
        :param message: Message to be saved to the filename
        -------------

        """

        if os.path.isfile(os.getcwd() + os.sep + "test_reports" + os.sep + filename):
            print("File to be append")
        else:
            print("To be created")
            robot_list = [{"Robot": robotname, "Sections": []}]
            self.append_to_json_file(os.getcwd() + os.sep + "test_reports" + os.sep + filename, robot_list)

    def append_to_jsondoc(self, fname=None, robotname=None, sectionname=None, message=None):
        """
        :param fname: Path to the .json file where the information will be saved.
        :param robotname: Name of the robot that generated the message to be saved
        :param sectionname: Current section title
        :param message: Message to be saved to the filename
        -------------

        """
        timestamp = datetime.datetime.now().isoformat().split(".")[0]
        entry = None
        messages = None
        value = re.sub("[^0-9.,-]", "", message).strip()
        entry_message = {"Timestamp": timestamp, "Type": "Normal", "Text": message, "Value": str(value)}
        entry_section = {"Messages": [{"Timestamp": timestamp, "Type": "Normal", "Text": message, "Value": str(value)}],
                         "Title": sectionname}
        print("Appending to json...", entry_message)
        with open(os.getcwd() + os.sep + "test_reports" + os.sep + fname) as feedsjson:
            feeds = json.load(feedsjson)

        already_added = False
        for section in feeds:
            messages = section["Sections"]
            for message in messages:
                try:
                    title = message["Title"]
                    if title == sectionname:
                        messa = message["Messages"]
                        messa.append(entry_message)
                        already_added = True
                        break
                    else:
                        secto = section["Sections"]
                except Exception as e:
                    print("Error in adding")
                    print(e)
                    secto = section["Sections"]
                    break
            if already_added == False:
                print("Already added")
                secto = section["Sections"]
                secto.append(entry_section)
        with open(os.getcwd() + os.sep + "test_reports" + os.sep + fname, mode='w') as f:
            f.write(json.dumps(feeds, indent=4))

    def file_exists(self, filepath):
        return os.path.isfile(filepath)

    def append_to_json_file(self, filename=None, to_save=None):
        """
        :param filename: Path to the .json file where the information will be saved. Must be full path.
        :param to_save: Information to save to the json file
        -------------

        Constructs a string based on the message and time and saves it to the filename under the robotname key
        """

        try:
            with io.open(filename, "a", encoding='utf-8') as myfile:
                myfile.write(json.dumps(to_save, ensure_ascii=False, indent=4))
        except IOError as e:
            self.fail("Error writing data to the file ({0}): {1}".format(e.errno, e.strerror))

