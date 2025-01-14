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
        Load books from a CSV dataset.
        """
        import pandas as pd
        try:
            df = pd.read_csv(filepath)
            for _, row in df.iterrows():
                # Clean price by removing '£' and converting to float
                price_str = str(row['price']).replace('£', '')
                
                if not is_valid_isbn(str(row['isbn'])):
                    print(f"Skipping invalid ISBN: {row['isbn']}")
                    continue

                book = Book(
                    title=row['title'],
                    authors=row['authors'],
                    genre=row['genre'],
                    price=float(price_str),
                    isbn=str(row['isbn']),
                    publication_date=row['publication_date'],
                    average_rating=float(row['average_rating']),
                    num_pages=int(row['num_pages'])
                )
                self.add_book(book)
        except Exception as e:
            print(f"Error loading dataset: {e}")

    def find_book_by_title(self, title):
        """
        Find a book by title.
        """
        for book in self.books:
            if book.title == title:
                return book
        return None

    def find_by_isbn(self, isbn: str) -> Book:
        """Find book by ISBN in inventory"""
        for book in self.books:
            if book.isbn == isbn:
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
                f"Pages: {book.num_pages} | "
                f"ISBN: {book.isbn}"
            )


def is_valid_isbn(isbn):
    """
    Validate ISBN format. Accepts ISBN-10 and ISBN-13.
    """
    if not isbn:
        return False
        
    # Remove any hyphens or spaces
    isbn = str(isbn).replace('-', '').replace(' ', '')
    
    # ISBN-13
    if len(isbn) == 13:
        try:
            # All characters should be digits
            if not isbn.isdigit():
                return False
            
            # ISBN-13 validation algorithm
            total = 0
            for i in range(12):
                if i % 2 == 0:
                    total += int(isbn[i])
                else:
                    total += int(isbn[i]) * 3
            check = (10 - (total % 10)) % 10
            return check == int(isbn[-1])
        except ValueError:
            return False
            
    # ISBN-10
    elif len(isbn) == 10:
        try:
            # Check if first 9 characters are digits
            if not isbn[:9].isdigit():
                return False
            
            # Last character can be 'X' or digit    
            if not (isbn[-1].isdigit() or isbn[-1].upper() == 'X'):
                return False
                
            # ISBN-10 validation algorithm    
            total = 0
            for i in range(9):
                total += int(isbn[i]) * (10 - i)
            last = isbn[-1].upper()
            if last == 'X':
                total += 10
            else:
                total += int(last)
            return total % 11 == 0
        except ValueError:
            return False
            
    return False


# Example usage
if __name__ == "__main__":
    inventory = Inventory()
    inventory.load_from_dataset("../data/catalog.csv")
    inventory.list_inventory()
