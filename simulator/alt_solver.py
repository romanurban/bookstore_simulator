import random
from typing import List, Tuple
from inventory import Book
from copy import deepcopy
from datetime import datetime
from customer import Customer

def alt_solve(store, books: List['Book'], remaining_capacity: int, current_date: datetime) -> List[Tuple['Book', int]]:
    """Late Acceptance Hill Climbing solver for restocking optimization."""
    def calculate_preference_score(book: Book) -> float:
        """Calculate a preference score based on known customer behaviors"""
        score = 0.0
        
        # Author popularity (15% of customers prefer specific authors)
        author_weight = 0.15
        if book.authors in store.inventory.books[:1000]:  # Assuming first 1000 are popular
            score += author_weight * 100
            
        # Genre preference (10% of customers prefer specific genres)
        genre_weight = 0.10
        popular_genres = ["Fiction", "Mystery", "Romance", "Fantasy"]  # Add more based on data
        if book.genre in popular_genres:
            score += genre_weight * 100
            
        # Rating preference (higher rated books are preferred)
        rating_weight = 0.25
        if book.average_rating:
            score += rating_weight * float(book.average_rating) * 20
            
        # Price sensitivity (20% of customers prefer books under 15.0)
        price_weight = 0.20
        if float(book.price) <= 15.0:
            score += price_weight * 100
            
        return score

    def cost(decisions: List[Tuple['Book', int]]) -> float:
        total_cost = 0
        total_quantity = 0
        month = current_date.month
        seasonal_keywords = Customer.seasonal_keywords.get(month, [])
        
        for book, quantity in decisions:
            total_quantity += quantity
            
            # Capacity penalty (highest priority)
            capacity_diff = abs(remaining_capacity - total_quantity)
            total_cost += 3000 * capacity_diff
            
            # Customer preference score (negative because we want to minimize cost)
            preference_score = calculate_preference_score(book)
            total_cost -= preference_score * quantity
            
            # Seasonal relevance
            book_text = f"{book.title} {book.authors} {book.genre}".lower()
            seasonal_matches = sum(1 for keyword in seasonal_keywords if keyword.lower() in book_text)
            total_cost -= 30 * seasonal_matches * quantity
            
            # Stock balance (encourage diverse stock)
            current_stock = store.stock.get(book, 0)
            if current_stock < 5:
                total_cost -= 15 * quantity  # Encourage restocking low stock
            elif current_stock > 50:
                total_cost += 10 * quantity  # Discourage overstocking single titles
            
            # Price range optimization
            price = float(book.price)
            if 10 <= price <= 30:
                total_cost -= 8 * quantity  # Prefer middle-range prices
                
            # Rating-based stocking
            rating = float(book.average_rating if book.average_rating else 0)
            if rating >= 4.5:
                total_cost -= 25 * quantity  # Heavily favor highly-rated books
            elif rating >= 4.0:
                total_cost -= 15 * quantity  # Moderately favor well-rated books
        
        return total_cost

    def create_neighbor(current_decisions: List[Tuple['Book', int]]) -> List[Tuple['Book', int]]:
        """Generate a neighboring solution with small modifications."""
        new_decisions = deepcopy(current_decisions)
        current_total = sum(qty for _, qty in new_decisions)
        
        # Adjust quantities to approach target capacity
        if current_total < remaining_capacity:
            # Add more books or increase quantities
            if random.random() < 0.6 or not new_decisions:  # Higher chance to add new books when under capacity
                available_books = [b for b in books if b not in [d[0] for d in new_decisions]]
                if available_books:
                    new_book = random.choice(available_books)
                    new_qty = min(random.randint(5, 20), remaining_capacity - current_total)
                    new_decisions.append((new_book, new_qty))
            else:
                # Increase existing quantities
                idx = random.randrange(len(new_decisions))
                book, qty = new_decisions[idx]
                increase = min(random.randint(1, 10), remaining_capacity - current_total)
                new_decisions[idx] = (book, qty + increase)
        else:
            # Regular modifications
            if new_decisions:
                idx = random.randrange(len(new_decisions))
                book, qty = new_decisions[idx]
                delta = random.choice([-2, -1, 1, 2])
                new_qty = max(0, qty + delta)
                if new_qty == 0:
                    new_decisions.pop(idx)
                else:
                    new_decisions[idx] = (book, new_qty)
        
        return new_decisions

    # Initialize solution with smarter initial selection
    current_decisions = []
    initial_total = 0
    
    # Start with highly-rated seasonal books
    seasonal_books = [b for b in books if any(k.lower() in f"{b.title} {b.authors} {b.genre}".lower() 
                     for k in Customer.seasonal_keywords.get(current_date.month, []))]
    
    for book in sorted(seasonal_books, key=lambda x: float(x.average_rating or 0), reverse=True)[:20]:
        if initial_total < remaining_capacity:
            qty = min(random.randint(10, 30), remaining_capacity - initial_total)
            current_decisions.append((book, qty))
            initial_total += qty
    
    # Fill remaining capacity with popular books
    remaining_books = sorted(
        [b for b in books if b not in [d[0] for d in current_decisions]],
        key=calculate_preference_score,
        reverse=True
    )
    
    while initial_total < remaining_capacity and remaining_books:
        book = remaining_books.pop(0)
        qty = min(random.randint(5, 20), remaining_capacity - initial_total)
        current_decisions.append((book, qty))
        initial_total += qty

    # LAHC parameters
    history_length = 10  # Increased history length
    cost_history = [cost(current_decisions)] * history_length
    best_decisions = current_decisions
    best_cost = cost(current_decisions)
    
    # Main LAHC loop with increased iterations
    iterations = 200  # Doubled iterations for better optimization
    for i in range(iterations):
        candidate_decisions = create_neighbor(current_decisions)
        candidate_cost = cost(candidate_decisions)
        
        if (candidate_cost <= cost_history[i % history_length] or 
            candidate_cost <= best_cost):
            current_decisions = candidate_decisions
            if candidate_cost < best_cost:
                best_decisions = candidate_decisions
                best_cost = candidate_cost
        
        cost_history[i % history_length] = cost(current_decisions)
    
    return [(book, qty) for book, qty in best_decisions if qty > 0]