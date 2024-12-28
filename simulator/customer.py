import random
from physical_store import PhysicalStore

class Customer:
    def __init__(
        self,
        customer_id,
        name,
        preferred_genres,
        price_range,
        min_rating,
        preferred_authors=None,
        page_preference=None,          # ("short", "long", or None)
        publication_year_preference=None,
        willing_to_accept_alternative=False
    ):
        self.customer_id = customer_id
        self.name = name
        self.preferred_genres = preferred_genres  # List of preferred genres
        self.price_range = price_range  # Tuple (min_price, max_price)
        self.min_rating = min_rating  # Minimum acceptable rating
        self.preferred_authors = preferred_authors or []
        self.page_preference = page_preference
        self.publication_year_preference = publication_year_preference
        self.willing_to_accept_alternative = willing_to_accept_alternative


    def matches_preferences(self, book):
        """
        Check if a book matches the customer's preferences.
        """
        if book.genre not in self.preferred_genres:
            return False
        if not (self.price_range[0] <= book.price <= self.price_range[1]):
            return False
        if book.rating < self.min_rating:
            return False
        if self.preferred_authors and book.author not in self.preferred_authors:
            return False
        if self.page_preference == "short" and book.pages > 300:
            return False
        if self.page_preference == "long" and book.pages < 300:
            return False
        if self.publication_year_preference and book.publication_year != self.publication_year_preference:
            return False
        return True

    def purchase_books(self, store):
        """
        Simulate a customer's book purchasing decisions based on preferences.
        """
        purchased_books = []

        # Get the books on display
        books_on_display = store.get_books_on_display()

        print(f"{self.name} found {len(books_on_display)} books on display.")

        # Filter books that match customer's preferences
        matching_books = [
            book for book in books_on_display
            if self.matches_preferences(book)
        ]

        # Shuffle the list to simulate browsing randomness
        random.shuffle(matching_books)

        for book in matching_books:
            # Check availability and budget
            if store.display_shelves.get(book.isbn, 0) > 0:
                store.sell_book(book.isbn, 1)  # Purchase one book
                purchased_books.append(book)
                print(f"{self.name} purchased '{book.title}'.")

            # Stop purchasing if the budget runs out
            if random.uniform(self.price_range[0], self.price_range[1]) < book.price:
                break

        if not purchased_books and self.willing_to_accept_alternative:
            # Try alternatives if no preferred books are available
            alternative_books = [
                book for book in books_on_display
                if book.price <= self.price_range[1] and book.rating >= self.min_rating
            ]
            random.shuffle(alternative_books)

            for book in alternative_books:
                if store.display_shelves.get(book.isbn, 0) > 0:
                    store.sell_book(book.isbn, 1)
                    purchased_books.append(book)
                    print(f"{self.name} settled for an alternative: '{book.title}'.")
                    break

        return purchased_books


    def __repr__(self):
        return f"Customer(id={self.customer_id}, name={self.name})"


class CustomerManager:
    def __init__(self):
        self.customers = []

    def generate_random_customers(self, num_customers):
        """
        Generate a list of random customers.
        """
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        genres = [
    "Fiction", "Non-Fiction", "Mystery", "Thriller", "Romance", "Science Fiction", "Fantasy", "Young Adult",
    "Historical Fiction", "Biography", "Autobiography", "Self-Help", "Horror", "Adventure", "Crime", "Graphic Novels",
    "Children's Literature", "Poetry", "Contemporary", "Dystopian", "Memoir", "Classics", "Spirituality", "Philosophy",
    "Humor", "Paranormal", "Drama", "Urban Fiction", "Literary Fiction", "Short Stories", "Political Fiction", "Science",
    "Travel", "Cookbooks", "Essays", "Western", "True Crime", "LGBTQ+", "Women's Fiction", "Satire", "Business", "Education",
    "Psychology", "Medical", "Technology", "Religion", "Art", "War", "Nature", "Sports", "Anthology"
]
        for i in range(num_customers):
            customer = Customer(
                customer_id=i,
                name=random.choice(names),
                preferred_genres=random.sample(genres, k=random.randint(1, 3)),
                price_range=(random.uniform(5, 15), random.uniform(20, 50)),
                min_rating=random.uniform(3.0, 5.0),
            )
            self.customers.append(customer)

    def simulate_customer_actions(self, store):
        for customer in self.customers:
            print(f"{customer.name} is browsing the bookstore...")
            purchased_books = customer.purchase_books(store)
            if purchased_books:
                print(f"{customer.name} purchased {len(purchased_books)} books.")
            else:
                print(f"{customer.name} didn't find any books to buy.")


    def list_customers(self):
        """
        Display all customers.
        """
        for customer in self.customers:
            print(customer)


# Example usage
if __name__ == "__main__":
    from inventory import Inventory

    # Initialize inventory
    inventory = Inventory()
    inventory.load_from_dataset("data/catalog.csv")

    # Initialize customers
    customer_manager = CustomerManager()
    customer_manager.generate_random_customers(5)

    store = PhysicalStore(display_capacity=100, storage_capacity=300, inventory=inventory)

    # Simulate customer actions
    customer_manager.simulate_customer_actions(store)

