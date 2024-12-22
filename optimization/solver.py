from timefold.solver import SolverFactory
from model import Book, RestockPlan, OptimizationSolution
from constraints import define_constraints

def create_solver():
    """
    Create and configure the Timefold solver.
    """
    solver_factory = SolverFactory()
    
    # Add domain model and constraints
    solver_factory.addPlanningEntity(RestockPlan)
    solver_factory.addPlanningSolution(OptimizationSolution)
    solver_factory.setConstraintProvider(define_constraints)

    # Configure the solver phases
    solver_factory.setConstructionHeuristicPhase()
    solver_factory.addLocalSearchPhase()

    # Set termination conditions
    solver_factory.setTerminationSpentLimit(seconds=60)  # Run for 60 seconds
    solver_factory.setTerminationScoreThreshold(best_score_feasible=True)  # Stop if a feasible solution is found

    return solver_factory.buildSolver()

def load_problem_data():
    """
    Load data for the optimization problem.
    """
    # Example: Static data for testing (replace with dynamic data loading)
    books = [
        Book(title="Book A", genre="Fiction", price=10.0, stock=20, demand_forecast=50),
        Book(title="Book B", genre="Non-fiction", price=15.0, stock=15, demand_forecast=30),
        Book(title="Book C", genre="Mystery", price=8.0, stock=25, demand_forecast=40),
    ]
    restock_plans = [RestockPlan(book=book) for book in books]
    return OptimizationSolution(restock_plans=restock_plans)

def solve_problem(solver, problem):
    """
    Run the optimization solver on the provided problem data.
    """
    print("Running the optimization solver...")
    solution = solver.solve(problem)
    print("Optimization completed.")
    return solution

def display_solution(solution):
    """
    Display the optimized solution.
    """
    print("\nOptimized Restocking Plan:")
    for plan in solution.restock_plans:
        print(f"{plan.book.title}: Restock {plan.restock_quantity} units")

    print(f"\nTotal Cost: ${solution.calculate_total_cost():.2f}")
    print(f"Optimization Score: {solution.score}")

if __name__ == "__main__":
    # Step 1: Create the solver
    solver = create_solver()

    # Step 2: Load the problem data
    problem = load_problem_data()

    # Step 3: Solve the problem
    solution = solve_problem(solver, problem)

    # Step 4: Display the solution
    display_solution(solution)
