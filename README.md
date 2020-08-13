# QAutoLibrary

QAutofamily testing framework library. To be used as RobotFramework testing library and collection of web-testing tools for python.

## Getting Started

QAutoLibrary requires Python, and different additional libraries depending on which QAutoLibrary modules you want to use.

The library can be installed using pip, or straight from the source code using setup.py file.

**NOTE:** Optionally, QAutoLibrary can be set up as a PYTHONPATH environment variable.

### Prerequisites

QAutoLibrary requires [Python 3.7+](https://docs.python.org/3/) in order to be usable.

Additionally, QAutoLibrary modules may require other library installations, as detailed in the following sections.

#### QAutoRobot Prerequisites

**NOTE:** If you have installed QAutomate tool, libraries required by QAutoRobot should already be installed.

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

**NOTE:** See [/QAutoLibrary/README.md](./QAutoLibrary/README.md) for PythonOCR installation instructions.

PythonOCR module requires the following libraries:

[pyautogui](https://pypi.org/project/PyAutoGUI/)

[poppler](https://github.com/oschwartz10612/poppler-windows)

[pdf2image](https://pypi.org/project/pdf2image/), with more information at https://github.com/Belval/pdf2image

[Google Tesseract OCR](https://github.com/tesseract-ocr/tessdoc)

[pytesseract](https://pypi.org/project/pytesseract/)

### Installing with pip

QAutoLibrary can be downloaded and installed to your local Python libraries, using pip:

```
pip install --upgrade https://customer.qautomate.fi/downloadQautoLibrary.html
```

### Installing from Source Files

Alternatively, QAutoLibrary can be installed straight from the source files. The library is installed using [setup.py](setup.py) file.

1. Open Command Prompt and navigate to a directory path where you want to download QAutoLibrary.

2. Download the source files by cloning the Git repository:

```
git clone https://github.com/QAutofamily/QAutoLibrary
```

3. Navigate to the QAutoLibrary directory:

```
cd QAutoLibrary
```

4. Run setup.py module as a script:

```
python -m setup.py install
```

### Setting QAutoLibrary to PYTHONPATH

Optional. QAutoLibrary can be used by setting it as a PYTHONPATH environment variable (useful for continuous integration like Jenkins).

1. On Windows, go to: ```Advanced System Properties > Environment Variables...```

2. Create a new system variable, or edit an existing System variable called: ```PYTHONPATH```

3. Make sure PYTHONPATH variable value contains Python directory path. If not, add the Python directory path. ```C:\path\to\Python\version```

4. Add QAutoLibrary directory path as PYTHONPATH variable value. ```C:\path\to\QAutoLibrary```

Separate different variable values with semicolons: ```first;second```

5. Edit System variable called ```Path```, and add the following values to the variable values: ```%PYTHONPATH%```;```%PYTHONPATH%\Lib```;```%PYTHONPATH%\DLLs```;```%PYTHONPATH%\Lib\lib-tk```

6. If QAutoLibrary was installed using pip, include the following value to the Path variable values: ```%PYTHONPATH%\Scripts```

## Usage

QAutoLibrary modules can provide additional functionality to Python code or QAutoRobot.

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
<module>.<function>()
```

And class objects can be instantiated as follows:

```
<Object> = <Class>()
```

**Examples**

```
from QAutoLibrary import PythonOCR

image_file = "./images/screenshot.png"
PythonOCR.find_coordinates("Python", image_file)
```

```
from QAutoLibrary.QAutoSelenium import CommonMethods

my_methods = CommonMethods()
my_methods.set_speed(timeout=5)
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
*** Tasks ***
Test Case
    <Module Keyword>  |  ${<argument>}
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
@{results_list}

*** Tasks ***
Example 2
    @{results_list} = |  Find Words  |  Python  |  ./files/test_file.pdf  |  ./output/
```

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

