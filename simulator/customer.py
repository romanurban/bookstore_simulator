import random
from collections import Counter
from datetime import datetime

class Customer:
    seasonal_keywords = {
        1: [
            "Habits", "Motivation", "Resolutions", "Change", "Clear", "Sincero", "Kiyosaki",
            "Mindset", "Goals", "Minimalism", "Atomic", "Power", "Purpose", "Clarity",
            "Growth", "Robbins", "Success", "Wealth", "Focus", "Planning", "Determination",
            "Energy", "New", "Start", "Beginnings", "Discipline", "Achievement", "Strategy",
            "Vision", "Optimism", "Renewal", "Career", "Dreams", "Balance", "Reinvention",
            "Resolve", "Practice", "Choices", "Wellness", "Health", "Challenge", "Routine",
            "Self", "Discovery", "Inner", "Strength", "Clarity", "Progress", "Foundations",
            "Building", "Empower", "Reboot", "Goals", "Clear"
        ],
        2: [
            "Love", "Romance", "Sparks", "Austen", "Brontë", "Hearts", "Cupid", "Pride",
            "Prejudice", "Outlander", "Passion", "Valentine", "Affection", "Jane", "Darcy",
            "Wedding", "Relationships", "Sweet", "Nicholas", "Tenderness", "Crush", "Roses",
            "Letters", "Poetry", "Emotions", "Yearning", "Longing", "Forever", "Destiny",
            "Devotion", "Admire", "Cherish", "Couples", "Amour", "Connection", "Sentiments",
            "Romance", "Roses", "Charm", "Charming", "Elegant", "Couples", "Darling",
            "Kisses", "Flirt", "Attraction", "Sweetheart", "Candlelight", "Darling",
            "Wistful", "Endearing", "Magnetic", "Swoon"
        ],
        3: [
            "Spring", "Growth", "Green", "Empowerment", "Feminism", "Angelou", "Blossoms",
            "Change", "Equality", "Renewal", "Women", "Sheryl", "Wollstonecraft", "Nature",
            "Forest", "Awakening", "Maya", "Dreams", "Rights", "Courage", "Strength",
            "Resilience", "Spirit", "Voice", "March", "Embrace", "Blossoming", "Equality",
            "Reform", "Advocacy", "Leaders", "Unity", "Visionary", "Inspire", "Bloom",
            "Roots", "Canopy", "Branches", "Petals", "Eco", "Seeds", "Rivers", "Sunshine",
            "Morning", "New", "Fields", "Meadows", "Hope", "Rejuvenate", "Sheryl", "Bright",
            "History", "Compassion", "Leader", "Fragrance"
        ],
        4: [
            "Nature", "Tolkien", "Hobbit", "Garden", "Easter", "Middle-Earth", "Flowers",
            "Rivers", "Trees", "Adventures", "Renewal", "Mystical", "Green", "Outdoor",
            "Magic", "Bloom", "Spring", "Lore", "Wanderlust", "Fantasy", "Serenity",
            "Wildlife", "Planting", "Wander", "Frodo", "Shire", "Trails", "Mountains",
            "Quiet", "Peace", "Village", "Plant", "Blossom", "Rain", "Budding", "Hiking",
            "Renewal", "Outdoor", "Woods", "Earth", "Sunshine", "Growth", "Gardens",
            "Simplicity", "Nurture", "Landscapes", "Awaken", "Leaves", "Tolkien", "Fauna",
            "Flora", "Cycles", "Meadow", "Fields"
        ],
        5: [
            "Mother", "Family", "Gifting", "Home", "Domestic", "Cookbooks", "Recipes",
            "Love", "Parenting", "Barbara", "Sisters", "Nurture", "Alcott", "Little",
            "Women", "Warmth", "Care", "Comfort", "Kingsolver", "Traditions", "Memories",
            "Heartfelt", "Generations", "Household", "Gathering", "Kindness", "Loyalty",
            "Support", "Affection", "Mom", "Floral", "Motherhood", "Matriarch", "Love",
            "Heritage", "Feminine", "Daughter", "Son", "Close", "Heirloom", "Memories",
            "Tales", "Portrait", "Serenity", "Heartwarming", "Kitchen", "Dinner",
            "Gathering", "Togetherness", "Bonds", "Warm", "Cooks", "Handwritten"
        ],
        6: [
            "Pride", "Love", "Wilde", "LGBTQ+", "Freedom", "Equality", "Rainbow", "Summer",
            "Romance", "Colorful", "Alice", "Heartstopper", "Bright", "Levithan", "Inclusion",
            "Adventures", "Stories", "Joy", "Sunlight", "Bonds", "Allies", "Festivals", "Prideful",
            "Bold", "Empower", "Celebration", "Courage", "Stories", "Awareness", "Creativity",
            "Literature", "Identity", "Acceptance", "Friendship", "Discovery", "Humanity", "Brave",
            "Storytelling", "Vibrant", "Bonds", "Authentic", "Expression", "Diversity", "Voice",
            "Society", "Progress", "Liberation", "Sparkle", "Unique", "Spectrum", "Parade", "Euphoria"
        ],
        7: [
            "Adventure", "King", "Thrillers", "Patterson", "Heat", "Island", "Sand", "Beach",
            "Murder", "Crime", "Suspense", "Fire", "Danger", "Sun", "Mystery", "Clues", "Waves",
            "Stephen", "Chase", "James", "Journey", "Summer", "Coast", "Detectives", "Dunes",
            "Secrets", "Hidden", "Sea", "Oceans", "Heatwave", "Plot", "Intrigue", "Cryptic", "Twists",
            "Breakout", "Sunset", "Island", "Quest", "Lagoon", "Obsession", "Mirage", "Ambush",
            "Spy", "Intensity", "Tides", "Chills", "Fog", "Puzzles"
        ],
        8: [
            "Education", "School", "Potter", "Rowling", "Magic", "Fantasy", "Students", "Library",
            "Knowledge", "Spells", "Wands", "Hogwarts", "Children", "Youth", "Backpacks", "Lessons",
            "Wisdom", "Reading", "Discover", "Secrets", "Textbooks", "Fiction", "Enigma", "Study",
            "Triumph", "Dormitories", "Wizards", "Teachers", "Quidditch", "Potions", "Maps", "Tales",
            "Fantastic", "Learning", "Pages", "Adventure", "Scholars", "Ladders", "Genius", "Inspiration",
            "Stories", "Discovery", "Dreams", "Imagination", "History", "Writing", "Fantasy"
        ],
        9: [
            "Classics", "Literature", "Orwell", "Fitzgerald", "Steinbeck", "College", "Reading",
            "Study", "Gatsby", "Essays", "Culture", "Mice", "Hemingway", "Victorian", "Seminar",
            "Discourse", "Renaissance", "Fiction", "Chapter", "Verse", "Legacy", "Knowledge",
            "Classrooms", "Wisdom", "Libraries", "Timeless", "Heritage", "Canon", "Poetry", 
            "Structure", "Reflection", "Analysis", "Prose", "Stories", "Timeless", "Study", "Booklist"
        ],
        10: [
            "Halloween", "Horror", "Monsters", "Dracula", "Ghosts", "King", "Poe", "Shadows",
            "Nightmares", "Darkness", "Frights", "Spooky", "Haunted", "Creepy", "Shelley",
            "Witches", "Magic", "Thrills", "Vampires", "Fog", "Evil", "Paranormal", "Candles",
            "Graveyard", "Midnight", "Sorcery", "Chills", "Howling", "Frights", "Screams",
            "Mysterious", "Curse", "Phantom", "Cryptic", "Haze", "Terror", "Gothic", "Eerie"
        ],
        11: [
            "Family", "Thanksgiving", "Harvest", "Dinner", "Gratitude", "Traditions", "Stories", 
            "Feast", "Home", "Warmth", "Togetherness", "Closeness", "Gathering", "Kinship",
            "Bonds", "Seasonal", "Table", "Nostalgia", "Cooking", "Kindness", "Support",
            "Giving", "Celebration", "Unity", "Heartfelt", "Generations", "Heritage", "Recipes"
        ],
        12: [
            "Christmas", "Magic", "Rowling", "Potter", "Cozy", "Snow", "Gifts", "Dickens", 
            "Family", "Traditions", "Holiday", "Lights", "Wands", "Hearth", "Joy", "Yule",
            "Cheer", "Santa", "Nostalgia", "Cookies", "Fireplace", "Candles", "Festive",
            "Frost", "Lanterns", "Classic", "Snowfall", "Ornaments", "Carols", "Tree", 
            "Merry", "Sleigh", "North", "Heartwarming", "December", "Magic"
        ]
    }


    def __init__(self, preference_type, preference_value):
        self.preference_type = preference_type
        self.preference_value = preference_value

    def choose_book(self, store, current_date):
        if self.preference_type == "author":
            return self._choose_by_author(store)
        elif self.preference_type == "genre":
            return self._choose_by_genre(store, current_date)
        elif self.preference_type == "title":
            return self._choose_by_title(store)
        elif self.preference_type == "rating":
            return self._choose_by_rating(store, current_date)
        elif self.preference_type == "price":
            return self._choose_by_price(store)
        else:
            return self._choose_by_none(store, current_date)

    def _choose_by_author(self, store):
        matched_books = [book for book in store.stock.keys() 
                        if self.preference_value in book.authors]
        # 80% chance to walk away if no exact match
        if not matched_books and random.random() < 0.8:
            return None
        return random.choice(matched_books) if matched_books else None

    def _choose_by_genre(self, store, current_date):
        month = current_date.month
        keywords = self.seasonal_keywords.get(month, [])
        seasonal_matches = []
        genre_matches = []
        
        for book in store.stock.keys():
            if self.preference_value == book.genre:
                if any(keyword in (book.title + " " + book.authors) for keyword in keywords):
                    seasonal_matches.append(book)
                genre_matches.append(book)
        
        # First try seasonal matches
        if seasonal_matches:
            return random.choice(seasonal_matches)
        # Then try genre matches, but 80% chance to walk away if not seasonal
        if genre_matches and random.random() > 0.8:
            return random.choice(genre_matches)
        return None

    def _choose_by_title(self, store):
        for book in store.stock.keys():
            if self.preference_value == book.title:
                return book
        # 80% chance to walk away if exact title not found
        if random.random() < 0.8:
            return None
        return None

    def _choose_by_rating(self, store, current_date):
        month = current_date.month
        keywords = self.seasonal_keywords.get(month, [])
        seasonal_rated_books = []
        high_rated_books = []
        
        for book in store.stock.keys():
            if book.average_rating >= 4.5:
                if any(keyword in (book.title + " " + book.authors) for keyword in keywords):
                    seasonal_rated_books.append(book)
                high_rated_books.append(book)
        
        # Try seasonal high-rated books first
        if seasonal_rated_books:
            return random.choice(seasonal_rated_books)
        # Then try just high-rated books, but 80% chance to walk away if not seasonal
        if high_rated_books and random.random() > 0.8:
            return random.choice(high_rated_books)
        return None

    def _choose_by_price(self, store):
        month = datetime.now().month
        keywords = self.seasonal_keywords.get(month, [])
        seasonal_cheap_books = []
        cheap_books = []
        
        for book in store.stock.keys():
            if book.price <= 8.0:  # Changed from 9.0 to 8.0
                if any(keyword in (book.title + " " + book.authors) for keyword in keywords):
                    seasonal_cheap_books.append(book)
                cheap_books.append(book)
        
        # Try seasonal affordable books first
        if seasonal_cheap_books:
            return min(seasonal_cheap_books, key=lambda x: x.price)
        # Then try just cheap books, but 80% chance to walk away if not seasonal
        if cheap_books and random.random() > 0.8:
            return min(cheap_books, key=lambda x: x.price)
        return None

    def _choose_by_none(self, store, current_date):
        month = current_date.month
        keywords = self.seasonal_keywords.get(month, [])
        seasonal_books = []
        backup_books = []

        for book in store.stock.keys():
            if any(keyword in (book.title + " " + book.authors) for keyword in keywords):
                if book.price <= 8.0 and book.average_rating >= 4.5:  
                    seasonal_books.append(book)
            elif book.price <= 8.0 and book.average_rating >= 4.5:  
                backup_books.append(book)

        # Try seasonal good books first
        if seasonal_books:
            return random.choice(seasonal_books)
        # Then try backup books, but 80% chance to walk away if not seasonal
        if backup_books and random.random() > 0.8:
            return random.choice(backup_books)
        return None

    @staticmethod
    def generate_customer_profiles(num_customers, store):
        customer_profiles = []
        inventory_titles = [book.title for book in store.inventory.books]
        inventory_authors = [book.authors for book in store.inventory.books]
        inventory_genres = [book.genre for book in store.inventory.books]

        # Find the most popular authors and genres
        author_counts = Counter(inventory_authors)
        most_popular_authors = [author for author, count in author_counts.most_common(5)]
        genre_counts = Counter(inventory_genres)
        most_popular_genres = [genre for genre, count in genre_counts.most_common(5)]

        # New distribution with increased seasonal/genre importance
        for _ in range(num_customers // 50):  # 2% title preference
            title = random.choice(inventory_titles)
            customer_profiles.append(Customer("title", title))
            
        for _ in range(num_customers // 25):  # 4% author preference
            author = random.choice(most_popular_authors)
            customer_profiles.append(Customer("author", author))
            
        for _ in range(num_customers * 25 // 100):  # 25% genre/seasonal preference (major increase)
            genre = random.choice(most_popular_genres)
            customer_profiles.append(Customer("genre", genre))
            
        for _ in range(num_customers * 30 // 100):  # 30% rating preference
            customer_profiles.append(Customer("rating", None))
            
        for _ in range(num_customers * 35 // 100):  # 35% price preference
            customer_profiles.append(Customer("price", 8.0))  
            
        remaining = num_customers - len(customer_profiles)  # ~4% no specific preference
        for _ in range(remaining):
            customer_profiles.append(Customer("none", None))
            
        return customer_profiles