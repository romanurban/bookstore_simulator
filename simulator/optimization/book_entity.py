from dataclasses import dataclass
from typing import Optional, Annotated
from timefold.solver.domain import planning_entity, PlanningVariable, ValueRangeProvider

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

    # Value range for restock_quantity
    restock_quantity_range: Annotated[
        list[int],
        ValueRangeProvider(id="restock_quantity_range")
    ] = range(0, 101)  # Example: 0 to 100 inclusive

    # Planning variable for restocking
    restock_quantity: Annotated[
        Optional[int],
        PlanningVariable(value_range_provider_refs=["restock_quantity_range"])
    ] = None
