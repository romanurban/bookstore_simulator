from timefold.planning import ConstraintProvider
from timefold.planning.scores import HardSoftScore

# Define constants for weights
HARD_CONSTRAINT_WEIGHT = 10_000  # Penalty for violating hard constraints
SOFT_CONSTRAINT_WEIGHT = 100     # Penalty for violating soft constraints

# Define constants for business rules
MAX_BUDGET = 10_000  # Maximum budget for restocking
MAX_CAPACITY = 1_000  # Maximum store capacity (number of books)
MIN_GENRE_DIVERSITY = 5  # Minimum number of genres to maintain

@ConstraintProvider
def define_constraints(constraint_factory):
    constraints = []

    # HARD CONSTRAINT: Budget limit
    constraints.append(
        constraint_factory.forEach(RestockPlan)
        .groupBy(lambda rp: rp.book.price * rp.restock_quantity, sum)
        .filter(lambda total_cost: total_cost > MAX_BUDGET)
        .penalize("Exceeds budget", HardSoftScore.ofHard(HARD_CONSTRAINT_WEIGHT))
    )

    # HARD CONSTRAINT: Store capacity
    constraints.append(
        constraint_factory.forEach(RestockPlan)
        .groupBy(lambda rp: rp.restock_quantity, sum)
        .filter(lambda total_stock: total_stock > MAX_CAPACITY)
        .penalize("Exceeds store capacity", HardSoftScore.ofHard(HARD_CONSTRAINT_WEIGHT))
    )

    # SOFT CONSTRAINT: Maintain genre diversity
    constraints.append(
        constraint_factory.forEach(RestockPlan)
        .groupBy(lambda rp: rp.book.genre, countDistinct)
        .filter(lambda genre_count: genre_count < MIN_GENRE_DIVERSITY)
        .penalize("Insufficient genre diversity", HardSoftScore.ofSoft(SOFT_CONSTRAINT_WEIGHT))
    )

    # SOFT CONSTRAINT: Balance stock levels
    constraints.append(
        constraint_factory.forEach(RestockPlan)
        .penalize(
            "Excess stock",
            HardSoftScore.ofSoft(SOFT_CONSTRAINT_WEIGHT),
            lambda rp: max(0, rp.book.stock + rp.restock_quantity - rp.book.demand_forecast * 1.2)
        )
    )

    # SOFT CONSTRAINT: Favor cheaper books for restocking
    constraints.append(
        constraint_factory.forEach(RestockPlan)
        .reward(
            "Favor cheaper books",
            HardSoftScore.ofSoft(SOFT_CONSTRAINT_WEIGHT),
            lambda rp: max(0, 50 - rp.book.price)
        )
    )

    return constraints
