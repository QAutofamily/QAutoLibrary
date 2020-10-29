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
from QAutoLibrary.extension.util.common_methods_helpers import DebugLog
from time import sleep
import datetime
import os, errno
import json
import io
import re
import platform
import pymongo
import ssl
from pymongo.errors import ConnectionFailure, OperationFailure
from robot.libraries.BuiltIn import BuiltIn


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
                        password="", sslbool=True):
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
                    self.mongodbc = pymongo.MongoClient("mongodb://" + mongodbIPPort, username=username, password=password, ssl=sslbool, ssl_cert_reqs=ssl.CERT_NONE)
                else:
                    self.mongodbc = pymongo.MongoClient("mongodb://" + mongodbIPPort)
                DebugLog.log(self.mongodbc.admin.command('ismaster'))
            except (ConnectionFailure, OperationFailure) as e:
                DebugLog.log(e)
                self.mongodbc = None
                DebugLog.log("Mongodb Server not available or authentication failed")
                self.warning(
                    "RPA Mongodb Server not available or authentication failed. Please check connection parameters.")
        if filename:
            if os.path.isfile(os.getcwd() + os.sep + "test_reports" + os.sep + filename):
                DebugLog.log("RPA logger file exists")
            else:
                DebugLog.log("RPA logger file will be created")
                robot_list = [{"Robot": robotname, "Sections": []}]
                self.append_to_file(os.getcwd() + os.sep + "test_reports" + os.sep + filename, robot_list)
        self.filename = filename
        self.robotname = robotname.replace(" ", "_")
        self.runid = int(runid)
        self.vmname = vmname

    def save_rpa_data(self, **kwargs):
        """
        *DEPRECATED* Use keyword `Save data` instead.
        """
        self.save_data(**kwargs)

    def save_data(self, **kwargs):
        """
        **Saves robot data to database**

        :param \**kwargs: 1..n named arguments
        -------------
        Examples:
        | Save data      | MyDataName=MyDataValue | SecondDataName=SecondDataValue

        """

        if len(kwargs.keys()) == 0:
            self.warning("RPA data missing! Nothing to add database!")
            return
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot save data!")
            return

        # Filter to find existing document
        filter = {"Runid": self.runid, "Robot": self.robotname}
        # Data to add or modify document
        rpa_data={}
        for key, value in kwargs.items():
            rpa_data.update({key: value})
        update = [{ "$addFields": {"rpaData": rpa_data}}]

        # Add to database. If 'filter' do not find any documents new will added
        # otherwise existing rpaData will be updated
        self.mongodbc.robotData.robotSavedData.update_one(filter, update, upsert=True)

    def save_resources(self, **kwargs):
        """
        **Saves robot permanent data to database**

        :param \**kwargs: 1..n named arguments, "robotname" in **kwargs it used to identify robot resource
        -------------
        Examples:
        | *Robot level example*
        | Save resources      | MyDataName=MyDataValue | SecondDataName=SecondDataValue
        | *Page model level example*
        | ``QAutoRobot.save_resources(MyDataName=MyData)``

        """
        if len(kwargs.keys()) == 0:
            self.warning("RPA data missing! Nothing to add database!")
            return
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot save data!")
            return

        # Filter to find existing document
        robotname = kwargs.pop("robotname") if "robotname" in kwargs else self.robotname
        filter = {"Robot": robotname}
        # Data to add or modify document
        data_to_save={}
        for key, value in kwargs.items():
            data_to_save.update({key: value})
        update = [{ "$addFields": data_to_save}]

        # Add to database. If 'filter' do not find any documents new will added
        # otherwise existing data will be updated
        self.mongodbc.robotData.robotResources.update_one(filter, update, upsert=True)
        DebugLog.log(f"* '{robotname}' data saved to robotResources: {data_to_save}")

    def get_resource_data(self, field=None, robotname=None):
        """
        **Get all robot saved data from robotResources**

        :param robotname: String name of the robot (optional)
        :param field: String name of document field (optional)
        :return:    Robot resources whole document or only one field
        -------------
        Examples:
        | *Robot level example*
        | Get resource data
        | Get resource data    | field=documentFieldName
        | *Page model level example*
        | ``QAutoRobot.get_resource_data(field="documentFieldName")"``

        """
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot get resource data")
            return  None
        # Set query parameters
        robotname = robotname if robotname else self.robotname
        query = {"Robot": robotname}

        results = self.mongodbc.robotData.robotResources.find_one(query)
        if field:
            if field in results:
                return results[field]
            else:
                self.warning(f"'{robotname}' resource document has not field '{field}'")
                return None
        return results

    def remove_resource_document(self, robotname=None):
        """
        **Removes whole document from robot resources**

        :param robotname: String name of the robot (optional)
        -------------
        Examples:
        | *Robot level example*
        | Remove resource document
        | *Page model level example*
        | ``QAutoRobot.remove_resource_document()``

        """
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot remove resource data")
            return  None
        # Set query parameters
        robotname = robotname if robotname else self.robotname
        query = {"Robot": robotname}

        results = self.mongodbc.robotData.robotResources.delete_one(query)
        if results.deleted_count == 0:
            self.warning(f"Nothing removed! Maybe resource document '{robotname}' does not exists!")
        else:
            DebugLog.log(f"* '{robotname}' document removed from resources")

    def remove_resource_field(self, field_path, robotname=None):
        """
        **Removes field from robot resources**

        :param field_path: String path to field to remove (dot presentation)
        :param robotname: String name of the robot (optional)
        -------------
        Examples:
        | *Robot level example*
        | Remove resource field      | field.to.remove
        | *Page model level example*
        | ``QAutoRobot.remove_resource_field("field.to.remove")``

        """
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot remove resource data")
            return  None
        # Set query parameters
        robotname = robotname if robotname else self.robotname
        query = {"Robot": robotname}

        results = self.mongodbc.robotData.robotResources.update_one(query, {"$unset": {field_path: 1 }})
        if results.modified_count == 0:
            self.warning(f"Nothing removed from '{robotname}' resources. Maybe field '{field_path}' does not exists!")
        else:
            DebugLog.log(f"* Field '{field_path}' removed from '{robotname}' resources")

    def remove_resource_list_value(self, field_path, list_value, robotname=None):
        """
        **Removes field from robot resources**

        :param field_path: String path to field to remove (dot presentation)
        :param list_value: Any  list value to remove
        :param robotname: String name of the robot (optional)
        -------------
        Examples:
        | *Robot level example*
        | Remove resource list value      | field.list.remove    | list value
        | *Page model level example*
        | ``QAutoRobot.remove_resource_list_value("field.list.remove", "list value")``

        """
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot remove resource data")
            return  None
        # Set query parameters
        robotname = robotname if robotname else self.robotname
        query = {"Robot": robotname}

        results = self.mongodbc.robotData.robotResources.update_one(query, {"$pull": {field_path: list_value}})
        if results.modified_count == 0:
            self.warning(f"Nothing removed from '{robotname}' resources. Maybe field '{field_path}' or list value '{list_value}' does not exists!")
        else:
            DebugLog.log(f"* '{robotname}' resources list value '{list_value}' removed from field '{field_path}'.")

    def set_custom_post_trigger(self, condition=True):
        """
        **Save custom post trigger to database**

        If set True, other robot can be triggered, regardless of current robots result.

        :param: condition: Boolean to set custom post trigger on/off. Default True.
        -------------
        Examples:
        | Set custom post trigger      | True
        | Set custom post trigger      | ${TRUE}
        | Set custom post trigger      | ${FALSE}

        """
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot set custom trigger!")
            return

        # Filter to find existing document
        filter = {"Runid": self.runid, "Robot": self.robotname}
        # Add or modify document
        update = [{ "$addFields": {"CustomPostTrigger": str(condition).capitalize()}}]

        # Add/update to database. If 'filter' do not find any documents new will added
        # otherwise existing document will be updated
        self.mongodbc.robotData.robotSavedData.update_one(filter, update, upsert=True)
        DebugLog.log(f"* Set custom post trigger to: {str(condition).capitalize()}")

    def set_savings_multiply(self, value):
        """
        **Save savings multiply to database**

        This value will be used to calculate robot savings. If set 0 (zero), robot has not
        done any actual savings.

        :param: value: Integer.
        -------------
        Examples:
        | Set savings multiply      | 2
        | Set savings multiply      | 0

        """
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot set custom trigger!")
            return

        # Filter to find existing document
        filter = {"Runid": self.runid, "Robot": self.robotname}
        # Add or modify document
        update = [{ "$addFields": {"SavingsMultiply": int(value)}}]

        # Add/update to database. If 'filter' do not find any documents new will added
        # otherwise existing document will be updated
        self.mongodbc.robotData.robotSavedData.update_one(filter, update, upsert=True)
        DebugLog.log(f"* Updated robot savings multiply to: {value}")

    def setup_rpa_data (self, runid=None, robotname=None):
        """
        *DEPRECATED* Use keyword `Setup data` instead.
        """
        self.setup_data(runid, robotname)

    def setup_data(self, runid=None, robotname=None):
        """
        **Setup robot data from database**

        :param runid:  Integer id of robot run
        :param robotname: String name of the robot that is running
        -------------
        Examples:
        | Setup data      | runid=${RUNID} | robotname=${ROBOTNAME}
        | Setup data      | ${RUNID} | ${ROBOTNAME}

        """

        # Set query parameters
        runid = runid if runid else self.runid
        robotname = robotname if robotname else self.robotname
        query = {"Runid": runid, "Robot": robotname}
        DebugLog.log("Query parameters: %s" % query)

        # Find robot data
        result = self.mongodbc.robotData.robotSavedData.find_one(query)
        # Add data to robot variables
        if result and "rpaData" in result:
            for key, value in result["rpaData"].items():
                if isinstance(value, dict):
                    string_list = ["%s=%s" % (k, v) for k, v in value.items()]
                    value = BuiltIn().create_dictionary(*string_list)
                elif isinstance(value, list):
                    value = BuiltIn().create_list(*value)

                BuiltIn().set_suite_variable("${%s}" % key, value)

    def get_rpa_executed_tasks(self, runid=None, robotname=None):
        """
        **Get all tasks (tags) that robot has executed/saved**

        :param runid: Integer id of robot run that was executed
        :param robotname: String name of the robot that was executed
        :return:    List of states (tags) that robot has executed/saved
        -------------
        Examples:
        | Get rpa executed tasks      | runid=${RUNID} | robotname=${ROBOTNAME}
        | Get rpa executed tasks      | ${RUNID} | ${ROBOTNAME}

        """
        if self.mongodbc == None:
            self.warning("Mongodb Server not available, cannot get rerun tasks")
            return  None
        # Set query parameters
        runid = runid if runid else self.runid
        robotname = robotname if robotname else self.robotname
        query = {"Runid": runid, "Robot": robotname, "State" : {"$exists" : True, "$ne" : ""}}

        # Find all states (tags) that robot has executed with this Runid
        tags = []
        result = self.mongodbc.robotData.robotInfo.find(query)
        for doc in result:
            tags.append(doc["State"])

        return tags

    def log_rpa(self, **kwargs):
        """
        *DEPRECATED* Use keyword `Log data` instead.
        """
        self.log_data(**kwargs)

    def log_data(self, **kwargs):
        """
        :param \**kwargs:
        **state (string): Current robot state (optional)
        **title (string): Current message title (optional)
        **msg (string): Message to be saved to logs (optional)
        -------------
        Examples:
        | Log data      | state=ReadyReading | title=excelRead  | msg=All reading completed
        | Log data      | state=ReadyOngoing |
        | Log data      | title=excelRead | msg=All reading failed | type=Warning
        | Log data      | title=excelRead | msg=Generic error | type=Error

        """
        if self.filename == None:
            DebugLog.log("RPA logger file missing. Call rpa_logger_init first.")
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
            DebugLog.log(f"Title: {sectionname}, Message: {message}")

        #DebugLog.log("Appending to json...", entry_message)
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
                    DebugLog.log("Error in adding")
                    DebugLog.log(e)
                    secto = section["Sections"]
                    break
            if already_added == False:
                #DebugLog.log("Already added")
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

