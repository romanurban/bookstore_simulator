from datetime import datetime
from timefold.solver import SolverStatus
from timefold.solver.domain import *
from timefold.solver.score import HardSoftScore  
from typing import Annotated
from pydantic import Field

from .json_serialization import *


class Book(JsonDomainBase):
    isbn: Annotated[str, PlanningId]
    title: str
    author: str
    rating: float
    price: float
    current_stock: int = 2
    remaining_capacity: int = 0
    current_date: datetime 
    genre: str = "Unknown"


@planning_entity
class RestockingDecision(JsonDomainBase):
    isbn: Annotated[str, PlanningId]
    author: str
    rating: float
    current_date: datetime  # Add current date field
    restock_quantity: Annotated[int, 
                              PlanningVariable,
                              Field(default=0, ge=0, le=5)]  # Increased max to 5
    genre: str


@planning_solution
class RestockingSolution(JsonDomainBase):
    books: Annotated[list[Book], ProblemFactCollectionProperty]
    decisions: Annotated[list[RestockingDecision], PlanningEntityCollectionProperty]
    quantities: Annotated[list[int], ValueRangeProvider] = list(range(0, 5))  
    score: Annotated[HardSoftScore | None,  
                     PlanningScore, Field(default=None)]
    solver_status: Annotated[SolverStatus | None, Field(default=None)]