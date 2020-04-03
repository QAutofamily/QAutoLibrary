# encoding: utf-8+
from QAutoLibrary.QAutoElement import QAutoElement
from time import sleep
import datetime
import os, errno
import json
import io
import re
import platform
import pymongo
from pymongo.errors import ConnectionFailure, OperationFailure


class RpaLogger():

    def __init__(self):
        """
        Class initialization

        """
        self.mongodbc = None
        self.robotname = ""
        self.filename = None
        self.vmname = ""

    def rpa_logger_init(self, filename=None, robotname=None, runid=1, mongodbIPPort="localhost:27017/", vmname="", username="",
                        password="", ssl=False):
        """
        :param filename: Path to the .json file where the information will be saved. Mandatory
        :param robotname: Name of the robot that generated the message to be saved Mandatory
        :param mongodbIPPort: ip and port: e.g localhost:27017/ Mandatory
        :param username: MongoDb username. Default empty. Optional
        :param password: MongoDb password. Default empty. Optional
        :param ssl: True or False. DefaultFalse. Optional
        -------------

        """
        if mongodbIPPort != "":
            try:
                if username == "":
                    try:
                        username = os.environ["MONGODBUSER"]
                    except:
                        pass
                if password == "":
                    try:
                        password = os.environ["MONGODBPASSWD"]
                    except:
                        pass
                if username != "":
                    self.mongodbc = pymongo.MongoClient("mongodb://" + mongodbIPPort, username=username,
                                                        password=password)
                else:
                    self.mongodbc = pymongo.MongoClient("mongodb://" + mongodbIPPort)
                print(self.mongodbc.admin.command('ismaster'))
            except (ConnectionFailure, OperationFailure) as e:
                print(e)
                self.mongodbc = None
                print("Mongodb Server not available or authentication failed")
                self.warning(
                    "RPA Mongodb Server not available  or authentication failed. Please check connection parameters.")

        if os.path.isfile(os.getcwd() + os.sep + "test_reports" + os.sep + filename):
            print("RPA logger file exists")
        else:
            print("RPA logger file will be created")
            robot_list = [{"Robot": robotname, "Sections": []}]
            self.append_to_file(os.getcwd() + os.sep + "test_reports" + os.sep + filename, robot_list)
        self.filename = filename
        self.robotname = robotname
        self.runid = runid
        self.vmname = vmname

    def save_rpa_data (self, **kwargs):
        """
        **Saves robot data to database**

        :param \**kwargs: 1..n named arguments 
        -------------
        Examples:
        | Save rpa data      | MyDataName=MyDataValue | SecondDataName=SecondDataValue

        """

        if len(kwargs.keys()) == 0:
            self.warning("RPA data missing! Nothing to add database!")
            return
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot save data!")
            return

        # Filter to find existing document
        filter = {"Runid":self.runid, "Robot": self.robotname}
        # Data to add or modify document
        rpa_data={}
        for key, value in kwargs.items():
            rpa_data.update({key: value})
        update = [{ "$addFields": {"rpaData": rpa_data}}]
        
        # Add to database. If 'filter' do not find any documents new will added
        # otherwise existing rpaData will be updated
        self.mongodbc.robotData.robotSavedData.update_one(filter, update, upsert=True) 

    def log_rpa(self, **kwargs):
        """
        :param \**kwargs:
        **state (string): Current robot state (optional)
        **title (string): Current message title (optional)
        **msg (string): Message to be saved to logs (optional)
        -------------
        Examples:
        | Log rpa      | state=ReadyReading | title=excelRead  | msg=All reading completed
        | Log rpa      | state=ReadyOngoing |
        | Log rpa      | title=excelRead | msg=All reading failed | type=Warning
        | Log rpa      | title=excelRead | msg=Generic error | type=Error

        """
        if self.filename == None:
            print("RPA logger file missing. Call rpa_logger_init first.")
            self.fail("RPA logger file missing. Call rpa_logger_init first.")

        message = ""
        sectionname = ""
        state = ""
        type = "Normal"
        if len(kwargs.keys()) == 0:
            self.fail("Log rpa Keyword arguments missing state or title or msg.")
        for kwarg in kwargs.keys():
            if kwarg == "title":
                sectionname = kwargs["title"]
            if kwarg == "msg":
                message = kwargs["msg"]
            if kwarg == "state":
                state = kwargs["state"]
            if kwarg == "type":
                type = kwargs["type"]

        timestamp = datetime.datetime.now().isoformat().split(".")[0]
        entry = None
        messages = None
        value = re.sub("[^0-9.,-]", "", message).strip()
        entry_message = {"Timestamp": timestamp, "Type": type, "Text": message, "Value": str(value)}
        entry_section = {"Messages": [{"Timestamp": timestamp, "Type": type, "Text": message, "Value": str(value)}],
                         "Title": sectionname}
        if self.mongodbc != None:
            mydb = self.mongodbc["robotData"]
            mycol = mydb["robotInfo"]
            entry_message_db = {"Timestamp": timestamp, "Type": type, "Text": message, "Value": str(value),
                                "Title": sectionname, "Robot": self.robotname, "Runid": self.runid, "State": state,
                                "VMname": self.vmname}
            x = mycol.insert_one(entry_message_db)
            print(x)

        print("Appending to json...", entry_message)
        with open(os.getcwd() + os.sep + "test_reports" + os.sep + self.filename) as feedsjson:
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
        with open(os.getcwd() + os.sep + "test_reports" + os.sep + self.filename, mode='w') as f:
            f.write(json.dumps(feeds, indent=4))

    def file_exists(self, filepath):
        return os.path.isfile(filepath)

    def append_to_file(self, filename=None, to_save=None):
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

