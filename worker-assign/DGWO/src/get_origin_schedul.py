# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 09:32:32 2024

@author: 20140
"""
from settings import config
from calculateMakespan import calculateMakespan,calculateMakespan_Flowline,calculateMakespan_Assembly 

def worker_pool(machine_proficiencies, assembly_proficiencies):
    mac_result = []
    ass_result = []
    for col in machine_proficiencies.columns:
        machine_result = []
        for index, value in machine_proficiencies[col].items():
            if value != 0:
                machine_result.append((index, value))
        mac_result.append(machine_result)
    sorted_mac_result = [sorted(sublist, key=lambda x: x[1], reverse=True) for sublist in mac_result]
    
    for col in assembly_proficiencies.columns:
        assembly_result = []
        for index, value in assembly_proficiencies[col].items():
            if value != 0:
                assembly_result.append((index, value))
        ass_result.append(assembly_result)
    sorted_ass_result = [sorted(sublist, key=lambda x: x[1], reverse=True) for sublist in ass_result]
    machine_schedul, assembly_schedul = timetaken()
    return machine_schedul, assembly_schedul , sorted_mac_result, sorted_ass_result

def timetaken():
    individual= config['order']
    macninetimes = config['macninetimes']
    machines = config['machines']
    process_num = config['process_num']
    product_num= config['product_num']
    machine_num= config['machine_num']
    assembly_times = config['assembly_times']
    result, table = calculateMakespan(macninetimes, machines, individual,process_num,product_num,machine_num)
    finaltime_to_assemblystage =calculateMakespan_Flowline( product_num,table)
    machine_operations_all,result=calculateMakespan_Assembly(  individual,finaltime_to_assemblystage,assembly_times)
    return table, machine_operations_all