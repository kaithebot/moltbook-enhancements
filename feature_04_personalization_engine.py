#!/usr/bin/env python3
"""
Feature #4: Personalization at Scale for MoltBook
Recommendation engine and user preference system
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class PersonalizationEngine:
    """Generate personalized recommendations and track user preferences"""
    
    def __init__(self, user_id=None):
        self.user_id = user_id or "anonymous"
        self.data_dir = Path.home() / ".moltbook" / "personalization"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.user_file = self.data_dir / f"user_{self.user_id}.json"
        self.catalog_file = self.data_dir / "catalog.json"
        
        self.user_data = self._load_user_data()
        self.catalog = self._load_catalog()
    
    def _load_user_data(self):
        """Load user preferences and history"""
        if self.user_file.exists():
            return json.loads(self.user_file.read_text())
        return {
            "preferences": {
                "genres": [],
                "authors": [],
                "themes": [],
                "reading_level": "general",
                "format_preference": ["digital", "audio"]
            },
            "history": [],
            "ratings": {},
            "bookmarks": [],
            "created_at": datetime.now().isoformat()
        }
    
    def _load_catalog(self):
        """Load book catalog"""
        if self.catalog_file.exists():
            return json.loads(self.catalog_file.read_text())
        return {"books": []}
    
    def save_user_data(self):
        """Save user data"""
        self.user_file.write_text(json.dumps(self.user_data, indent=2))
    
    def add_preference(self, category, value):
        """Add user preference"""
        if category in self.user_data["preferences"]:
            if isinstance(self.user_data["preferences"][category], list):
                if value not in self.user_data["preferences"][category]:
                    self.user_data["preferences"][category].append(value)
            else:
                self.user_data["preferences"][category] = value
        self.save_user_data()
    
    def record_interaction(self, book_id, action, rating=None):
        """Record user interaction with a book"""
        interaction = {
            "book_id": book_id,
            "action": action,  # viewed, read, completed, bookmarked
            "timestamp": datetime.now().isoformat(),
            "rating": rating
        }
        
        self.user_data["history"].append(interaction)
        
        if rating:
            self.user_data["ratings"][book_id] = rating
        
        if action == "bookmarked":
            if book_id not in self.user_data["bookmarks"]:
                self.user_data["bookmarks"].append(book_id)
        
        self.save_user_data()
    
    def get_recommendations(self, n=5):
        """Generate personalized book recommendations"""
        if not self.catalog["books"]:
            return self._get_default_recommendations(n)
        
        # Score books based on user preferences
        book_scores = []
        
        for book in self.catalog["books"]:
            score = self._calculate_relevance_score(book)
            book_scores.append((book, score))
        
        # Sort by score and return top N
        book_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Filter out already read books
        read_books = {h["book_id"] for h in self.user_data["history"]}
        recommendations = [
            book for book, score in book_scores 
            if book.get("id") not in read_books
        ][:n]
        
        return recommendations
    
    def _calculate_relevance_score(self, book):
        """Calculate relevance score for a book based on user preferences"""
        score = 0
        prefs = self.user_data["preferences"]
        
        # Genre match (weight: 3)
        book_genres = book.get("genres", [])
        user_genres = prefs.get("genres", [])
        genre_matches = set(book_genres) & set(user_genres)
        score += len(genre_matches) * 3
        
        # Author match (weight: 4)
        book_author = book.get("author", "")
        if book_author in prefs.get("authors", []):
            score += 4
        
        # Theme match (weight: 2)
        book_themes = book.get("themes", [])
        user_themes = prefs.get("themes", [])
        theme_matches = set(book_themes) & set(user_themes)
        score += len(theme_matches) * 2
        
        # Reading level match (weight: 2)
        if book.get("reading_level") == prefs.get("reading_level"):
            score += 2
        
        # Format preference match (weight: 1)
        available_formats = book.get("formats", [])
        preferred_formats = prefs.get("format_preference", [])
        format_matches = set(available_formats) & set(preferred_formats)
        score += len(format_matches)
        
        # Rating bonus (weight: 5 if highly rated by similar users)
        avg_rating = book.get("average_rating", 0)
        if avg_rating >= 4.5:
            score += 5
        elif avg_rating >= 4.0:
            score += 3
        
        return score
    
    def _get_default_recommendations(self, n=5):
        """Get default recommendations when no user data"""
        # Return most popular books
        books = self.catalog.get("books", [])
        if not books:
            return []
        
        # Sort by popularity/rating
        sorted_books = sorted(
            books, 
            key=lambda x: (x.get("average_rating", 0), x.get("popularity", 0)), 
            reverse=True
        )
        
        return sorted_books[:n]
    
    def generate_personalized_feed(self):
        """Generate personalized content feed"""
        feed = {
            "recommendations": self.get_recommendations(5),
            "continue_reading": self._get_continue_reading(),
            "new_in_genres": self._get_new_in_preferred_genres(),
            "trending": self._get_trending(),
            "generated_at": datetime.now().isoformat()
        }
        return feed
    
    def _get_continue_reading(self):
        """Get books user started but hasn't finished"""
        in_progress = []
        for interaction in self.user_data["history"]:
            if interaction["action"] == "started":
                book_id = interaction["book_id"]
                # Check if not completed
                completed = any(
                    h["book_id"] == book_id and h["action"] == "completed"
                    for h in self.user_data["history"]
                )
                if not completed:
                    book = self._get_book_by_id(book_id)
                    if book:
                        in_progress.append(book)
        return in_progress[:3]
    
    def _get_new_in_preferred_genres(self):
        """Get new releases in user's preferred genres"""
        preferred_genres = self.user_data["preferences"].get("genres", [])
        new_books = []
        
        for book in self.catalog.get("books", []):
            book_genres = book.get("genres", [])
            if any(g in preferred_genres for g in book_genres):
                # Check if added recently (within 30 days)
                added_date = book.get("added_date", "")
                if added_date:
                    from datetime import datetime, timedelta
                    try:
                        date = datetime.fromisoformat(added_date)
                        if (datetime.now() - date).days <= 30:
                            new_books.append(book)
                    except:
                        pass
        
        return new_books[:5]
    
    def _get_trending(self):
        """Get trending books"""
        books = self.catalog.get("books", [])
        # Sort by recent popularity
        trending = sorted(
            books,
            key=lambda x: x.get("recent_views", 0),
            reverse=True
        )
        return trending[:5]
    
    def _get_book_by_id(self, book_id):
        """Get book by ID"""
        for book in self.catalog.get("books", []):
            if book.get("id") == book_id:
                return book
        return None
    
    def analyze_preferences(self):
        """Analyze user preferences and provide insights"""
        history = self.user_data["history"]
        
        if not history:
            return {
                "message": "Not enough data to analyze preferences",
                "recommendations": ["Start reading books to get personalized recommendations"]
            }
        
        # Most read genres
        genre_counts = defaultdict(int)
        for interaction in history:
            book = self._get_book_by_id(interaction["book_id"])
            if book:
                for genre in book.get("genres", []):
                    genre_counts[genre] += 1
        
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Reading patterns
        actions = defaultdict(int)
        for interaction in history:
            actions[interaction["action"]] += 1
        
        # Average rating given
        ratings = list(self.user_data["ratings"].values())
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "top_genres": [g[0] for g in top_genres],
            "reading_patterns": dict(actions),
            "average_rating_given": round(avg_rating, 2),
            "total_books_interacted": len(set(h["book_id"] for h in history)),
            "suggestions": self._generate_preference_suggestions(top_genres)
        }
    
    def _generate_preference_suggestions(self, top_genres):
        """Generate suggestions based on preferences"""
        suggestions = []
        
        if not top_genres:
            suggestions.append("Explore different genres to get better recommendations")
        elif len(top_genres) < 3:
            suggestions.append(f"You seem to like {top_genres[0][0]} - try exploring similar genres")
        
        if len(self.user_data["ratings"]) < 5:
            suggestions.append("Rate more books to improve recommendations")
        
        return suggestions


