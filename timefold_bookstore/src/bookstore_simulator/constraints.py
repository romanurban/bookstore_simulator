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
        limit_total_capacity(constraint_factory),
        # Soft constraints
        prefer_higher_rated_books(constraint_factory)
    ]

def minimum_stock(constraint_factory: ConstraintFactory):
    """Each restocking decision should be at least 0"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .filter(lambda decision: decision.restock_quantity < 0)
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Minimum stock"))

def limit_total_capacity(constraint_factory: ConstraintFactory):
    """Ensure total restocked books don't exceed remaining capacity"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book,
                  Joiners.equal(lambda decision: decision.isbn,
                              lambda book: book.isbn))
            .group_by(lambda decision, book: book.remaining_capacity,
                     ConstraintCollectors.sum(lambda decision, book: decision.restock_quantity))
            .filter(lambda capacity, total: total > capacity)
            .penalize(HardSoftScore.ONE_HARD,
                     lambda capacity, total: total - capacity)
            .as_constraint("Total capacity"))

def prefer_higher_rated_books(constraint_factory: ConstraintFactory):
    """Basic reward for higher rated books"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .filter(lambda decision: decision.restock_quantity > 0)
            .reward(HardSoftScore.ONE_SOFT)
            .as_constraint("Prefer higher rated books"))