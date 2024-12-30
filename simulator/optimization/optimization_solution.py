from dataclasses import dataclass, field
from typing import List
from timefold.solver.domain import planning_solution, PlanningEntityCollectionProperty, PlanningScore
from optimization.book_entity import BookEntity

@planning_solution
@dataclass
class OptimizationSolution:
    # Annotate the books field as a PlanningEntityCollectionProperty
    books: List[BookEntity] = field(default_factory=list, metadata={"planning_entity_collection_property": True})

    # Total stock capacity (optional problem fact)
    total_stock_capacity: int = field(default=0)

    # Planning score (required)
    score: PlanningScore = None