def main():
    parser = argparse.ArgumentParser(description='MoltBook Personalization Engine')
    parser.add_argument('--user', default='anonymous', help='User ID')
    parser.add_argument('--action', choices=['recommend', 'feed', 'analyze', 'rate'],
                       default='recommend', help='Action to perform')
    parser.add_argument('--book-id', help='Book ID for rating')
    parser.add_argument('--rating', type=int, help='Rating (1-5)')
    
    args = parser.parse_args()
    
    engine = PersonalizationEngine(args.user)
    
    if args.action == 'recommend':
        recommendations = engine.get_recommendations()
        print("📚 Personalized Recommendations:")
        for i, book in enumerate(recommendations, 1):
            print(f"{i}. {book.get('title', 'Unknown')} by {book.get('author', 'Unknown')}")
    
    elif args.action == 'feed':
        feed = engine.generate_personalized_feed()
        print("📰 Your Personalized Feed:")
        print(json.dumps(feed, indent=2))
    
    elif args.action == 'analyze':
        analysis = engine.analyze_preferences()
        print("📊 Preference Analysis:")
        print(json.dumps(analysis, indent=2))
    
    elif args.action == 'rate':
        if args.book_id and args.rating:
            engine.record_interaction(args.book_id, 'rated', args.rating)
            print(f"✅ Rated book {args.book_id}: {args.rating}/5")
        else:
            print("❌ Please provide --book-id and --rating")


if __name__ == '__main__':
    main()
