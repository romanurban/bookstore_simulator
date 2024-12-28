import pandas as pd
import random

class Book:
    def __init__(self, title, authors, genre, price, isbn, publication_date=None, average_rating=0.0, num_pages=0):
        self.title = title
        self.authors = authors
        self.genre = genre
        self.price = price
        self.isbn = isbn
        self.publication_date = publication_date
        self.average_rating = average_rating
        self.num_pages = num_pages

    def __repr__(self):
        return f"Book(title={self.title}, isbn={self.isbn})"


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
            try:
                rating = float(row['average_rating'])
            except ValueError:
                rating = 0.0
            try:
                pages = int(row['num_pages'])
            except (ValueError, KeyError):
                pages = 0
            book = Book(
                title=row['title'],
                authors=row['authors'],
                genre=row['genre'],
                price=float(row['price'].replace('£', '')),
                isbn=row['isbn'],
                publication_date=row['publication_date'],
                average_rating=rating,
                num_pages=pages
            )
            self.add_book(book)

    def find_book_by_title(self, title):
        """
        Find a book by title.
        """
        for book in self.books:
            if book.title == title:
                return book
        return None

    def list_inventory(self):
        """
        Display all books in the inventory.
        """
        for book in self.books:
            print(
                f"{book.title} | {book.authors} | {book.genre} | "
                f"£{book.price:.2f} | "
                f"Published: {book.publication_date} | Rating: {book.average_rating} | "
                f"Pages: {book.num_pages}"
            )


# Example usage
if __name__ == "__main__":
    inventory = Inventory()
    inventory.load_from_dataset("data/catalog.csv")
    inventory.list_inventory()
