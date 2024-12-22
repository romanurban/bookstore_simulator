import pandas as pd
import random

class Book:
    def __init__(self, title, author, genre, price, stock):
        self.title = title
        self.author = author
        self.genre = genre
        self.price = price
        self.stock = stock

    def sell(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            return True  # Sale successful
        return False  # Insufficient stock

    def restock(self, quantity):
        self.stock += quantity

    def __repr__(self):
        return f"Book(title={self.title}, stock={self.stock})"


class Inventory:
    def __init__(self):
        self.books = []

    def add_book(self, book):
        self.books.append(book)

    def load_from_dataset(self, filepath):
        """
        Load books from a dataset (e.g., Goodreads Books dataset).
        """
        data = pd.read_csv(filepath)
        for _, row in data.iterrows():
            # Customize column names as per dataset
            book = Book(
                title=row['title'],
                author=row['author'],
                genre=row['genre'],
                price=float(row['price']),
                stock=random.randint(5, 50)  # Random initial stock
            )
            self.add_book(book)

    def find_book(self, title):
        """
        Find a book by title.
        """
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def sell_book(self, title, quantity):
        """
        Sell a book and update inventory.
        """
        book = self.find_book(title)
        if book and book.sell(quantity):
            print(f"Sold {quantity} copy(ies) of '{title}'.")
        else:
            print(f"Failed to sell '{title}' - insufficient stock or not found.")

    def restock_book(self, title, quantity):
        """
        Restock a book.
        """
        book = self.find_book(title)
        if book:
            book.restock(quantity)
            print(f"Restocked {quantity} copy(ies) of '{title}'.")
        else:
            print(f"Book '{title}' not found in inventory.")

    def list_inventory(self):
        """
        Display all books in the inventory.
        """
        for book in self.books:
            print(f"{book.title} | {book.author} | {book.genre} | ${book.price:.2f} | Stock: {book.stock}")

    def get_sales_data(self):
        """
        Generate sales data for analysis.
        """
        return [{"title": book.title, "stock": book.stock, "price": book.price} for book in self.books]


# Example usage
if __name__ == "__main__":
    inventory = Inventory()
    inventory.load_from_dataset("data/goodreads_books.csv")
    inventory.list_inventory()
    inventory.sell_book("Book Title Example", 2)
    inventory.restock_book("Book Title Example", 5)
    inventory.list_inventory()
