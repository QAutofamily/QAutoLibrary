"""
#    QAutomate Ltd 2018. All rights reserved.
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
import os
from xml.etree import cElementTree as ET
from collections import OrderedDict

from QAutoLibrary.extension.util.GlobalUtils import GlobalUtils


class XmlScreenshotParser(object):
    """

    """

    def __init__(self):
        self.xml_root = None
        self.tree = None
        self._set_xml_root()

    def _set_xml_root(self):
        """
        Set xml Element tree root

        :return: None
        """
        self._screenshot_folder = os.path.join(os.getcwd(), GlobalUtils.SCREENSHOTS_FOLDER_NAME)
        self._screenshot_file = os.path.join(self._screenshot_folder, GlobalUtils.SCREENSHOTS_XML_FILE)
        if os.path.isfile(self._screenshot_file):
            self.tree = ET.parse(self._screenshot_file)
            self.xml_root = self.tree.getroot()
        else:
            self.xml_root = None
            self.tree = None

    def _screenshot_xml_to_dict(self):
        """
        Transforms screenshot xml to dict

        :return: Dictionary of screenshot files or empty dict if no screenshots found
        """
        screenshot_dict = OrderedDict()
        if not self.xml_root:
            return screenshot_dict

        for screenshot in self.xml_root:
            filename = screenshot.attrib['name']
            area = bool(screenshot.find('area').text.lower() == 'true')
            for browser in screenshot.iter('browser'):
                browser_name = browser.attrib['name']
                for screen in browser.iter('screen'):
                    screenres = screen.attrib['res']
                    # check if screenshot exist
                    screenshot_file_name = filename + "_" + browser_name + "-" + screenres
                    if os.path.isfile(os.path.join(self._screenshot_folder, screenshot_file_name + ".png")):
                        similarity = int(screen.find('similarity').text)
                        screenshot_dict.update({screenshot_file_name:{'area': area, 'similarity': similarity,
                                                                      'browser': browser_name, 'res': screenres}})
                        if area:
                            x = int(screen.find('x').text)
                            y = int(screen.find('y').text)
                            w = int(screen.find('w').text)
                            h = int(screen.find('h').text)
                            screenshot_dict[screenshot_file_name].update({'x': x, 'y': y, 'w': w, 'h': h})

        return screenshot_dict

    def _get_screenshot_metadata(self, name, browser, screenres, meta_node=None):
        """
        Return screenshot file metadata

        :param name: screenshot file name in xml as a String
        :param browser: screenshot file browser name in xml as a String
        :param screenres: screenshot file resolution in xml as a String
        :param meta_node:
        :return: Dictionary of screenshot file metadata or None if metadata not found
        """
        metadata = {}
        if not self.xml_root:
            return None
        # have we already found meta node
        if not meta_node:
            meta_node = self._find_metadata_node(name, browser, screenres)
        if meta_node:
            area = bool(self.xml_root.find("screenshot[@name='%s']/area" % name).text.lower() == 'true')
            if area:
                x = int(meta_node.find('x').text)
                y = int(meta_node.find('y').text)
                w = int(meta_node.find('w').text)
                h = int(meta_node.find('h').text)
                metadata.update({'x': x, 'y': y, 'w': w, 'h': h})
            similarity = int(meta_node.find('similarity').text)
            metadata.update({'area': area, 'similarity': similarity})
            return metadata
        return None

    def _find_metadata_node(self, name, browser, screenres):
        """


        :param name:
        :param browser:
        :param screenres:
        :return:
        """
        return self.xml_root.find("screenshot[@name='%s']/browser[@name='%s']/screen[@res='%s']" % (name, browser, screenres))

    def _find_screenshot_name_node(self, name):
        """


        :param name:
        :return:
        """
        return self.xml_root.find("screenshot[@name='%s']" % name)

    def _find_browser_node(self, name, browser):
        """


        :param name:
        :param browser:
        :return:
        """
        return self.xml_root.find("screenshot[@name='%s']/browser[@name='%s']" % (name, browser))

    def _find_best_match(self, name, browser, screenres):
        """


        :param name:
        :param browser:
        :param screenres:
        :return:
        """
        current_file_name = name + "_" + browser + "-" + screenres + ".png"
        metadata = {}
        screenshot_node = self._find_screenshot_name_node(name)
        if screenshot_node:
            browsers = screenshot_node.findall('browser')
            xml_browser = (len(browsers) == 1 and browsers[0].attrib['name'] or '')
            if xml_browser != '' and xml_browser != browser:
                meta_node = self._find_metadata_node(name, xml_browser, screenres)
                if meta_node:
                    metadata = self._get_screenshot_metadata(name, xml_browser, screenres, meta_node)
                    metadata.update({'browser': xml_browser})
                    new_file_name = name + "_" + xml_browser + "-" + screenres + ".png"
                    if os.path.isfile(os.path.join(self._screenshot_folder, new_file_name)):
                        # screenshot file found with different browser
                        return (True, metadata, new_file_name, '')
                    else:
                        # screenshot metadata found but file not exists
                        return (False, False, current_file_name, "Reference screenshot file not found. File or meta data is missing.")
                else:
                    # different browser found, but cannot find screenshot with same resolution
                    return (False, False, current_file_name, 'Cannot find reference screenshot with current resolution (%s), even with different browser. File or meta data is missing.' % screenres)
            else:
                if len(browsers) == 1:
                    # found browser, but no screenshot for used resolution
                    return (False, False, current_file_name, "Reference screenshot file not found for current screen resolution (%s). File or meta data is missing." % screenres)
                else:
                    # found many different browsers, we don't know what to select
                    return (False, False, current_file_name, "Reference screenshot file not found for current browser (%s) and there is too many browser to select some other. File or meta data is missing." % browser)
        else:
            # screenshot file not found
            return (False, False, current_file_name, "Reference screenshot file not found. File or meta data is missing.")

    def _set_similarity_level(self, name, browser, screenres, similarity):
        """
        Sets screenshot similarity level

        :param name: screenshot file name in xml as a String
        :param browser: screenshot file browser name in xml as a String
        :param screenres: screenshot file resolution in xml as a String
        :param similarity: new value for screenshot similarity level in xml as a String
        :return: True if change success otherwise False
        """
        if not self.xml_root:
            return False
        meta_node = self._find_metadata_node(name, browser, screenres)
        if meta_node:
            meta_node.find('similarity').text = str(similarity)
            self.tree.write(self._screenshot_file, encoding="utf-8")
            return True

        return False

    def _set_coordinates(self, name, browser, screenres, x, y, w, h):
        """


        :param name:
        :param browser:
        :param screenres:
        :param x:
        :param y:
        :param w:
        :param h:
        :return:
        """
        if not self.xml_root:
            return False
        meta_node = self._find_metadata_node(name, browser, screenres)
        if meta_node:
            meta_node.find('x').text = str(x)
            meta_node.find('y').text = str(y)
            meta_node.find('w').text = str(w)
            meta_node.find('h').text = str(h)
            self.tree.write(self._screenshot_file, encoding="utf-8")
            return True

        return False

    def _set_screenshot_filename(self, old_name, new_name):
        """

        :param old_name:
        :param new_name:
        :return:
        """
        if not self.xml_root:
            return False
        screenshot_node = self._find_screenshot_name_node(old_name)
        if screenshot_node:
            screenshot_node.set('name', new_name)
            self.tree.write(self._screenshot_file, encoding="utf-8")
            return True

        return False

    def _delete_element(self, name, browser, screenres):
        """
        Delete element from xml

        :param name: screenshot file name in xml as a String
        :param browser: screenshot file browser name in xml as a String
        :param screenres: screenshot file resolution in xml as a String
        :return: True if remove success otherwise False
        """
        if not self.xml_root:
            return False
        screenshot_node = self._find_screenshot_name_node(name)

        if screenshot_node:

            # if only one browser element
            if len(screenshot_node.findall('browser')) == 1:
                browser_node = self._find_browser_node(name, browser)

                #if only one screen node
                if len(browser_node.findall('screen')) == 1:
                    self.xml_root.remove(screenshot_node)
                #if many screen nodes
                else:
                    # Node to screen element
                    meta_data_node = self._find_metadata_node(name, browser, screenres)
                    browser_node.remove(meta_data_node)

            # else many browsers
            else:
                browser_node = self._find_browser_node(name, browser)

                #if only one screen node
                if len(browser_node.findall('screen')) == 1:
                    screenshot_node.remove(browser_node)
                #if many screen nodes
                else:
                    #Node to screen element
                    meta_data_node = self._find_metadata_node(name, browser, screenres)
                    browser_node.remove(meta_data_node)

            self.tree.write(self._screenshot_file, encoding="utf-8")
            return True

        return False

    def _create_new_screenshot(self, name, browser, screenres, area, similarity, x=False, y=False, w=False, h=False):
        """


        :param name:
        :param browser:
        :param screenres:
        :param area:
        :param similarity:
        :param x:
        :param y:
        :param w:
        :param h:
        :return:
        """
        if not self.xml_root:
            # start creating new xml
            self._create_new_xml()

        meta_node = self._find_metadata_node(name, browser, screenres)
        if meta_node :
            # file exists in xml, update content
            if bool(self.xml_root.find("screenshot[@name='%s']/area" % name).text.lower() == 'true') and not area:
                print("Cannot add element screenshot under area screenshot!")
                return False
            elif bool(self.xml_root.find("screenshot[@name='%s']/area" % name).text.lower() == 'false') and area:
                print("Cannot add area screenshot under element screenshot!")
                return False
            self._set_similarity_level(name, browser, screenres, similarity)
            if area:
                self._set_coordinates(name, browser, screenres, x, y, w, h)
            return True
        else:
            filename_node = self._find_screenshot_name_node(name)
            if not filename_node:
                filename_node = ET.SubElement(self.xml_root, 'screenshot', {'name': name})
                ET.SubElement(filename_node, 'area').text = str(area).lower()
                browser_node = ET.SubElement(filename_node, 'browser', {'name': browser})
                screen_node = ET.SubElement(browser_node, 'screen', {'res': screenres})
                self._add_new_metadata(screen_node, area, similarity, x, y, w, h)
                self._indent(self.xml_root)
                self.tree.write(self._screenshot_file, encoding="utf-8")
                return True
            browser_node = self._find_browser_node(name, browser)
            if not browser_node:
                browser_node = ET.SubElement(filename_node, 'browser', {'name': browser})
                screen_node = ET.SubElement(browser_node, 'screen', {'res': screenres})
                self._add_new_metadata(screen_node, area, similarity, x, y, w, h)
                self._indent(self.xml_root)
                self.tree.write(self._screenshot_file, encoding="utf-8")
                return True

            screen_node = ET.SubElement(browser_node, 'screen', {'res': screenres})
            self._add_new_metadata(screen_node, area, similarity, x, y, w, h)
            self._indent(self.xml_root)
            self.tree.write(self._screenshot_file, encoding="utf-8")
            return True

    def _add_new_metadata(self, element, area, similarity, x, y, w, h):
        """


        :param element:
        :param area:
        :param similarity:
        :param x:
        :param y:
        :param w:
        :param h:
        :return:
        """
        ET.SubElement(element, 'similarity').text = similarity
        if area:
            ET.SubElement(element, 'x').text = x
            ET.SubElement(element, 'y').text = y
            ET.SubElement(element, 'w').text = w
            ET.SubElement(element, 'h').text = h

    def _create_new_xml(self, save_to_file=False):
        """

        :param save_to_file:
        :return:
        """
        element = ET.Element('screenshots')
        self.tree = ET.ElementTree(element)
        self.xml_root = self.tree.getroot()
        if save_to_file:
            self.tree.write(self._screenshot_file, encoding="utf-8")

    def _indent(self, elem, level=0):
        """


        :param elem:
        :param level:
        :return:
        """
        i = "\n" + level * "    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
