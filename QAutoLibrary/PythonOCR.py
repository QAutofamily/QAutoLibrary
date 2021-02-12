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


import warnings
import pyautogui
import pdf2image
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import pytesseract
from pytesseract import Output

"""
#  PythonOCR contains functions for finding and locating words on screen, in image files or PDF files using OCR (Optical
#  Character Recognition).
#
#  PythonOCR documentation is contained in this file, README.md and in QAutoLibrary.
#
#  CONTENTS
#  Internal functions:
#      _get_word_coordinate_from_data()
#      _is_valid_image()
#      _is_valid_pdf()
#      _validate_file()
#      _click_coordinates()
#  Main functions:
#      get_file_data()
#      click_word()
#      find_words()
#      find_coordinates()
#      verify_word()
#  Exceptions:
#      PythonOCRError
#      InvalidFileTypeError
#      InvalidImageTypeError
"""


# INTERNAL FUNCTIONS:
def _get_word_coordinates_from_data(word, image_data, page_number=1):
    """
    **Retrieves the data of found instances of a specified word and their coordinates from given data.**
    Internal function.

    :param word: Required. The specified word.
    :param image_data: Required. Given image data, such as data retrieved by pytesseract.
                       Must be a dictionary of lists.
    :param page_number: Optional. Page number to be included with the returned data. By default, 1.

    :return: Found instances of the word and their coordinates in image.
             A list of dictionaries, each dictionary consisting of: {"text": found text, "left": left coordinates (X),
             "top": top coordinates (Y), "width": text width, "height": text height, "page": page number}.
    """
    results = []
    # 'image_data' is a dictionary of lists.
    # Accessing specific data list in dictionary:  image_data[<dictionary_key>]
    # Accessing specific data in a list, by index: image_data[<dictionary_key>][<index>]
    number_of_items = len(image_data["text"])
    for index in range(number_of_items):
        text = image_data["text"][index]

        if word in text:
            new_item = {
                "text": text,
                "left": image_data["left"][index],
                "top": image_data["top"][index],
                "width": image_data["width"][index],
                "height": image_data["height"][index],
                "page": page_number
            }
            results.append(new_item)

    return results


def _is_valid_image(file_path):
    """
    **Checks if given file is .jpg, .jpeg or .png file.** Internal function.
    """
    if file_path.endswith(".jpg") or file_path.endswith(".jpeg") or file_path.endswith(".png"):
        return True
    else:
        return False


def _is_valid_pdf(file_path):
    """
    **Checks if given file is .pdf file.** Internal function.
    """
    if file_path.endswith(".pdf"):
        return True
    else:
        return False


def _validate_file(file_path, output_path):
    """
    **Verifies that a given file is a valid image file or PDF file.** Converts a PDF file to images:
    each page into its own image file. Returns image(s). Internal function.

    :param file_path: Required. Image or PDF file path.
    :param output_path: Output directory for image files converted from the PDF file. Not required if processing image files.
                        By default, current project directory.

    :return: A list of image files.
    """
    image_list = []
    if _is_valid_image(file_path):
        image_list.append(file_path)
    elif _is_valid_pdf(file_path):
        image_list = pdf2image.convert_from_path(file_path, fmt="jpeg", output_folder=output_path)
    else:
        raise InvalidFileTypeError("Could not recognize '{file}' as a .jpg, .jpeg, .png nor .pdf file!"
                                   .format(file=file_path))
    return image_list


def _click_coordinates(data_list, element_index=0):
    """
    **Moves mouse cursor on screen to coordinates retrieved from data, and clicks the location.** If data contains
    multiple elements and their coordinates, specific coordinates can be chosen by index. Internal function.

    :param data_list: Required. Data as a list of dictionaries. Dictionaries must consist of: {"text": found text,
                      "left": left coordinates (X), "top": top coordinates (Y), "width": text width, "height": text
                      height, "page": page number (Optional)}
    :type data_list: list
    :param element_index: Optional. Index of the data element. By default, 0 (zero; first element).
    :type element_index: int
    """
    # Element in 'data_list' consists of: (text, left coordinates (X), top coordinates (Y), text width, text height)
    x_coordinate = data_list[element_index]["left"] + data_list[element_index]["width"] / 2
    y_coordinate = data_list[element_index]["top"] + data_list[element_index]["height"] / 2
    pyautogui.moveTo(x_coordinate, y_coordinate, duration=0)
    pyautogui.click()


