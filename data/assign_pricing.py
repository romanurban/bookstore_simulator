import csv
import math
import sys

def calculate_price(num_pages):
    base_price = 5.00 + (0.01 * num_pages)
    raw_retail_price = base_price * 1.2
    retail_price = math.floor(raw_retail_price) + 0.99
    return base_price, retail_price

def assign_prices_to_csv(input_csv, output_csv):
    with open(input_csv, mode='r', newline='', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        # Filter out any None or blank fieldnames
        valid_fieldnames = [f for f in reader.fieldnames if f and f.strip()]
        fieldnames = valid_fieldnames + ["Price", "RetailPrice"]
        rows = []

        for row in reader:
            # Instead of using "Length", use "num_pages"
            pages_str = row.get("num_pages") or "0"
            pages = int(pages_str) if pages_str.isdigit() else 0
            base_price, retail_price = calculate_price(pages)
            row["Price"] = f"£{base_price:.2f}"
            row["RetailPrice"] = f"£{retail_price:.2f}"
            # Remove any None or blank keys
            clean_row = {k: v for k,v in row.items() if k and k.strip()}
            rows.append(clean_row)

    with open(output_csv, mode='w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.csv> <output.csv>")
        sys.exit(1)
    assign_prices_to_csv(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()