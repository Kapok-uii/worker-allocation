# -*- coding: utf-8 -*-
"""
Created on Thu May 23 10:42:17 2024

@author: 20140
"""
from criticalprocess import critical_nodes_confirm
from settings import config

def convert_jsp_result_to_nodes(jsp_result):
    operation_counter = {}
    node_machine_dur = []
    node_machine = []

    for machine_num, machine in enumerate(jsp_result):
        for start_time, end_time, product, task_num in machine:
            duration = end_time - start_time
            node_machine_dur.append([product, task_num, machine_num, start_time, duration])

    node_machine_dur.sort(key=lambda x: x[3])

    for product, task_num, machine_num, start_time, duration in node_machine_dur:
        if product not in operation_counter:
            operation_counter[product] = {}
        if task_num not in operation_counter[product]:
            operation_counter[product][task_num] = 0

        operation = operation_counter[product][task_num]
        node = [product, task_num, operation]
        node_machine.append([node, duration, machine_num, start_time])

        operation_counter[product][task_num] += 1
    return node_machine

def convert_jsp_order_to_edges(node_machine, product_num, dur_num):
    all_order_edge = []

    for proith in range(product_num):
        for durith in range(dur_num):
            order_edge = [taski for taski in node_machine if taski[0][0] == proith and taski[0][1] == durith]
            for ith in range(len(order_edge) - 1):
                all_order_edge.append((order_edge[ith][0], order_edge[ith + 1][0], order_edge[ith][1]))

    return all_order_edge

def convert_jsp_result_to_edges(node_machine, machine_num):
    all_machine_edge = []

    for j in range(machine_num):
        machine_edge = [tasks for tasks in node_machine if tasks[2] == j]
        machine_edge.sort(key=lambda x: x[3])
        for ith in range(len(machine_edge) - 1):
            all_machine_edge.append((machine_edge[ith][0], machine_edge[ith + 1][0], machine_edge[ith][1]))

    return all_machine_edge


def map_list_to_int(input_list):
    mapped_dict = {} 
    mapped_list = []
    count = 1 
    for sub_list in input_list:
        mapped_sub_list = [] 
        for sub_item in sub_list:
            if isinstance(sub_item, list): 
                sub_item_tuple = tuple(sub_item)
                if sub_item_tuple not in mapped_dict: 
                    mapped_dict[sub_item_tuple] = count
                    count += 1 
                mapped_sub_list.append(mapped_dict[sub_item_tuple]) 
            else:
                mapped_sub_list.append(sub_item) 
        mapped_list.append(tuple(mapped_sub_list)) 

    return mapped_list, mapped_dict

def add_virtual_nodes_and_edges(node_machine, product_num, dur_num):
    virtual_start_node = [1]
    virtual_edges_first = []
    first_operations = {}
    for node in node_machine:
        product, task_num, operation = node[0]
        if product not in first_operations:
            first_operations[product] = {}
        if task_num not in first_operations[product]:
            first_operations[product][task_num] = node
    for product in first_operations:
        for task_num in first_operations[product]:
            first_op = first_operations[product][task_num][0]
            virtual_edges_first.append((virtual_start_node, first_op, 0))


    return virtual_edges_first
def add_JSP_fsp_aged(node_machine, fsp_result,product_num,dur_num):
    last_operations = {}
    result=[]
    for node in node_machine:
        product, task_num, operation = node[0]
        if product not in last_operations:
            last_operations[product] = {}
        last_operations[product][task_num] = node

    for product, tasks in last_operations.items():
        for task_num, operation in tasks.items():
            for task_group in fsp_result:
                for task in task_group:
                    task_product, task_number = task[0]
                    if product == task_product and (task_num == 2*task_number  or task_num == (2*task_number+1)):
                        combined = (operation[0], task[0], operation[1])
                        result.append(combined)
    return result

def fsp_result_to_edges(fsp_result ):
    same_list_result = []
    diff_list_result = []
    for sublist in fsp_result:
        for i in range(len(sublist) - 1):
            node1 = sublist[i][0]
            node2 = sublist[i + 1][0]
            weight = sublist[i ][1]
            same_list_result.append((node1, node2, weight))
        last_node = sublist[-1][0]
        weight = sublist[-1][1]
        same_list_result.append((last_node, [56], weight))
    if len(fsp_result) > 1:
        for i in range(min(len(fsp_result[0]), len(fsp_result[1]))):
            node1 = fsp_result[0][i][0]
            node2 = fsp_result[1][i][0]
            weight = fsp_result[0][i][1]
            diff_list_result.append((node1, node2, weight))
    return  same_list_result,diff_list_result

def map_int_to_list(critical_nodes, mapped_dict):
    produ_operation_order = []
    for index, value in enumerate(critical_nodes):
        if value < 0.000001: # considering float number
            key_index = index + 1
            for key, val in mapped_dict.items():
                if val == key_index:
                    produ_operation_order.append(key)
                    break
    
    if len(produ_operation_order) > 1:
        produ_operation_order = produ_operation_order[1:-1]
    return produ_operation_order

def seek_critical_function(jsp_result ,fsp_result):
    process_num = config['process_num']
    product_num= config['product_num']
    machine_number= config['machine_num']
    node_machine_dur = convert_jsp_result_to_nodes(jsp_result)
    jsp_to_fsp_edge= add_JSP_fsp_aged(node_machine_dur,fsp_result,product_num, process_num)
    all_machine_edge = convert_jsp_result_to_edges(node_machine_dur, machine_number)
    all_order_edge = convert_jsp_order_to_edges(node_machine_dur, product_num, process_num)
    virtual_edges_first = add_virtual_nodes_and_edges(node_machine_dur, product_num,process_num)
    fsp_same_product_result,fsp_diff_product_result=fsp_result_to_edges(fsp_result)
    combined_edges =  virtual_edges_first+all_order_edge + all_machine_edge +jsp_to_fsp_edge+fsp_diff_product_result+fsp_same_product_result
    edges, mapped_dict = map_list_to_int(combined_edges) 
    critical_list,ve,vl=critical_nodes_confirm(edges, len( mapped_dict),len(combined_edges))
    critical_nodes = map_int_to_list(critical_list, mapped_dict)
    return critical_nodes[:-1]
