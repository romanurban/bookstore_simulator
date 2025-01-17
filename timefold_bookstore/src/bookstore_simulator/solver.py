from timefold.solver import SolverManager, SolverFactory, SolutionManager
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                   TerminationConfig, Duration)

from .domain import RestockingSolution, RestockingDecision
from .constraints import define_constraints
from .utils import get_seasonal_keywords  # Add this import

solver_config = SolverConfig(
    solution_class=RestockingSolution,
    entity_class_list=[RestockingDecision],
    score_director_factory_config=ScoreDirectorFactoryConfig(
        constraint_provider_function=define_constraints
    ),
    termination_config=TerminationConfig(
        spent_limit=Duration(seconds=60),  # Give it more time
        unimproved_spent_limit=Duration(seconds=20)  # Stop if no improvement for 20 seconds
    )
)

solver_manager = SolverManager.create(SolverFactory.create(solver_config))
solution_manager = SolutionManager.create(solver_manager)

def custom_neighborhood_function(solution: RestockingSolution):
    """Apply custom neighborhood changes to the solution"""
    decisions = solution.decisions
    if not decisions:
        return
    
    # Try to improve the solution by adjusting quantities for high-rated, affordable, seasonal books
    current_date = solution.books[0].current_date if solution.books else None
    if current_date:
        month = current_date.month
        seasonal_keywords = get_seasonal_keywords(month)  # Use utility function
        
        for decision in decisions:
            book = next((b for b in solution.books if b.isbn == decision.isbn), None)
            if book:
                is_seasonal = any(keyword.lower() in f"{book.title} {book.author}".lower() 
                                for keyword in seasonal_keywords)
                is_affordable = book.price <= 8.0
                is_highly_rated = book.rating >= 4.5
                
                if is_seasonal and is_affordable and is_highly_rated:
                    # Increase quantity for good candidates
                    decision.restock_quantity = min(30, decision.restock_quantity + 5)
                elif not (is_seasonal or is_affordable or is_highly_rated):
                    # Decrease quantity for less desirable books
                    decision.restock_quantity = max(0, decision.restock_quantity - 5)
    
    # Remove decisions with zero quantity
    solution.decisions = [d for d in decisions if d.restock_quantity > 0]