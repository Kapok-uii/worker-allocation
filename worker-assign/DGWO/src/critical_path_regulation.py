# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 10:03:10 2024

@author: 20140
"""

import random
from checkor import maincheckor
from settings import config

def swap_muntion_process(order_list,node_index, machidx, mac_result ):
    id1 = order_list[node_index]
    mach = machidx[node_index]
    workerset = mac_result[mach] 
    worktemp = []
    for worktoassign in workerset:
        worktemp.append ( worktoassign [0])
    for j in range(0, len(worktemp)//2):
        if worktemp[j] not in id1:
            id1.append(worktemp[j])
    order_list[node_index] = id1
    return order_list

def swap_muntion_assembly (node_list,critical_asse_nodes,ass_result, asseschedul):
    workstationtemp = []
    index1= None
    index2= None
    for i, prod in enumerate(asseschedul):
        for j ,workstation in enumerate(prod):
            if workstation[0] == list(critical_asse_nodes):
                index1 = i
                index2 = j
    workertoadd = node_list[index1][index2]
    workstation =ass_result[index2] 
    for workstationlist in workstation:
        workstationtemp.append(workstationlist[0])
    for toaddworkernum in range(0,len(workstationtemp)//2):
        if workstationtemp[toaddworkernum] not in workertoadd:
            workertoadd.append(workstationtemp[toaddworkernum])
    node_list[index1][index2] = workertoadd
    return node_list

def mach_worker_set ( machine_schedul,mach_result):
    empty_A = [[[] for _ in machine] for machine in machine_schedul]
    for i in range(len(machine_schedul)):
        for j, task in enumerate(machine_schedul[i]):
            for k in mach_result[i]:
                worker_id = k[0]
                empty_A[i][j].append(worker_id)
    return empty_A

def asse_worker_set ( assembly_schedul, ass_result):
    empty_B = []
    for product_tasks in assembly_schedul:
        product_worker_set = []
        for task in product_tasks:
            task_number = task[0][1]
            worker_efficiency_list = ass_result[task_number]
            workers_for_task = [worker_id for worker_id, _ in worker_efficiency_list]
            product_worker_set.append(workers_for_task)
        empty_B.append(product_worker_set)
    return empty_B

def can_insert_task(A_sorted , B):
    if len(A_sorted) != 0:
        if B[1] <= A_sorted[0][0]:
            return [(B[0], B[1],B[2], B[3])] + A_sorted, True
        for i in range(len(A_sorted) - 1):
            prev_end = A_sorted[i][1]
            next_start = A_sorted[i + 1][0]
            if B[0] >= prev_end and B[1] <= next_start:
                return A_sorted[:i + 1] + [(B[0], B[1],B[2], B[3])] + A_sorted[i + 1:], True
            if B[1] <= next_start:
                break
        if B[0] >= A_sorted[-1][1]:
            return A_sorted + [(B[0], B[1],B[2], B[3])], True
    return A_sorted, False

def can_insert_asse_task(A_sorted , B):
    if len(A_sorted) != 0:
        b_start = B[2]
        b_end = B[1] + B[2]
        if b_start <= A_sorted[0][0]:
            return [(b_start, b_end,B[0])] + A_sorted, True 
        for i in range(len(A_sorted) - 1):
            prev_end = A_sorted[i][1]
            next_start = A_sorted[i + 1][0]
            if b_start >= prev_end and b_end <= next_start:
                return A_sorted[:i + 1] + [(b_start, b_end,B[0])] + A_sorted[i + 1:], True
            if b_end <= next_start:
                break
        if b_start >= A_sorted[-1][1]:
            return A_sorted + [(b_start, b_end,B[0])], True
    return A_sorted, False

def restart_pop(bas_mach_sch, bas_asse_sch,basic_pop, bas_mac_rlt, bas_asse_rlt):

    update_mach_schedul, update_assem_schedul, update_mach_worker ,update_asse_worker, finalresult, criticalmechschedul, machidx, mach_worker_timelines, asse_worker_timelines = maincheckor ( bas_mach_sch, bas_asse_sch,basic_pop, bas_mac_rlt, bas_asse_rlt )
    basic_pop[0][1] = finalresult
    basic_pop[0][2] = criticalmechschedul
    basic_pop[0][3] = update_assem_schedul
    basic_pop[0][4] = mach_worker_timelines
    basic_pop[0][5] = asse_worker_timelines 
    return basic_pop

def add_stage(crit_mach_indices, crit_asse_list, basic_pop, bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt, parmeters):

    mach_ability_set = mach_worker_set (bas_mach_sch, bas_mac_rlt)
    asse_ability_set = asse_worker_set (bas_asse_sch, bas_asse_rlt)
    assembyl_order = config['order'][0][0]

    for i in crit_mach_indices:
        critical_task_nodes = basic_pop[0][2][i[0]][i[1]]
        workers_critical_task_nodes = basic_pop[0][0][i[0]][i[1]] 
        
        non_worker_task =  [x for x in mach_ability_set[i[0]][i[1]] if x not in workers_critical_task_nodes] # 找到符合能力但是未分配的人员
        wheth_add = True
        
        for w in non_worker_task:
            worker_lines = basic_pop[0][4][w]
            worker_lines, wheth_add = can_insert_task (worker_lines, critical_task_nodes)
            if wheth_add:
                basic_pop[0][0][i[0]][i[1]].append(w)
                basic_pop = restart_pop(bas_mach_sch, bas_asse_sch,basic_pop, bas_mac_rlt, bas_asse_rlt)

    for asse_task in crit_asse_list:
        row = assembyl_order.index(asse_task[0])
        col = asse_task[1]
        workers_critical_asse_nodes = basic_pop[1][row][col]
        asse_non_worker_task =  [x for x in asse_ability_set[row][col] if x not in workers_critical_asse_nodes]
        
        wheth_add = True

        for w in asse_non_worker_task:
            asse_worker_lines = basic_pop[0][5][w]
            asse_worker_lines, wheth_add = can_insert_asse_task (asse_worker_lines, basic_pop[0][3][row][col])
            if wheth_add:
                basic_pop[1][row][col].append(w)
                basic_pop = restart_pop(bas_mach_sch, bas_asse_sch,basic_pop, bas_mac_rlt, bas_asse_rlt)
    return basic_pop
    
def crossover_stage (goal_pop, basic_pop, bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt, parmeters):
    goal_mach_worker = goal_pop [0][0]
    grew_mach_worker = basic_pop [0][0]
    mach_row = random.randint(0, len(goal_mach_worker)-1)
    basic_pop [0][0][mach_row] = swap_sublists(goal_mach_worker[mach_row], grew_mach_worker[mach_row],parmeters)
    basic_pop = restart_pop(bas_mach_sch, bas_asse_sch,basic_pop, bas_mac_rlt, bas_asse_rlt)
    goal_asse_worker = goal_pop [1]
    asse_row = random.randint(0, len(goal_asse_worker)-1)
    asse_loc = random.randint(0, len(goal_asse_worker[asse_row])-1)
    basic_pop [1][asse_row][asse_loc] = goal_pop [1][asse_row][asse_loc] 
    return basic_pop

def swap_sublists(A, B, parmeters):
    max_length = parmeters['ratio']
    n = len(A)
    max_sublist_length = max(1, int(n * max_length))
    while True:
        i, j = sorted(random.sample(range(n), 2))
        sublist_length = j - i
        if sublist_length <= max_sublist_length:
            break
    
    A_sub = A[i:j]
    B[i:j] = A_sub
    return B