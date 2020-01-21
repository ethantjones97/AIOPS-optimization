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
#need to set to your bin
os.environ["PATH"] += os.pathsep + r'C:\Users\etjones\Desktop\AI OPS\AIOPS-optimization\minimum_cost_flow\release\bin'

class network:
    
    def __init__ (self):
        # TODO write initialization for user to set repositories/bins
        self.data_connections = []
        self.data_supply= []
        self.data_demand= []
        self.L = []
        self.NodeDict = {}
        self.start_nodes = []
        self.end_nodes = []
        self.capacities = []
        self.unit_costs = []
        self.edges = []
        self.supply_nodes = []
        self.supply_values = []
        self.demand_nodes = []
        self.demand_values = []
        self.combo_nodes = []
        self.combo_values = []
        self.solution_lol = []
        self.solution_df = []
           
    def define_nodes(self):
        # update to your local repository
        # TODO decide whether or not we are going to use Source/Sink
        self.data_connections = pd.read_csv(r"C:\Users\etjones\Desktop\AI OPS\AIOPS-optimization\minimum_cost_flow\data_files\Transportation_Network2.csv") 
        self.data_supply = pd.read_csv(r"C:\Users\etjones\Desktop\AI OPS\AIOPS-optimization\minimum_cost_flow\data_files\supply2.csv") 
        self.data_demand = pd.read_csv(r"C:\Users\etjones\Desktop\AI OPS\AIOPS-optimization\minimum_cost_flow\data_files\demand2.csv")
        list1 = self.data_connections.start.unique()
        list2 = self.data_connections.end.unique()
        self.L = list(set().union(list1, list2))
        self.NodeDict = {i: self.L[i] for i in range(0, len(self.L))}
        print('NodeDict:', self.NodeDict, '\n')
        for index, row in self.data_connections.iterrows():
            self.start_nodes.append(self.data_connections['start'][index])
            self.end_nodes.append(self.data_connections['end'][index])
            self.capacities.append(self.data_connections['capacities'][index])
            self.unit_costs.append(self.data_connections['unit costs'][index])
        for key, value in self.NodeDict.items():
            for i in range(len(self.start_nodes)):
                if self.start_nodes[i] == value:
                    self.start_nodes[i] = key
            for i in range(len(self.end_nodes)):
                if self.end_nodes[i] == value:
                    self.end_nodes[i] = key 
        print("start nodes:", self.start_nodes, "\n")
        print("end nodes:", self.end_nodes, "\n")
        print("capacities:", self.capacities, "\n")
        print("unit costs:", self.unit_costs, "\n")
    
    def define_edges(self):   
        for ii in range(len(self.start_nodes)):
            self.edges.append((self.start_nodes[ii], self.end_nodes[ii]))
            print("edges:", self.edges, "\n")
    
    def build_network_definition_viz(self):
        f = Digraph('graphviz plot1', filename='transportation network viz')
        f.attr(rankdir='LR', size='8,3') 
        for ii in range(len(self.start_nodes)):
            f.attr('node', shape='circle')
            node1 = self.edges[ii][0]
            node2 = self.edges[ii][1]
            title1 = self.NodeDict[node1]
            title2 = self.NodeDict[node2]
            f.edge(f'{title1}', f'{title2}', label = f'Capacity: {self.capacities[ii]} Cost: {self.unit_costs[ii]}')
        f.view()
        
    def build_supply_vec(self):
         for index, row in self.data_supply.iterrows():
             self.supply_nodes.append(self.data_supply['node'][index])
             self.supply_values.append(self.data_supply['supply'][index])        
         supply_values1 =  [None] * len(self.NodeDict)        
         for ii in range(len(self.NodeDict)):
             if self.NodeDict[ii] in self.supply_nodes:
                 index = self.supply_nodes.index(self.NodeDict[ii])
                 supply_values1[ii] = self.supply_values[index]
             else:
                 supply_values1[ii] = 0                     
         self.supply_values = supply_values1 
         for key, value in self.NodeDict.items():
             for i in range(len(self.supply_nodes)):
                 if self.supply_nodes[i] == value:
                     self.supply_nodes[i] = key
             for i in range(len(self.supply_values)):
                 if self.supply_values[i] == value:
                     self.supply_values[i] = key    
                     
    def build_demand_vec(self):
        for index, row in self.data_demand.iterrows():
              self.demand_nodes.append(self.data_demand['node'][index])
              self.demand_values.append(self.data_demand['demand'][index])
        demand_values1 =  [None] * len(self.NodeDict)
        for ii in range(len(self.NodeDict)):
            if self.NodeDict[ii] in self.demand_nodes:
                index = self.demand_nodes.index(self.NodeDict[ii])
                demand_values1[ii] = self.demand_values[index]
            else:
                demand_values1[ii] = 0     
        self.demand_values = demand_values1
        for key, value in self.NodeDict.items():
            for i in range(len(self.demand_nodes)):
                if self.demand_nodes[i] == value:
                    self.demand_nodes[i] = key
            for i in range(len(self.demand_values)):
                if self.demand_values[i] == value:
                    self.demand_values[i] = key
                    
    def build_combo_vec(self):
        self.combo_nodes = range(len(self.NodeDict))
        self.combo_values = []
        for ii in range(len(self.combo_nodes)): 
            self.combo_values.append(self.supply_values[ii] + self.demand_values[ii]) 
        if sum(self.combo_values) != 0: # TODO fix this logic so that supply can be greater than demand
            raise Exception('The total supply in each of the nodes mush equal the total demand.' + '\n' + 
                            f'Total Demand = {sum(self.demand_values)}' + '\n' +
                            f'Total supply = {sum(self.supply_values)}' + '\n')
    
    def google_soln(self, min_cost_flow = []):
        self.capacities = [int(i) for i in self.capacities]
        self.unit_costs = [int(i) for i in self.unit_costs]
        self.combo_nodes = [int(i) for i in self.combo_nodes]
        self.combo_values = [int(i) for i in self.combo_values]
        self.min_cost_flow = pywrapgraph.SimpleMinCostFlow()
        for ii in range(0, len(self.start_nodes)):
            self.min_cost_flow.AddArcWithCapacityAndUnitCost(self.start_nodes[ii], self.end_nodes[ii], self.capacities[ii], self.unit_costs[ii])
        for ii in range(0, len(self.combo_values)):
            self.min_cost_flow.SetNodeSupply(self.combo_nodes[ii], self.combo_values[ii])   
        if self.min_cost_flow.Solve() == self.min_cost_flow.OPTIMAL:
            print('GOOGLE self.min_cost_flow SOLVER:' + '\n' + 'Minimum cost:', self.min_cost_flow.OptimalCost())
            print('')
            for i in range(self.min_cost_flow.NumArcs()):
              cost = self.min_cost_flow.Flow(i) * self.min_cost_flow.UnitCost(i)
              self.solution_lol.append([self.NodeDict[self.min_cost_flow.Tail(i)],self.NodeDict[self.min_cost_flow.Head(i)]
                                    ,self.min_cost_flow.Flow(i), self.min_cost_flow.Capacity(i),cost])
              col_names = ['From','To','Flow','Capacity','Cost']
              self.solution_df = pd.DataFrame(self.solution_lol,columns = col_names)
        else:
            print('There was an issue with the min cost flow input.')
        export_csv = self.solution_df.to_csv(r'C:\Users\etjones\Desktop\AI OPS\AIOPS-optimization\solution_dataframe.csv',index=False) 
        print(self.solution_df)    
    
    def show_soln(self):  
        g = Digraph('graphviz plot2', filename='solution network viz') # TODO change output to a inline visualization
        # TODO see marginal cost decrease from capacity increase
        g.attr(rankdir='LR', size='8,3')
        for ii in range(len(self.start_nodes)):
            g.attr('node', shape='circle')
            if self.solution_lol[ii][2] != 0:
                node1 = self.solution_lol[ii][0]
                node2 = self.solution_lol[ii][1]
                if self.solution_lol[ii][2] == self.solution_lol[ii][3]:
                    g.edge(f'{node1}', f'{node2}', label = f'Flow: {self.solution_lol[ii][2]} Capacity: {self.solution_lol[ii][3]} Cost: {self.solution_lol[ii][4]}', fontcolor = 'red')
                else:
                    g.edge(f'{node1}', f'{node2}', label = f'Flow: {self.solution_lol[ii][2]} Capacity: {self.solution_lol[ii][3]} Cost: {self.solution_lol[ii][4]}')
        
        g.node('legend', 'Legend: \l' + '   red - channel is at max capacity', shape = 'rectangle', fontsize ='14')
        g.node('mincost', f'Minimum Cost: {self.min_cost_flow.OptimalCost()}', shape = 'rectangle', fontsize ='22',fontcolor='blue')        
        g.view()
     
    def ampl_solve(self, argc, argv):
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
            print('\n' + "AMPL MODEL:" + '\n')
            ampl.solve()
            totalcost = ampl.getObjective('Total_Cost')
            print("Minimum Cost:", totalcost.value())
            print('\n' + "Optimal Flow:")
            ampl.display('Trans')
            print('\n' + "Compare pdf flow to the above table to confirm optmial flows")
        except Exception as e:
            print(e)
            raise
        
if __name__ == '__main__':
    #%%
    network1 = network()
    network1.define_nodes()
    #%%
    network1.define_edges()
    network1.build_network_definition_viz()
    #%%
    network1.build_supply_vec()
    network1.build_demand_vec()
    network1.build_combo_vec()
    #%%
    network1.google_soln()
    network1.show_soln()
    #%%
    network1.ampl_solve(len(sys.argv), sys.argv)
    
    