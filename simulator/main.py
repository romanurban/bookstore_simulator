from inventory import Inventory
from customer import CustomerManager
from physical_store import PhysicalStore, create_random_restock_plan
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
    store = PhysicalStore(display_capacity=100, storage_capacity=300, inventory=inventory)
    store.global_inventory = inventory  # Link store with inventory
    store.restock_from_inventory(inventory, create_random_restock_plan(inventory))

    for day in range(1, num_days + 1):
        print(f"\nDay {day}:")
        daily_revenue = 0
        for _ in range(random.randint(250, 350)):
            customer = random.choice(customer_manager.customers)
            purchased_books = customer.purchase_books(store)
            daily_revenue += sum(book.price for book in purchased_books)

        # Weekly restock
        if day % 7 == 0:
            store.restock_from_inventory(inventory, create_random_restock_plan(inventory))

        daily_sales.append({
            "day": day,
            "remaining_stock_store": sum(store.display_shelves.values()) + sum(store.storage_room.values()),
            "total_revenue": daily_revenue
        })
    return daily_sales

def create_random_restock_plan(inventory):
    plan = {}
    for book in inventory.books:
        plan[book.title] = random.randint(5, 20)
    return plan

def max_capacity_plan(inventory, store):
    plan = {}
    # Fill up to store.display_capacity + store.storage_capacity
    # Example naive approach
    for book in inventory.books:
        plan[book.title] = 10  # or some logic
    return plan

def generate_report(daily_sales):
    """
    Generate a summary report of the simulation.
    """
    print("\nSimulation Summary Report:")
    total_revenue = sum(day["total_revenue"] for day in daily_sales)
    total_stock_remaining = daily_sales[-1]["remaining_stock_store"]

    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Remaining Stock at End of Simulation: {total_stock_remaining} books")

    print("\nDaily Breakdown:")
    for day in daily_sales:
        print(f"Day {day['day']}: Revenue = ${day['total_revenue']:.2f}, Remaining Stock = {day['remaining_stock_store']} books")

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
