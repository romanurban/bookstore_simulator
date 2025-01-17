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
        
        # Rating preference (33% of customers)
        rating_weight = 0.33
        if book.average_rating:
            score += rating_weight * float(book.average_rating) * 20
            
        # Price sensitivity (33% of customers prefer books under 8.0)
        price_weight = 0.33
        if float(book.price) <= 8.0:  # Changed from 9.0 to 8.0
            score += price_weight * 100
        
        # Author popularity (5% of customers)
        author_weight = 0.05
        if book.authors in store.inventory.books[:1000]:
            score += author_weight * 100
            
        # Genre preference (5% of customers)
        genre_weight = 0.05
        popular_genres = ["Fiction", "Mystery", "Romance", "Fantasy"]
        if book.genre in popular_genres:
            score += genre_weight * 100
            
        return score

    def cost(decisions: List[Tuple['Book', int]]) -> float:
        total_cost = 0
        total_quantity = 0
        month = current_date.month
        seasonal_keywords = Customer.seasonal_keywords.get(month, [])
        unique_authors = set()
        
        for book, quantity in decisions:
            if total_quantity > remaining_capacity:
                return float('inf')
            
            total_quantity += quantity
            unique_authors.add(book.authors)
            
            # Price sensitivity (major factor but reduced weight)
            if book.price <= 8.0:  # Changed from 9.0 to 8.0
                total_cost -= 100 * quantity
            else:
                total_cost += (book.price - 8.0) * quantity * 20  # Changed from 9.0 to 8.0
            
            # Rating importance (reduced weight)
            rating = float(book.average_rating if book.average_rating else 0)
            if rating >= 4.5:
                total_cost -= rating * quantity * 30  # Reduced from 40
            
            # Author diversity bonus (new)
            if len(unique_authors) < 20:  # Encourage at least 20 different authors
                total_cost += 200  # Penalty for low diversity
            
            # Seasonal and stock balance (unchanged)
            seasonal_matches = sum(1 for keyword in seasonal_keywords 
                                if keyword.lower() in f"{book.title} {book.authors}".lower())
            total_cost -= seasonal_matches * quantity * 20
            
            current_stock = store.stock.get(book, 0)
            if current_stock < 3:
                total_cost -= 50 * quantity
            elif current_stock > 30:
                total_cost += 40 * quantity

        # Additional diversity incentives
        author_count_bonus = len(unique_authors) * 50  # Reward for each unique author
        total_cost -= author_count_bonus
        
        # Capacity utilization (unchanged)
        if total_quantity < remaining_capacity * 0.8:
            total_cost += (remaining_capacity - total_quantity) * 10
            
        return total_cost

    def create_neighbor(current_decisions: List[Tuple['Book', int]]) -> List[Tuple['Book', int]]:
        new_decisions = deepcopy(current_decisions)
        current_authors = set(book.authors for book, _ in new_decisions)
        
        if random.random() < 0.4:  # 40% chance to add new author
            # Try to add books from new authors
            available_books = [b for b in books 
                             if b not in [d[0] for d in new_decisions]
                             and b.authors not in current_authors
                             and b.price <= 8.0  # Fixed: Changed from 9.0 to 8.0
                             and float(b.average_rating or 0) >= 4.5]  # Fixed: Changed from 4.0 to 4.5
            if available_books:
                new_book = random.choice(available_books)
                new_qty = random.randint(3, 10)
                new_decisions.append((new_book, new_qty))
        else:
            # Original modification logic
            if new_decisions:
                idx = random.randrange(len(new_decisions))
                book, qty = new_decisions[idx]
                if book.price <= 8.0 and book.average_rating >= 4.5:  # Fixed: Changed values
                    delta = random.randint(1, 5)
                else:
                    delta = random.randint(-5, -1)
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
                     for k in Customer.seasonal_keywords.get(current_date.month, []))]  # Changed to use utils function
    
    # Calculate seasonal portion based on total capacity
    # Use 40% of capacity for seasonal books since they're highly likely to sell
    seasonal_portion = int(remaining_capacity * 0.4)  
    
    # Filter seasonal books by rating and price for better selection
    seasonal_books = [b for b in seasonal_books 
                     if float(b.average_rating or 0) >= 4.5  # Fixed: Changed from 4.0 to 4.5
                     and float(b.price) <= 8.0]  # Fixed: Changed from 9.0 to 8.0
    
    # Take top rated seasonal books without arbitrary limits
    for book in sorted(seasonal_books, key=lambda x: float(x.average_rating or 0), reverse=True):
        if initial_total < seasonal_portion:
            # Calculate quantity based on remaining seasonal portion
            remaining_seasonal = seasonal_portion - initial_total
            qty = min(15, max(5, remaining_seasonal // 10))  # Dynamic quantity
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