import random
import logging
from inventory import Inventory
from optimization.solver import solve_problem
from optimization.book_entity import BookEntity
from customer import Customer

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Store:
    def __init__(self, inventory, storage_capacity):
        self.inventory = inventory
        self.storage_capacity = storage_capacity
        self.stock = {}
        self.initiate_stock()

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

    def restock_optimized(self):
        books = [
            BookEntity(
                title=book.title,
                author=book.authors,
                genre=book.genre,
                price=book.price,
                rating=book.average_rating,
                is_seasonal=self.is_seasonal(book),
                current_stock=self.stock.get(book, 0)
            )
            for book in self.inventory.books
        ]

        solution = solve_problem(books, total_stock_capacity=self.storage_capacity)
        for book, plan in zip(self.inventory.books, solution.books):
            self.stock[book] = plan.restock_quantity
    def is_seasonal(self, book):
        """
        Determines if a book is seasonal based on current month and book's genre, title, or keywords.
        """
        from datetime import datetime
        current_month = datetime.now().month

        # Example logic: Check if book's genre or title matches seasonal keywords
        seasonal_keywords = Customer.seasonal_keywords.get(current_month, [])
        return any(keyword in (book.title + " " + book.authors) for keyword in seasonal_keywords)
    
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