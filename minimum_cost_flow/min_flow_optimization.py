#%%
from __future__ import print_function, absolute_import, division
import pandas as pd 
from time import process_time
import networkx as nx
import graphviz
from graphviz import Digraph
import matplotlib.pyplot as plt
from ortools.graph import pywrapgraph
import os
from builtins import map, range, object, zip, sorted
import sys
import os
from amplpy import AMPL, Environment
os.environ["PATH"] += os.pathsep + 'C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/release/bin'

#%%
t1_start = process_time()
#import libraries
# update to your local repository
data_connections = pd.read_csv("C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/Transportation_Network2.csv") 
data_supply = pd.read_csv("C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/supply2.csv") 
data_demand = pd.read_csv("C:/Users/etjones/Desktop/AI OPS/AIOPS-optimization/demand2.csv") 
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

# G = nx.DiGraph()
# G.add_edges_from(edges)

# H = nx.relabel_nodes(G, NodeDict)
# pos = nx.spring_layout(H)
# nx.draw(H, pos, with_labels=True)
# plt.show()

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
    print('GOOGLE min_cost_flow SOLVER:' + '\n' + 'Minimum cost:', min_cost_flow.OptimalCost())
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


#%% AMPL Model
def main(argc, argv):
    ampl = AMPL(Environment(r'C:\Users\etjones\Desktop\AI OPS\AMPL\amplide.mswin64'))
    os.chdir(os.path.dirname(__file__) or os.curdir)
    try:
        if argc > 1:
            ampl.setOption('solver', argv[1])

        # Read the model and data files.
        #modelDirectory = argv[2] if argc == 3 else os.path.join('..', 'models')
        #ampl.read(os.path.join(modelDirectory, 'diet/diet.mod'))
        #ampl.readData(os.path.join(modelDirectory, 'diet/diet.dat'))
        ampl.read(r'C:\Users\etjones\Desktop\AI OPS\AMPL\custom_models\transp.mod')
        ampl.readData(r'C:\Users\etjones\Desktop\AI OPS\AMPL\custom_models\transp.dat')

        # Solve
        print('\n' + "AMPL MODEL:" + '\n')
        ampl.solve()
        totalcost = ampl.getObjective('Total_Cost')
        print("Minimum Cost:", totalcost.value())
        print('\n' + "Optimal Flow:")
        ampl.display('Trans')
        print('\n' + "Compare pdf flow to the above table to confirm optmial flows")
        #a = ampl.getVariable('Trans')
        #print("Objective is:", a.value())
        

        # Get objective entity by AMPL name
        #totalcost = ampl.getObjective('total_cost')
        # Print it
        #print("Objective is:", totalcost.value())

        # Reassign data - specific instances
        # cost = ampl.getParameter('cost')
        # cost.setValues({'BEEF': 5.01, 'HAM': 4.55})
        # print("Increased costs of beef and ham.")

        # Resolve and display objective
        # ampl.solve()
        # print("New objective value:", totalcost.value())

        # Reassign data - all instances
        # elements = [3, 5, 5, 6, 1, 2, 5.01, 4.55]
        # cost.setValues(elements)
        # print("Updated all costs.")

        # Resolve and display objective
        # ampl.solve()
        # print("New objective value:", totalcost.value())

        # Get the values of the variable Buy in a dataframe object
        # buy = ampl.getVariable('Buy')
        # df = buy.getValues()
        # Print them
        # print(df)

        # Get the values of an expression into a DataFrame object
        # df2 = ampl.getData('{j in FOOD} 100*Buy[j]/Buy[j].ub')
        # # Print them
        # print(df2)
    except Exception as e:
        print(e)
        raise

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)

# RECOMMENDED NEXT STEPS:
# 1. Validate results using AMPL
# 2. Improve Network visualization
# 3. Visualize optimal flow network