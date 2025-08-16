# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 13:00:32 2024

@author: 20140
"""
import random
from gwoimprove import mainimprove, impmethod
from critical_path_regulation import add_stage
from confictsolve import neh_critic_addworker
import copy
from settings import config

def rvodam( population):
    rf = population[0]
    ft = population[1]
    gm = population[2]
    
    result_rf = rf[0][1]
    result_ft = ft[0][1]
    result_gm = gm[0][1]
    total = result_rf + result_ft + result_gm
    result_rf_prob = result_rf / total
    result_ft = result_ft / total
    for i in range(3,len(population)):
        rand = random.random()
        if rand < result_rf_prob:
            return rf
        elif rand < result_rf_prob + result_ft:
            return ft
        else:
            return gm

def assign_grade(value, boundaries):
    for i in range(len(boundaries) - 1):
        if value <= boundaries[i + 1]:
            return i
    return len(boundaries) - 1
def cal_class(A):
    min_A = min(A)
    max_A = max(A)
    interval_length = (max_A - min_A) / 2
    boundaries = [min_A + i * interval_length for i in range(3)]
    grades = [assign_grade(val, boundaries) for val in A]
    return grades

def igwo(bas_mach_sch, bas_asse_sch ,population, bas_mac_rlt, dbas_asse_rlt,parmeters):
    cal_class_avedis = []
    cal_class_result = []
    gery_order = []
    for i in range (3, len(population)):
        bestgewo = rvodam( population)
        all_avedis, results = mainimprove (bestgewo, population[i]) 
        cal_class_avedis .append(all_avedis)
        cal_class_result .append( results)
        gery_order .append( bestgewo )
        
    grade_avedis = cal_class(cal_class_avedis)
    grade_result = cal_class(cal_class_result)
    for idv in range (0, len(population)-3):
        pop = impmethod(grade_avedis[idv],grade_result[idv],gery_order[idv],population[idv+3],bas_mach_sch, bas_asse_sch , bas_mac_rlt, dbas_asse_rlt,parmeters)
        population[idv+3] = pop
    return population

def gwomain(bas_mach_sch, bas_asse_sch ,population,bas_mac_rlt,bas_asse_rlt,parmeters,inter):
    
    origin_pop = copy.deepcopy( population )
    MR = 1- inter/config['iterations']
    for i in range (0,len(population)):
        if random.random() < MR :
            crit_mach_indices, crit_asse_list = neh_critic_addworker ( population[i][0][2], population[i][0][3]) 
            newpop =  add_stage (crit_mach_indices, crit_asse_list, population[i], bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt, parmeters)
            if i == 0:
                if newpop[0][1] < origin_pop[i][0][1]:
                    population[i] = newpop
                else:
                    population[i] = origin_pop[i]
            else:
                population[i] = newpop
    population = igwo(bas_mach_sch, bas_asse_sch ,population,bas_mac_rlt,bas_asse_rlt,parmeters)
    return population