#%%
import pandas as pd 
from time import process_time
import networkx as nx
import graphviz
from graphviz import Digraph
import matplotlib.pyplot as plt
from ortools.graph import pywrapgraph
import os
os.environ["PATH"] += os.pathsep + 'C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/release/bin'

#%%
t1_start = process_time()
#import libraries
# update to your local repository
data_connections = pd.read_csv("C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/Transportation_Network.csv") 
data_supply = pd.read_csv("C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/supply.csv") 
data_demand = pd.read_csv("C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/demand.csv") 
#%%
list1 = data_connections.start.unique()
list2 = data_connections.end.unique()

L = list(set().union(list1, list2))
print(list1)
print(list2)
print(L)

NodeDict = {i: L[i] for i in range(0, len(L))}
print('NodeDict:', NodeDict, '\n')

start_nodes = []
end_nodes = []
capacities = []
unit_costs = []

for index, row in data_connections.iterrows():
    start_nodes.append(data_connections['start'][index])
    end_nodes.append(data_connections['end'][index])
    capacities.append(data_connections['capacities'][index])
    unit_costs.append(data_connections['unit costs'][index])
    
for key, value in NodeDict.items():
    for i in range(len(start_nodes)):
        if start_nodes[i] == value:
            start_nodes[i] = key
    for i in range(len(end_nodes)):
        if end_nodes[i] == value:
            end_nodes[i] = key

print("start nodes:", start_nodes, "\n")
print("end nodes:", end_nodes, "\n")
print("capacities:", capacities, "\n")
print("unit costs:", unit_costs, "\n")
#%%
edges = []
for ii in range(len(start_nodes)):
    edges.append((start_nodes[ii], end_nodes[ii]))
#    edges.append((start_nodes[ii],end_nodes[ii],{'capacity': capacities[ii]},{'cost': costs[ii]}))
print("edges:", edges, "\n")

G = nx.DiGraph()
G.add_edges_from(edges)

H = nx.relabel_nodes(G, NodeDict)
pos = nx.spring_layout(H)
nx.draw(H, pos, with_labels=True)
plt.show()

#%%
f = Digraph('graphviz plot1', filename='transportation network viz')
f.attr(rankdir='LR', size='8,3')

for ii in range(len(start_nodes)):
    f.attr('node', shape='circle')
    node1 = edges[ii][0]
    node2 = edges[ii][1]
    title1 = NodeDict[node1]
    title2 = NodeDict[node2]
    f.edge(f'{title1}', f'{title2}', label = f'Capacity: {capacities[ii]} Cost: {unit_costs[ii]}')

f.view()
#%%

supply_nodes = []
supply_values = []
for index, row in data_supply.iterrows():
    supply_nodes.append(data_supply['node'][index])
    supply_values.append(data_supply['supply'][index])

for key, value in NodeDict.items():
    for i in range(len(supply_nodes)):
        if supply_nodes[i] == value:
            supply_nodes[i] = key
    for i in range(len(supply_values)):
        if supply_values[i] == value:
            supply_values[i] = key

demand_nodes = []
demand_values = []
for index, row in data_demand.iterrows():
    demand_nodes.append(data_demand['node'][index])
    demand_values.append(data_demand['demand'][index])

for key, value in NodeDict.items():
    for i in range(len(demand_nodes)):
        if demand_nodes[i] == value:
            demand_nodes[i] = key
    for i in range(len(demand_values)):
        if demand_values[i] == value:
            demand_values[i] = key

combo_nodes = supply_nodes
combo_values = []
for ii in range(len(combo_nodes)): 
    combo_values.append(supply_values[ii] + demand_values[ii]) 

#%%
#cast to python integers from NumPy integers:
capacities = [int(i) for i in capacities]
unit_costs = [int(i) for i in unit_costs]
combo_nodes = [int(i) for i in combo_nodes]
combo_values = [int(i) for i in combo_values]

min_cost_flow = pywrapgraph.SimpleMinCostFlow()
for ii in range(0, len(start_nodes)):
    min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[ii], end_nodes[ii], capacities[ii], unit_costs[ii])
for ii in range(0, len(combo_values)):
    min_cost_flow.SetNodeSupply(combo_nodes[ii], combo_values[ii])
#%%
#print(min_cost_flow.OPTIMAL)
#print(min_cost_flow.Solve())
#%%
    
solution_lol = [] #initiate solution list of lists
if min_cost_flow.Solve() == min_cost_flow.OPTIMAL:
    print('\n' + 'Minimum cost:', min_cost_flow.OptimalCost())
    print('')
    for i in range(min_cost_flow.NumArcs()):
      cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
      solution_lol.append([NodeDict[min_cost_flow.Tail(i)],NodeDict[min_cost_flow.Head(i)]
                            ,min_cost_flow.Flow(i), min_cost_flow.Capacity(i),cost])
      col_names = ['From','To','Flow','Capacity','Cost']
      solution_df = pd.DataFrame(solution_lol,columns = col_names)

else:
    print('There was an issue with the min cost flow input.')

export_csv = solution_df.to_csv(r'C:\Users\etjones\Desktop\AI OPS\AIOPS-optimization\solution_dataframe.csv',index=False) 
print(solution_df)    
print('\n', "Time =", process_time() - t1_start, "seconds")

#%%
g = Digraph('graphviz plot2', filename='solution network viz')
g.attr(rankdir='LR', size='8,3')

for ii in range(len(start_nodes)):
    g.attr('node', shape='circle')
    if solution_lol[ii][2] != 0:
        node1 = solution_lol[ii][0]
        node2 = solution_lol[ii][1]
        if solution_lol[ii][2] == solution_lol[ii][3]:
            g.edge(f'{node1}', f'{node2}', label = f'Flow: {solution_lol[ii][2]} Capacity: {solution_lol[ii][3]} Cost: {solution_lol[ii][4]}', fontcolor = 'red')
        else:
            g.edge(f'{node1}', f'{node2}', label = f'Flow: {solution_lol[ii][2]} Capacity: {solution_lol[ii][3]} Cost: {solution_lol[ii][4]}')

g.node('legend', 'Legend: \l' + '   red - channel is at max capacity', shape = 'rectangle', fontsize ='14')
g.node('mincost', f'Minimum Cost: {min_cost_flow.OptimalCost()}', shape = 'rectangle', fontsize ='22',fontcolor='blue')

g.view()
# RECOMMENDED NEXT STEPS:
# 1. Validate results using AMPL
# 2. Improve Network visualization
# 3. Visualize optimal flow network