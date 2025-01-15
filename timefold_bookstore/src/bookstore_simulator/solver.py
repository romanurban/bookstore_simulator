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
        spent_limit=Duration(seconds=60),  # Give it more time
        unimproved_spent_limit=Duration(seconds=20)  # Stop if no improvement for 20 seconds
    )
)

solver_manager = SolverManager.create(SolverFactory.create(solver_config))
solution_manager = SolutionManager.create(solver_manager)