import random
import logging
from inventory import Inventory, Book
from customer import Customer
from typing import List, Tuple
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
from alt_solver import alt_solve

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Store:
    def __init__(self, inventory, storage_capacity):
        self.inventory = inventory
        self.storage_capacity = storage_capacity
        self.stock = {}
        self.initiate_stock()
        self.session = self._setup_http_session()

    def _setup_http_session(self):
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount('http://', HTTPAdapter(max_retries=retries))
        return session

    def initiate_stock(self):
        current_total = 0
        while current_total < self.storage_capacity:
            book = random.choice(self.inventory.books)
            if book not in self.stock:
                quantity = random.randint(1, self.storage_capacity - current_total)
                self.stock[book] = quantity
                current_total += quantity
                log.debug(f"Initiated stock for {book.title} (ISBN: {book.isbn}). Now have {self.stock[book]} copies.")
            else:
                log.debug(f"{book.title} (ISBN: {book.isbn}) is already in stock.")

    def list_stock(self):
        for book, quantity in self.stock.items():
            log.debug(f"{book.title} (ISBN: {book.isbn}): {quantity} copies")

    def sell_book(self, title, quantity=1):
        for book in self.stock:
            if book.title == title:
                if self.stock[book] >= quantity:
                    self.stock[book] -= quantity
                    log.debug(f"Sold {quantity} copies of {title} (ISBN: {book.isbn}).")
                    if self.stock[book] == 0:
                        del self.stock[book]
                    return book
                else:
                    log.debug(f"Not enough copies of {title} (ISBN: {book.isbn}) to sell. Available: {self.stock[book]}")
                    return None
        log.debug(f"{title} is not in stock.")
        return None

    def _collect_metrics(self, current_date, decisions=None, prefix=""):
        """Helper function to collect metrics about stock state."""
        month = current_date.month
        seasonal_keywords = Customer.seasonal_keywords.get(month, [])
        
        def calculate_stock_metrics():
            """Calculate metrics for current stock state"""
            total = sum(self.stock.values())
            rating_sum = sum(float(book.average_rating or 0) * qty for book, qty in self.stock.items())
            avg_rating = rating_sum / total if total > 0 else 0
            seasonal = sum(1 for book in self.stock.keys() 
                         if any(k.lower() in f"{book.title} {book.authors} {book.genre}".lower() 
                              for k in seasonal_keywords))
            affordable_books = sum(qty for book, qty in self.stock.items() if book.price <= 8.0)  # Changed from 9.0 to 8.0
            affordable_percentage = (affordable_books / total * 100) if total > 0 else 0
            
            return {
                'total': total,
                'avg_rating': avg_rating,
                'seasonal_matches': seasonal,
                'affordable_books': affordable_books,
                'affordable_percentage': affordable_percentage
            }

        # If we have decisions, these are "after" metrics
        if decisions:
            after_total = sum(self.stock.values())
            after_affordable = sum(qty for book, qty in self.stock.items() if book.price <= 8.0)
            
            metrics = {
                'after_total': after_total,
                'after_avg_rating': (sum(float(book.average_rating or 0) * qty 
                                   for book, qty in self.stock.items()) / 
                                   after_total if after_total else 0),
                'after_seasonal_matches': sum(1 for book in self.stock.keys() 
                                         if any(k.lower() in f"{book.title} {book.authors} {book.genre}".lower() 
                                              for k in seasonal_keywords)),
                'after_affordable_books': after_affordable,
                'after_affordable_percentage': (after_affordable / after_total * 100) if after_total > 0 else 0,
                'restock_quantity': sum(qty for _, qty in decisions),
                'unique_books_added': len(set(book for book, _ in decisions))
            }
            
            # Calculate before values
            before_total = metrics['after_total'] - metrics['restock_quantity']
            before_affordable = metrics['after_affordable_books'] - sum(qty for book, qty in decisions if book.price <= 8.0)
            
            metrics.update({
                'before_total': before_total,
                'before_avg_rating': metrics['after_avg_rating'],  # Approximate
                'before_seasonal_matches': metrics['after_seasonal_matches'] - sum(1 for book, _ in decisions 
                                                                               if any(k.lower() in f"{book.title} {book.authors} {book.genre}".lower() 
                                                                                    for k in seasonal_keywords)),
                'before_affordable_books': before_affordable,
                'before_affordable_percentage': (before_affordable / before_total * 100) if before_total > 0 else 0
            })
        else:
            # If no decisions, just get current state
            current_metrics = calculate_stock_metrics()
            metrics = {
                'before_total': current_metrics['total'],
                'before_avg_rating': current_metrics['avg_rating'],
                'before_seasonal_matches': current_metrics['seasonal_matches'],
                'before_affordable_books': current_metrics['affordable_books'],
                'before_affordable_percentage': current_metrics['affordable_percentage'],
                'after_total': current_metrics['total'],
                'after_avg_rating': current_metrics['avg_rating'],
                'after_seasonal_matches': current_metrics['seasonal_matches'],
                'after_affordable_books': current_metrics['affordable_books'],
                'after_affordable_percentage': current_metrics['affordable_percentage'],
                'restock_quantity': 0,
                'unique_books_added': 0
            }

        return metrics  # Just return metrics without printing

    def restock(self):
        """Basic restocking with metrics collection."""
        # Collect metrics before restocking
        before_metrics = self._collect_metrics(datetime.now())
        
        current_total = sum(self.stock.values())
        remaining_capacity = self.storage_capacity - current_total
        decisions = []
        
        # Create a diverse selection of books (same as other methods)
        # Take some high-rated books with random noise in rating
        top_rated = sorted(
            self.inventory.books,
            key=lambda x: float(x.average_rating if x.average_rating else 0) + random.uniform(-0.2, 0.2)
        )[:1000]  # Keep exactly 1000 top books
        
        # Take random books from remaining
        remaining_books = [b for b in self.inventory.books if b not in top_rated]
        random_selection = random.sample(remaining_books, 
                                      min(2000+remaining_capacity, len(remaining_books)))
        
        # Combine and shuffle the selection
        candidate_books = random.sample(top_rated + random_selection, 
                                    len(top_rated) + len(random_selection))
        
        log.info(f"Selected {len(candidate_books)} books for basic restocking")
        
        # Perform basic restocking from selected books
        while current_total < self.storage_capacity:
            book = random.choice(candidate_books)
            quantity = random.randint(1, 5)
            if current_total + quantity > self.storage_capacity:
                quantity = self.storage_capacity - current_total
            if book in self.stock:
                self.stock[book] += quantity
            else:
                self.stock[book] = quantity
            current_total += quantity
            decisions.append((book, quantity))
            log.debug(f"Restocked {quantity} copies of {book.title} (ISBN: {book.isbn})")

        # Collect metrics after restocking and print comparison
        after_metrics = self._collect_metrics(datetime.now(), decisions, prefix="Basic ")
        self._print_metrics_comparison(before_metrics, after_metrics, "Basic ")
        return decisions, after_metrics

    def restock_timefold_optimized(self, current_date) -> List[Tuple[Book, int]]:
        """Use solver API to optimize restocking decisions with metrics collection."""
        # Collect metrics before restocking
        before_metrics = self._collect_metrics(current_date)
        
        try:
            current_total = sum(self.stock.values())
            remaining_capacity = self.storage_capacity - current_total
            log.info(f"Remaining storage capacity: {remaining_capacity}")
            
            # Create a diverse selection of books
            # Take some high-rated books with random noise in rating
            top_rated = sorted(
                self.inventory.books,
                key=lambda x: (float(x.average_rating) if x.average_rating else 0) + random.uniform(-0.2, 0.2),
                reverse=True
            )[:1000]  # Keep exactly 1000 top books
            
            # Take exactly 2000 random books from remaining
            remaining_books = [b for b in self.inventory.books if b not in top_rated]
            random_selection = random.sample(remaining_books, 
                                          min(2000+remaining_capacity, len(remaining_books)))  # Fixed at 2000
            
            # Combine and shuffle
            sorted_books = random.sample(top_rated + random_selection, 
                                       len(top_rated) + len(random_selection))
            
            log.info(f"Selected {len(sorted_books)} books")
            
            # Prepare inventory data with current date
            current_stock = [
                {
                    "isbn": book.isbn,
                    "author": book.authors,
                    "title": book.title,
                    "price": book.price,
                    "current_stock": self.stock.get(book, 0),
                    "avg_daily_sales": 2.5,
                    "rating": book.average_rating,
                    "genre": book.genre,  # Add genre to the data sent to solver
                    "restock_quantity": 0,
                    "remaining_capacity": remaining_capacity,
                    "current_date": current_date.isoformat()  # Add current date to each book entry
                }
                for book in sorted_books
            ]

            # Call solver
            log.info(f"Sending {len(current_stock)} books to solver")
            log.debug(f"First 5 books being sent: {current_stock[:5]}")
            
            response = requests.post(
                "http://localhost:8080/optimize-restock",
                json=current_stock,
                timeout=120
            )
            response.raise_for_status()
            job_id = response.json()
            log.info(f"Got job_id: {job_id}")

            # Poll for solution
            max_retries = 300  # Reduced retries but increased sleep
            attempt = 1
            
            while attempt <= max_retries:
                status = requests.get(
                    f"http://localhost:8080/solutions/{job_id}/status",
                    timeout=10
                ).json()
                
                log.debug(f"Attempt {attempt}: Status = {status['status']} Score = {status.get('score', 'N/A')}")
                
                if status["status"] in ["SOLVED"]:
                    solution_response = requests.get(
                        f"http://localhost:8080/solutions/{job_id}",
                        timeout=10
                    )
                    
                    if solution_response.status_code == 200:
                        try:
                            solution_data = solution_response.json()
                            log.debug(f"Solution data: {solution_data}")
                            
                            # Handle nested 'decisions' structure
                            if isinstance(solution_data, dict) and 'decisions' in solution_data:
                                decisions = []
                                total_restock = 0
                                log.info(f"Raw solution decisions: {solution_data['decisions'][:5]}")  # Show first 5
                                for item in solution_data['decisions']:
                                    isbn = item.get('isbn')
                                    restock_qty = item.get('restockQuantity', 0)
                                    if isbn:  # Log all decisions, not just positive ones
                                        log.debug(f"Decision for ISBN {isbn}: {restock_qty}")
                                    if isbn and restock_qty > 0:
                                        book = next((b for b in sorted_books if b.isbn == isbn), None)
                                        if book:
                                            decisions.append((book, restock_qty))
                                            total_restock += restock_qty
                                            
                                log.info(f"Total books to restock: {total_restock}")
                                log.info(f"Number of different books to restock: {len(decisions)}")
                                if decisions:
                                    log.info("First 5 restocking decisions:")
                                    for book, qty in decisions[:5]:
                                        log.info(f"  - {book.title}: {qty} copies")
                                
                                # After getting decisions, apply them to stock
                                if decisions:
                                    for book, quantity in decisions:
                                        if book in self.stock:
                                            self.stock[book] += quantity
                                        else:
                                            self.stock[book] = quantity
                                        log.debug(f"Restocked {book.title}: added {quantity} (new total: {self.stock[book]})")
                                    
                                    total_after = sum(self.stock.values())
                                    log.info(f"Books after restocking: {total_after}")
                                    
                                # After getting decisions and applying them, collect and compare metrics
                                after_metrics = self._collect_metrics(current_date, decisions, prefix="Timefold ")
                                self._print_metrics_comparison(before_metrics, after_metrics, "Timefold ")
                                return decisions, after_metrics
                            else:
                                log.warning(f"Unexpected solution format: {solution_data}")
                                fallback_decisions = self._basic_restock()
                                after_metrics = self._collect_metrics(current_date, fallback_decisions, prefix="Timefold Fallback ")
                                self._print_metrics_comparison(before_metrics, after_metrics, "Timefold Fallback ")
                                return fallback_decisions, after_metrics
                        except ValueError as e:
                            log.warning(f"Failed to parse solution: {e}")
                            fallback_decisions = self._basic_restock()
                            after_metrics = self._collect_metrics(current_date, fallback_decisions, prefix="Timefold Fallback ")
                            self._print_metrics_comparison(before_metrics, after_metrics, "Timefold Fallback ")
                            return fallback_decisions, after_metrics
                
                attempt += 1
                time.sleep(2)
            
            log.warning("Optimization timed out - falling back to basic optimization")
            fallback_decisions = self._basic_restock()
            after_metrics = self._collect_metrics(current_date, fallback_decisions, prefix="Timefold Fallback ")
            self._print_metrics_comparison(before_metrics, after_metrics, "Timefold Fallback ")
            return fallback_decisions, after_metrics
            
        except Exception as e:
            log.warning(f"Solver optimization failed: {e}")
            fallback_decisions = self._basic_restock()
            after_metrics = self._collect_metrics(current_date, fallback_decisions, prefix="Timefold Fallback ")
            self._print_metrics_comparison(before_metrics, after_metrics, "Timefold Fallback ")
            return fallback_decisions, after_metrics

    def _basic_restock(self) -> List[Tuple[Book, int]]:
        """Fallback method for basic restocking"""
        decisions = []
        for book in self.inventory.books:
            current_stock = self.stock.get(book, 0)
            if current_stock < 3:  # Fixed: Changed from 10 to 3 to match other thresholds
                restock_amount = 10 - current_stock
                decisions.append((book, restock_amount))
                # Apply the restock immediately
                if book in self.stock:
                    self.stock[book] += restock_amount
                else:
                    self.stock[book] = restock_amount
        return decisions

    def restock_alternative(self, current_date):
        """Use alt_solver to optimize restocking without Timefold."""
        # Collect metrics before restocking
        before_metrics = self._collect_metrics(current_date)
        
        current_total = sum(self.stock.values())
        remaining_capacity = self.storage_capacity - current_total
        
        # Collect initial metrics
        initial_metrics = self._collect_metrics(current_date)
        log.info(f"Books before alternative restocking: {initial_metrics['before_total']}")
        
        # Create a diverse selection of books (similar to timefold_optimized)
        # Take some high-rated books with random noise in rating
        top_rated = sorted(
            self.inventory.books,
            key=lambda x: float(x.average_rating if x.average_rating else 0) + random.uniform(-0.2, 0.2)
        )[:1000]  # Keep exactly 1000 top books
        
        # Take random books from remaining
        remaining_books = [b for b in self.inventory.books if b not in top_rated]
        random_selection = random.sample(remaining_books, 
                                      min(2000+remaining_capacity, len(remaining_books)))
        
        # Combine and shuffle the selection
        candidate_books = random.sample(top_rated + random_selection, 
                                    len(top_rated) + len(random_selection))
        
        log.info(f"Selected {len(candidate_books)} books for optimization")
        
        decisions = alt_solve(self, candidate_books, remaining_capacity, current_date)
        
        # Apply decisions to actual stock
        for book, quantity in decisions:
            if book in self.stock:
                self.stock[book] += quantity
            else:
                self.stock[book] = quantity
        
        # After decisions are made and applied, collect and compare metrics
        after_metrics = self._collect_metrics(current_date, decisions, prefix="Alternative ")
        self._print_metrics_comparison(before_metrics, after_metrics, "Alternative ")
        return decisions, after_metrics

    def _print_metrics_comparison(self, before_metrics, after_metrics, prefix=""):
        """Helper method to print metrics comparison."""
        log.info(f"\n{prefix}Restock Metrics:")
        log.info(f"Total Stock: {before_metrics['before_total']} → {after_metrics['after_total']} ({after_metrics['after_total'] - before_metrics['before_total']:+d})")
        log.info(f"Average Rating: {before_metrics['before_avg_rating']:.2f} → {after_metrics['after_avg_rating']:.2f} ({after_metrics['after_avg_rating'] - before_metrics['before_avg_rating']:+.2f})")
        log.info(f"Seasonal Matches: {before_metrics['before_seasonal_matches']} → {after_metrics['after_seasonal_matches']} ({after_metrics['after_seasonal_matches'] - before_metrics['before_seasonal_matches']:+d})")
        log.info(f"Affordable Books (≤£8): {before_metrics['before_affordable_books']} → {after_metrics['after_affordable_books']} ({after_metrics['after_affordable_books'] - before_metrics['before_affordable_books']:+d})")
        log.info(f"Affordable Percentage: {before_metrics['before_affordable_percentage']:.1f}% → {after_metrics['after_affordable_percentage']:.1f}% ({after_metrics['after_affordable_percentage'] - before_metrics['before_affordable_percentage']:+.1f}%)")
    
# Example usage
if __name__ == "__main__":
    inventory = Inventory()
    inventory.load_from_dataset("data/catalog.csv")
    store = Store(inventory, storage_capacity=5)
    store.list_stock()

    # Pick and sell 5 random books from stock
    for _ in range(10):
        if store.stock:
            book = random.choice(list(store.stock.keys()))
            store.sell_book(book.title, quantity=random.randint(1,2))
        else:
            log.debug("No more books available to sell.")
            break

    store.restock()
    store.list_stock()