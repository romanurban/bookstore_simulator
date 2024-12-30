from timefold.solver import constraint_factory as cf

from simulator.optimization.book_entity import BookEntity

def define_constraints(factory):
    return [
        # Reward higher ratings
        factory.for_each(BookEntity)
            .reward("High rating books", cf.soft_reward())
            .filter(lambda book: book.rating > 4.0),

        # Reward seasonal books
        factory.for_each(BookEntity)
            .reward("Seasonal books", cf.soft_reward())
            .filter(lambda book: book.is_seasonal),

        # Penalize books priced over £15
        factory.for_each(BookEntity)
            .penalize("Expensive books", cf.soft_penalty())
            .filter(lambda book: book.price > 15.0),

        # Ensure diverse authors
        factory.for_each_unique_pair(BookEntity, lambda b1, b2: b1.author != b2.author)
            .reward("Author diversity", cf.soft_reward()),

        # Ensure each book has at least a minimum quantity
        factory.for_each(BookEntity)
            .penalize("Minimum stock", cf.hard_penalty())
            .filter(lambda book: book.restock_quantity < 5),

        # Respect total stock capacity
        factory.for_each(BookEntity)
            .penalize("Stock exceeds capacity", cf.hard_penalty())
            .group_by_sum(lambda book: book.restock_quantity)
            .filter(lambda total: total > factory.solution.total_stock_capacity),
    ]
