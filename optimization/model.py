from timefold.planning import PlanningEntity, PlanningVariable, PlanningSolution

@PlanningEntity
class Book:
    def __init__(self, title, genre, price, stock, demand_forecast):
        self.title = title
        self.genre = genre
        self.price = price
        self.stock = stock
        self.demand_forecast = demand_forecast  # Predicted demand for optimization

    def __repr__(self):
        return f"Book(title={self.title}, stock={self.stock})"


@PlanningEntity
class RestockPlan:
    def __init__(self, book, restock_quantity=0):
        self.book = book
        self.restock_quantity = restock_quantity  # Quantity to order

    @PlanningVariable
    def get_restock_quantity(self):
        return self.restock_quantity

    def __repr__(self):
        return f"RestockPlan(book={self.book.title}, restock_quantity={self.restock_quantity})"


@PlanningSolution
class OptimizationSolution:
    def __init__(self, restock_plans, total_cost=0, score=None):
        self.restock_plans = restock_plans  # List of RestockPlan entities
        self.total_cost = total_cost  # Sum of all restocking costs
        self.score = score  # Optimization score (calculated by Timefold)

    def calculate_total_cost(self):
        """
        Calculate the total cost of restocking.
        """
        self.total_cost = sum(plan.book.price * plan.restock_quantity for plan in self.restock_plans)
        return self.total_cost

    def __repr__(self):
        return f"OptimizationSolution(total_cost={self.total_cost}, plans={self.restock_plans})"
