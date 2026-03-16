#!/usr/bin/env python3
"""Script to update books with author information"""

import requests

# Get authors from catalog service
authors_resp = requests.get("http://localhost:8004/authors/")
authors = authors_resp.json()

# Build author map (name -> id), taking first occurrence
author_map = {}
for a in authors:
    name = a["name"]
    if name not in author_map:
        author_map[name] = a["author_id"]

print("Available authors:", list(author_map.keys()))

# Book to author mapping
book_author = {
    "Tôi Thấy Hoa Vàng Trên Cỏ Xanh": "Nguyễn Nhật Ánh",
    "Mắt Biếc": "Nguyễn Nhật Ánh",
    "Cho Tôi Xin Một Vé Đi Tuổi Thơ": "Nguyễn Nhật Ánh",
    "Dế Mèn Phiêu Lưu Ký": "Tô Hoài",
    "Tắt Đèn": "Tô Hoài",
    "Clean Code": "Robert C. Martin",
    "Refactoring": "Martin Fowler",
    "Domain-Driven Design": "Eric Evans",
    "Design Patterns": "Eric Evans",
    "The Pragmatic Programmer": "Martin Fowler",
    "Harry Potter and the Sorcerer's Stone": "J.K. Rowling",
    "1984": "George Orwell",
}

# Get books from book service
books_resp = requests.get("http://localhost:8005/books/")
books = books_resp.json()

print(f"\nUpdating {len(books)} books...")

for book in books:
    title = book["title"]
    author_name = book_author.get(title, "")
    author_id = author_map.get(author_name)

    if author_id:
        # Update book with author_id
        resp = requests.patch(
            f"http://localhost:8005/books/{book['book_id']}/",
            json={"author_id": author_id},
        )
        if resp.status_code == 200:
            print(f"✅ Updated: {title} -> {author_name}")
        else:
            print(f"❌ Failed: {title} - {resp.text[:100]}")
    else:
        print(f"⏭️  Skipped: {title} (no author mapping)")

print("\nDone!")
