from dataclasses import dataclass, field
from typing import List, Annotated
from timefold.solver.domain import planning_solution, PlanningScore, PlanningEntityCollectionProperty
from timefold.solver.score import HardSoftScore  # Import the specific score type

from optimization.book_entity import BookEntity

@planning_solution
@dataclass
class OptimizationSolution:
    # Annotate the books field with PlanningEntityCollectionProperty
    books: Annotated[List[BookEntity], PlanningEntityCollectionProperty] = field(default_factory=list)

    # Total stock capacity (optional problem fact)
    total_stock_capacity: int = 0

    # Planning score, annotated with @PlanningScore
    score: Annotated[HardSoftScore | None, PlanningScore] = None
