# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 09:19:13 2024

@author: 20140
"""

import pandas as pd
def load_worker_proficiencise(file_path_machine,file_path_assembly):
    df = pd.read_excel(file_path_machine)
    machine_proficiencies = df.iloc[:, 1:]
    df = pd.read_excel(file_path_assembly)  
    assembly_proficiencies = df.iloc[:, 1:]
    return machine_proficiencies, assembly_proficiencies


