from evolution_process import resign
import pandas as pd
import csv
import os
from load_proficiencise import load_worker_proficiencise
import time
from get_origin_schedul import worker_pool
from initialization import generate_population
import copy

#taguchi=pd.read_csv("data/Taguchi.csv") 
#columns = ["No.", "CPM", "HMP", "HAP", "LMP", "LAP"]

'''
If you need to perform different experiments, different input files are required:
    file_MILP: Comparison of DGWO and MILP model; file_Ablation:Ablation experiment
    file_Taguchi:Taguchi orthogonal experiment; file_Compare: Comparative with other algorithms
'''

data = []
with open('data/file_Ablation.csv', mode='r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data.append(row)
    data=data[1:]

folder_path = 'data'
for case_list in data:
    case_ID=case_list[0]
    case_mach = case_list[1]
    case_asse = case_list[2]
    instance_mach_path = os.path.join(folder_path,case_mach + '.xlsx')
    instance_asse_path = os.path.join(folder_path,case_asse + '.xlsx')
    converted_paths_mach = instance_mach_path.replace('\\', '/')
    converted_paths_asse = instance_asse_path.replace('\\', '/')
    df_result = pd.DataFrame()
    df_time = pd.DataFrame()
    tested_times = 0
    machine_proficiencies, assembly_proficiencies = load_worker_proficiencise(converted_paths_mach,converted_paths_asse)
    bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt = worker_pool (machine_proficiencies, assembly_proficiencies)
    parmeters = {'CPM':0.5, 'HMP': 0.7, 'HAP' : 0.9, 'LMP' : 0.2, 'LAP' : 0.3}
    origin_pop_set  = generate_population (bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt)
# The below comment code is executed during the taguchi experiment

    # for index, row in taguchi.iterrows():
    #     i=0
    #     parmeters = {'CPM':row['CPM'], 'HMP': row['HMP'], 'HAP' : row['HAP'], 'LMP' : row['LMP'], 'LAP' : row['LAP'] }
    #     while tested_times < 5:
    #         best_individual, best_result, best_mach_schedul, best_assem_schedul = resign (copy.deepcopy(origin_pop_set), machine_proficiencies, assembly_proficiencies,parmeters,bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt)
    #         df_result.loc[case_ID, i] = best_result
    #         i+=1
    #         print(case_list,row['No.'], i)
    #     df_result.to_excel('case_{0}_{1}.xlsx'.format(case_ID, index), index= False)

    while tested_times < 10:
        t_start = time.time()
        best_individual, best_result, best_mach_schedul, best_assem_schedul = resign (copy.deepcopy(origin_pop_set), machine_proficiencies, assembly_proficiencies,parmeters,bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt)
        df_result.loc[case_ID, tested_times] = best_result
        t_end = time.time()
        ave_total_time = (t_end - t_start)
        df_time.loc[case_ID, tested_times] = ave_total_time
        df_result.to_excel('AE0_case_result_{0}_{1}.xlsx'.format(case_ID, tested_times), index= False)
        df_time.to_excel('case_time_{0}.xlsx'.format(case_ID), index= False)
        tested_times+=1