import logging
from timefold.solver.score import constraint_provider, ConstraintFactory, HardSoftScore, Joiners
from timefold.solver.score import ConstraintCollectors
from .domain import RestockingDecision, Book
from datetime import datetime
from .utils import get_seasonal_keywords

log = logging.getLogger(__name__)

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        limit_total_capacity(constraint_factory),
        # Soft constraints
        prefer_higher_rated_books(constraint_factory),
        prefer_seasonal_books(constraint_factory),
        prefer_popular_authors(constraint_factory),
        prefer_affordable_books(constraint_factory)
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
                     lambda capacity, total: (total - capacity) * 2)
            .as_constraint("Total capacity"))

def prefer_higher_rated_books(constraint_factory: ConstraintFactory):
    """Reward books based on rating with exponential scaling"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .filter(lambda decision: decision.restock_quantity > 0)
            .reward(HardSoftScore.ONE_SOFT,
                   lambda decision: 
                   50 if decision.rating >= 4.8 else 
                   25 if decision.rating >= 4.5 else
                   1)
            .as_constraint("Prefer higher rated books"))

def prefer_seasonal_books(constraint_factory: ConstraintFactory):
    """Enhanced seasonal matching with multiple keyword bonus"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book,
                  Joiners.equal(lambda decision: decision.isbn,
                              lambda book: book.isbn))
            .filter(lambda decision, book: 
                    any(keyword.lower() in str(book.title).lower() or 
                        keyword.lower() in str(book.author).lower()
                        for keyword in get_seasonal_keywords(book.current_date.month)))
            .reward(HardSoftScore.of(0, 50))  # Increased seasonal importance
            .as_constraint("Seasonal preference"))

def prefer_affordable_books(constraint_factory: ConstraintFactory):
    """Reward books under £9 to maintain affordable options"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book,
                  Joiners.equal(lambda decision: decision.isbn,
                              lambda book: book.isbn))
            .filter(lambda decision, book: book.price < 8.0)
            .reward(HardSoftScore.ONE_SOFT,
                   lambda decision, book: 5)
            .as_constraint("Affordable books preference"))

def prefer_popular_authors(constraint_factory: ConstraintFactory):
    """Reward books by popular authors (high rating & frequency)"""
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book,
                  Joiners.equal(lambda decision: decision.isbn,
                              lambda book: book.isbn))
            .group_by(
                lambda decision, book: book.author,  # Group key
                ConstraintCollectors.count_bi()  # Count collector
            )
            .filter(lambda author, count: count >= 2)  # Authors with multiple books
            .reward(HardSoftScore.ONE_SOFT,
                   lambda author, count: count)
            .as_constraint("Popular authors"))