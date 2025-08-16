# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 20:53:58 2024

@author: 20140
"""
'''
'''
from seek_critical_node import seek_critical_function
from checkor import maincheckor, globalcheckor
import random
from settings import config

def find_indices(A, B):
    results = []
    asse_node = []
    process_segments = {}
    for index_a, sublist in enumerate(A):
        for index_b, segment in enumerate(sublist):
            key = (segment[2], segment[3])
            if key not in process_segments:
                process_segments[key] = []
            process_segments[key].append((index_a, index_b, segment))
    for key in process_segments:
        process_segments[key].sort(key=lambda x: x[2][0])
    for b in B:
        if len(b) > 2:
            product_id, part_id, process_id = b
            key = (product_id, part_id)
            
            if key in process_segments:
                sorted_segments = process_segments[key]
                if 0 <= process_id < len(sorted_segments):
                    index_a, index_b, _ = sorted_segments[process_id]
                    results.append((index_a, index_b))
        else:
            asse_node.append( b)
    return results, asse_node

def neh_critic_addworker (machine_schedul, assembly_schedul):
    critical_nodes =  seek_critical_function (machine_schedul, assembly_schedul) 
    result_indices, asse_result_list = find_indices (machine_schedul , critical_nodes)
    return result_indices, asse_result_list

def renew_pop(result_indices, asse_result_list, mac_result, ass_result, pop, bas_asse_schedul):
    mach_worker = pop [0][0]
    asse_worker = pop [1]
    for i in result_indices:
        mach_index = i [0]
        order_index = i [1]
        old_worker_set = mach_worker [mach_index][order_index]
        pre_workerset = mac_result[mach_index]
        random.shuffle(pre_workerset)
        for j in range(0,len(pre_workerset)):
            if pre_workerset[j][0] not in old_worker_set:
                old_worker_set.append (pre_workerset[j][0])
        mach_worker[mach_index][order_index] = old_worker_set
        
    for critical_asse_nodes in asse_result_list:
        index1= None
        index2= None
        for i, prod in enumerate(bas_asse_schedul):
            for j ,workstation in enumerate(prod):
                if workstation[0] == list(critical_asse_nodes):
                    index1 = i
                    index2 = j
        workertoadd = asse_worker [index1][index2] 
        workstation =ass_result[index2] 
        random.shuffle(workstation)
        for toaddworkernum in range(0,len(workstation)):
            if workstation[toaddworkernum][0] not in workertoadd:
                workertoadd.append(workstation[toaddworkernum][0])
        asse_worker[index1][index2] = workertoadd

    pop[0][0] = mach_worker
    pop [1] = asse_worker
    
    return pop

def categorize_tasks_by_machine(re_up_mach_wker , machidx):
    max_machine_id = max(machidx)
    C = [[] for _ in range(max_machine_id + 1)]
    for i, task in enumerate(re_up_mach_wker):
        machine_id = machidx[i]
        C[machine_id].append(task)
    return C

def find_nested_index(nested_list, target):
    results = []
    def _search(items, current_path):
        for i, item in enumerate(items):
            new_path = current_path + [i]
            if item == target:
                results.append(new_path)
            elif isinstance(item, list):
                _search(item, new_path)
    _search(nested_list, [])
    return results

def count_elements(lst):
    count = 0
    for element in lst:
        if isinstance(element, list):
            count += count_elements(element)
        else:
            count += 1
    return count

def mainconfict ( bas_mach_sch, bas_asse_sch, bas_mac_rlt, bas_asse_rlt, basic_pop ):
    assembyl_order = config['order'][0][0]
# Passive conflict resolution
    while True:
        break_all = False
        update_mach_schedul, update_assem_schedul, update_mach_worker ,update_asse_worker, finalresult, criticalmechschedul, machidx, mach_worker_timelines, asse_worker_timelines = maincheckor ( bas_mach_sch, bas_asse_sch,basic_pop, bas_mac_rlt, bas_asse_rlt )
        mach_result_indices, asse_result_list = neh_critic_addworker ( criticalmechschedul, update_assem_schedul) 
        random.shuffle(mach_result_indices)
        for i in mach_result_indices:
            critical_task_nodes = criticalmechschedul [i[0]][i[1]]
            start_time = critical_task_nodes [0]
            end_time = critical_task_nodes [1]
            workers_critical_task_nodes = basic_pop[0][0][i[0]][i[1]]
            random.shuffle( workers_critical_task_nodes )
            for j in workers_critical_task_nodes:
                task_set_j = mach_worker_timelines[j]
                for k in task_set_j:
                    if list(k) != critical_task_nodes:
                        if not (end_time <= k[0] or start_time >= k[1]):
                            try:
                                task_index = find_nested_index(criticalmechschedul, list(k))
                                basic_pop[0][0][task_index[0][0]][task_index[0][1]].remove(j)
                                break_all = True
                                break
                            except:
                                pass
                if break_all:
                    break
            if break_all:
                break
        if not break_all:
            break

    while True:
        break_all = False
        update_mach_schedul, update_assem_schedul, update_mach_worker ,update_asse_worker, finalresult, criticalmechschedul, machidx, mach_worker_timelines, asse_worker_timelines = maincheckor ( bas_mach_sch, bas_asse_sch,basic_pop, bas_mac_rlt, bas_asse_rlt )
        mach_result_indices, asse_result_list = neh_critic_addworker ( criticalmechschedul, update_assem_schedul) 
        random.shuffle(asse_result_list)
        for critical_task_nodes in asse_result_list:
            row = assembyl_order.index(critical_task_nodes[0])
            col = critical_task_nodes[1]
            start_time = update_assem_schedul [row][col][2]
            end_time = start_time + update_assem_schedul [row][col][1]
            asse_workers_critical_task_nodes = basic_pop[1][row][col] 
            random.shuffle( asse_workers_critical_task_nodes)
            for j in asse_workers_critical_task_nodes:
                task_set_j = asse_worker_timelines[j] 
                for k in task_set_j:
                    if k[2] != list(critical_task_nodes):
                        if not (end_time <= k[0] or start_time >= k[1]):
                            try:
                                row_k = assembyl_order.index(k[2][0])
                                col_k = k[2][1]
                                basic_pop[1][row_k][col_k].remove(j)
                                break_all = True
                                break
                            except:
                                pass
                if break_all:
                    break
            if break_all:
                break
        if not break_all:
            break
# Active conflict resolution
    update_mach_sche, update_assem_sche, update_mach_wker ,up_asse_wker, finalresult, criticalmechschedul, machidx, mach_worker_timelines, asse_worker_timelines = globalcheckor (bas_mach_sch, bas_asse_sch, bas_mac_rlt, bas_asse_rlt,basic_pop)
    print("加工阶段的人员数：", count_elements(basic_pop[0][0]))
    print( finalresult)
    return update_mach_sche, update_assem_sche, update_mach_wker ,up_asse_wker, finalresult, criticalmechschedul, machidx, mach_worker_timelines, asse_worker_timelines, basic_pop