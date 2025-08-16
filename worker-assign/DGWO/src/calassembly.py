# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 17:03:17 2024

@author: 20140
"""

from collections import defaultdict
def calculateMakespan_Assembly(produc_order,assembly_times,product_num,table):
    finaltime_to_assemblystage = calculateMakespan_Flowline(product_num,table)
    num_tasks = len(assembly_times) 
    num_machines = len(assembly_times[0])
    machine_end_times = [0] * num_machines
    task_end_times = [0] * num_tasks
    assembly_times_order=[assembly_times[i] for i in produc_order]
    finalssemblystage_order=[finaltime_to_assemblystage[i] for i in produc_order]
    machine_operations_all=[]
    for task_index in range(num_tasks):
        machine_operations=[]
        for machine_index in range(num_machines):
            processing_time = assembly_times_order[task_index][machine_index]
            if machine_index == 0:
                prev_machine_end_time = 0
            else:
                prev_machine_end_time = task_end_times[task_index]
            machine_free_time = machine_end_times[machine_index]
            start_time = max(finalssemblystage_order[task_index][machine_index],prev_machine_end_time, machine_free_time)
            end_time = start_time + processing_time
            machine_end_times[machine_index] = end_time
            task_end_times[task_index] = end_time
            name_task = [produc_order[task_index],machine_index]
            machine_operations.append((name_task, processing_time, start_time))
        machine_operations_all.append(machine_operations)
    return machine_operations_all, finalssemblystage_order,assembly_times_order

def calculateMakespan_Flowline(product_num,table):
    task_times = defaultdict(lambda: defaultdict(int))
    for task in table:
        start_time, end_time, product, job = task
        if task_times[product][job]==None:
            task_times[product][job]=end_time
        if task_times[product][job]<end_time:
            task_times[product][job]=end_time
    time_process_final=[]
    for k in range(0,product_num):
        sub_dict=task_times[k]
        time_process_finish=[]
        for jobs in range(0,len(sub_dict)):
            values_jobs=sub_dict[jobs]
            time_process_finish.append(values_jobs )
        time_process_final.append(time_process_finish)
    return time_process_final


