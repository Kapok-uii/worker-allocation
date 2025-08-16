from collections import deque
def add_edge(h, e, w, ne, idx, a, b, c):
    e[idx] = b 
    w[idx] = c 
    ne[idx] = h[a] 
    h[a] = idx 
    return idx + 1 

def topsort(n, hs, e, ne, d):
    q = deque()
    for i in range(1, n+1):
        if d[i] == 0:
            q.append(i)
    
    topo_order = []
    while q:
        t = q.popleft()
        topo_order.append(t)
        i = hs[t]
        while i != -1:
            j = e[i]
            d[j] -= 1
            if d[j] == 0:
                q.append(j)
            i = ne[i]
    
    if len(topo_order) == n:
        return topo_order
    else:
        raise ValueError("Graph is not a DAG")

def critical_path(n, hs, ht, e, w, ne, d,N,M):
    ve = [0] * N 
    vl = [float('inf')] * N  
    ee = [0] * M 
    el = [0] * M 
    q = topsort(n, hs, e, ne, d) 

    ve[1] = 0 
    for ver in q:
        i = hs[ver]
        while i != -1:
            j = e[i]
            ve[j] = max(ve[j], ve[ver] + w[i])
            i = ne[i]
    
    vl[q[-1]] = ve[q[-1]]
    for ver in reversed(q):
        i = ht[ver]
        while i != -1:
            j = e[i]
            vl[j] = min(vl[j], vl[ver] - w[i])
            i = ne[i]

    for ver in q:
        i = hs[ver]
        while i != -1:
            ee[i] = ve[ver]
            i = ne[i]

    for ver in reversed(q):
        i = ht[ver]
        while i != -1:
            el[i] = vl[ver] - w[i]
            i = ne[i]

    return ve, vl, ee, el, q

def dfs_v(u, hs, e, vl, ve, path, res, ne):
    path.append(u)
    if hs[u] == -1:
        res.append(path[:])
    i = hs[u]
    while i != -1:
        j = e[i]
        if vl[j] - ve[j] == 0:
            dfs_v(j, hs, e, vl, ve, path, res, ne)
        i = ne[i]
    path.pop()

def dfs_e(u, hs, e, el, ee, edge, edges_result, ne, w):
    i = hs[u]
    while i != -1:
        j = e[i]
        if el[i] - ee[i] == 0:
            edge.append((u, j, w[i]))
            dfs_e(j, hs, e, el, ee, edge, edges_result, ne, w)
            edge.pop()
        i = ne[i]
    if hs[u] == -1 and edge:
        edges_result.append(edge[:])

def output(n, ve, vl, ee, el, idx):
    print("\nve :      ", ve[1:n + 1])
    print("vl :      ", vl[1:n + 1])
    print("vl - ve : ", [vl[i] - ve[i] for i in range(1, n + 1)])
    print("-------------------------------")
    print("ee :      ", ee[:idx:2])
    print("el :      ", el[:idx:2])
    print("el - ee : ", [el[i] - ee[i] for i in range(0, idx, 2)])

def critical_nodes_confirm(edges,n, m):
    N = 10100 
    M = 1000100 
    hs = [-1] * N
    ht = [-1] * N
    e = [0] * M
    w = [0] * M
    ne = [0] * M
    idx = 0
    d = [0] * N
    path = []
    res = []
    edge = []
    edges_result = []

    for a, b, c in edges:
        idx = add_edge(hs, e, w, ne, idx, a, b, c)
        idx = add_edge(ht, e, w, ne, idx, b, a, c)
        d[b] += 1

    ve, vl, ee, el, q = critical_path(n, hs, ht, e, w, ne, d,N,M)
    dfs_v(1, hs, e, vl, ve, path, res, ne)
    dfs_e(1, hs, e, el, ee, edge, edges_result, ne, w)
    node_list=[vl[i] - ve[i] for i in range(1, n + 1)]
    return node_list,ve,vl


    
    
    
