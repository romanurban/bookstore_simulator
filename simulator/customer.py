import random

class Customer:
    def __init__(self, preference_type, preference_value):
        self.preference_type = preference_type
        self.preference_value = preference_value

    def choose_book(self, store):
        if self.preference_type == "author":
            return self._choose_by_author(store)
        elif self.preference_type == "genre":
            return self._choose_by_genre(store)
        elif self.preference_type == "title":
            return self._choose_by_title(store)
        elif self.preference_type == "rating":
            return self._choose_by_rating(store)
        elif self.preference_type == "price":
            return self._choose_by_price(store)
        else:
            return None

    def _choose_by_author(self, store):
        for book in store.stock.keys():
            if self.preference_value in book.authors:
                return book
        return None

    def _choose_by_genre(self, store):
        for book in store.stock.keys():
            if self.preference_value == book.genre:
                return book
        return None

    def _choose_by_title(self, store):
        for book in store.stock.keys():
            if self.preference_value == book.title:
                return book
        return None

    def _choose_by_rating(self, store):
        highest_rated_book = None
        highest_rating = 4.0
        for book in store.stock.keys():
            if book.average_rating > highest_rating:
                highest_rated_book = book
                highest_rating = book.average_rating
        return highest_rated_book

    def _choose_by_price(self, store):
        for book in store.stock.keys():
            if book.price <= self.preference_value:
                return book
        return None

    @staticmethod
    def generate_customer_profiles(num_customers):
        customer_profiles = []
        for _ in range(num_customers // 10):  # 10% prefer a particular title
            customer_profiles.append(Customer("title", "If the River Was Whiskey"))
        for _ in range(num_customers // 10):  # 10% prefer a particular author
            customer_profiles.append(Customer("author", "Somerset Maugham"))
        for _ in range(num_customers // 10):  # 10% prefer a particular genre
            customer_profiles.append(Customer("genre", "Fantasy"))
        for _ in range(num_customers // 10):  # 10% prefer highest rating books
            customer_profiles.append(Customer("rating", None))
        for _ in range(num_customers // 10):  # 10% prefer books under a specific price
            customer_profiles.append(Customer("price", 10.0))
        for _ in range(num_customers // 2):  # 50% have no specific preference
            customer_profiles.append(Customer("none", None))
        return customer_profiles