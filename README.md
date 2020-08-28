# QAutoLibrary

QAutoLibrary is an extension for RobotFramework and Python, providing automation tools and RPA (Robotic Process Automation) libraries.

## Main Libraries

**QAutoRobot**, extensive RPA and test automation library for Robot Framework.

**QAutowin**, a testing tool for native Windows applications. QAutowin can be used with QAutoRobot.

**PythonOCR**, Python library of functions for finding and locating words on screen, in image files or PDF files using OCR (Optical Character Recognition).

**NOTE:** PythonOCR is unreliable at best when finding words in files, and should only be used as an assistance to process files. Usage of other confirmation methods (such as manual labor) is adviced, when processing important files!

## Getting Started

QAutoLibrary requires Python, and additional libraries depending on which QAutoLibrary modules you want to use.

The library can be installed using pip, or straight from the source code using setup.py file.

Extensive and detailed instructions on prerequisites, installing, importing and usage, with examples, is provided in [INSTRUCTIONS.md](INSTRUCTIONS.md) file.

### Prerequisites

QAutoLibrary requires [Python 3.7](https://docs.python.org/3/) in order to be usable.

Additionally, QAutoLibrary modules may require other library installations, as detailed in the following sections.

#### QAutoRobot Prerequisites

**NOTE:** If you have installed [QAutomate tool](https://qautomate.fi/qautomate/), the libraries required by QAutoRobot should already be installed.

QAutoRobot modules require the following library installations:

[Selenium](https://www.seleniumhq.org/docs/): ```pip install selenium```

[Robot Framework](http://robotframework.org/#documentation): ```pip install robotframework```

[Requests](http://docs.python-requests.org/en/master/): ```pip install requests```

[Pillow](https://pillow.readthedocs.io/en/stable/): ```pip install Pillow```

[LXML](https://lxml.de/): ```pip install lxml```

[SimpleJSON](https://simplejson.readthedocs.io/en/latest/): ```pip install simplejson```

[pymongo](https://pypi.org/project/pymongo/): ```pip install pymongo```

[pycryptodome](https://pypi.org/project/pycryptodome/): ```pip install pycryptodome```

#### PythonOCR Prerequisites

**NOTE:** See on INSTRUCTIONS.md file, in [PythonOCR Prerequisites](INSTRUCTIONS.md#pythonocr-prerequisites)-section, for PythonOCR prerequisites' installation instructions.

PythonOCR module requires the following libraries:

[pyautogui](https://pypi.org/project/PyAutoGUI/)

[poppler](https://github.com/oschwartz10612/poppler-windows)

[pdf2image](https://pypi.org/project/pdf2image/), with more information at https://github.com/Belval/pdf2image

[Google Tesseract OCR](https://github.com/tesseract-ocr/tessdoc)

[pytesseract](https://pypi.org/project/pytesseract/)

### Installing

The library can be installed using pip, or straight from the source code using setup.py file. Instructions on how to install from the source files is provided in INSTRUCTIONS.md file, in [Installing from Source Files](INSTRUCTIONS.md#installing-from-source-files)-section.

QAutoLibrary can be downloaded and installed to your local Python libraries, using pip:

```
pip install --upgrade https://customer.qautomate.fi/downloadQautoLibrary.html
```

## Usage

QAutoLibrary modules can provide additional functionality to Python code or Robot.

Extensive and detailed instructions, with examples, are provided in INSTRUCTIONS.md file, in [Usage](INSTRUCTIONS.md#usage)-section.

### Usage in Python code

**Importing**

To import a QAutoLibrary module to Python code:

```
from QAutoLibrary import <Module>
```

To import a class from a module:

```
from QAutoLibrary.<Module> import <Class>
```

**Usage**

Module functions can then be used as follows:

```
<Module>.<function>()
```

Class objects can be instantiated as follows:

```
<Object> = <Class>()
```

**Examples**

```
from QAutoLibrary.QAutoSelenium import CommonMethods

my_methods = CommonMethods()
my_methods.set_speed(timeout=5)
```

```
from QAutoLibrary import PythonOCR

PythonOCR.find_coordinates("Python", "./images/screenshot.png")
```

### Usage in QAutoRobot

**Importing**

QAutoLibrary modules can be imported to QAutoRobot as libraries. Import a module to robot in the Settings field:

```
*** Settings ***
Library  |  QAutoLibrary.<Module>
```

**Usage**

Keywords of the module can then be used in the robot:

```
*** Test Cases ***
Test Case
  |  <Module Keyword>  |  ${<argument1>}  |  ${<argument2>}  |  ...
```

**Examples**

```
*** Settings ***
Library  |  QAutoLibrary.QAutowin

*** Tasks ***
Example 1
    Open Application  |  notepad.exe
```

```
*** Settings ***
Library  |  QAutoLibrary.PythonOCR

*** Variables ***
${file} =  ./files/test_file.pdf
@{results_list}

*** Tasks ***
Example 2
    @{results_list} =  |  Find Words  |  Python  |  ${file}  |  ./output/
```

### Custom libraries in QAutoRobot

Custom Python libraries can be provided to QAutoRobot. QAutoRobot dynamically (during runtime) imports modules located in the robot's 'pagemodel' folder.

Detailed instructions on how to create and use custom Python modules with QAutoRobot can be found in INSTRUCTIONS.md file, in [Importing Custom Libraries](INSTRUCTIONS.md#importing-custom-libraries)-section.

## Built With
* [Python 3.7](https://docs.python.org/3/) - Programming language
* [Python 2.7](https://docs.python.org/2/) - Programming language Old
* [Selenium](https://www.seleniumhq.org/docs/) - Web-testing framework

## Contributing

TBA later.

## Authors

* **QAutomate Oy** - *Development* - [QAutomate Oy](https://www.qautomate.fi/)

See also the list of [contributors](https://github.com/QAutoFamily/QAutoLibrary/contributors) who participated in this project.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details

