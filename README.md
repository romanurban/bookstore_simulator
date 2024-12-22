Bookstore Simulator and Optimization Project
This project consists of a simulation of a bookstore with customer interactions and an optimization module to improve restocking decisions using Timefold.

Project Structure
1. simulator/ (Phase 1: Bookstore Simulation)
Handles the simulation of a bookstore, including inventory management and customer purchasing behavior.

Files:
inventory.py
Manages the bookstore inventory.
Key Features:
Load book data from a dataset.
Manage stock levels and restocking.
Provide sales data for analysis.
customer.py
Simulates customer behavior in the bookstore.
Key Features:
Define customer preferences (e.g., genres, price range).
Simulate book purchases based on preferences.
Interact with the inventory system.
main.py
The central script to run the bookstore simulation.
Key Features:
Initialize the inventory and customers.
Simulate customer visits and purchases over several days.
Generate reports on daily revenue and inventory changes.

2. optimization/ (Phase 2: Restocking Optimization)
Implements the optimization module using Timefold to improve restocking decisions.

Files:
model.py
Defines the domain model for the optimization.
Key Features:
Book class: Represents books with attributes like stock and demand.
RestockPlan class: Decision variable for restocking quantities.
OptimizationSolution class: Encapsulates restocking decisions and optimization scores.
constraints.py
Encodes the business rules for the optimization problem.
Key Features:
Hard Constraints:
Budget limit.
Store capacity.
Soft Constraints:
Maintain genre diversity.
Minimize excess stock.
Favor restocking cheaper books.
solver.py
Integrates the domain model and constraints with the Timefold solver.
Key Features:
Configures solver phases and termination conditions.
Loads problem data and runs the optimization.
Displays the optimized restocking plan and total costs.

Future Enhancements
Integrate seasonal trends and promotions into customer behavior.
Visualize daily trends using matplotlib.
Extend the optimization module to include more constraints like supplier-specific rules.