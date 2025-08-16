import copy
from collections import defaultdict
def resolve_blocking_scheduling(tasks, num_workstations):
    def find_start_time(product_tasks, task_index, workstation_departure_times):
        (_, workstation_id), duration, _ = product_tasks[task_index]
        start_time = 0
        if task_index > 0:
            prev_task = product_tasks[task_index - 1]
            prev_end_time = prev_task[2] + prev_task[1]
            start_time = max(start_time, prev_end_time)
        start_time = max(start_time, workstation_departure_times[workstation_id])
        
        return start_time
    workstation_departure_times = {i: 0 for i in range(num_workstations)}
    adjusted_tasks = [[] for _ in range(len(tasks))]
    for product_index, product_tasks in enumerate(tasks):
        for task_index, task in enumerate(product_tasks):
            (product_id, workstation_id), duration, scheduled_start_time = task
            if product_index == 0:
                start_time = scheduled_start_time
            else:
                start_time = find_start_time(product_tasks, task_index, workstation_departure_times)
            end_time = start_time + duration
            adjusted_tasks[product_index].append((task[0], duration, start_time))
            if task_index < num_workstations - 1:
                next_start_time = find_start_time(product_tasks, task_index + 1, workstation_departure_times)
                departure_time = max(end_time, next_start_time)
            else:
                departure_time = end_time
            workstation_departure_times[workstation_id] = departure_time

    for product_index in range(1, len(tasks)):
        prev_product_tasks = adjusted_tasks[product_index - 1]
        current_product_tasks = adjusted_tasks[product_index]
        for task_index in range(num_workstations):
            current_task = current_product_tasks[task_index]
            prev_task = prev_product_tasks[task_index]
            (_, workstation_id), duration, start_time = current_task
            (_, prev_workstation_id), prev_duration, prev_start_time = prev_task
            
            prev_end_time = prev_start_time + prev_duration
            if start_time < prev_end_time:
                start_time = prev_end_time
                end_time = start_time + duration
                current_product_tasks[task_index] = (current_task[0], duration, start_time)
                
                if task_index < num_workstations - 1:
                    next_start_time = find_start_time(current_product_tasks, task_index + 1, workstation_departure_times)
                    departure_time = max(end_time, next_start_time)
                else:
                    departure_time = end_time
                workstation_departure_times[workstation_id] = departure_time

    max_completion_time = 0
    for product_tasks in adjusted_tasks:
        for task in product_tasks:
            (_, workstation_id), duration, start_time = task
            end_time = start_time + duration
            if end_time > max_completion_time:
                max_completion_time = end_time

    return adjusted_tasks, max_completion_time


def calculateMakespan_Assembly(pop_individual,finaltime_to_assemblystage,assembly_times):
    produc_order=pop_individual[0][0]
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
    adjusted_tasks, max_completion_time = resolve_blocking_scheduling(machine_operations_all, num_workstations=2)

    return adjusted_tasks, max_completion_time

def calculateMakespan_Flowline(product_num,table):
    task_times = defaultdict(lambda: defaultdict(int))
    for task_list in table: 
        for task in task_list:
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

def calculateMakespan(times, machines,  config , process_num,product_num,machine_number):
    time_table = []
    times = copy.deepcopy(times)
    machines = copy.deepcopy(machines)
    for i in range(machine_number):
        time_table.append([])

    current_times = [[0 for _ in range(process_num)] for _ in range(product_num)]
    total_time = 0
    for j in config[1]:
        prod=j[0]
        job=j[1]
        current_machine = machines[prod][job].pop(0)
        current_time = current_times[prod][job]
        machine_usage = time_table[current_machine]
        usage_time = times[prod][job].pop(0)
        current_time, total_time = fillTimeSlot(machine_usage, current_time, usage_time,prod, job, total_time)
        current_times[prod][job] = current_time
    return total_time, time_table 

def fillTimeSlot(machine_usage, current_time, usage_time,prod, job, total_time):
    if len(machine_usage) > 0:
        prev = 0 
        slot = None 
        for used_slots in machine_usage:
            start = used_slots[0]
            end = used_slots[1]
            if start < current_time < end:
                current_time = end
            if prev == 0 and start > current_time + usage_time:
                slot = [current_time, usage_time + current_time, prod,job]
                break
            elif start - prev >= usage_time and current_time <= prev:
                slot = [current_time, current_time + usage_time,prod, job]
                break
            prev = end 
            if end > current_time:
                current_time = end
        if slot is None:
            slot = [current_time, current_time + usage_time,prod, job]
        current_time = slot[1]
        machine_usage.append(slot)
        machine_usage.sort(key=lambda x: x[1])
        if slot[1] > total_time:
            total_time = slot[1]
    else: 
        machine_usage.append([current_time, usage_time + current_time, prod, job])
        current_time += usage_time

    return current_time, total_time
