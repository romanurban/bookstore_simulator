from dataclasses import dataclass, field
from typing import Optional
from timefold.solver.domain import planning_entity, PlanningVariable

@planning_entity
@dataclass
class BookEntity:
    title: str
    author: str
    genre: str
    price: float
    rating: float
    is_seasonal: bool
    current_stock: int

    # Planning variable for restocking
    restock_quantity: Optional[int] = field(default=None, metadata={"planning_variable": True})
