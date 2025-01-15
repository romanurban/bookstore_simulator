import os
import random
from datetime import datetime, timedelta
from inventory import Inventory
from store import Store
from customer import Customer

def log_sale(isbn, quantity, sale_date, log_filename):
    with open(log_filename, "a") as log_file:
        log_file.write(f"{sale_date.strftime('%Y-%m-%d')} - Sold ISBN: {isbn}, Quantity: {quantity}\n")

def log_revenue(day, daily_sold, daily_revenue, total_revenue, revenue_log_filename):
    with open(revenue_log_filename, "a") as log_file:
        log_file.write(f"Day {day}: Books Sold: {daily_sold}, Daily Revenue: £{daily_revenue:.2f}, Total Revenue: £{total_revenue:.2f}\n")

def simulate_sales(store, days, log_filename, revenue_log_filename, use_optimized_restock=False):
    total_sold = 0
    total_revenue = 0.0
    x = use_optimized_restock
    current_date = datetime(2025, 1, 1)  # Set a fixed start date for simulation

    avg_sbd = {0: 150, 1: 160, 2: 170, 3: 180, 4: 190, 5: 200, 6: 210}
    
    for d in range(1, days + 1):
        day_of_week = current_date.weekday()
        ads = avg_sbd[day_of_week]
        
        ds = int(random.gauss(ads, 20) * (1.5 if x and d > 14 else (1.3 if x and d > 7 else 1)))
        daily_sold = 0
        daily_revenue = 0.0
        print(f"Day {d} - {current_date.strftime('%Y-%m-%d')}")
        
        # Generate new customer profiles each day
        customer_profiles = Customer.generate_customer_profiles(100, store)
        
        for _ in range(ds):
            if store.stock:
                customer = random.choice(customer_profiles)
                book = customer.choose_book(store, current_date)
                if book:
                    quantity = 1
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
        print(f"Total revenue today: £{daily_revenue:.2f}")
        
        log_revenue(d, daily_sold, daily_revenue, total_revenue, revenue_log_filename)
        
        if d % 7 == 0:  # Restock every week
            if use_optimized_restock:
                store.restock_optimized(current_date)  # Pass current_date to restock_optimized
            else:
                store.restock()
        store.list_stock()
        
        current_date += timedelta(days=1)
    
    print(f"Total books sold over {days} days: {total_sold}")
    print(f"Total revenue over {days} days: £{total_revenue:.2f}")
    with open(revenue_log_filename, "a") as log_file:
        log_file.write(f"Total books sold over {days} days: {total_sold}\n")
        log_file.write(f"Total revenue over {days} days: £{total_revenue:.2f}\n")

if __name__ == "__main__":
    inventory = Inventory()
    inventory.load_from_dataset("../data/catalog.csv")
    store = Store(inventory, storage_capacity=3000)
    store.list_stock()

    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)
    log_filename = os.path.join(log_folder, f"{int(datetime.now().timestamp())}_sales.log")
    revenue_log_filename = os.path.join(log_folder, f"{int(datetime.now().timestamp())}_revenue.log")

    # Run simulation with random restocking
    # simulate_sales(store, days=365, log_filename=log_filename, revenue_log_filename=revenue_log_filename, use_optimized_restock=False)

    # Run simulation with optimized restocking
    simulate_sales(store, days=31, log_filename=log_filename, revenue_log_filename=revenue_log_filename, use_optimized_restock=False)