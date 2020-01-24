from amplpy import AMPL, Environment
from graphviz import Digraph
import logging
from ortools.graph import pywrapgraph
from os import remove
from os.path import exists
import pandas as pd 


_LOGGER = logging.getLogger(__file__)
__all__ = ["Network"]


class Network:
    """Define network and run optimization routines.

    Parameters
    ----------
    connections_path : str
        Path to connections data.

    supply_path : str
        Path to supply data.
    
    demand_path : str
        Path to demand data.

    verbose : bool
        Whether to print status of network optimization.
    """
    def __init__(self, 
                 connections_path, 
                 supply_path, 
                 demand_path,
                 verbose=True):        
        # Define attributes
        self.connections_path = connections_path
        self.supply_path      = supply_path
        self.demand_path      = demand_path
        self.verbose          = verbose
        self._network_defined = False
        self._converged       = False


    def __str__(self):
        """Print string representation of class.

        Parameters
        ----------
        None.
        
        Returns
        -------
        str
            Name of class.
        """
        return "Network"


    def _define_nodes(self):
        """Define nodes in network.
        
        Parameters
        ----------
        None.

        Returns
        -------
        self
            Instance of Network.
        """
        # TODO: decide whether or not we are going to use Source/Sink
        try:
            self.data_connections = pd.read_csv(self.connections_path)
        except Exception:
            _LOGGER.exception("error reading connections path " +
                              f"{self.connections_path}")
        try:
            self.data_supply = pd.read_csv(self.supply_path)
        except Exception:
            _LOGGER.exception("error reading supply path " +
                              f"{self.supply_path}")
        try:
            self.data_demand = pd.read_csv(self.demand_path)
        except Exception:
            _LOGGER.exception("error reading demand path " +
                              f"{self.demand_path}")
        
        # Get union of start and end connections and define node dictionary
        nodes = list(
            set().union(
                self.data_connections['start'],
                self.data_connections['end']
            )
        )
        self.node_dict     = dict(zip(range(len(nodes)), nodes))
        self.inv_node_dict = dict(zip(nodes, range(len(nodes))))
        if self.verbose: 
            _LOGGER.info(f"node dictionary: {self.node_dict}")

        # Build network and map string to integer representation      
        func             = lambda x: self.inv_node_dict[x]
        self.start_nodes = list(map(func, self.data_connections['start']))
        self.end_nodes   = list(map(func, self.data_connections['end']))
        self.capacities  = self.data_connections['capacities'].tolist()
        self.unit_costs  = self.data_connections['unit costs'].tolist()
        if self.verbose:
            _LOGGER.info(f"start nodes: {self.start_nodes}")
            _LOGGER.info(f"end nodes: {self.end_nodes}")
            _LOGGER.info(f"capacities: {self.capacities}")
            _LOGGER.info(f"unit costs: {self.unit_costs}")
        return self


    def _define_edges(self): 
        """Define edges in network.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        self
            Instance of Network.
        """  
        self.edges = list(zip(self.start_nodes, self.end_nodes))
        if self.verbose:
            _LOGGER.info(f"edges: {self.edges}")
        return self
    

    def _build_supply_vec(self):
        """Build supply vectors.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        self
            Instance of Network.
        """
        # Get supply nodes and values
        nodes  = self.data_supply['node'].tolist()
        values = self.data_supply['supply'].tolist() 

        # Map supply values back to full node dictionary
        mapper             = dict(zip(nodes, values))
        func               = lambda x: mapper.get(x, 0)
        self.supply_values = list(map(func, self.node_dict.values()))

        # Map supply nodes to integer representation
        func              = lambda x: self.inv_node_dict[x]
        self.supply_nodes = list(map(func, nodes))
        return self        


    def _build_demand_vec(self):
        """Build demand vectors.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        self
            Instance of Network.
        """
        # Get demand nodes and values
        nodes  = self.data_demand['node'].tolist()
        values = self.data_demand['demand'].tolist()

        # Map demand values back to full node dictionary
        mapper             = dict(zip(nodes, values))
        func               = lambda x: mapper.get(x, 0)
        self.demand_values = list(map(func, self.node_dict.values()))

        # Map demand nodes to integer representation
        func              = lambda x: self.inv_node_dict[x]
        self.demand_nodes = list(map(func, nodes))
        return self  


    def _build_combo_vec(self):
        """Build combination vectors.

        Parameters
        ----------
        None.

        Returns
        -------
        self
            Instance of Network.
        """
        # Define combination nodes and values
        self.combo_nodes  = list(range(len(self.node_dict)))
        self.combo_values = list(
            map(lambda x, y: x + y, self.supply_values, self.demand_values) 
        )

        # Check exception
        if sum(self.combo_values) != 0: # TODO fix this logic so that supply can be greater than demand
            raise Exception('The total supply in each of the nodes mush equal the total demand.' + '\n' + 
                            f'Total Demand = {sum(self.demand_values)}' + '\n' +
                            f'Total supply = {sum(self.supply_values)}' + '\n')
        return self


    def build_network(self):
        """Run methods required to build network.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        self
            Instance of Network.
        """
        # Run private methods
        self._define_nodes()
        self._define_edges()
        self._build_supply_vec()
        self._build_demand_vec()
        self._build_combo_vec()
        
        self._network_defined = True
        return self


    def view_network(self, filename=None):
        """Builds network definition visualization.
        
        Parameters
        ----------
        filename : str
            File name used to save network visualization in PDF format.
        
        Returns
        -------
        self
            Instance of Network.
        """
        # Error checking first
        if not self._network_defined:
            _LOGGER.exception("must define network before visualizing")
            raise ValueError
        
        # Build visualization
        f = Digraph(filename=filename)
        f.attr(rankdir='LR', size='8,3')
        for i in range(len(self.start_nodes)):
            f.attr('node', shape='circle')
            start_node  = self.edges[i][0]
            end_node    = self.edges[i][1]
            start_name  = self.node_dict[start_node]
            end_name    = self.node_dict[end_node]
            f.edge(f'{start_name}', 
                   f'{end_name}', 
                   label=f'Capacity: {self.capacities[i]} Cost: {self.unit_costs[i]}')
        f.view()

        # Clean up created files if no filename provided
        if not filename:
            if exists('graphviz plot1.gv.pdf'): remove('graphviz plot1.gv.pdf')

        return self


    def solve(self, save_name=None):
        """Solve network optimization using Google OR tools MinCostFlow solver.
        
        Parameters
        ----------
        save_name : str
            File name used to save network optimization results in csv format.
        
        Returns
        -------
        df_solution : pandas DataFrame
            Optimized solution
        """
        if not self._network_defined: 
            _LOGGER.exception("build network before running solve method")
            raise ValueError

        # Map to integers
        self.capacities   = list(map(int, self.capacities))
        self.unit_costs   = list(map(int, self.unit_costs))
        self.combo_nodes  = list(map(int, self.combo_nodes))
        self.combo_values = list(map(int, self.combo_values))

        # Instantiate solver 
        self.solver = pywrapgraph.SimpleMinCostFlow()
        for i in range(len(self.start_nodes)):
            self.solver.AddArcWithCapacityAndUnitCost(
                self.start_nodes[i], 
                self.end_nodes[i], 
                self.capacities[i], 
                self.unit_costs[i]
                )
        for i in range(len(self.combo_values)):
            self.solver.SetNodeSupply(
                self.combo_nodes[i], 
                self.combo_values[i]
                )   
        
        # If optimal solution found, proceed
        if self.solver.Solve() == self.solver.OPTIMAL:
            if self.verbose:
                _LOGGER.info("Google solver obtained minimum cost = " +
                            f"{self.solver.OptimalCost()}")
            
            self.solution = []
            for i in range(self.solver.NumArcs()):
                cost = self.solver.Flow(i) * self.solver.UnitCost(i)
                self.solution.append([
                    self.node_dict[self.solver.Tail(i)],
                    self.node_dict[self.solver.Head(i)],
                    self.solver.Flow(i), 
                    self.solver.Capacity(i),
                    cost
                    ])
            
            # Convert to dataframe
            columns         = ['From', 'To', 'Flow', 'Capacity', 'Cost']
            df_solution     = pd.DataFrame(self.solution, columns=columns)
            self._converged = True
        else:
            if self.verbose:
                _LOGGER.warn("there was an issue with the min cost flow input")
        
        # Save if specified
        if save_name:
            if not save_name.endswith('.csv'): save_name += '.csv'
            df_solution.to_csv(save_name, index=False)
            if self.verbose:
                _LOGGER.info("results of optimized solution saved to disk " + 
                            f"at {save_name}")
        return df_solution
    

    def view_solution(self, filename=None): 
        """View visual solution of network optimization.
        
        Parameters
        ----------
        None.

        Returns
        -------
        self
            Instance of Network.
        """ 
        if not self._converged: 
            _LOGGER.exception("run solve method before viewing solution")
            raise ValueError

        # TODO: change output to a inline visualization
        g = Digraph(filename=None) 

        # TODO: see marginal cost decrease from capacity increase
        g.attr(rankdir='LR', size='8,3')
        for i in range(len(self.start_nodes)):
            g.attr('node', shape='circle')
            if self.solution[i][2] != 0:
                node1 = self.solution[i][0]
                node2 = self.solution[i][1]
                equal = self.solution[i][2] == self.solution[i][3]
                g.edge(f'{node1}', 
                       f'{node2}', 
                       label=f'Flow: {self.solution[i][2]} ' +
                             f'Capacity: {self.solution[i][3]} ' +
                             f'Cost: {self.solution[i][4]}', 
                       fontcolor='red' if equal else None )
        g.node('legend', 
               'Legend: \l' + '   red - channel is at max capacity', 
               shape='rectangle', 
               fontsize ='14')
        g.node('mincost', 
              f'Minimum Cost: {self.solver.OptimalCost()}', 
              shape='rectangle', 
              fontsize ='22',
              fontcolor='blue')        
        g.view()

        # Clean up created files if no filename provided
        if not filename: 
            if exists('Digraph.gv'): remove('Digraph.gv')
            if exists('Digraph.gv.pdf'): remove('Digraph.gv.pdf')

        return self
     

    def solve_with_ampl(self, argc, argv):
        """ADD HERE.
        
        Parameters
        ----------
        
        Returns
        -------
        """
        raise NotImplementedError("in progress...")
        # ampl = AMPL(Environment(r'C:\Users\etjones\Desktop\AI OPS\AMPL\amplide.mswin64'))
        # os.chdir(os.path.dirname(__file__) or os.curdir)
        # try:
        #     if argc > 1:
        #         ampl.setOption('solver', argv[1])
        #     # Read the model and data files.
        #     #modelDirectory = argv[2] if argc == 3 else os.path.join('..', 'models')
        #     #ampl.read(os.path.join(modelDirectory, 'diet/diet.mod'))
        #     #ampl.readData(os.path.join(modelDirectory, 'diet/diet.dat'))
        #     ampl.read(r'C:\Users\etjones\Desktop\AI OPS\AMPL\custom_models\transp.mod')
        #     ampl.readData(r'C:\Users\etjones\Desktop\AI OPS\AMPL\custom_models\transp.dat')
        #     print('\n' + "AMPL MODEL:" + '\n')
        #     ampl.solve()
        #     totalcost = ampl.getObjective('Total_Cost')
        #     print("Minimum Cost:", totalcost.value())
        #     print('\n' + "Optimal Flow:")
        #     ampl.display('Trans')
        #     print('\n' + "Compare pdf flow to the above table to confirm optmial flows")
        # except Exception as e:
        #     print(e)
        #     raise    