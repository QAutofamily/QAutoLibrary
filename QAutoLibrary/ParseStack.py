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
from QAutoLibrary.JsonLogger import JsonLogger
from datetime import datetime
from xml.dom import minidom
import os

xmldoc = minidom.parse(os.path.join('test_reports', 'output.xml'))
itemlist = xmldoc.getElementsByTagName('test')
kwlist = xmldoc.getElementsByTagName('kw')

JsonLogger().json_logger_init("time_stack.json", itemlist[0].attributes['name'].value)
FMT = '%Y%m%d %H:%M:%S.%f'
index = 0
for s in kwlist:
    if "run keyword if" in s.attributes['name'].value.lower() and index == 0:
        index = index + 1
        pass
    if s.attributes['name'].value == "Teardown":
        break
    elif "suite" in s.attributes['name'].value.lower() or "log" in s.attributes['name'].value.lower() or "setup" in \
            s.attributes['name'].value.lower() or "open browser" in s.attributes['name'].value.lower() or "set speed" \
            in s.attributes['name'].value.lower() or "start recording" in s.attributes['name'].value.lower() or \
            "run keyword if" in s.attributes['name'].value.lower():
        pass
    else:
        s1 = s.getElementsByTagName("status")[0].attributes['starttime'].value
        s2 = s.getElementsByTagName("status")[0].attributes['endtime'].value

        tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
        JsonLogger().append_to_jsondoc("time_stack.json", itemlist[0].attributes['name'].value,
                                       s.attributes['name'].value, str(tdelta)[:-3])
