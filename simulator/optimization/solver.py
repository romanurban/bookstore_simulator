from timefold.solver import SolverFactory
from timefold.solver.config import SolverConfig
from simulator.optimization.constraints import define_constraints
from simulator.optimization.optimization_solution import OptimizationSolution
from simulator.optimization.book_entity import BookEntity

def create_solver():
    # Create a SolverConfig instance
    solver_config = SolverConfig()

    # Set the solution and entity classes
    solver_config.solution_class = OptimizationSolution
    solver_config.entity_class_list = [BookEntity]

    # Set the constraints provider
    solver_config.constraint_provider_class = define_constraints

    # Set termination criteria
    solver_config.termination_config.spent_limit_seconds = 60

    # Create and return the solver
    factory = SolverFactory.create(solver_config)
    return factory.build_solver()
