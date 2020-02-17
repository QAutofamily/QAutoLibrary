from tika import parser
import os
from datetime import date
import datetime



class TikaParser:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.data = []
        #       self.logger = logger
        #    self.logger.info("Processing file %s", self.pdf_path)
        self.text = self.convert_pdf_to_text()
        self.date_format = "%d.%m.%Y"

    def is_float(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def get_validated_lines(self, lines_to_be_validated):
        append_flag=False
        word = ""
        index_to_fix = 0
        offset = 0
        for i, j in enumerate(lines_to_be_validated):
            if self.is_int(j.split()[0]) and self.is_int(j.split()[1]):
                append_flag = False
                index_to_fix += 1
            else:
                offset += 1
                append_flag=True
            if append_flag:
                word = word+" " + j
            else:
                if word != "":
                    lines_to_be_validated[index_to_fix-2:index_to_fix-1+offset] = [lines_to_be_validated[index_to_fix-2] + word]
                    word = ""
                    index_to_fix = index_to_fix+offset
                    offset = 0

        return lines_to_be_validated

    def get_following_linenro_item_by_offset(self, lines, base_line_index, offset):
        #get value after baseline index by offset
        #useful when its known that certain value is followed by certain baseline index
        return lines[base_line_index + offset]

    def get_following_linenro_item_by_keyword(self,base_line_index, lines, keyword):
        #get value after baseline index by keyword
        #useful when its known that certain value is followed by certain baseline index and has specific keyword
        for s in range(base_line_index, len(lines) - 1):
            if keyword in lines[s]:
                return lines[s]

        return ""

    def get_last_of_line(self,keyword, keywords_sequence, lines, occurance_nro):
        #Returns last value found in line by keyword, occurance_nro can be greater than 0 if multiple occurances in file
        #Parameters:
        #Keywords_sequence: if lines contains specific sequence of keywords, supply these keywords as list for smart parsing

        index_of_keyword=[i for i, s in enumerate(lines) if keyword in s][occurance_nro]
        parsed_item=[line.replace(keyword + " ", "") for line in lines if line.startswith(keyword)][occurance_nro]
        if keywords_sequence:
            for j in range(index_of_keyword, len(lines)-1):
                for item in keywords_sequence:
                    if item in lines[j + 1]:
                        return parsed_item
                parsed_item = parsed_item + " " + lines[j + 1].strip()

            self.fail("Failed to locate last of line")
        else:
            return parsed_item


    def get_line_nro_of_keyword(self, keyword, lines, occurance_nro):
        #Returns index number of keyword, occurance_nro can be greater than 0 if multiple occurances in file
        return [i for i, s in enumerate(lines) if keyword in s][occurance_nro]

    def get_matching_occurance_from_anywhere(self, list_of_search_values, lines, occurance_nro):
        #returns matching value anywhere from file, occurance_nro can be greater than 0 if multiple occurances in file
        #requires list of values to be searched from file
        #Useful when one knows which values to search from file (for example currency: EUR,USD...)
        return [currency for currency in list_of_search_values if currency in " ".join(lines)][occurance_nro]

    def get_values_between_keywords(self, start_keyword,end_keyword, occurance_nro_start, occurance_nro_end, lines):
        #returns lines between two keywords
        Start = [i for i, s in enumerate(lines) if start_keyword in s][occurance_nro_start]
        End = [i for i, s in enumerate(lines) if end_keyword in s][occurance_nro_end]
        Values = lines[Start + 1:End]
        return Values

    def convert_pdf_to_text(self):
        """Use Tika to convert PDF to text"""
        #   self.logger.debug("Converting PDF to text")
        parsed = parser.from_file(self.pdf_path)
        # print(parsed["content"])
        return parsed["content"]
    

