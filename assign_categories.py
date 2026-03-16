#!/usr/bin/env python3
"""
Assign categories and authors to books.
Books are created without category_id and author_id.
This script maps them based on the seed data ordering.
"""
import requests

BOOK_URL = "http://localhost:8005"
CATALOG_URL = "http://localhost:8004"

# Category slug → book index ranges (from seed_data.py comments)
CATEGORY_BOOK_RANGES = {
    "van-hoc-viet-nam": (1, 15),  # Books 1-15
    "van-hoc-nuoc-ngoai": (16, 30),  # Books 16-30
    "cong-nghe-lap-trinh": (31, 50),  # Books 31-50
    "kinh-te-kinh-doanh": (51, 65),  # Books 51-65
    "khoa-hoc": (66, 75),  # Books 66-75
    "tam-ly-ky-nang-song": (76, 85),  # Books 76-85
    "thieu-nhi": (86, 90),  # Books 86-90
    "lich-su-van-hoa": (91, 95),  # Books 91-95
    "ton-giao-triet-hoc": (96, 100),  # Books 96-100
    # "nghe-thuat-thiet-ke" has no books in seed data
}

# Author name → author_id mapping from seed data
BOOK_AUTHORS = [
    # Văn học Việt Nam (1-15)
    "Tô Hoài",
    "Nguyễn Nhật Ánh",
    "Ngô Tất Tố",
    "Nam Cao",
    "Nguyễn Du",
    "Vũ Trọng Phụng",
    "Nguyễn Ngọc Tư",
    "Nguyễn Huy Thiệp",
    "Nguyễn Nhật Ánh",
    "Nguyễn Nhật Ánh",
    "Nam Cao",
    "Vũ Trọng Phụng",
    "Nguyễn Nhật Ánh",
    "Trần Đăng Khoa",
    "Nguyễn Ngọc Tư",
    # Văn học nước ngoài (16-30)
    "J.K. Rowling",
    "J.K. Rowling",
    "J.K. Rowling",
    "George Orwell",
    "George Orwell",
    "Haruki Murakami",
    "Haruki Murakami",
    "Paulo Coelho",
    "Antoine de Saint-Exupéry",
    "Fyodor Dostoevsky",
    "Fyodor Dostoevsky",
    "Gabriel García Márquez",
    "Gabriel García Márquez",
    "Haruki Murakami",
    "Haruki Murakami",
    # Công nghệ & Lập trình (31-50)
    "Robert C. Martin",
    "Robert C. Martin",
    "Robert C. Martin",
    "Eric Evans",
    "Eric Evans",
    "Martin Fowler",
    "Martin Fowler",
    "Andrew Hunt",
    "Robert C. Martin",
    "Andrew Hunt",
    "Eric Evans",
    "Martin Fowler",
    "Martin Fowler",
    "Andrew Hunt",
    "Andrew Hunt",
    "Eric Evans",
    "Robert C. Martin",
    "Andrew Hunt",
    "Robert C. Martin",
    "Andrew Hunt",
    # Kinh tế & Kinh doanh (51-65)
    "Dale Carnegie",
    "Dale Carnegie",
    "Napoleon Hill",
    "Robert Kiyosaki",
    "Robert Kiyosaki",
    "Dale Carnegie",
    "Napoleon Hill",
    "Dale Carnegie",
    "Daniel Kahneman",
    "Daniel Kahneman",
    "Napoleon Hill",
    "Robert Kiyosaki",
    "Napoleon Hill",
    "Robert Kiyosaki",
    "Dale Carnegie",
    # Khoa học (66-75)
    "Stephen Hawking",
    "Stephen Hawking",
    "Yuval Noah Harari",
    "Yuval Noah Harari",
    "Yuval Noah Harari",
    "Stephen Hawking",
    "Stephen Hawking",
    "Yuval Noah Harari",
    "Daniel Kahneman",
    "Daniel Kahneman",
    # Tâm lý & Kỹ năng sống (76-85)
    "Mark Manson",
    "Mark Manson",
    "Hector Garcia",
    "Dale Carnegie",
    "Mark Manson",
    "Dale Carnegie",
    "Hector Garcia",
    "Daniel Kahneman",
    "Daniel Kahneman",
    "Daniel Kahneman",
    # Thiếu nhi (86-90)
    "Tô Hoài",
    "Tô Hoài",
    "Nguyễn Nhật Ánh",
    "Tô Hoài",
    "Antoine de Saint-Exupéry",
    # Lịch sử & Văn hóa (91-95)
    "Đặng Nhật Minh",
    "Đặng Nhật Minh",
    "Yuval Noah Harari",
    "Đặng Nhật Minh",
    "Đặng Nhật Minh",
    # Tôn giáo & Triết học (96-100)
    "Thích Nhất Hạnh",
    "Thích Nhất Hạnh",
    "Thích Nhất Hạnh",
    "Trần Đăng Khoa",
    "Paulo Coelho",
]


def main():
    # 1. Fetch categories
    print("Fetching categories...")
    resp = requests.get(f"{CATALOG_URL}/categories/")
    categories = resp.json()
    slug_to_id = {c["slug"]: c["category_id"] for c in categories}
    print(f"  Found {len(categories)} categories")

    # 2. Fetch authors
    print("Fetching authors...")
    resp = requests.get(f"{CATALOG_URL}/authors/")
    authors = resp.json()
    name_to_id = {a["name"]: a["author_id"] for a in authors}
    print(f"  Found {len(authors)} authors")

    # 3. Fetch books (ordered by created_at to match seed order)
    print("Fetching books...")
    resp = requests.get(f"{BOOK_URL}/books/?ordering=created_at")
    books = resp.json()
    print(f"  Found {len(books)} books")

    if len(books) != 100:
        print(f"  WARNING: Expected 100 books, got {len(books)}")

    # 4. Build book_index -> category_id mapping
    idx_to_category = {}
    for slug, (start, end) in CATEGORY_BOOK_RANGES.items():
        cat_id = slug_to_id.get(slug)
        if not cat_id:
            print(f"  WARNING: Category slug '{slug}' not found!")
            continue
        for i in range(start, end + 1):
            idx_to_category[i - 1] = cat_id  # 0-indexed

    # 5. Update each book
    updated = 0
    errors = 0
    for i, book in enumerate(books):
        cat_id = idx_to_category.get(i)
        author_name = BOOK_AUTHORS[i] if i < len(BOOK_AUTHORS) else None
        author_id = name_to_id.get(author_name) if author_name else None

        update_data = {}
        if cat_id and book.get("category_id") != cat_id:
            update_data["category_id"] = cat_id
        if author_id and book.get("author_id") != author_id:
            update_data["author_id"] = author_id

        if update_data:
            resp = requests.put(
                f"{BOOK_URL}/books/{book['book_id']}/",
                json=update_data,
            )
            if resp.status_code == 200:
                updated += 1
                print(
                    f"  ✅ [{i+1}] {book['title'][:40]} → cat={cat_id is not None}, author={author_id is not None}"
                )
            else:
                errors += 1
                print(
                    f"  ❌ [{i+1}] {book['title'][:40]}: {resp.status_code} {resp.text[:100]}"
                )
        else:
            print(f"  ⏭️  [{i+1}] {book['title'][:40]} (already set)")

    print(
        f"\nDone! Updated: {updated}, Errors: {errors}, Skipped: {len(books) - updated - errors}"
    )


if __name__ == "__main__":
    main()