# MAIN FUNCTIONS:
def get_file_data(file_path, output_path="./"):
    """
    **Returns OCR-data found in the specified file.** Able to process '.jpg',
    '.jpeg', '.png', and '.pdf' files.

    :param file_path: Required. Image or PDF file path. Can be absolute or relative to the current project directory.
    :type file_path: str
    :param output_path: Optional. Output directory for image files converted from the PDF file. Provided directory path MUST pre-exist!
                        By default, current project directory.
    :type output_path: str

    :return: OCR-data found by pytesseract. List of images, if the given file was '.pdf' and contained multiple pages.
             Within this list, there are dictionaries which contain lists for each found text instance.
    :rtype: list

    -------------
    :Example:
        | *Returns the found OCR-data from file ('image_file.png').*
        | ``get_file_data("Python", "image_file.png")``
        | *Returns the found OCR-data from file located in folder
          ('project_files') in the project directory. Converted images are saved to folder ('output_folder') in the
          project directory.*
        | ``get_file_data("./project_files/pdf_file.pdf", "./output_folder")``
        | *Data usage:*
        | ``data = pythonocr.get_file_data(...)``
        | ``data[<image>][<dictionary>][<index>]``
        | *Access first image's second recognized text's 'text'-data.*
        | ``data[0]["text"][1]``
        | *Access third image's first recognized text's X-coordinate data ('left').*
        | ``data[2]["left"][0]``
    """
    image_list = _validate_file(file_path, output_path)
    results = []

    for image in image_list:
        image_data = pytesseract.image_to_data(image, lang="eng+fin", output_type=Output.DICT)

        results.append(image_data)
    return results


def click_word(word, save_screenshot_as="", index=-1):
    """
    **Searches for a specified word on screen and clicks the word's location.** Takes a screenshot using pyautogui
    and recognizes text in it with pytesseract. Optionally, can save screenshot as a specified image file.

    If able to find a single instance of the word, retrieves its coordinates and clicks the location with mouse,
    using pyautogui. If multiple instances of the word are found, a specific one can be selected to be clicked by
    its index.
    By default, does not click any found word, if multiple instances are found.

    :param word: Required. The specified word. Upper and lowercase sensitive!
    :type word: str
    :param save_screenshot_as: Optional. File name for saved screenshot.
                               MUST include valid file type ending, such as '.jpg' or '.png'. Additionally, may include
                               absolute path or relative directory path to current project folder, where the screenshot
                               is saved at. Provided directory path MUST pre-exist!
                               By default, or if empty, screenshot is not saved.
    :type save_screenshot_as: str
    :param index: Optional. Index of a specific found word. First found instance of the word is at position 0 (zero).
                  By default, or if less than 0, no instance will be chosen and none of the multiple found words will be clicked.
    :type index: int

    -------------
    :Example:
        | *Searches and clicks the word ('Python') on screen.*
        | ``click_word("Python")``
        | *Searches and clicks the word on screen. Saves screenshot as a file ('screenshot.png') to folder
          ('screenshots') in the current project directory.*
        | ``click_word("Python", "./screenshots/screenshot.png")``
        | *Searches and clicks the instance (0; zero) of the word on screen.*
        | ``click_word("Python", index=0)``
        | *In QAutoRobot:*
        | ``Click Word  |  ${word}  |  ${screenshot_file}  |  ${index}``
        | *Searches and clicks the word ('Python') on screen.*
        | ``Click Word  |  Python``
        | *Searches and clicks the word on screen. Saves screenshot as a file ('screenshot.png') to folder ('images')
          in the current robot directory.*
        | ``Click Word  |  Python  |  ./images/screenshot.png``
        | *Searches and clicks the instance (0; zero) of the word on screen.*
        | ``Click Word  |  Python  |  index=0``
    """
    screenshot = pyautogui.screenshot()
    if save_screenshot_as:
        # PyAutoGUI uses Pillow (or PIL) module for image-related features, such as saving an image.
        screenshot.save(save_screenshot_as)

    image_data = pytesseract.image_to_data(screenshot, lang="eng+fin", output_type=Output.DICT)

    results = _get_word_coordinates_from_data(word, image_data)

    if len(results) == 1:
        _click_coordinates(results)

    elif len(results) > 1:
        if index > -1:
            _click_coordinates(results, index)

        warning_message = "pythonocr.click_word(): Found multiple instances ({amount}) of the word '{param}' " \
                          "on screen!".format(amount=len(results), param=word)
        warnings.warn(warning_message, RuntimeWarning)

    else:
        raise NoInstancesFoundError("pythonocr.click_word(): Found no instances of the word '{param}' on screen."
                                    .format(param=word))


