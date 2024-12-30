from optimization.optimization_solution import OptimizationSolution
from optimization.book_entity import BookEntity
from timefold.solver import SolverFactory
from timefold.solver.config import SolverConfig, TerminationConfig
from timefold.solver.config._config import Duration  # Correct import for Duration

# Test a minimal problem
test_books = [
    BookEntity(
        title="Minimal Test Book",
        author="Test Author",
        genre="Test Genre",
        price=9.99,
        rating=5.0,
        is_seasonal=False,
        current_stock=0,
        restock_quantity=5
    )
]

test_solution = OptimizationSolution(books=test_books, total_stock_capacity=50)

# Configure and solve
solver_config = SolverConfig()
solver_config.solution_class = OptimizationSolution
solver_config.entity_class_list = [BookEntity]

# Set proper termination configuration using Duration
termination_config = TerminationConfig()
termination_config.spent_limit = Duration(seconds=10)  # Set 10-second duration
solver_config.termination_config = termination_config

factory = SolverFactory.create(solver_config)
solver = factory.build_solver()

# Solve the problem
solution = solver.solve(test_solution)
print(solution)
