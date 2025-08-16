# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 09:02:08 2024

@author: 20140
"""
from confictsolve import neh_critic_addworker
from critical_path_regulation import add_stage
import random
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def mach_avedis(best_mach_list, norm_mach_list):
    dis = 0
    for i in range(0,len(best_mach_list)):
        for j in range (0, len(best_mach_list[i])):
            set1 =set(best_mach_list[i][j])
            set2 =set(norm_mach_list[i][j])
            similarity = jaccard_similarity(set1, set2)
            dis =dis + similarity
    avedis = dis/len( best_mach_list)
    return avedis

def asse_avedis(best_asse_list, norm_asse_list):
    dis = 0
    A = []
    B = []
    for prod in best_asse_list:
        for workstation in prod:
            A .append( workstation )
    
    for prod in norm_asse_list:
        for workstation in prod:
            B .append( workstation )

    for i in range(0,len(A)):
        set1 =set(A[i])
        set2 =set(B[i])
        similarity = jaccard_similarity(set1, set2)
        dis =dis + similarity
    avedis = dis/len(A)
    return avedis

def mach_diff (bestgewo, gewo):
    dis = []
    best_mach_list = bestgewo [0][0]
    norm_mach_list = gewo [0][0]
    for i in range(0,len(best_mach_list)):
        for j in range(0,len(best_mach_list[i])):
            set1 =set(best_mach_list[i][j])
            set2 =set(norm_mach_list[i][j])
            similarity = jaccard_similarity(set1, set2)
        dis .append( similarity)
    return dis

def asse_diff (bestgewo, gewo):
    asse_dis = []
    A = []
    B = []
    best_asse_list = bestgewo [1]
    norm_asse_list = gewo [1]
    
    for prod in best_asse_list:
        for workstation in prod:
            A .append( workstation )
    
    for prod in norm_asse_list:
        for workstation in prod:
            B .append( workstation )

    for i in range(0,len(A)):
        set1 =set(A[i])
        set2 =set(B[i])
        similarity = jaccard_similarity(set1, set2)
        asse_dis.append( similarity)
    return asse_dis

def first_method ( gwo,bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt,parmeters):
    crit_mach_indices, crit_asse_list = neh_critic_addworker (gwo[0][2], gwo[0][3]) 
    newpop =  add_stage (crit_mach_indices, crit_asse_list, gwo, bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt, parmeters)
    return newpop

def cal_node_class( node_diff, range_probility) :
    
    num_elements = int(len(node_diff) * range_probility )
    sorted_node_diff = sorted(node_diff)
    smallest_values = sorted_node_diff [:num_elements]
    
    indices_of_smallest = [index for index, value in enumerate(node_diff) if value in smallest_values]
    
    return indices_of_smallest [:num_elements]

def second_method (bas_mach_sch, bas_asse_sch, bestgewo, gewo, bas_mac_rlt, dbas_asse_rlt,mach_range_probility,asse_range_probility):
    
    best_mach_list = bestgewo [0][0]
    norm_mach_list = gewo [0][0]
    best_asse_list = bestgewo [1]
    norm_asse_list = bestgewo [1]

    for i in range(0,len(norm_mach_list)):
        for j in range (0,len(norm_mach_list[i])):
            if random.random() < mach_range_probility :
                norm_mach_list[i][j] = best_mach_list[i][j]
    
    for i in range(0,len(norm_asse_list)):
        for j in range (0,len(norm_asse_list[i])):
            if random.random() < asse_range_probility :
                norm_asse_list[i][j] = best_asse_list[i][j]

    gewo [0][0] = norm_mach_list
    gewo [1] = norm_asse_list
    gewo [0][1] = None
    return gewo

def mainimprove(bestgewo, gewo):
    best_mach_list = bestgewo [0][0]
    best_asse_list = bestgewo [1]
    norm_mach_list = gewo [0][0]
    norm_asse_list = bestgewo [1]
    machavedis = mach_avedis(best_mach_list, norm_mach_list)
    asseavedis = asse_avedis(best_asse_list, norm_asse_list)
    all_avedis = 0.5*( machavedis + asseavedis)
    results = (gewo [0][1] - bestgewo [0][1] )/bestgewo [0][1]
    return all_avedis, results

def impmethod(avedis_idx, result_idx, bestgwo, gwo,bas_mach_sch, bas_asse_sch, bas_mac_rlt, dbas_asse_rlt,parmeters):
    if  result_idx == 0:
        return first_method (gwo,bas_mach_sch, bas_asse_sch , bas_mac_rlt, dbas_asse_rlt,parmeters)
    elif avedis_idx == 1 and result_idx == 1:
        return second_method (bas_mach_sch, bas_asse_sch, bestgwo, gwo, bas_mac_rlt, dbas_asse_rlt, mach_range_probility = parmeters['HMP'], asse_range_probility = parmeters['HAP'])
    else:
        return second_method ( bas_mach_sch, bas_asse_sch, bestgwo, gwo, bas_mac_rlt, dbas_asse_rlt, mach_range_probility = parmeters['LMP'], asse_range_probility = parmeters['LAP'])