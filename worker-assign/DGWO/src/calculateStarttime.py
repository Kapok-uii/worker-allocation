def calculate_earliest_start_time(tasks,product_index ,task_index , workstation_departure_times, finaltime_to_assemblystage):
    (product_id, workstation_id), duration, scheduled_start_time = tasks[product_index][task_index]
    if product_index == 0 and task_index == 0:
        start_time = scheduled_start_time 
    else:
        start_time = find_start_time(tasks[product_index],product_index, task_index, workstation_departure_times, finaltime_to_assemblystage)
    return start_time
def find_start_time(product_tasks, product_index, task_index, workstation_departure_times , finaltime_to_assemblystage):
    (_, workstation_id), duration, _ = product_tasks[task_index]
    start_time = 0
    if task_index > 0:
        prev_task = product_tasks[task_index - 1]
        prev_end_time = prev_task[2] + prev_task[1]
        start_time = max(start_time, prev_end_time,  finaltime_to_assemblystage[product_index][task_index])
    start_time = max(start_time, workstation_departure_times[workstation_id])
    return start_time
