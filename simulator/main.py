import os
import random
from datetime import datetime, timedelta
from inventory import Inventory
from store import Store
from customer import Customer

def log_sale(isbn, quantity, sale_date, log_filename):
    with open(log_filename, "a") as log_file:
        log_file.write(f"{sale_date.strftime('%Y-%m-%d')} - Sold ISBN: {isbn}, Quantity: {quantity}\n")

def simulate_sales(store, days, daily_sales, log_filename):
    total_sold = 0
    total_revenue = 0.0
    current_date = datetime.now()
    
    for day in range(1, days + 1):
        daily_sold = 0
        daily_revenue = 0.0
        print(f"Day {day} - {current_date.strftime('%Y-%m-%d')}")
        
        # Generate new customer profiles each day
        customer_profiles = Customer.generate_customer_profiles(100)
        
        for _ in range(daily_sales):
            if store.stock:
                customer = random.choice(customer_profiles)
                book = customer.choose_book(store)
                if book:
                    quantity = random.randint(1, 2)
                    sold_book = store.sell_book(book.title, quantity=quantity)
                    if sold_book:
                        log_sale(sold_book.isbn, quantity, current_date, log_filename)
                        daily_sold += quantity
                        daily_revenue += sold_book.price * quantity
            else:
                print("No more books available to sell.")
                break

        total_sold += daily_sold
        total_revenue += daily_revenue
        print(f"Total books sold today: {daily_sold}")
        print(f"Total revenue today: ${daily_revenue:.2f}")
        
        if day % 7 == 0:  # Restock every week
            store.restock()
        store.list_stock()
        
        current_date += timedelta(days=1)
    
    print(f"Total books sold over {days} days: {total_sold}")
    print(f"Total revenue over {days} days: £{total_revenue:.2f}")

if __name__ == "__main__":
    inventory = Inventory()
    inventory.load_from_dataset("data/catalog.csv")
    store = Store(inventory, storage_capacity=100)
    store.list_stock()

    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)
    log_filename = os.path.join(log_folder, f"{int(datetime.now().timestamp())}.log")

    simulate_sales(store, days=365, daily_sales=10, log_filename=log_filename)