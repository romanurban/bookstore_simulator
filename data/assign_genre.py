import pandas as pd
import random

# List of genres
genres = [
    "Fiction", "Non-Fiction", "Mystery", "Thriller", "Romance", "Science Fiction", "Fantasy", "Young Adult",
    "Historical Fiction", "Biography", "Autobiography", "Self-Help", "Horror", "Adventure", "Crime", "Graphic Novels",
    "Children's Literature", "Poetry", "Contemporary", "Dystopian", "Memoir", "Classics", "Spirituality", "Philosophy",
    "Humor", "Paranormal", "Drama", "Urban Fiction", "Literary Fiction", "Short Stories", "Political Fiction", "Science",
    "Travel", "Cookbooks", "Essays", "Western", "True Crime", "LGBTQ+", "Women's Fiction", "Satire", "Business", "Education",
    "Psychology", "Medical", "Technology", "Religion", "Art", "War", "Nature", "Sports", "Anthology"
]

# Main function to process the dataset
def process_books_by_isbn(input_csv, output_csv):
    # Load the dataset
    df = pd.read_csv(input_csv)
    
    # Check if the ISBN column exists
    if "isbn" not in df.columns:
        raise ValueError("Input CSV must contain an 'isbn' column.")
    
    # Randomly assign genres to each book
    df["main_category"] = [random.choice(genres) for _ in range(len(df))]
    
    # Save the updated DataFrame to a new CSV
    df.to_csv(output_csv, index=False)
    print(f"Updated dataset saved to {output_csv}")

# Script entry point
if __name__ == "__main__":
    # Input and output CSV files
    input_csv = "data/catalog.csv"  # Replace with your input CSV filename
    output_csv = "data/catalog_with_genres.csv"  # Desired output CSV filename
    
    # Process the dataset
    process_books_by_isbn(input_csv, output_csv)