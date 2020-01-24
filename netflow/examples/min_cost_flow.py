from os.path import join
from pathlib import Path

# Package imports
from netflow import Network

DATA_DIR = join(Path(__file__).resolve().parent, "data")

def main():
    """Toy example demonstration of network optimization.
    """
    # Define network based on configuration files
    network = Network(
        connections_path=join(DATA_DIR, "transportation_network2.csv"),
        supply_path=join(DATA_DIR, "supply2.csv"),
        demand_path=join(DATA_DIR, "demand2.csv")
        )

    # Build network based on definitions in .csv files
    network.build_network()

    # Visualize network to ensure proper structure
    network.view_network()

    # Solve optimization problem
    network.solve()

    # View solution
    network.view_solution()

    # Compare with AMPL
    # network.solve_with_ampl(len(sys.argv), sys.argv)

if __name__ == "__main__":
    main()