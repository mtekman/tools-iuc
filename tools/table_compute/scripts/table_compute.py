#!/usr/bin/env python

import configparser as cp
import pandas as pd

from sys import argv


# Parsing Config
config = cp.ConfigParser()
with open(argv[1], 'r') as userconf:
    config.read_file(userconf)

user_mode = config["Default"]["user_mode"]

if user_mode == "single":
    # Read in file
    data = pd.DataFrame(
        config["SingleTableOps"]["reader_file"],
        header=1 if config["SingleTableOps"]["reader_header"] else 0,
        index_col=config["SingleTableOps"]["reader_row_col"],
        keep_default_na=config["Default"]["narm"]
    )
    user_mode_single = config.get["SingleTableOps"]["user_mode_single"]

    if user_mode_single == "select":
        sto_set = config["SingleTableOps.SELECT"]

        ## table_compute.R -- line 358

        
    # elif user_mode_single == "sort":
    #     sto_set = config["SingleTableOps.SELECT"]
    elif user_mode_single == "filtersum":
        sto_set = config["SingleTableOps.FILTERSUM"]

    elif user_mode_single == "matrixapply":
        sto_set = config["SingleTableOps.MATRIXAPPLY"]

    elif user_mode_single == "element":
        sto_set = config["SingleTableOps.ELEMENT"]

    elif user_mode_single == "fulltable":
        sto_set = config["SingleTableOps.FULLTABLE"]

    else:
        print("No such mode!", user_mode_single)
        exit(-1)


elif user_mode == "multiple":
    table_sections = [lambda x: x.startswith("MultipleTableOps.TABLE"),
                      config.sections()]

    if (len(table_sections) == 0):
        print("Multiple table sets not given!")
        exit(-1)

    reader_skip = config["Default"]["reader_skip"]

    multiple_tables = pd.DataFrame(columns=['file', 'header', 'row.names',
                                            'ismatrix', 'skip'])
    for sect in table_sections:
        tmp = pd.DataFrame([[
            config[sect]["file"],
            config[sect]["header"],
            config[sect]["row_names"],
            config[sect]["ismatrix"],
            reader_skip
        ]], columns=['file', 'header', 'row.names', 'ismatrix', 'skip'])

        multiple_tables = multiple_tables.append(tmp)
