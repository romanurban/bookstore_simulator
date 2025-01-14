import logging
from timefold.solver.score import constraint_provider, ConstraintFactory, Joiners, HardSoftScore
from .domain import RestockingDecision, Book

log = logging.getLogger(__name__)

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        maintain_minimum_stock(constraint_factory),
        prevent_excess_stock(constraint_factory),
        # Soft constraints
        optimize_stock_by_rating(constraint_factory),
        optimize_stock_by_sales(constraint_factory)
    ]

def maintain_minimum_stock(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(RestockingDecision)
            .filter(lambda decision: decision.restock_quantity < 3)  # Minimum 3 books
            .penalize(HardSoftScore.ONE_HARD,
                     lambda decision: 3 - decision.restock_quantity)
            .as_constraint("Minimum stock level"))

def prevent_excess_stock(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book,
                  Joiners.equal(lambda decision: decision.isbn,
                              lambda book: book.isbn))
            .filter(lambda decision, book: 
                    decision.restock_quantity > (10 + book.avg_daily_sales * 7))  # Don't overstock
            .penalize(HardSoftScore.ONE_HARD,
                     lambda decision, book: 
                        decision.restock_quantity - (10 + book.avg_daily_sales * 7))
            .as_constraint("Prevent excess stock"))

def optimize_stock_by_rating(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book,
                  Joiners.equal(lambda decision: decision.isbn,
                              lambda book: book.isbn))
            .reward(HardSoftScore.ONE_SOFT,
                   lambda decision, book: 
                        int(decision.restock_quantity * book.rating))
            .as_constraint("Stock by rating"))

def optimize_stock_by_sales(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book,
                  Joiners.equal(lambda decision: decision.isbn,
                              lambda book: book.isbn))
            .reward(HardSoftScore.ONE_SOFT,
                   lambda decision, book: 
                        int(decision.restock_quantity * book.avg_daily_sales))
            .as_constraint("Stock by sales"))