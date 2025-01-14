import random
import logging
from inventory import Inventory, Book
from customer import Customer
import httpx
import asyncio
from typing import List, Tuple
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

    def restock(self):
        log.info(f"Books before restocking: {sum(self.stock.values())}")
        current_total = sum(self.stock.values())
        while current_total < self.storage_capacity:
            book = random.choice(self.inventory.books)
            quantity = random.randint(1, 5)  # Random quantity between 1 and 5
            if current_total + quantity > self.storage_capacity:
                quantity = self.storage_capacity - current_total
            if book in self.stock:
                self.stock[book] += quantity
            else:
                self.stock[book] = quantity
            current_total += quantity
            log.debug(f"Restocked {quantity} copies of {book.title} (ISBN: {book.isbn}). Now have {self.stock[book]} copies.")

    def restock_optimized(self) -> List[Tuple[Book, int]]:
        """Use solver API to optimize restocking decisions"""
        log.info(f"Books before restocking: {sum(self.stock.values())}")
        current_total = sum(self.stock.values())
        
        try:
            # Prepare inventory data
            current_stock = [
                {
                    "isbn": book.isbn,
                    "author": book.authors,
                    "title": book.title,
                    "price": book.price,
                    "current_stock": self.stock.get(book, 0),
                    "avg_daily_sales": 2.5,
                    "rating": book.average_rating
                }
                for book in self.inventory.books
            ]

            # Call solver with correct port
            response = requests.post(
                "http://localhost:8080/optimize-restock",  # Changed from 8080 to 8000
                json=current_stock,
                timeout=60  # Increased timeout
            )
            response.raise_for_status()
            job_id = response.json()

            # Poll for solution with proper attempt tracking
            max_retries = 100  # Reduce max retries
            attempt = 1
            
            while attempt <= max_retries:
                status = requests.get(
                    f"http://localhost:8080/solutions/{job_id}/status",
                    timeout=5
                ).json()
                
                print(f"Attempt {attempt}: Status = {status['status']}")
                
                if status["status"] == "SOLVED":
                    solution = requests.get(
                        f"http://localhost:8080/solutions/{job_id}",
                        timeout=5
                    ).json()
                    
                    # Filter only positive quantity decisions
                    decisions = [
                        (self.inventory.find_by_isbn(d["isbn"]), d["restockQuantity"]) 
                        for d in solution["decisions"]
                        if d["restockQuantity"] > 0  # Only include positive quantities
                    ]
                    
                    # Mirror basic restock approach
                    for book, quantity in decisions:
                        if current_total >= self.storage_capacity:
                            break
                            
                        if quantity > 0:  # Double check quantity is positive
                            # Adjust quantity if would exceed capacity
                            if current_total + quantity > self.storage_capacity:
                                quantity = self.storage_capacity - current_total
                            
                            # Update stock
                            if book in self.stock:
                                self.stock[book] += quantity
                            else:
                                self.stock[book] = quantity
                            
                            current_total += quantity
                            log.info(f"Restocked {quantity} copies of {book.title}. Now have {self.stock[book]} copies.")
                    
                    total_restocked = sum(qty for _, qty in decisions)
                    print(f"\nSOLVED! Optimization complete.")
                    print(f"Restocked {total_restocked} books up to capacity {self.storage_capacity}")
                    print(f"Total books in store now: {sum(self.stock.values())}")
                    
                    return decisions
                
                attempt += 1  # Increment attempt counter
                time.sleep(1)  # Add delay between attempts
            
            # Timeout reached
            print("\nOptimization timed out - falling back to basic optimization")
            return self.restock()
            
        except Exception as e:
            log.warning(f"Solver optimization failed: {e}")
            return self.restock()

        print("\nFalling back to basic optimization...")
        # Fallback to basic optimization
        return [(book, max(0, 10 - self.stock.get(book, 0))) 
                for book in self.inventory.books]
    
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