from timefold.solver import SolverManager, SolverFactory, SolutionManager
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                   TerminationConfig, Duration)

from .domain import RestockingSolution, RestockingDecision
from .constraints import define_constraints

solver_config = SolverConfig(
    solution_class=RestockingSolution,
    entity_class_list=[RestockingDecision],
    score_director_factory_config=ScoreDirectorFactoryConfig(
        constraint_provider_function=define_constraints
    ),
    termination_config=TerminationConfig(
        spent_limit=Duration(seconds=30)  # Increase from 5 to 30
    )
)

solver_manager = SolverManager.create(SolverFactory.create(solver_config))
solution_manager = SolutionManager.create(solver_manager)