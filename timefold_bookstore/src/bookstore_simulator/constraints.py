from timefold.solver.score import constraint_provider, ConstraintFactory, Joiners, HardSoftDecimalScore
from .domain import RestockingDecision, Book

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        enforce_budget_limit(constraint_factory),
        enforce_storage_capacity(constraint_factory),
        # Soft constraints
        maximize_sales(constraint_factory),
        ensure_stock_diversity(constraint_factory)
    ]

def enforce_budget_limit(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book, Joiners.equal(lambda decision: decision.isbn, 
                                    lambda book: book.isbn))
            .filter(lambda decision, book: decision.restock_quantity * book.price > 1000)
            .penalize(HardSoftDecimalScore.ONE_HARD)
            .as_constraint("Budget limit exceeded"))

def enforce_storage_capacity(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book, Joiners.equal(lambda decision: decision.isbn,
                                    lambda book: book.isbn))
            .filter(lambda decision, book: (book.current_stock + decision.restock_quantity) > 100)
            .penalize(HardSoftDecimalScore.ONE_HARD)
            .as_constraint("Storage capacity exceeded"))

def maximize_sales(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(RestockingDecision)
            .join(Book, Joiners.equal(lambda decision: decision.isbn,
                                    lambda book: book.isbn))
            .reward(HardSoftDecimalScore.ONE_SOFT,
                   lambda decision, book: decision.restock_quantity * book.avg_daily_sales)
            .as_constraint("Maximize potential sales"))

def ensure_stock_diversity(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(RestockingDecision)
            .filter(lambda decision: decision.restock_quantity == 0)
            .penalize(HardSoftDecimalScore.ONE_SOFT)
            .as_constraint("Maintain stock diversity"))