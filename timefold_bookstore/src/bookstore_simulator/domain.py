from timefold.solver import SolverStatus
from timefold.solver.domain import *
from timefold.solver.score import HardSoftDecimalScore
from typing import Annotated
from pydantic import Field

from .json_serialization import *


class Book(JsonDomainBase):
    isbn: Annotated[str, PlanningId]
    title: str
    price: float
    current_stock: int = 0
    avg_daily_sales: float = 0.0


@planning_entity
class RestockingDecision(JsonDomainBase):
    isbn: Annotated[str, PlanningId]
    restock_quantity: Annotated[int, 
                              PlanningVariable,
                              Field(default=0)]


@planning_solution
class RestockingSolution(JsonDomainBase):
    books: Annotated[list[Book], ProblemFactCollectionProperty]
    decisions: Annotated[list[RestockingDecision], PlanningEntityCollectionProperty]
    quantities: Annotated[list[int], ValueRangeProvider] = list(range(101))
    score: Annotated[HardSoftDecimalScore | None,
                     PlanningScore, ScoreSerializer, ScoreValidator, Field(default=None)]
    solver_status: Annotated[SolverStatus | None, Field(default=None)]