def find_words(word, file_path, output_path="./"):
    """
    **Searches for all instances of a specified word in image or PDF file.**
    Converts a PDF file to image(s), and recognizes the text in image(s) with pytesseract. Able to process '.jpg',
    '.jpeg', '.png', and '.pdf' files.

    :param word: Required. The specified word. Upper and lowercase sensitive!
    :type word: str
    :param file_path: Required. Image or PDF file path. Can be absolute or relative to the current project directory.
    :type file_path: str
    :param output_path: Output directory for image files converted from the PDF file. Not required if processing
                        image files. Provided directory path MUST pre-exist!
                        By default, current project directory.
    :type output_path: str

    :return: A list of found instances of the specified word as a list of dictionaries. Each dictionary consisting of:
             {"text": found text, "page": page number}.
    :rtype: list

    -------------
    :Example:
        | *Returns the found instances of the word ('Python') from file ('image_file.png').*
        | ``find_words("Python", "image_file.png")``
        | *Returns the found instances of the word from file, located in folder ('project_files') in the project
          directory. Converted images are saved to folder ('output_folder') in the project directory.*
        | ``find_words("Python", "./project_files/pdf_file.pdf", "./output_folder")``
        | *In QAutoRobot:*
        | ``Find Words  |  ${word}  |  ${file_path}  |  ${output_path}``
        | *Found instances of the word ('Python') in file are assigned to list ('result_list'). The file
          ('screenshot.png') is located in folder ('images') in the current robot directory.*
        | ``@{results_list} =  |  Find Words  |  Python  |  ./images/screenshot.png``
        | *Found instances of the word in file are assigned to the list variable. The image files converted from
          file ('pdf_file.pdf') are saved to folder ('images') in the current robot directory.*
        | ``@{results_list} =  |  Find Words  |  Python  |  ./resource_files/pdf_file.pdf  |  ./images/``
    """
    image_list = _validate_file(file_path, output_path)
    results = []
    page_number = 1

    for image in image_list:
        text_in_image = pytesseract.image_to_string(image, lang="eng+fin")

        # In order to find multiple instances of the word in text,
        # "if word in text_in_image:" is not sufficient.
        text_array = text_in_image.splitlines()
        for line in text_array:
            if word in line:
                new_item = {
                    "text": line,
                    "page": page_number
                }
                results.append(new_item)

        page_number += 1
    return results


