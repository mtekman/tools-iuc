#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
from SectionHandler import *	   
from CommandParse import CommandParse


class Document2Section:

    def __init__(self, html_file):
        
        with open(html_file, 'r') as f:
            html = f.read()            
            self.xml_text = Document2Section.parse(html)


    @staticmethod
    def parse(text):

        bsobj = bs(text, 'html.parser')
        main_div = bsobj.body.find('div', attrs={'class':'col-md-9'})
        tables = main_div.find_all('table')
        
        tmp_section = None
        h2_map = {}

        return_text=""
          
        for table in tables:
            # Previous H1
            h2 = table.find_previous_sibling('h2')    
            title = h2.text

            # DEBUGGING ONLY
            #if title != "Automatic model selection":
            #    continue

            # Unique headers for multiple tables under the same header
            while title in h2_map:
                title = title + '-X-'
            h2_map[title] = True

            if tmp_section != None:
                return_text += tmp_section.printSection()

            # New section
            tmp_section = Section(title)

            # Each table is a section
            thead = table.thead
            thead1 = thead.th.text
            thead2 = thead.th.nextSibling.text

            datatype_table = False

            if thead1 == "Option" and thead2 == "Usage and meaning":
                print("Section:", title, file=sys.stderr)
                #continue
            else:
                continue
                # Special tables for defining extra -m param types (RateType, DataType, FreqType)
                #datatype_table = True
                #print( "- subsection", thead1, thead2, file=sys.stderr)

            tbody = table.tbody

            try:
                helps = [tr.td.nextSibling.text for tr in tbody.findAll('tr')]
                flags = []

                if not(datatype_table):       
                    flags = [tr.td.code.text for tr in tbody.findAll('tr')]
                else:
                    tmp_section.setSubSection(thead1)
                    flags = [tr.td.text for tr in tbody.findAll('tr')]

            except AttributeError:
                import pdb; pdb.set_trace()

            if len(flags) != len(helps):
                print("Table mismatch", file=sys.stderr)
                exit(-1)

            flag_helper = list(zip(flags, helps))

            for flag, helper in flag_helper:    
                parts = flag.split(' ')
                flag = parts[0]
                flag_params = None

                if len(parts) > 1:
                    flag_params = parts[1:]

                #flag, flag_params, short, help
                tmp_section.insertFlag(flag, flag_params, helper)


        # Print final
        return return_text + tmp_section.printSection()



Document2Section(sys.argv[1])

#cc = CommandParse(flag_map, exclude_map)

#import pdb;pdb.set_trace()
