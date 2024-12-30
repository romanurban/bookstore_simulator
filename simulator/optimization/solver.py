from timefold.solver import SolverFactory
from timefold.solver.config import SolverConfig
from timefold.solver.config import TerminationConfig
from optimization.optimization_solution import OptimizationSolution
from optimization.book_entity import BookEntity

def create_solver():
    """
    Create and configure a SolverFactory using SolverConfig with a proper TerminationConfig.
    """
    # Create a SolverConfig instance
    solver_config = SolverConfig()

    # Configure the solver
    solver_config.solution_class = OptimizationSolution
    solver_config.entity_class_list = [BookEntity]

    # Set termination configuration properly
    termination_config = TerminationConfig()
    termination_config.spent_limit_seconds = 60  # Terminate after 60 seconds
    solver_config.termination_config = termination_config

    # Create the SolverFactory with the configured SolverConfig
    factory = SolverFactory.create(solver_config)
    
    # Build and return the solver
    return factory.build_solver()

def solve_problem(books, total_stock_capacity):
    """
    Solve the optimization problem.
    """
    problem = OptimizationSolution(books=books, total_stock_capacity=total_stock_capacity)
    solver = create_solver()
    solution = solver.solve(problem)
    return solution
