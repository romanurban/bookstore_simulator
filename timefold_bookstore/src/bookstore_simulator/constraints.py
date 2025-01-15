import logging
from timefold.solver.score import constraint_provider, ConstraintFactory, HardSoftScore, Joiners
from timefold.solver.score import ConstraintCollectors
from .domain import RestockingDecision, Book

log = logging.getLogger(__name__)

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        minimum_stock(constraint_factory),
        #check_remaining_capacity(constraint_factory),
        # Soft constraints
        prefer_higher_rated_books(constraint_factory),
        limit_total_books(constraint_factory)
    ]

def minimum_stock(constraint_factory: ConstraintFactory):
    """Each restocking decision should be at least 0"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .filter(lambda decision: decision.restock_quantity < 0)
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Minimum stock"))

def check_remaining_capacity(constraint_factory: ConstraintFactory):
    """Individual book quantities should not exceed remaining capacity"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .filter(lambda decision: decision.restock_quantity > 20)  # Use fixed max value
            .penalize(HardSoftScore.ONE_HARD,
                     lambda decision: decision.restock_quantity - 20)
            .as_constraint("Individual capacity"))

def prefer_higher_rated_books(constraint_factory: ConstraintFactory):
    """Basic reward for higher rated books"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .filter(lambda decision: decision.restock_quantity > 0)
            .reward(HardSoftScore.ONE_SOFT)
            .as_constraint("Prefer higher rated books"))

def limit_total_books(constraint_factory: ConstraintFactory):
    """Ensure total restocked books don't exceed 20."""
    return (
        constraint_factory.for_each(RestockingDecision)
        .group_by(ConstraintCollectors.sum(lambda d: d.restock_quantity))
        .filter(lambda total: total > 20)
        .penalize(HardSoftScore.ONE_HARD, lambda total: total - 20)
        .as_constraint("Limit total books to 20")
    )