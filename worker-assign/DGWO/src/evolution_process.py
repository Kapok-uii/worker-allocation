# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 09:21:28 2024

@author: 20140
"""
from gwonewpop import gwomain
from settings import config
from confictsolve import  mainconfict
import copy

def resign(origin_pop, machine_proficiencies, assembly_proficiencies,parmeters,bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt):
    
    def sortAndGetBestIndividual(population,bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt):
        best_individual = None
        best_result = None 
        best_mach_schedul = None
        best_assem_schedul = None
        iterations = config['iterations']
        for i in range(iterations):
            for individual in range(len(population)):
                up_mach_sche, up_asse_sche, up_mach_wker ,up_asse_wker,finresult,criticalmechschedul,machidx, mach_worker_timelines, asse_worker_timelines, basic_pop = mainconfict(bas_mach_sch, bas_asse_sch, bas_mac_rlt, bas_asse_rlt, population[individual])
                population[individual] = basic_pop
                population[individual][0][1] = finresult
                population[individual][0][2] = criticalmechschedul
                population[individual][0][3] = up_asse_sche
                population[individual][0][4] = mach_worker_timelines
                population[individual][0][5] = asse_worker_timelines
                if not best_result or population[individual][0][1] < best_result:
                    best_result = population[individual][0][1]
                    best_individual = copy.deepcopy(population[individual])
            population.sort(key=lambda x: x[0][1])
            population = gwomain (bas_mach_sch, bas_asse_sch ,population,bas_mac_rlt,bas_asse_rlt,parmeters,i)
        return best_individual, best_result, best_mach_schedul, best_assem_schedul
    best_individual, best_result, best_mach_schedul, best_assem_schedul = sortAndGetBestIndividual(origin_pop,bas_mach_sch, bas_asse_sch , bas_mac_rlt, bas_asse_rlt)
    return best_individual, best_result, best_mach_schedul, best_assem_schedul
