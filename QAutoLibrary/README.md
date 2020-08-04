# QAutoLibrary Modules

Description.

## PythonOCR

PythonOCR contains functions for finding and locating words on screen, in image files or PDF files using OCR (Optical Character Recognition).

### Prerequisites

PythonOCR utilizes the following modules:

**pyautogui** for taking screenshots and mouse controls.

**poppler** to read, render and modify PDF files.

**pdf2image** to convert PDF files to image files. pdf2image is a wrapper around poppler.

**pytesseract** to recognize text in image files. pytesseract requires **Google Tesseract OCR** in order to function.

#### Python

Install Python (3.7+) and include pip with the installation. **Add Python to PATH.**

Download Python: https://www.python.org/downloads/

#### pyautogui

Install pyautogui using pip:

```
pip install pyautogui
```

More information at: https://pypi.org/project/PyAutoGUI/

#### poppler

Download the latest poppler release (.zip file) from: https://github.com/oschwartz10612/poppler-windows/releases/

More information at: https://github.com/oschwartz10612/poppler-windows

1. Unzip the poppler release file.

2. Add the poppler folder ('poppler-xx') to your Program Files. (For example, to: ```C:\Program Files (x86)\Poppler\ ```.)

3. Include the 'poppler-xx\bin' folder as a SYSTEM PATH environment variable. (For example, add: ```C:\Program Files (x86)\Poppler\poppler-0.90.1\bin``` to PATH.)

#### pdf2image

**NOTE:** Install poppler before installing pdf2image!

Install pdf2image using pip:

```
pip install pdf2image
```

More information at: https://pypi.org/project/pdf2image/ and https://github.com/Belval/pdf2image

#### Tesseract OCR

Install Google Tesseract OCR and include Finnish. **Add Tesseract-OCR to PATH.**

Download Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki

More information at: https://github.com/tesseract-ocr/tessdoc

#### pytesseract

**NOTE:** Install Tesseract OCR before installing pytesseract!

Install pytesseract using pip:

```
pip install pytesseract
```

More information at: https://pypi.org/project/pytesseract/

### Installing

Install QAutoLibrary containing PythonOCR.py module.

QAutoLibrary download and installation instructions: https://github.com/QAutofamily/QAutoLibrary

### Usage

Import PythonOCR module from QAutoLibrary to your code:

```
from QAutoLibrary import PythonOCR
```

PythonOCR functions can then be used as follows:

```
PythonOCR.click_word(<word>)

PythonOCR.find_words(<word>, <file path>)

PythonOCR.find_coordinates(<word>, <file path>)

PythonOCR.verify_word(<word>, <file path>)
```