def find_coordinates(word, file_path, output_path="./"):
    """
    **Searches for all instances of a specified word and their coordinates in image or PDF file.**
    Converts a PDF file to image(s), and recognizes the text in image(s) with pytesseract. Able to process '.jpg',
    '.jpeg', '.png', and '.pdf' files.

    :param word: Required. The specified word. Upper and lowercase sensitive!
    :type word: str
    :param file_path: Required. Image or PDF file path. Can be absolute or relative to the current project directory.
    :type file_path: str
    :param output_path: Optional. Output directory for image files converted from the PDF file. Provided directory
                        path MUST pre-exist!
                        By default, current project directory.
    :type output_path: str

    :return: Found instances of the word and their coordinates in image as a list of dictionaries. Each dictionary
             consisting of: {"text": found text, "left": left coordinates (X), "top": top coordinates (Y),
             "width": text width, "height": text height, "page": page number}.
    :rtype: list

    -------------
    :Example:
        | *Returns the found instances of the word ('Python') and their coordinates from file ('image_file.png').*
        | ``find_coordinates("Python", "image_file.png")``
        | *Returns the found instances of the word and their coordinates from file located in folder
          ('project_files') in the project directory. Converted images are saved to folder ('output_folder') in the
          project directory.*
        | ``find_coordinates("Python", "./project_files/pdf_file.pdf", "./output_folder")``
        | *In QAutoRobot:*
        | ``Find Coordinates  |  ${word}  |  ${file_path}  |  ${output_path}``
        | *Found instances of the word ('Python') and their coordinates in file are assigned to list ('result_list').
          The file ('screenshot.png') is located in folder ('images') in the current robot directory.*
        | ``@{results_list} =  |  Find Coordinates  |  Python  |  ./images/screenshot.png``
        | *Found instances of the word and their coordinates in file are assigned to the list variable. The image
          files converted from file ('pdf_file.pdf') are saved to folder ('images') in the current robot directory.*
        | ``@{results_list} =  |  Find Coordinates  |  Python  |  ./resource_files/pdf_file.pdf  |  ./images/``
    """
    image_list = _validate_file(file_path, output_path)
    results = []
    page_number = 1

    for image in image_list:
        image_data = pytesseract.image_to_data(image, lang="eng+fin", output_type=Output.DICT)

        results.extend(_get_word_coordinates_from_data(word, image_data, page_number))
        page_number += 1
    return results


def verify_word(word, image_path):
    """
    **Returns whether or not can find any instance of a specified word in image file.**
    Recognizes the text in image with pytesseract. Able to process '.jpg', '.jpeg' and '.png' files.

    :param word: Required. The specified word. Upper and lowercase sensitive!
    :type word: str
    :param image_path: Required. Image file path. Can be absolute or relative to the current project directory.
    :type image_path: str

    :return: Returns True if found at least one instance of the specified word in image, False if none.
    :rtype: bool

    -------------
    :Example:
        | *Returns True or False if the word ('Python') was found from file ('image_file.png').*
        | ``verify_word("Python", "image_file.png")``
        | *Returns True or False if the word was found from file located in folder ('project_files') in the
          project directory.*
        | ``verify_word("Python", "./project_files/image_file.png")``
        | *In QAutoRobot:*
        | ``Verify Word  |  ${word}  |  ${file_path}``
        | Assigns True or False to variable ('found_word') if the word was found from file ('screenshot.png') located
          in folder ('images') in the current robot directory.
        | ``${found_word} =  |  Verify Word  |  Python  |  ./images/screenshot.png``
    """
    if not _is_valid_image(image_path):
        raise InvalidImageTypeError("Could not recognize '{file}' as a .jpg, .jpeg nor .png image file!"
                                    .format(file=image_path))

    text_in_image = pytesseract.image_to_string(image_path, lang="eng+fin")
    if word in text_in_image:
        return True
    else:
        return False


# EXCEPTIONS:
class PythonOCRError(Exception):
    """Base error class for PythonOCR errors."""
    def __init__(self, message):
        super().__init__(message)


class InvalidFileTypeError(PythonOCRError):
    """Error raised when given file is not a valid image nor PDF file."""
    pass


class InvalidImageTypeError(InvalidFileTypeError):
    """Error raised when given file is not a valid image file."""
    pass

class NoInstancesFoundError(PythonOCRError):
    """Error raised when no instances of the word are found."""
    pass
