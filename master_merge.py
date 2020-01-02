#%%
#import libraries
import pandas as pd 
import networkx as nx
import matplotlib.pyplot as plt
from ortools.graph import pywrapgraph
# update to your local repository
data = pd.read_csv("C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/Transportation_Network.csv") 

list1 = data.start.unique()
list2 = data.end.unique()

L = list(set().union(list1, list2))
print(list1)
print(list2)
print(L)

NodeDict = {i: L[i] for i in range(0, len(L))}
print('NodeDict:', NodeDict, '/n')

start_nodes = []
end_nodes = []
capacities = []
unit_costs = []

for index, row in data.iterrows():
    start_nodes.append(data['start'][index])
    end_nodes.append(data['end'][index])
    capacities.append(data['capacities'][index])
    unit_costs.append(data['unit costs'][index])
    
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
# CHEATING and definina all resources at the source to start. we need to find a way to have the user input this in the csv, then we can ingest it. 

supplies = [0, 0, 0, 0, 0, 0, 0, 0, 0, 10000, 0, 0]

#cast to python integers from NumPy integers:
capacities = [int(i) for i in capacities]
unit_costs = [int(i) for i in unit_costs]

min_cost_flow = pywrapgraph.SimpleMinCostFlow()
for ii in range(0, len(start_nodes)):
    min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[ii], end_nodes[ii], capacities[ii], unit_costs[ii])
for i in range(0, len(supplies)):
    min_cost_flow.SetNodeSupply(i, supplies[i])
#%%
print(min_cost_flow.OPTIMAL)
print(min_cost_flow.Solve())
#%%
if min_cost_flow.Solve() == min_cost_flow.OPTIMAL:
    print('Minimum cost:', min_cost_flow.OptimalCost())
    print('')
    print('  Arc    Flow / Capacity  Cost')
    for i in range(min_cost_flow.NumArcs()):
      cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
      print('%1s -> %1s   %3s  / %3s       %3s' % (
          min_cost_flow.Tail(i),
          min_cost_flow.Head(i),
          min_cost_flow.Flow(i),
          min_cost_flow.Capacity(i),
          cost))
else:
    print('There was an issue with the min cost flow input.')
