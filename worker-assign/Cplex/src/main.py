# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 22:14:46 2025
@author: 20140
"""

from docplex.mp.model import Model
import pandas as pd
file_path = 'A2.xlsx'  # A1;A2;A3;A4, Four different instances

params_df = pd.read_excel(file_path, sheet_name='Parameters')
params_dict = dict(zip(params_df['Parameter'], params_df['Value']))
num_products = int(params_dict['num_products'])
num_machines = int(params_dict['num_machines'])
num_workstations = int(params_dict['num_workstations'])
num_assembly_workers = int(params_dict['num_assembly_workers'])
num_machining_workers = int(params_dict['num_machining_workers'])
max_events = int(params_dict['max_events'])
BIG_M = int(params_dict['BIG_M'])

P = range(num_products)
M = range(num_machines)
W = range(num_workstations)
T_a = range(num_assembly_workers)
T_r = range(num_machining_workers)
K_r = range(max_events)
K_a = range(max_events)
L = range(max_events)
K_m = range(max_events)

n_pw_df = pd.read_excel(file_path, sheet_name='n_pw')
n_pw = {(int(row['Product']), int(row['Workstation'])): int(row['Num_Workers']) 
        for _, row in n_pw_df.iterrows()}

n_ocp_df = pd.read_excel(file_path, sheet_name='n_ocp')
n_ocp = {(int(row['Product']), int(row['Component']), int(row['Operation'])): int(row['Num_Workers']) 
         for _, row in n_ocp_df.iterrows()}

t_ocp_df = pd.read_excel(file_path, sheet_name='t_ocp')
t_ocp = {(int(row['Product']), int(row['Component']), int(row['Operation'])): int(row['Processing_Time']) 
         for _, row in t_ocp_df.iterrows()}

t_pw_df = pd.read_excel(file_path, sheet_name='t_pw')
t_pw = {(int(row['Product']), int(row['Workstation'])): int(row['Processing_Time']) 
        for _, row in t_pw_df.iterrows()}

transfer_time_df = pd.read_excel(file_path, sheet_name='transfer_time')
transfer_time = {(int(row['Product']), int(row['Component'])): int(row['Transfer_Time']) 
                 for _, row in transfer_time_df.iterrows()}

skill_assembly_df = pd.read_excel(file_path, sheet_name='skill_assembly', index_col=0)
skill_assembly = skill_assembly_df.values.tolist()

skill_machining_df = pd.read_excel(file_path, sheet_name='skill_machining', index_col=0)
skill_machining = skill_machining_df.values.tolist()

lambda_w_df = pd.read_excel(file_path, sheet_name='lambda_w')
lambda_w = {int(row['Workstation']): float(row['Efficiency']) 
            for _, row in lambda_w_df.iterrows()}

lambda_m_df = pd.read_excel(file_path, sheet_name='lambda_m')
lambda_m = {int(row['Machine']): float(row['Efficiency']) 
            for _, row in lambda_m_df.iterrows()}

machine_tasks = {}
for m in M:
    sheet_name = f'Machine_{m}_Tasks'
    tasks_df = pd.read_excel(file_path, sheet_name=sheet_name)
    machine_tasks[m] = [tuple(map(int, row)) for _, row in tasks_df.iterrows()]

assembly_tasks = {}
for w in W:
    sheet_name = f'Workstation_{w}_Tasks'
    tasks_df = pd.read_excel(file_path, sheet_name=sheet_name)
    assembly_tasks[w] = [tuple(map(int, row)) for _, row in tasks_df.iterrows()]

C_p = {}
for p in P:
    components = set()
    for (prod, comp, op) in n_ocp.keys():
        if prod == p:
            components.add(comp)
    C_p[p] = sorted(list(components))

O_cp = {}
for (p, c, o) in n_ocp.keys():
    key = (p, c)
    if key not in O_cp:
        O_cp[key] = []
    O_cp[key].append(o)

for key in O_cp:
    O_cp[key] = sorted(O_cp[key])

z_ocpm = {}
for m in M:
    for idx, (p, c, o) in enumerate(machine_tasks.get(m, [])):
        z_ocpm[p, c, o, m] = 1  # 固定分配到指定机器

b_cpw = {}
for p in P:
    for c in C_p[p]:
        for w in W:
            b_cpw[p, c, w] = 1 if w == c % num_workstations else 0

model = Model('WAAJ_Optimization_McCormick_v2')

z_pwa = model.binary_var_dict([(p, w, a) for p in P for w in W for a in T_a], name='z_pwa')
z_ocpr = model.binary_var_dict([(p, c, o, r) for p, jobs in C_p.items() for c in jobs for o in O_cp.get((p,c), []) for r in T_r], name='z_ocpr')

X_ocprk = model.binary_var_dict([(p, c, o, r, k) for p, jobs in C_p.items() for c in jobs for o in O_cp.get((p,c), []) for r in T_r for k in K_r], name='X_ocprk')
X_pwak = model.binary_var_dict([(p, w, a, k) for p in P for w in W for a in T_a for k in K_a], name='X_pwak')

Lambda_ocp_S = model.continuous_var_dict([(p, c, o) for p, jobs in C_p.items() for c in jobs for o in O_cp.get((p,c), [])], lb=0, name='Lambda_ocp_S')
Lambda_ocp_E = model.continuous_var_dict([(p, c, o) for p, jobs in C_p.items() for c in jobs for o in O_cp.get((p,c), [])], lb=0, name='Lambda_ocp_E')
Lambda_pw_S = model.continuous_var_dict([(p, w) for p in P for w in W], lb=0, name='Lambda_pw_S')
Lambda_pw_E = model.continuous_var_dict([(p, w) for p in P for w in W], lb=0, name='Lambda_pw_E')

V_mt_S = model.continuous_var_dict([(m, t) for m in M for t in K_m], lb=0, name='V_mt_S')
V_mt_E = model.continuous_var_dict([(m, t) for m in M for t in K_m], lb=0, name='V_mt_E')
F_rk_S = model.continuous_var_dict([(r, k) for r in T_r for k in K_r], lb=0, name='F_rk_S')
F_ak_S = model.continuous_var_dict([(a, k) for a in T_a for k in K_a], lb=0, name='F_ak_S')

active_rk = model.binary_var_dict([(r, k) for r in T_r for k in K_r], name='active_rk')
active_ak = model.binary_var_dict([(a, k) for a in T_a for k in K_a], name='active_ak')

makespan = model.continuous_var(name='makespan')

Y_ocprk_delta = model.continuous_var_dict(
    [(p, c, o, r, k) for p in P for c in C_p.get(p, []) for o in O_cp.get((p, c), []) for r in T_r for k in K_r],
    lb=0,
    name='Y_ocprk_delta'
)

Y_pwak_delta = model.continuous_var_dict(
    [(p, w, a, k) for p in P for w in W for a in T_a for k in K_a],
    lb=0,
    name='Y_pwak_delta'
)

model.minimize(makespan)

for p in P:
    for w in W:
        model.add(model.sum(z_pwa[p, w, a] for a in T_a) <= n_pw[p, w])
    
    for c in C_p[p]:
        for o in O_cp.get((p, c), []):
            model.add(model.sum(z_ocpr[p, c, o, r] for r in T_r) <= n_ocp[p, c, o])

for p in P:
    for w in W:
        for a in T_a:
            if skill_assembly[w][a] == 0:
                model.add(z_pwa[p, w, a] == 0)
    
    for c in C_p[p]:
        for o in O_cp.get((p, c), []):
            assigned_machine = next(m for m in M if z_ocpm.get((p, c, o, m), 0) == 1)
            for r in T_r:
                if skill_machining[assigned_machine][r] == 0:
                    model.add(z_ocpr[p, c, o, r] == 0)

for p in P:
    for c in C_p[p]:
        for o in O_cp.get((p, c), []):
            for r in T_r:
                model.add(model.sum(X_ocprk[p, c, o, r, k] for k in K_r) == z_ocpr[p, c, o, r])
    
    for w in W:
        for a in T_a:
            model.add(model.sum(X_pwak[p, w, a, k] for k in K_a) == z_pwa[p, w, a])

for r in T_r:
    for k in K_r:
        model.add(model.sum(X_ocprk[p, c, o, r, k] for p in P for c in C_p.get(p, []) for o in O_cp.get((p, c), [])) <= 1)
        model.add(active_rk[r, k] == model.sum(X_ocprk[p, c, o, r, k] for p in P for c in C_p.get(p, []) for o in O_cp.get((p, c), [])))
        if k < max_events - 1:
            model.add(active_rk[r, k] >= active_rk[r, k+1])

for a in T_a:
    for k in K_a:
        model.add(model.sum(X_pwak[p, w, a, k] for p in P for w in W) <= 1)
        model.add(active_ak[a, k] == model.sum(X_pwak[p, w, a, k] for p in P for w in W))
        if k < max_events - 1:
            model.add(active_ak[a, k] >= active_ak[a, k+1])

for p in P:
    for w in W:
        effective_workers = sum(z_pwa[p, w, a] * skill_assembly [w][a] for a in T_a)
        t_pw_eff = t_pw[p, w] * (1 - lambda_w[w] * effective_workers)
        model.add(Lambda_pw_E[p, w] == Lambda_pw_S[p, w] + t_pw_eff)

    for c in C_p[p]:
        for o in O_cp.get((p, c), []):
            m = next(m for m in M if z_ocpm.get((p, c, o, m), 0) == 1)
            effective_workers = model.sum(z_ocpr[p, c, o, r] * skill_machining[m][r]for r in T_r)
            t_ocp_eff = t_ocp[p, c, o] * (1 - lambda_m[m] * effective_workers)
            model.add(Lambda_ocp_E[p, c, o] == Lambda_ocp_S[p, c, o] + t_ocp_eff)

for m in M:
    tasks = machine_tasks.get(m, [])
    for i in range(len(tasks)-1):
        p_prev, c_prev, o_prev = tasks[i]
        p_next, c_next, o_next = tasks[i+1]
        model.add(Lambda_ocp_E[p_prev, c_prev, o_prev] <= Lambda_ocp_S[p_next, c_next, o_next])
        
for p in P:
    for c in C_p[p]:
        operations = sorted(O_cp.get((p, c), []))
        for i in range(len(operations)-1):
            o_prev = operations[i]
            o_next = operations[i+1]
            model.add(Lambda_ocp_E[p, c, o_prev] <= Lambda_ocp_S[p, c, o_next])

for p in P:
    for c in C_p[p]:
        last_operation = max(O_cp.get((p, c), [0]))
        assembly_workstation = c % num_workstations
        model.add(Lambda_ocp_E[p, c, last_operation] + transfer_time[p, c] <= Lambda_pw_S[p, assembly_workstation])

for w in W:
    tasks = assembly_tasks.get(w, [])
    for i in range(len(tasks)-1):
        p_prev, c_prev = tasks[i]
        p_next, c_next = tasks[i+1]
        model.add(Lambda_pw_E[p_prev, w] <= Lambda_pw_S[p_next, w])

for p in P:
    for w in range(len(W)-1):
        model.add(Lambda_pw_E[p, w] <= Lambda_pw_S[p, w+1])

for a in T_a:
    for p1 in P:
        for w1 in W:
            for p2 in P:
                for w2 in W:
                    if (p1, w1) < (p2, w2): 
                        overlap = model.binary_var(name=f'overlap_{a}_{p1}_{w1}_{p2}_{w2}')
                        model.add(Lambda_pw_S[p1, w1] <= Lambda_pw_E[p2, w2] + BIG_M*(1 - overlap))
                        model.add(Lambda_pw_S[p2, w2] <= Lambda_pw_E[p1, w1] + BIG_M*(1 - overlap))
                        model.add(z_pwa[p1, w1, a] + z_pwa[p2, w2, a] <= 1 + (1 - overlap))

for p in P:
    for c in C_p.get(p, []):
        for o in O_cp.get((p, c), []):
            delta_ocp = Lambda_ocp_E[p, c, o] - Lambda_ocp_S[p, c, o]
            delta_lower = 0
            delta_upper = t_ocp[p, c, o]
            for r in T_r:
                for k in K_r:
                    X = X_ocprk[p, c, o, r, k]
                    Y = Y_ocprk_delta[p, c, o, r, k]
                    model.add(Y <= X * delta_upper)
                    model.add(Y >= X * delta_lower)
                    model.add(Y <= delta_ocp - (1 - X) * delta_lower)
                    model.add(Y >= delta_ocp - (1 - X) * delta_upper)

    for w in W:
        for a in T_a:
            for k in K_a:
                X = X_pwak[p, w, a, k]
                delta_pw = Lambda_pw_E[p, w] - Lambda_pw_S[p, w]
                delta_lower = 0
                delta_upper = t_pw[p, w]
                Y = Y_pwak_delta[p, w, a, k]
                model.add(Y <= X * delta_upper)
                model.add(Y >= X * delta_lower)
                model.add(Y <= delta_pw - (1 - X) * delta_lower)
                model.add(Y >= delta_pw - (1 - X) * delta_upper)

for r in T_r:
    model.add(F_rk_S[r, 0] >= 0)
    for k in range(1, max_events):
        model.add(F_rk_S[r, k] >= F_rk_S[r, k-1] + 
                 model.sum(Y_ocprk_delta[p, c, o, r, k-1] 
                          for p in P for c in C_p.get(p, []) for o in O_cp.get((p, c), [])))

for a in T_a:
    model.add(F_ak_S[a, 0] >= 0)
    for k in range(1, max_events):
        model.add(F_ak_S[a, k] >= F_ak_S[a, k-1] + 
                 model.sum(Y_pwak_delta[p, w, a, k-1] 
                          for p in P for w in W))

for r in T_r:
    for k in range(max_events - 2):
        model.add(F_rk_S[r, k] <= F_rk_S[r, k+1])

for a in T_a:
    for k in range(max_events - 2):
        model.add(F_ak_S[a, k] <= F_ak_S[a, k+1])
        
for p in P:
    for c in C_p[p]:
        for o in O_cp.get((p, c), []):
            for r in T_r:
                for k in K_r:
                    model.add(Lambda_ocp_S[p, c, o] >= F_rk_S[r, k] - BIG_M * (1 - X_ocprk[p, c, o, r, k]))
                    model.add(Lambda_ocp_S[p, c, o] <= F_rk_S[r, k] + BIG_M * (1 - X_ocprk[p, c, o, r, k]))

for p in P:
    for w in W:
        for a in T_a:
            for k in K_a:
                model.add(Lambda_pw_S[p, w] >= F_ak_S[a, k] - BIG_M * (1 - X_pwak[p, w, a, k]))
                model.add(Lambda_pw_S[p, w] <= F_ak_S[a, k] + BIG_M * (1 - X_pwak[p, w, a, k]))

for p in P:
    for c in C_p[p]:
        for o in O_cp.get((p, c), []):
            model.add(makespan >= Lambda_ocp_E[p, c, o])
    for w in W:
        model.add(makespan >= Lambda_pw_E[p, w])

for p in P:
    for c in C_p[p]:
        operations = sorted(O_cp.get((p, c), []))
        machine_assignments = {}
        for o in operations:
            for m in M:
                if (p, c, o, m) in z_ocpm and z_ocpm[p, c, o, m] == 1:
                    machine_assignments[o] = m
                    break
        for i in range(len(operations)-1):
            o_prev = operations[i]
            o_next = operations[i+1]
            m_prev = machine_assignments[o_prev]
            m_next = machine_assignments[o_next]
            
            model.add(Lambda_ocp_E[p, c, o_prev] <= Lambda_ocp_S[p, c, o_next])
            if m_prev != m_next:
                model.add(Lambda_ocp_E[p, c, o_prev] + transfer_time[p, c] <= Lambda_ocp_S[p, c, o_next])

model.parameters.timelimit = 1800
model.parameters.mip.strategy.search = 1
model.parameters.threads = 4

solution = model.solve(log_output=True)

if solution:
    print(f"\n  Optimal makespan {makespan.solution_value:.2f}")
    
    print("\n【Processing task schedule】")
    for m in M:
        print(f"\n Machine {m} task order:")
        for (p, c, o) in machine_tasks.get(m, []):
            start = Lambda_ocp_S[p, c, o].solution_value
            end = Lambda_ocp_E[p, c, o].solution_value
            workers = [r for r in T_r if z_ocpr[p, c, o, r].solution_value > 0.9]
            print(f"  operation ({p},{c},{o}): {start:.2f} - {end:.2f} | worker: {workers}")
    
    print("\n【Assembly task schedule】")
    for w in W:
        print(f"\n workstation {w} task order:")
        for (p, c) in assembly_tasks.get(w, []):
            start = Lambda_pw_S[p, w].solution_value
            end = Lambda_pw_E[p, w].solution_value
            workers = [a for a in T_a if z_pwa[p, w, a].solution_value > 0.9]
            print(f"  product{p} parts{c}: {start:.2f} - {end:.2f} | worker: {workers}")

else:
    print("No optimal solution found")
    if model.solve_details.status == "infeasible":
        print("\n  Analysis of the reasons for the infeasibility of the model:")
        conflict = model.refine_conflict()
        conflict.display()