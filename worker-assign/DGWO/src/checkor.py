# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 21:09:17 2024

@author: 20140
"""
from calculateStarttime import calculate_earliest_start_time
from calassembly import calculateMakespan_Assembly 
from settings import config

def resort_tasks_by_start_time(A, B):
    all_tasks = []
    for machine_index, machine_tasks in enumerate(A):
        for task_index, task in enumerate(machine_tasks):
            all_tasks.append((task[0], task[1], task[2], task[3], machine_index, task_index))
    all_tasks.sort(key=lambda x: x[0])
    new_A = []
    C = []
    for start_time, end_time, product, part, machine_index, task_index in all_tasks:
        new_A.append([start_time, end_time, product, part])
        C.append(machine_index)
    new_B = B
    return new_A, new_B, C

def sort_tasks_by_start_time(A, B):
    all_tasks = []
    for machine_index, machine_tasks in enumerate(A):
        for task_index, task in enumerate(machine_tasks):
            all_tasks.append((task[0], task[1], task[2], task[3], machine_index, task_index))
    all_tasks.sort(key=lambda x: x[0])

    new_A = []
    new_B = []
    C = []
    for start_time, end_time, product, part, machine_index, task_index in all_tasks:
        new_A.append([start_time, end_time, product, part])
        new_B.append(B[machine_index][task_index])
        C.append(machine_index)
    return new_A, new_B, C

def sort_asse_task_by_start_time(assembly_schedul, asse_worker):
    all_asse_tasks = []
    for prod_index, asse_prod in enumerate(assembly_schedul):
        for workstation_index, asse_tasks in enumerate( asse_prod):
            all_asse_tasks.append((asse_tasks[0][0], asse_tasks [0][1], asse_tasks[1], asse_tasks[2]))
    all_asse_tasks.sort(key= lambda x:x[2])
    
    new_assem_shcedul = []
    new_worker = []
    assemorder = []
    original_asse_durations = []
    
    for prod, workstation, duration, start_time in all_asse_tasks:
        end_time = start_time + duration
        new_assem_shcedul.append([start_time, end_time, prod, workstation])
        new_worker.append( asse_worker [prod][workstation])
        assemorder.append(prod)
        original_asse_durations.append(duration)
    
    return new_assem_shcedul, new_worker, assemorder,original_asse_durations

def calculate_duration_with_workers(worker_list, original_duration,machine, bas_mac_rlt):
    sumvalue = 0
    mach_effici_set = bas_mac_rlt [machine]
    for j in mach_effici_set:
        if j[0] in worker_list:
            sumvalue = sumvalue + j [1]
    calculated_duration = max(original_duration * (1 - 0.05 * sumvalue),  int(0.4*original_duration))
    return calculated_duration

def find_earliest_start_time(new_A, i, C, task_end_times):
    previous_task_end_time_machine = 0
    for j in range(i - 1, -1, -1):
        if C[j] == C[i]:
            previous_task_end_time_machine = task_end_times[j]
            break

    previous_task_end_time_part = 0
    for j in range(i - 1, -1, -1):
        if new_A[j][2] == new_A[i][2] and new_A[j][3] == new_A[i][3]:
            previous_task_end_time_part = task_end_times[j]
            break

    earliest_start_time = max(previous_task_end_time_machine, previous_task_end_time_part)
    return earliest_start_time

def update_worker_timelines(worker_timelines, worker_list, start_time, end_time,mach_shce):
    for worker in worker_list:
        worker_timelines[worker].append((start_time, end_time, mach_shce[2],mach_shce[3]))
        
def update_asse_worker_timelines(worker_timelines, worker_list, start_time, end_time,taskID):
    for worker in worker_list:
        worker_timelines[worker].append((start_time, end_time,taskID))

def mach_are_all_workers_available(worker_timelines, worker_list, start_time, end_time):
    for worker in worker_list:
        for existing_start, existing_end, _ , _ , in worker_timelines[worker]:
            if not (existing_end <= start_time or existing_start >= end_time): 
                return False
    return True

def asse_are_all_workers_available(worker_timelines, worker_list, start_time, end_time):
    for worker in worker_list:
        for existing_start, existing_end, _ in worker_timelines[worker]:
            if not (existing_end <= start_time or existing_start >= end_time): 
                return False
    return True

def adjust_workers_for_task(new_B, worker_timelines, i, earliest_start_time, calculated_duration, original_duration,C,bas_mac_rlt):
    workers_to_check = list(new_B[i])
    
    while workers_to_check:
        if mach_are_all_workers_available(worker_timelines, workers_to_check, earliest_start_time, earliest_start_time + calculated_duration):
            break
        for worker in workers_to_check:
            worker_timeline = worker_timelines[worker]
            for start, end ,_ ,_ in worker_timeline:
                if not (end <= earliest_start_time or start >= earliest_start_time + calculated_duration):
                    new_B[i].remove(worker)
                    calculated_duration = calculate_duration_with_workers(new_B[i], original_duration,C[i],bas_mac_rlt)
                    break
            else:
                continue
            break
        
        workers_to_check = list(new_B[i])
        if not workers_to_check:
            break
    return new_B, calculated_duration


def asse_adjust_workers_for_task (asse_worker, assm_worker_timelines, i,j ,earliest_start_time, calculated_duration, origin_duration, bas_asse_rlt):
    workers_to_check = list(asse_worker[i][j])
    
    while workers_to_check:
        if asse_are_all_workers_available(assm_worker_timelines, workers_to_check, earliest_start_time, earliest_start_time + calculated_duration):
            break
        for worker in workers_to_check:
            worker_timeline = assm_worker_timelines[worker]
            for start, end ,_ in worker_timeline:
                if not (end <= earliest_start_time or start >= earliest_start_time + calculated_duration):
                    asse_worker[i][j].remove(worker)
                    calculated_duration = calculate_duration_with_workers(asse_worker[i][j], origin_duration,j, bas_asse_rlt)
                    break
            else:
                continue
            break
        
        workers_to_check = list(asse_worker[i][j])
        if not workers_to_check:
            break
    return asse_worker, calculated_duration

def update_task_allocation(new_A, new_B, worker_timelines, original_durations, C, bas_mac_rlt):
    task_end_times = [0] * len(new_A)
    duration = []
    for i, task in enumerate(new_A):
        earliest_start_time = find_earliest_start_time(new_A, i, C, task_end_times)
        original_duration = original_durations[i]
        calculated_duration = calculate_duration_with_workers(new_B[i], original_duration,C[i],bas_mac_rlt)
        task_end_time = earliest_start_time + calculated_duration
        task_end_times[i] = task_end_time
        
        update_worker_timelines(worker_timelines, new_B[i], earliest_start_time, task_end_time, new_A[i])
        new_A[i][0] = earliest_start_time
        new_A[i][1] = task_end_time
        
        duration.append(calculated_duration)
    return new_A, new_B,C, worker_timelines


def gobal_update_task_allocation(new_A, new_B, worker_timelines, original_durations, C, bas_mac_rlt):
    task_end_times = [0] * len(new_A)
    duration = []
    for i, task in enumerate(new_A):
        
        earliest_start_time = find_earliest_start_time(new_A, i, C, task_end_times)
        original_duration = original_durations[i]
        calculated_duration = calculate_duration_with_workers(new_B[i], original_duration,C[i],bas_mac_rlt)
        new_B, calculated_duration = adjust_workers_for_task (new_B, worker_timelines, i, earliest_start_time, calculated_duration, original_duration,C,bas_mac_rlt)
        
        task_end_time = earliest_start_time + calculated_duration
        task_end_times[i] = task_end_time
        
        update_worker_timelines(worker_timelines, new_B[i], earliest_start_time, task_end_time, new_A[i])
        new_A[i][0] = earliest_start_time
        new_A[i][1] = task_end_time

        duration.append(calculated_duration)
    return new_A, new_B,C, worker_timelines

def update_assembly_allocation(assembly_schedul_tuple, asse_worker, update_mach_schedul, assembly_times, finaltime_to_assemblystage,worker_timelines, bas_asse_rlt):

    num_workstations = len(assembly_schedul_tuple[0])
    workstation_departure_times = {i: 0 for i in range (num_workstations)}
    assembly_schedul = []
    for item in assembly_schedul_tuple:
        new_item = [[list(t) if isinstance(t, tuple) else t for t in subitem] for subitem in item]
        assembly_schedul.append(new_item)

    for i ,prod in enumerate( assembly_schedul):
        for j, task in enumerate( prod):
            earliest_start_time = calculate_earliest_start_time (assembly_schedul,i ,j , workstation_departure_times, finaltime_to_assemblystage)
            origin_duration = assembly_times[i][j]
            calculated_duration = calculate_duration_with_workers (asse_worker[i][j], origin_duration,j, bas_asse_rlt)
            task_end_time = earliest_start_time + calculated_duration
            
            workstation_departure_times = endleavetime (task_end_time, workstation_departure_times, assembly_schedul, i ,j, earliest_start_time, calculated_duration, num_workstations , finaltime_to_assemblystage)
            update_asse_worker_timelines(worker_timelines, asse_worker[i][j], earliest_start_time, task_end_time,task[0] )
            
            assembly_schedul[i][j][2] = earliest_start_time
            assembly_schedul[i][j][1] = calculated_duration
    return assembly_schedul, asse_worker,task_end_time, worker_timelines


def gobal_update_assembly_allocation(assembly_schedul_tuple, asse_worker, update_mach_schedul, assembly_times, finaltime_to_assemblystage,worker_timelines, bas_asse_rlt):
    num_workstations = len(assembly_schedul_tuple[0])
    workstation_departure_times = {i: 0 for i in range (num_workstations)}
    assembly_schedul = []
    for item in assembly_schedul_tuple:
        new_item = [[list(t) if isinstance(t, tuple) else t for t in subitem] for subitem in item]
        assembly_schedul.append(new_item)
    for i ,prod in enumerate( assembly_schedul):
        for j, task in enumerate( prod):
            earliest_start_time = calculate_earliest_start_time (assembly_schedul,i ,j , workstation_departure_times, finaltime_to_assemblystage)
            origin_duration = assembly_times[i][j]
            calculated_duration = calculate_duration_with_workers (asse_worker[i][j], origin_duration,j, bas_asse_rlt)
            asse_worker, calculated_duration = asse_adjust_workers_for_task( asse_worker, worker_timelines, i,j ,earliest_start_time, calculated_duration, origin_duration, bas_asse_rlt)

            task_end_time = earliest_start_time + calculated_duration
            
            workstation_departure_times = endleavetime (task_end_time, workstation_departure_times, assembly_schedul, i ,j, earliest_start_time, calculated_duration, num_workstations , finaltime_to_assemblystage)
            update_asse_worker_timelines(worker_timelines, asse_worker[i][j], earliest_start_time, task_end_time,task[0] )
            
            assembly_schedul[i][j][2] = earliest_start_time
            assembly_schedul[i][j][1] = calculated_duration
            
    return assembly_schedul, asse_worker,task_end_time, worker_timelines

def endleavetime(end_time, workstation_departure_times, tasks, product_index, task_index, earliest_start_time, calculated_duration, num_workstations, finaltime_to_assemblystage):
    (product_id, workstation_id), duration, scheduled_start_time = tasks [product_index][task_index]
    product_tasks = tasks[product_index]
    if product_index ==0 or task_index == num_workstations:
        departure_time = end_time
    elif task_index > 0:
        prev_task = product_tasks[task_index - 1]
        prev_end_time = prev_task[2] + prev_task[1]
        departure_time = max( prev_end_time, finaltime_to_assemblystage[product_index][task_index],workstation_departure_times[workstation_id])
    elif product_index > 0  and  task_index == 0:
        departure_time = max(workstation_departure_times[workstation_id],finaltime_to_assemblystage[product_index][task_index])
    workstation_departure_times[task_index] = departure_time
    return workstation_departure_times

def calculate_original_durations(A):
    original_durations = []
    for task in A:
        start_time = task[0]
        end_time = task[1]
        duration = end_time - start_time
        original_durations.append(duration)
    return original_durations
def initialize_worker_timelines(mach_worker, asse_worker):
    mach_worker_timelines = {}
    assm_worker_timelines = {}
    for worker_list in mach_worker:
        for worker in worker_list:
            if worker[0] not in mach_worker_timelines:
                    mach_worker_timelines[worker[0]] = []
                    
    for worker_list in asse_worker:
        for worker in worker_list:
            if worker[0] not in assm_worker_timelines:
                    assm_worker_timelines[worker[0]] = []
    return mach_worker_timelines , assm_worker_timelines

def reinit_worker_timelines(mach_worker, asse_worker):
    mach_worker_timelines = {}
    assm_worker_timelines = {}
    for worker_list in mach_worker:
        for worker in worker_list:
            if worker not in mach_worker_timelines:
                mach_worker_timelines[worker] = []
    for worker_list in asse_worker:
        for worker in worker_list:
            for idv in worker:
                if idv not in assm_worker_timelines:
                    assm_worker_timelines[idv] = []
    return mach_worker_timelines , assm_worker_timelines

def categorize_tasks_by_machine(A, B):
    max_machine_id = max(B)
    C = [[] for _ in range(max_machine_id + 1)]
    for i, task in enumerate(A):
        machine_id = B[i]
        C[machine_id].append(task)
    return C


def maincheckor(machine_schedul ,assembly_schedul,individual,  bas_mac_rlt, bas_asse_rlt):
    product_num = config['product_num']
    assembly_times = config['assembly_times']
    order = config['order']
    asse_worker = individual[1]
    mach_worker = individual[0][0]
    mach_worker_timelines , assm_worker_timelines= initialize_worker_timelines( bas_mac_rlt, bas_asse_rlt)
    new_A, new_B, machidx = sort_tasks_by_start_time(machine_schedul, mach_worker)
    original_durations = calculate_original_durations (new_A)
    update_mach_schedul, update_mach_worker ,machidx, mach_worker_timelines = update_task_allocation(new_A, new_B, mach_worker_timelines, original_durations, machidx, bas_mac_rlt)
    assembly_order = order[0][0]
    new_assembly_schedul , finaltime_to_assemblystage_order,assembly_times_order = calculateMakespan_Assembly (assembly_order, assembly_times,product_num,update_mach_schedul)
    update_assem_schedul, update_asse_worker,finalresult, asse_worker_timelines = update_assembly_allocation (assembly_schedul, asse_worker, update_mach_schedul, assembly_times_order, finaltime_to_assemblystage_order, assm_worker_timelines, bas_asse_rlt)
    criticalmechschedul = categorize_tasks_by_machine (update_mach_schedul , machidx)

    return update_mach_schedul, update_assem_schedul, update_mach_worker ,update_asse_worker, finalresult, criticalmechschedul, machidx, mach_worker_timelines, asse_worker_timelines
def globalcheckor(machine_schedul ,assembly_schedul, bas_mac_rlt, bas_asse_rlt, individual):
    product_num = config['product_num']
    assembly_times = config['assembly_times']
    order = config['order']
    asse_worker = individual[1]
    mach_worker = individual[0][0]
    mach_worker_timelines , assm_worker_timelines= initialize_worker_timelines( bas_mac_rlt, bas_asse_rlt)
    new_A, new_B, machidx = sort_tasks_by_start_time(machine_schedul, mach_worker)

    original_durations = calculate_original_durations (new_A)
    update_mach_schedul, update_mach_worker ,machidx, mach_worker_timelines = gobal_update_task_allocation(new_A, new_B, mach_worker_timelines, original_durations, machidx, bas_mac_rlt)
    assembly_order = order[0][0]
    assembly_schedul , finaltime_to_assemblystage_order,assembly_times_order = calculateMakespan_Assembly(assembly_order, assembly_times,product_num,update_mach_schedul)
    update_assem_schedul, update_asse_worker,finalresult , asse_worker_timelines = gobal_update_assembly_allocation(assembly_schedul, asse_worker, update_mach_schedul, assembly_times_order, finaltime_to_assemblystage_order, assm_worker_timelines, bas_asse_rlt)
    criticalmechschedul = categorize_tasks_by_machine (update_mach_schedul , machidx)

    return update_mach_schedul, update_assem_schedul, update_mach_worker ,update_asse_worker, finalresult, criticalmechschedul, machidx, mach_worker_timelines, asse_worker_timelines