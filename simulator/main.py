from inventory import Inventory
from cusomer import CustomerManager
import random

def initialize_simulation():
    """
    Initialize the simulation environment.
    """
    # Load inventory
    print("Initializing inventory...")
    inventory = Inventory()
    inventory.load_from_dataset("data/catalog.csv")
    print("Inventory loaded.")

    # Generate customers
    print("Generating customers...")
    customer_manager = CustomerManager()
    customer_manager.generate_random_customers(10)
    print(f"{len(customer_manager.customers)} customers generated.")

    return inventory, customer_manager

def run_simulation(inventory, customer_manager, num_days=7):
    """
    Simulate a bookstore for a given number of days.
    """
    print(f"Running simulation for {num_days} days...")
    daily_sales = []

    for day in range(1, num_days + 1):
        print(f"\nDay {day}:")
        # Simulate customer actions
        customer_manager.simulate_customer_actions(inventory)

        # Collect daily sales data
        day_sales = {
            "day": day,
            "remaining_stock": sum(book.stock for book in inventory.books),
            "total_revenue": sum(
                (book.price * (original_stock - book.stock))
                for book, original_stock in zip(inventory.books, [book.stock for book in inventory.books])
            )
        }
        daily_sales.append(day_sales)

    return daily_sales

def generate_report(daily_sales):
    """
    Generate a summary report of the simulation.
    """
    print("\nSimulation Summary Report:")
    total_revenue = sum(day["total_revenue"] for day in daily_sales)
    total_stock_remaining = daily_sales[-1]["remaining_stock"]

    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Remaining Stock at End of Simulation: {total_stock_remaining} books")

    print("\nDaily Breakdown:")
    for day in daily_sales:
        print(f"Day {day['day']}: Revenue = ${day['total_revenue']:.2f}, Remaining Stock = {day['remaining_stock']} books")

if __name__ == "__main__":
    # Step 1: Initialize
    inventory, customer_manager = initialize_simulation()

    # Step 2: Run the simulation
    daily_sales = run_simulation(inventory, customer_manager, num_days=7)

    # Step 3: Generate a report
    generate_report(daily_sales)

    # Optional: Save data for optimization
    print("\nSaving simulation data for optimization phase...")
    sales_data = inventory.get_sales_data()
    print(f"Data saved: {sales_data}")
