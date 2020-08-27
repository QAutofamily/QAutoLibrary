# QAutoLibrary Instructions

QAutoLibrary Instructions on how to install prerequisites of the different modules, how to install QAutoLibrary and guide on how to use the different modules on your projects.

## Prerequisites

QAutoLibrary requires Python 3.7 in order to be used.

Additionally, modules of the QAutoLibrary may use external libraries, which have to be installed.

### Python

Install Python 3.7 and include pip with the installation. **Add Python to PATH.**

Download Python: https://www.python.org/downloads/

More information at: https://docs.python.org/3/

### QAutoRobot Prerequisites

QAutoRobot uses the following libraries:

**Selenium**

**Robot Framework**

**Requests**

**Pillow**

**LXML**

**SimpleJSON**

**pymongo**

**pycryptodome**

**NOTE:** If you have installed [QAutomate tool](https://qautomate.fi/qautomate/), the libraries required by QAutoRobot should already be installed.

#### Selenium

Install Selenium using pip:

```
pip install selenium
```

More information at: https://www.seleniumhq.org/docs/

#### Robot Framework

Install Robot Framework using pip:

```
pip install robotframework
```

More information at: http://robotframework.org/#documentation

#### Requests

Install Requests using pip:

```
pip install requests
```

More information at: http://docs.python-requests.org/en/master/

#### Pillow

Install Pillow using pip:

```
pip install Pillow
```

More information at: https://pillow.readthedocs.io/en/stable/

#### LXML

Install LXML using pip:

```
pip install lxml
```

More information at: https://lxml.de/

#### SimpleJSON

Install SimpleJSON using pip:

```
pip install simplejson
```

More information at: https://simplejson.readthedocs.io/en/latest/

#### pymongo

Install pymongo using pip:

```
pip install pymongo
```

More information at: https://pypi.org/project/pymongo/

#### pycryptodome

Install pycryptodome using pip:

```
pip install pycryptodome
```

More information at: https://pypi.org/project/pycryptodome/

### PythonOCR Prerequisites

PythonOCR uses the following libraries:

**pyautogui** for taking screenshots and mouse controls.

**poppler** to read, render and modify PDF files.

**pdf2image** to convert PDF files to image files. pdf2image is a wrapper around poppler.

**pytesseract** to recognize text in image files. pytesseract requires **Google Tesseract OCR** in order to function.

#### pyautogui

Install pyautogui using pip:

```
pip install pyautogui
```

More information at: https://pypi.org/project/PyAutoGUI/

#### poppler

**Windows:**

Download the latest poppler release (.zip file) from: https://github.com/oschwartz10612/poppler-windows/releases/

More information at: https://github.com/oschwartz10612/poppler-windows

1. Unzip the poppler release file.

2. Add the poppler folder ('poppler-xx') to your Program Files. (For example, to: ```C:\Program Files (x86)\Poppler\ ```.)

3. Include the 'poppler-xx\bin' folder as a SYSTEM PATH environment variable. (For example, add: ```C:\Program Files (x86)\Poppler\poppler-0.90.1\bin``` to PATH.)

**Linux:**

**NOTE:** Installing poppler is not be neccessarily needed, if ```pdftoppm``` and ```pdftocairo``` are installed.

To install poppler on Ubuntu:

```
sudo apt install poppler-utils
```

More information at: https://pdf2image.readthedocs.io/en/latest/installation.html

#### pdf2image

**NOTE:** Install poppler before installing pdf2image!

Install pdf2image using pip:

```
pip install pdf2image
```

More information at: https://pypi.org/project/pdf2image/ and https://github.com/Belval/pdf2image

#### Tesseract OCR

**Windows:**

Install Google Tesseract OCR and include Finnish. **Add Tesseract-OCR to PATH.**

Download Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki

More information at: https://github.com/tesseract-ocr/tessdoc

**Linux:**

Install Tesseract OCR using the command:

```
sudo apt install tesseract-ocr
```

#### pytesseract

**NOTE:** Install Tesseract OCR before installing pytesseract!

Install pytesseract using pip:

```
pip install pytesseract
```

More information at: https://pypi.org/project/pytesseract/

**Permission Error (Linux):**

If the attempt to install pytesseract on Linux resulted in Permission error, you can attempt to install pytesseract on access-level where you have persmissions.

To install to a user-specific directory, use ```--user``` flag. For example, to install pytesseract to user-specific directory as Python 3.7 module:

```
python3.7 -m pip install --user pytesseract
```

## Installation

Before installing QAutoLibrary, make sure all the prerequisites of the modules you want to use are met.

### Installing using pip

QAutoLibrary can be downloaded and installed to your local Python libraries, using pip:

```
pip install --upgrade https://customer.qautomate.fi/downloadQautoLibrary.html
```

### Installing from Source Files

Alternatively, QAutoLibrary can be installed straight from the source files. The library is installed using setup.py file.

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

## Usage

Use guides include QAutoRobot and PythonOCR use instructions. QAutoRobot use guide also includes how to include user-made, custom Python libraries to QAutoRobot.

### QAutoRobot Usage

QAutoRobot RPA module can be used in robot, or in Python code. Importing custom Python modules to a robot that utilizes QAutoRobot is simple, as QAutoRobot attempts to automatically import custom modules during runtime.

**NOTE:** Robots made with [QAutomate tools](https://qautomate.fi/qautomate/) already contain QAutoRobot libraries.

#### Usage in Robot

**Importing**

To import QAutoRobot into your robot:

```
*** Settings ***
Library  |  QAutoLibary.QAutoRobot
```

**Usage**

QAutoRobot keywords can then be used in your robot as follows:

```
*** Test Cases ***
<Test Case>
  |  <QAutoRobot Keyword>  |  <argument1>  |  <argument2>  |  ...
```

**Example**

In the following example, ```Start Recording``` and ```Stop Recording``` are the keywords from QAutoRobot:

```
*** Test Cases ***
Recording Example
  |  Start Recording  |  Recording Example
  |  Open Browser  |  https://qautomate.fi/  |  googlechrome
  |  Stop Recording
```

#### Importing Custom Libraries

Custom Python libraries can be added to the robot in 'pagemodel' folder. QAutoRobot dynamically (during runtime) imports modules located in the robot's 'pagemodel' folder.

Custom modules can, for example, provide custom keywords for QAutoRobot.

**Custom module requirements:**

* The Python file should locate in the robot's 'pagemodel' folder.

```/pagemodel/<module>.py```

* The Python file should contain a class. This class can contain custom functions.

```
class <Class>():

	def <function>():
		...
```

* The name of the Python file should match the name of the class. However, the file name should be all lowercase and the class name should start with Uppercase.

**Custom module example:**

```/pagemodel/add_numbers.py```

```
class Add_numbers():

	def add_integers(self, a, b):
		return int(a) + int(b)
```

The example function, 'add_integers()', can then be used as a keyword in QAutoRobot:

```
*** Tasks ***
Test Custom Module
  |  ${total} =  |  Add Integers  |  1  |  2
```

When creating custom libraries for QAutoRobot, follow the standard Python naming convention ([PEP 8](https://www.python.org/dev/peps/pep-0008/)).

#### Usage in Python code

QAutoRobot can be imported and used in Python code, for example, when creating custom Python modules for robot.

**Importing**

Import QAutoRobot to your Python code:

```
import QAutoRobot
```

**NOTE:** IDE compilers may complain that they cannot import QAutoRobot this way, but when robot dynamically imports custom modules during runtime, this kind of import succeeds.

**Usage**

Functions of the QAutoRobot module can then be used as follows:

```
QAutoRobot.<function>(<argument1>, <argument2>, ...)
```

### PythonOCR Usage

PythonOCR functions can be used in both Python code or robot.

**Main functions** of the PythonOCR are as follows:

```click_word()``` takes a screenshot, searches for a word on screen and clicks the location of a found instance.

```find_words()``` searches for all instances of a specified word in an image or PDF file, and returns results.

```find_coordinates()``` searches for all instances of a specified word and their coordinates in an image or PDF file, and returns results.

```verify_word()``` searches for any instance of a specified word in an image file, and returns True or False whether an instance was found.

**Parameters** of each of the main functions are as follows:

```click_word(word, save_screenshot_as, index)``` with ```save_screenshot_as``` and ```index``` being optional.

```find_words(word, file_path, output_path)``` with ```output_path``` being optional; used when processing PDF files.

```find_coordinates(word, file_path, output_path)``` with ```output_path``` being optional; used when processing PDF files.

```verify_word(word, image_path)```

**NOTE:** Provide file paths and directory paths in string format to function parameters. Include file type endings, such as '.jpg' or '.png', when providing file paths.

#### Usage in Python code

**Importing**

Import PythonOCR to your Python code:

```
from QAutoLibrary import PythonOCR
```

**Usage**

PythonOCR functions can be then used as follows:

```
PythonOCR.<function>(<parameter1>, <parameter2>,...)
```

#### Examples (Python)

**click_word()**

```PythonOCR.click_word("Python")``` Searches for word 'Python' on screen and if a single instance is found, clicks its location. Screenshot is not saved.

```PythonOCR.click_word("Python", "screenshot.png")``` As above, but the screenshot is saved to the current project directory as 'screenshot.png'.

```PythonOCR.click_word("Python", "./screenshots/screenshot.png")``` As above, but the screenshot is saved to 'screenshots' folder in the current project directory.

```PythonOCR.click_word("Python", "C:/project_folder/screenshots/screenshot.png")``` As above, but the screenshot is saved to the specific directory.

```PythonOCR.click_word("Python", index=0)``` Searches for the word on screen and if finds multiple instances of the word, clicks the first found instance (at index position 0 (zero)). Screenshot is not saved.

**find_words()**

```PythonOCR.find_words("Python", "image_file.png")``` Returns all found instances of the word 'Python' in 'image_file.png'.

```results_list = PythonOCR.find_words("Python", "image_file.png")``` As above, but the results are assigned to 'results_list' variable.

```print(PythonOCR.find_words("Python", "image_file.png"))``` As above, but the results are printed to console.

```PythonOCR.find_words("Python", "./project_files/image_file.png")``` Returns all found instances of the word in 'image_file.png' located in 'project_files' folder in the current project directory.

```PythonOCR.find_words("Python", "pdf_file.pdf")``` Returns all found instances of the word 'Python' in 'pdf_file.pdf'. Images converted from the PDF file are saved to the current project directory.

```PythonOCR.find_words("Python", "pdf_file.pdf", "./output")``` As above, but images are saved to 'output' folder in the current project directory.

```PythonOCR.find_words("Python", "C:/projet_folder/pdf_file.pdf", "C:/project_folder/output")``` As above, but file path and output folder for images are provided as absolute file paths.

**find_coordinates()**

```PythonOCR.find_coordinates("Python", "image_file.png")``` Returns all instances of the word 'Python' and their coordinates in 'image_file.png'.

```results_list = PythonOCR.find_coordinates("Python", "image_file.png")``` As above, but the results are assigned to 'results_list' variable.

```print(PythonOCR.find_coordinates("Python", "image_file.png"))``` As above, but the results are printed to console.

```PythonOCR.find_coordinates("Python", "./project_files/image_file.png")``` Returns all found instances of the word and their coordinates in 'image_file.png' located in 'project_files' folder in the current project directory.

```PythonOCR.find_coordinates("Python", "pdf_file.pdf")``` Returns all found instances of the word 'Python' and their coordinates in 'pdf_file.pdf'. Images converted from the PDF file are saved to the current project directory.

```PythonOCR.find_coordinates("Python", "pdf_file.pdf", "./output")``` As above, but images are saved to 'output' folder in the current project directory.

```PythonOCR.find_coordinates("Python", "C:/projet_folder/pdf_file.pdf", "C:/project_folder/output")``` As above, but file path and output folder for images are provided as absolute file paths.

**verify_word()**

```PythonOCR.verify_word("Python", "image_file.png")``` Returns True or False if finds any instances of the word 'Python' in 'image_file.png'.

```found_word = PythonOCR.verify_word("Python", "image_file.png")``` As above, but the result is assigned to 'found_word' variable.

```print(PythonOCR.verify_word("Python", "image_file.png"))``` As above, but the result is printed to console.

```PythonOCR.verify_word("Python", "./project_files/image_file.png")``` Returns the result regarding the 'image_file.png' located in 'project_files' folder in the current project directory.

```PythonOCR.verify_word("Python", "C:/project_folder/project_files/image_file.png")``` As above, but the file path is provided as an absolute path.

#### Usage in Robot

**Importing**

Import PythonOCR module from QAutoLibrary to the robot:

```
*** Settings ***
Library  |  QAutoLibrary.PythonOCR
```

**Usage**

PythonOCR functions can then be used as keywords:

```
*** Test Cases ***
<Test Case>
  |  <Function Keyword>  |  ${<argument1>}  |  ${argument2}  |  ...
```

#### Examples (Robot)

**click_word()**

```Click Word  |  Python``` Searches for word 'Python' on screen and if a single instance is found, clicks its location. Screenshot is not saved.

```Click Word  |  Python  |  screenshot.png``` As above, but the screenshot is saved to the current project directory as 'screenshot.png'.

```Click Word  |  Python  |  ./screenshots/screenshot.png``` As above, but the screenshot is saved to 'screenshots' folder in the current project directory.

```Click Word  |  Python  |  index=0``` Searches for the word on screen and if finds multiple instances of the word, clicks the first found instance (at index position 0 (zero)). Screenshot is not saved.

**find_words()**

```Find Words  |  Python  |  image_file.png``` Returns all found instances of the word 'Python' in 'image_file.png'.

```@{results_list} =  |  Find Words  |  Python  |  image_file.png``` As above, but the results are assigned to 'results_list' variable.

```Find Words  |  Python  |  ./project_files/image_file.png``` Returns all found instances of the word in 'image_file.png' located in 'project_files' folder in the current project directory.

```Find Words  |  Python  |  pdf_file.pdf``` Returns all found instances of the word 'Python' in 'pdf_file.pdf'. Images converted from the PDF file are saved to the current project directory.

```Find Words  |  Python  |  pdf_file.pdf  |  ./output``` As above, but images are saved to 'output' folder in the current project directory.

**find_coordinates()**

```Find Coordinates  |  Python  |  image_file.png``` Returns all instances of the word 'Python' and their coordinates in 'image_file.png'.

```@{results_list} =  |  Find Coordinates  |  Python  |  image_file.png``` As above, but the results are assigned to 'results_list' variable.

```Find Coordinates  |  Python  |  ./project_files/image_file.png``` Returns all found instances of the word and their coordinates in 'image_file.png' located in 'project_files' folder in the current project directory.

```Find Coordinates  |  Python  |  pdf_file.pdf``` Returns all found instances of the word 'Python' and their coordinates in 'pdf_file.pdf'. Images converted from the PDF file are saved to the current project directory.

```Find Coordinates  |  Python  |  pdf_file.pdf  |  ./output``` As above, but images are saved to 'output' folder in the current project directory.

**verify_word()**

```Verify Word  |  Python  |  image_file.png``` Returns True or False if finds any instances of the word 'Python' in 'image_file.png'.

```${found_word} =  |  Verify Word  |  Python  |  image_file.png``` As above, but the result is assigned to 'found_word' variable.
sult is printed to console.

```Verify Word  |  Python  |  ./project_files/image_file.png``` Returns the result regarding the 'image_file.png' located in 'project_files' folder in the current project directory.
