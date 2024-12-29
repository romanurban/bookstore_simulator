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
        for book in store.stock.keys():
            if self.preference_value in book.authors:
                return book
        return None

    def _choose_by_genre(self, store, current_date):
        month = current_date.month
        keywords = self.seasonal_keywords.get(month, [])
        for book in store.stock.keys():
            if self.preference_value == book.genre:
                if any(keyword in (book.title + " " + book.authors) for keyword in keywords):
                    if random.random() < 0.6:
                        return book
        return None

    def _choose_by_title(self, store):
        for book in store.stock.keys():
            if self.preference_value == book.title:
                return book
        return None

    def _choose_by_rating(self, store, current_date):
        month = current_date.month
        keywords = self.seasonal_keywords.get(month, [])
        highest_rated_book = None
        highest_rating = 4.0
        for book in store.stock.keys():
            if book.average_rating > highest_rating:
                if any(keyword in (book.title + " " + book.authors) for keyword in keywords):
                    if random.random() < 0.6:
                        highest_rated_book = book
                        highest_rating = book.average_rating
        return highest_rated_book

    def _choose_by_price(self, store):
        for book in store.stock.keys():
            if book.price <= self.preference_value:
                return book
        return None

    def _choose_by_none(self, store, current_date):
        month = current_date.month
        keywords = self.seasonal_keywords.get(month, [])
        highest_rated_book = None
        highest_rating = 4.0
        affordable_books = []

        for book in store.stock.keys():
            if book.average_rating > highest_rating:
                highest_rated_book = book
                highest_rating = book.average_rating
            if book.price < 15:
                affordable_books.append(book)

        for book in store.stock.keys():
            if any(keyword in (book.title + " " + book.authors) for keyword in keywords):
                if random.random() < 0.65:
                    return book

        if highest_rated_book and random.random() < 0.7:
            return highest_rated_book

        if affordable_books and random.random() < 0.7:
            return random.choice(affordable_books)

        return None

    @staticmethod
    def generate_customer_profiles(num_customers, store):
        customer_profiles = []
        inventory_titles = [book.title for book in store.inventory.books]
        inventory_authors = [book.authors for book in store.inventory.books]
        inventory_genres = [book.genre for book in store.inventory.books]

        # Find the most popular authors
        author_counts = Counter(inventory_authors)
        most_popular_authors = [author for author, count in author_counts.most_common(5)]

        # Find the most popular genres
        genre_counts = Counter(inventory_genres)
        most_popular_genres = [genre for genre, count in genre_counts.most_common(5)]

        for _ in range(num_customers // 20):  # 5% prefer a particular title
            title = random.choice(inventory_titles)
            customer_profiles.append(Customer("title", title))
        for _ in range(num_customers // 7):  # 15% prefer a particular author
            author = random.choice(most_popular_authors)
            customer_profiles.append(Customer("author", author))
        for _ in range(num_customers // 10):  # 10% prefer a particular genre
            genre = random.choice(most_popular_genres)
            customer_profiles.append(Customer("genre", genre))
        # for _ in range(num_customers // 10):  # 10% prefer highest rating books
        #     customer_profiles.append(Customer("rating", None))
        # for _ in range(num_customers // 5):  # 20% prefer books under a specific price
        #     customer_profiles.append(Customer("price", 15.0))
        for _ in range(num_customers // 2):  # 50% have no specific preference
            customer_profiles.append(Customer("none", None))
        return customer_profiles