import random

class Customer:
    def __init__(self, customer_id, name, preferred_genres, price_range, min_rating):
        self.customer_id = customer_id
        self.name = name
        self.preferred_genres = preferred_genres  # List of preferred genres
        self.price_range = price_range  # Tuple (min_price, max_price)
        self.min_rating = min_rating  # Minimum acceptable rating

    def select_books(self, inventory):
        """
        Select books to purchase based on preferences.
        Returns a list of selected books.
        """
        selected_books = []
        for book in inventory.books:
            if (
                book.genre in self.preferred_genres
                and self.price_range[0] <= book.price <= self.price_range[1]
                and random.random() > 0.5  # Randomly decide to buy within preferences
            ):
                selected_books.append(book)
        return selected_books

    def purchase_books(self, inventory):
        """
        Simulate the purchase of books from the inventory.
        """
        selected_books = self.select_books(inventory)
        for book in selected_books:
            quantity = random.randint(1, 3)  # Random quantity to purchase
            inventory.sell_book(book.title, quantity)
        return selected_books

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
        genres = ["Fiction", "Non-fiction", "Mystery", "Sci-fi", "Romance"]
        for i in range(num_customers):
            customer = Customer(
                customer_id=i,
                name=random.choice(names),
                preferred_genres=random.sample(genres, k=random.randint(1, 3)),
                price_range=(random.uniform(5, 15), random.uniform(20, 50)),
                min_rating=random.uniform(3.0, 5.0),
            )
            self.customers.append(customer)

    def simulate_customer_actions(self, inventory):
        """
        Simulate actions for all customers.
        """
        for customer in self.customers:
            print(f"{customer.name} is browsing the bookstore...")
            purchased_books = customer.purchase_books(inventory)
            if purchased_books:
                print(f"{customer.name} purchased: {[book.title for book in purchased_books]}")
            else:
                print(f"{customer.name} did not find any books to purchase.")

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
    inventory.load_from_dataset("data/goodreads_books.csv")

    # Initialize customers
    customer_manager = CustomerManager()
    customer_manager.generate_random_customers(5)

    # Simulate customer actions
    customer_manager.simulate_customer_actions(inventory)

    # Display remaining inventory
    inventory.list_inventory()
