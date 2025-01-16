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

def simulate_sales(store, days, log_filename, revenue_log_filename, solver_type="basic"):
    """
    solver_type options:
    - "basic": use basic restock
    - "timefold": use timefold optimization
    - "alternative": use alternative solver (LAHC)
    """
    total_sold = 0
    total_revenue = 0.0
    current_date = datetime(2025, 1, 1)  # Set a fixed start date for simulation

    avg_sbd = {0: 150, 1: 160, 2: 170, 3: 180, 4: 190, 5: 200, 6: 210}
    
    # Add metrics tracking
    restock_metrics = []
    
    for d in range(1, days + 1):
        day_of_week = current_date.weekday()
        ads = avg_sbd[day_of_week]
        
        ds = int(random.gauss(ads, 20))
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
            if solver_type == "alternative":
                decisions, metrics = store.restock_alternative(current_date)
                metrics['day'] = d
                restock_metrics.append(metrics)
            elif solver_type == "timefold":
                store.restock_timefold_optimized(current_date)
            else:
                decisions, metrics = store.restock()
                metrics['day'] = d
                restock_metrics.append(metrics)
        store.list_stock()
        
        current_date += timedelta(days=1)
    
    # Analysis at the end of simulation
    if restock_metrics:  # Now works for both basic and alternative
        print(f"\n{solver_type.capitalize()} Solver Performance Analysis:")
        print("=======================================")
        avg_metrics = {
            'avg_diversity_improvement': sum(m['after_diversity'] - m['before_diversity'] for m in restock_metrics) / len(restock_metrics),
            'avg_rating_improvement': sum(m['after_avg_rating'] - m['before_avg_rating'] for m in restock_metrics) / len(restock_metrics),
            'avg_seasonal_improvement': sum(m['after_seasonal_matches'] - m['before_seasonal_matches'] for m in restock_metrics) / len(restock_metrics),
            'avg_restock_quantity': sum(m['restock_quantity'] for m in restock_metrics) / len(restock_metrics),
            'avg_unique_books': sum(m['unique_books_added'] for m in restock_metrics) / len(restock_metrics),
        }
        
        print(f"Average Improvements per Restock:")
        print(f"- Book Diversity: {avg_metrics['avg_diversity_improvement']:.2f}")
        print(f"- Rating: {avg_metrics['avg_rating_improvement']:.2f}")
        print(f"- Seasonal Matches: {avg_metrics['avg_seasonal_improvement']:.2f}")
        print(f"- Restock Quantity: {avg_metrics['avg_restock_quantity']:.2f}")
        print(f"- Unique Books Added: {avg_metrics['avg_unique_books']:.2f}")
        
        # Save metrics to file
        metrics_filename = os.path.join(log_folder, f"{int(datetime.now().timestamp())}_metrics.log")
        with open(metrics_filename, 'w') as f:
            for metric in restock_metrics:
                f.write(f"Day {metric['day']}: {str(metric)}\n")
            f.write("\nAverages:\n")
            f.write(str(avg_metrics))
    
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

    # Run simulation with different solvers
    #simulate_sales(store, days=31, log_filename=log_filename, revenue_log_filename=revenue_log_filename, solver_type="basic")
    # simulate_sales(store, days=31, log_filename=log_filename, revenue_log_filename=revenue_log_filename, solver_type="timefold")
    simulate_sales(store, days=31, log_filename=log_filename, revenue_log_filename=revenue_log_filename, solver_type="alternative")