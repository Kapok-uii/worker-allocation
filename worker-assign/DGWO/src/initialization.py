# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 09:30:19 2024
@author: 20140
"""

from settings import config
import random
from confictsolve import mainconfict

def neh_addworker( machine_schedul, assembly_schedul,mac_result,ass_result):
    empty_A = [[[] for _ in machine] for machine in machine_schedul]
    for i in range(len(machine_schedul)):
        for j, task in enumerate(machine_schedul[i]):
            for k in mac_result[i]:
                worker_id = k[0]
                empty_A[i][j].append(worker_id)
    mechine_neh = [empty_A, None , None, None , None, None  ]
    empty_B = []
    for product_tasks in assembly_schedul:
        product_worker_set = []
        for task in product_tasks:
            task_number = task[0][1]
            worker_efficiency_list = ass_result[task_number]
            workers_for_task = [worker_id for worker_id, _ in worker_efficiency_list]
            product_worker_set.append(workers_for_task)
        empty_B.append(product_worker_set)
    return [mechine_neh,empty_B]

def addRandomIndividual(machine_schedul, assembly_schedul,mac_result,ass_result):
    empty_rand = [[[] for _ in machine] for machine in machine_schedul]
    for i in range(len(machine_schedul)):
        for j, task in enumerate(machine_schedul[i]):
            for k in mac_result[i]:
                random_bool = random.choice([True,False])
                if random_bool:
                    worker_id = k[0]
                    empty_rand[i][j].append(worker_id)
            
    randompop= [empty_rand, None , None, None , None, None ]
    
    empty_B = []
    for product_tasks in assembly_schedul:
        product_worker_set = []
        for task in product_tasks:
            task_number = task[0][1]
            worker_efficiency_list = ass_result[task_number]
            workers_for_task = []
            for worker_id, _ in worker_efficiency_list:
                random_bool = random.choice([True,False])
                if random_bool:
                    workers_for_task.append(worker_id)
            product_worker_set.append(workers_for_task)
        empty_B.append(product_worker_set)
    pop = [randompop,empty_B]
    return pop

def generate_population(machine_schedul, assembly_schedul,mac_result,ass_result ):
    i = 0 
    population =[]
    while i < config['popular_num']:
        if random.random() < 0.5 :
            pop_neh = neh_addworker ( machine_schedul, assembly_schedul, mac_result, ass_result)
            update_mach_sche, _,_,_, finresult, _,_, _, _ ,basic_pop = mainconfict(machine_schedul, assembly_schedul,mac_result,ass_result,pop_neh )
        else:
            pop_neh = addRandomIndividual ( machine_schedul, assembly_schedul, mac_result, ass_result )
            update_mach_sche, _,_,_, finresult, _,_, _, _ ,basic_pop = mainconfict(machine_schedul, assembly_schedul,mac_result,ass_result,pop_neh )
        population.append(basic_pop)
    return population









