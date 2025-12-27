import json
import csv
import requests
from pathlib import Path

class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year
        }

class MiniLibraryManager:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.books = self.load_books()

    def load_books(self):
        if not self.data_path.exists():
            return []
        with open(self.data_path, "r") as file:
            return json.load(file)

    def save_books(self):
        with open(self.data_path, "w") as file:
            json.dump(self.books, file, indent=2)

    def add_book(self, title, author, year):
        book = Book(title, author, year)
        self.books.append(book.to_dict())
        self.save_books()
        print("Book added successfully!")

    def search_local_books(self, keyword):
        return [
            book for book in self.books
            if keyword.lower() in book["title"].lower()
            or keyword.lower() in book["author"].lower()
        ]

    def search_api_books(self, keyword):
        url = f"https://openlibrary.org/search.json?q={keyword}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return []
        except requests.exceptions.RequestException:
            return []

        data = response.json()
        results = []
        key = keyword.lower()

        for book in data.get("docs", []):
            title = book.get("title", "")
            authors = book.get("author_name", [])

            if not title or not authors:
                continue

            if key not in title.lower() and not any(key in a.lower() for a in authors):
                continue

            results.append({
                "title": title,
                "author": authors[0],
                "year": book.get("first_publish_year", "N/A")
            })

            if len(results) == 3:
                break

        return results

    def generate_csv_report(self, books):
        report_path = Path(__file__).resolve().parent / "books_report.csv"
        with open(report_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["title", "author", "year"])
            for book in books:
                writer.writerow([
                    str(book.get("title", "")),
                    str(book.get("author", "")),
                    str(book.get("year", ""))
                ])
        print(f"\nCSV report generated: {report_path.name}")

    def list_books(self, keyword):
        results = []
        results.extend(self.search_local_books(keyword))
        results.extend(self.search_api_books(keyword))

        if not results:
            print("\nNo books found.")
            return

        print("\n--- Books ---")
        for i, book in enumerate(results, start=1):
            print(f"{i}. {book['title']} | {book['author']} | {book['year']}")

        self.generate_csv_report(results)

def main():
    base_dir = Path(__file__).resolve().parent
    data_file = base_dir / "data" / "books.json"
    manager = MiniLibraryManager(data_file)

    while True:
        print("\n--- Mini Library Manager ---")
        print("1. Add Book")
        print("2. Search & List Books")
        print("3. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            title = input("Enter book title: ").strip()
            author = input("Enter author name: ").strip()
            year = input("Enter published year: ").strip()

            if not title or not author or not year:
                print("Invalid input.")
                continue

            manager.add_book(title, author, year)

        elif choice == "2":
            keyword = input("Enter book title or author: ").strip()
            manager.list_books(keyword)

        elif choice == "3":
            print("Thank You!")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()



