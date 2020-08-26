# QAutoLibrary Instructions

QAutoLibrary Instructions on how to install prerequisites of the different modules, how to install QAutoLibrary and guide on how to use the different modules on your projects.

## Prerequisites

QAutoLibrary requires Python 3.7 in order to be used.

Additionally, modules of the QAutoLibrary may use external libraries, which have to be installed. See sections [QAutoRobot Prerequisites](#qautorobot-prerequisites) and [PythonOCR Prerequisites](#pythonocr-prerequisites) for further details.

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

#### poppler (Windows)

**Windows:**

Download the latest poppler release (.zip file) from: https://github.com/oschwartz10612/poppler-windows/releases/

More information at: https://github.com/oschwartz10612/poppler-windows

1. Unzip the poppler release file.

2. Add the poppler folder ('poppler-xx') to your Program Files. (For example, to: ```C:\Program Files (x86)\Poppler\ ```.)

3. Include the 'poppler-xx\bin' folder as a SYSTEM PATH environment variable. (For example, add: ```C:\Program Files (x86)\Poppler\poppler-0.90.1\bin``` to PATH.)

**Linux:**

Work in progress...

#### pdf2image

**NOTE:** Install poppler before installing pdf2image!

Install pdf2image using pip:

```
pip install pdf2image
```

More information at: https://pypi.org/project/pdf2image/ and https://github.com/Belval/pdf2image

#### Tesseract OCR (Windows)

**Windows:**

Install Google Tesseract OCR and include Finnish. **Add Tesseract-OCR to PATH.**

Download Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki

More information at: https://github.com/tesseract-ocr/tessdoc

**Linux:**

Work in progress...

```
sudo apt install poppler-utils tesseract-ocr
```

#### pytesseract (Windows)

**NOTE:** Install Tesseract OCR before installing pytesseract!

**Windows:**

Install pytesseract using pip:

```
pip install pytesseract
```

More information at: https://pypi.org/project/pytesseract/

**Linux:**

Work in progress...

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

### QAutoRobot Usage

**Importing**

**Usage**

**Examples**

#### Importing Custom Libraries

### PythonOCR Usage

PythonOCR main functions:

```click_word()``` takes a screenshot, searches for a word on screen and clicks the location of a found instance.

```find_words()``` searches for all instances of a specified word in an image or PDF file, and returns results.

```find_coordinates()``` searches for all instances of a specified word and their coordinates in an image or PDF file, and returns results.

```verify_word()``` searches for any instance of a specified word in an image file, and returns True or False whether an instance was found.

PythonOCR functions can be used in both Python code or robot.

#### Usage in Python code

**Importing**

To import PythonOCR to your Python code:

```
from QAutoLibrary import PythonOCR
```

**Usage**

PythonOCR functions can be then used as follows:

```
PythonOCR.<function>()
```

Parameters of each of the main functions are as follows:

```
PythonOCR.click_word(word, save_screenshot_as, index)
```

```
PythonOCR.find_words(word, file_path, output_path)
```

```
PythonOCR.find_coordinates(word, file_path, output_path)
```

```
PythonOCR.verify_word(word, image_path)
```

#### Examples (Python)

**click_word()**

```PythonOCR.click_word("Python")``` Searches for word 'Python' on screen and if a single instance is found, clicks its location. Screenshot is not saved.

```PythonOCR.click_word("Python", "screenshot.png")``` As above, but the screenshot is saved to the current project directory as 'screenshot.png'.

```PythonOCR.click_word("Python", "./screenshots/screenshot.png")``` As above, but the screenshot is saved to folder 'screenshots' in the current project directory.

```PythonOCR.click_word("Python", "C:/project_folder/screenshots/screenshot.png")``` As above, but the screenshot is saved to the specific directory.

```PythonOCR.click_word("Python", index=0)``` Searches for the word on screen and if finds multiple instances of the word, clicks the first found instance (at index position 0 (zero)). Screenshot is not saved.

**find_words()**

**find_coordinates()**

**verify_word()**

#### Usage in Robot

**Importing**

**Usage**

#### Examples (Robot)