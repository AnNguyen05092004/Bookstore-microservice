#!/usr/bin/env python3
"""Update book cover images"""
import requests

BOOK_URL = "http://localhost:8005"

# Get all books
books = requests.get(f"{BOOK_URL}/books/").json()
print(f"Found {len(books)} books")

# Cover images map by title
covers = {
    "Clean Code": "https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg",
    "Design Patterns": "https://images-na.ssl-images-amazon.com/images/I/51szD9HC9pL._SX395_BO1,204,203,200_.jpg",
    "Domain-Driven Design": "https://images-na.ssl-images-amazon.com/images/I/51sZW87slRL._SX375_BO1,204,203,200_.jpg",
    "Dế Mèn Phiêu Lưu Ký": "https://salt.tikicdn.com/cache/w1200/ts/product/5e/18/24/2a6154ba08df6ce6161c13f4303fa19e.jpg",
    "Cho Tôi Xin Một Vé Đi Tuổi Thơ": "https://images-na.ssl-images-amazon.com/images/I/41u8u4KUZQL.jpg",
    "Harry Potter and the Sorcerer's Stone": "https://images-na.ssl-images-amazon.com/images/I/51UoqRAxwEL._SX331_BO1,204,203,200_.jpg",
    "1984": "https://images-na.ssl-images-amazon.com/images/I/41aM4xOZxaL._SX277_BO1,204,203,200_.jpg",
    "The Pragmatic Programmer": "https://images-na.ssl-images-amazon.com/images/I/51cUVaBWZzL._SX380_BO1,204,203,200_.jpg",
    "Refactoring": "https://images-na.ssl-images-amazon.com/images/I/41LBzpPXCOL._SX379_BO1,204,203,200_.jpg",
    "Tắt Đèn": "https://images-na.ssl-images-amazon.com/images/I/51gUjnWRqUL._SX342_BO1,204,203,200_.jpg",
    "Mắt Biếc": "https://images-na.ssl-images-amazon.com/images/I/41U2Eb0G3yL.jpg",
    "Tôi Thấy Hoa Vàng Trên Cỏ Xanh": "https://images-na.ssl-images-amazon.com/images/I/41lXD+dvqfL.jpg",
    "Harry Potter và Hòn Đá Phù Thủy": "https://images-na.ssl-images-amazon.com/images/I/51UoqRAxwEL._SX331_BO1,204,203,200_.jpg",
    "Đắc Nhân Tâm": "https://images-na.ssl-images-amazon.com/images/I/51X7dEUFgoL.jpg",
    "Nghĩ Giàu Làm Giàu": "https://images-na.ssl-images-amazon.com/images/I/61y04z8SKEL.jpg",
    "7 Thói Quen Hiệu Quả": "https://images-na.ssl-images-amazon.com/images/I/51hV5vJqwvL.jpg",
    "Sapiens: Lược Sử Loài Người": "https://images-na.ssl-images-amazon.com/images/I/41lZKXt1+ML.jpg",
    "Cosmos": "https://images-na.ssl-images-amazon.com/images/I/91Cnrbd4eOL.jpg",
    "Nhà Giả Kim": "https://images-na.ssl-images-amazon.com/images/I/51Z0nLAfLmL.jpg",
    "Tuổi Trẻ Đáng Giá Bao Nhiêu": "https://images-na.ssl-images-amazon.com/images/I/41FDjE9i+jL.jpg",
    "Cà Phê Cùng Tony": "https://images-na.ssl-images-amazon.com/images/I/41pAYp5aHOL.jpg",
    "Sống Đơn Giản Cho Mình Thanh Thản": "https://images-na.ssl-images-amazon.com/images/I/51uPjkA3URL.jpg",
    "Muôn Kiếp Nhân Sinh": "https://images-na.ssl-images-amazon.com/images/I/51HlqHOT9rL.jpg",
}

updated = 0
for book in books:
    title = book["title"]
    if title in covers and not book.get("cover_image_url"):
        resp = requests.patch(
            f"{BOOK_URL}/books/{book['book_id']}/",
            json={"cover_image_url": covers[title]},
        )
        if resp.status_code == 200:
            print(f"✅ Updated: {title}")
            updated += 1
        else:
            print(f"❌ Failed: {title} - {resp.status_code}")

print(f"\n📚 Updated {updated} books with cover images")
