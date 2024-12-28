import random
from inventory import Inventory

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
                print(f"Initiated stock for {book.title} (ISBN: {book.isbn}). Now have {self.stock[book]} copies.")
            else:
                print(f"{book.title} (ISBN: {book.isbn}) is already in stock.")

    def list_stock(self):
        for book, quantity in self.stock.items():
            print(f"{book.title} (ISBN: {book.isbn}): {quantity} copies")

    def sell_book(self, title, quantity=1):
        for book in self.stock:
            if book.title == title:
                if self.stock[book] >= quantity:
                    self.stock[book] -= quantity
                    print(f"Sold {quantity} copies of {title} (ISBN: {book.isbn}).")
                    if self.stock[book] == 0:
                        del self.stock[book]
                    return
                else:
                    print(f"Not enough copies of {title} (ISBN: {book.isbn}) to sell. Available: {self.stock[book]}")
                    return
        print(f"{title} is not in stock.")

    def restock(self):
        current_total = sum(self.stock.values())
        while current_total < self.storage_capacity:
            book = random.choice(self.inventory.books)
            if book in self.stock:
                self.stock[book] += 1
            else:
                self.stock[book] = 1
            current_total += 1
            print(f"Restocked {book.title} (ISBN: {book.isbn}). Now have {self.stock[book]} copies.")

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
            print("No more books available to sell.")
            break
