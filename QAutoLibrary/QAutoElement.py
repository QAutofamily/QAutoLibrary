from selenium.webdriver.common.by import By


class QAutoElement(object):
    """
    **Class that contains information about web element
    """

    def __init__(self, locator, **kwargs):
        """
        :param locator: Tuple representing element: (By, 'value')
        :param kwargs: Additional parameter containing element information
        -------------
        :Example:
            | ``MY_ELEMENT = QAutoElement((By.LINK_TEXT, u'Trial'), tag='DIV', size=(100, 200))``
            | Elements inside frame must refer to frame element
            | ``MY_ELEMENT_IN_FRAME = QAutoElement((By.LINK_TEXT, u'Trial'), size=(100, 200), frame=MY_ELEMENT)``

        """
        self.by = locator[0]
        self.value = locator[1]
        self.locator = locator
        self.metadata = kwargs
        for attr_name in kwargs:
            setattr(self, attr_name, kwargs[attr_name])

    def __iter__(self):
        for i in self.metadata:
            yield i

    def __getitem__(self, index):
        """
        Provides a way to access attributes by indexing

        :param index: Integer 0 or 1 or String set with kwargs
        :return: Queried attribute
                -------------
        :Example:
            | ``MY_ELEMENT = QAutoElement((By.LINK_TEXT, u'Trial'), tag='DIV', size=(100, 200))``
            | tag = MY_ELEMENT["tag"]
            | locator_by = MY_ELEMENT[0]

        """
        if type(index) == str:
            return self.metadata[index]
        elif index == 0:
            return self.by
        elif index == 1:
            return self.value
        else:
            raise IndexError(index)

    def __setitem__(self, key, value):
        if key == 0:
            self.by = value
        elif key == 1:
            self.value = value
        else:
            raise IndexError

    def get_by_locator_string(self):
        """
        Converts supported locators e.g 'xpath' --> By.XPATH or returns same value if format is already correct

        :return: converted locator string
        """
        if self.by == By.ID or self.by == "By.ID":
            return "By.ID"
        elif self.by == By.LINK_TEXT or self.by == "By.LINK_TEXT":
            return "By.LINK_TEXT"
        elif self.by == By.CLASS_NAME or self.by == "By.CLASS_NAME":
            return "By.CLASS_NAME"
        elif self.by == By.TAG_NAME or self.by == "By.TAG_NAME":
            return "By.TAG_NAME"
        elif self.by == By.CSS_SELECTOR or self.by == "By.CSS_SELECTOR":
            return "By.CSS_SELECTOR"
        elif self.by == By.XPATH or self.by == "By.XPATH":
            return "By.XPATH"

    def get_element_string_for_saving(self):
        """
        Converts QAutoElement to string format for saving elements to file

        :return: String e.g QAutoElement((By.LINK_TEXT, u'Trial'), tag='DIV', size=(100, 200))``
        """
        priority_list = ["tag", "coordinates", "size", "frame"]
        attributes = [value for key, value in self.__dict__.items() if key == "metadata"][0]
        if len(attributes) > 0:
            # get list of attributes ordered by priority list
            priority_attributes = []

            for x in priority_list:
                for key, value in attributes.items():

                    if key == x:
                        if type(value) == str:
                            if key == "frame":
                                attribute_string = key + "=" + str(value)
                                priority_attributes.append(attribute_string)
                            else:
                                attribute_string = key + "='" + str(value) + "'"
                                priority_attributes.append(attribute_string)

                        else:
                            attribute_string = key + "=" + str(value)
                            priority_attributes.append(attribute_string)

            # get list of non priority attributes
            non_priority_attributes = [key for key in attributes if key not in priority_list]
            # sort non_priority_attributes alphabetically
            non_priority_attributes = sorted(non_priority_attributes, key=str.lower)
            # match sorted keys with values and construct list
            additional_keywords = [key + "='" + str(value) + "'" for x in non_priority_attributes for key, value in
                                   attributes.items() if key == x]

            priority_attributes.extend(additional_keywords)

            metadata_string = ", ".join(priority_attributes)

            return "QAutoElement(({by}, u'{value}'), {metadata})".format(by=self.get_by_locator_string(),
                                                                         value=self.value,
                                                                         metadata=metadata_string)

        else:
            return "QAutoElement(({by}, u'{value}'))".format(by=self.get_by_locator_string(), value=self.value)