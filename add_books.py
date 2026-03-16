#!/usr/bin/env python3
"""Script to add Vietnamese books to the bookstore"""
import requests
import json

BOOK_SERVICE = "http://localhost:8005"
CATALOG_SERVICE = "http://localhost:8004"

# Get authors and categories
authors_resp = requests.get(f"{CATALOG_SERVICE}/authors/")
authors = {a["name"]: a["author_id"] for a in authors_resp.json()}

categories_resp = requests.get(f"{CATALOG_SERVICE}/categories/")
categories = {c["name"]: c["category_id"] for c in categories_resp.json()}

print("Authors:", list(authors.keys())[:5])
print("Categories:", list(categories.keys()))

# Vietnamese books data
books = [
    # Văn học Việt Nam
    {
        "title": "Tắt Đèn",
        "author_name": "Ngô Tất Tố",
        "category": "Fiction",
        "price": 45000,
        "description": "Tiểu thuyết hiện thực phê phán nổi tiếng của văn học Việt Nam, khắc họa cuộc sống cơ cực của người nông dân trước Cách mạng tháng Tám.",
        "isbn": "978-604-1-12345-1",
        "stock": 50,
    },
    {
        "title": "Cho Tôi Xin Một Vé Đi Tuổi Thơ",
        "author_name": "Nguyễn Nhật Ánh",
        "category": "Children",
        "price": 85000,
        "description": "Tác phẩm nổi tiếng của Nguyễn Nhật Ánh, đưa người đọc trở về với những kỷ niệm tuổi thơ trong sáng và đẹp đẽ.",
        "isbn": "978-604-1-12345-2",
        "stock": 100,
    },
    {
        "title": "Dế Mèn Phiêu Lưu Ký",
        "author_name": "Tô Hoài",
        "category": "Children",
        "price": 55000,
        "description": "Câu chuyện phiêu lưu của chú Dế Mèn qua các vùng đất, gặp gỡ nhiều loài vật và học được nhiều bài học quý giá.",
        "isbn": "978-604-1-12345-3",
        "stock": 80,
    },
    {
        "title": "Mắt Biếc",
        "author_name": "Nguyễn Nhật Ánh",
        "category": "Fiction",
        "price": 95000,
        "description": "Câu chuyện tình yêu đẹp và buồn của Ngạn dành cho Hà Lan từ thuở nhỏ đến khi trưởng thành.",
        "isbn": "978-604-1-12345-4",
        "stock": 120,
    },
    {
        "title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh",
        "author_name": "Nguyễn Nhật Ánh",
        "category": "Children",
        "price": 75000,
        "description": "Câu chuyện về tuổi thơ hồn nhiên của hai anh em Thiều và Tường ở một làng quê miền Trung.",
        "isbn": "978-604-1-12345-5",
        "stock": 90,
    },
    # Sách Công nghệ
    {
        "title": "Clean Code",
        "author_name": "Robert C. Martin",
        "category": "Technology",
        "price": 450000,
        "description": "Hướng dẫn cách viết code sạch, dễ đọc và bảo trì. Cuốn sách kinh điển dành cho lập trình viên.",
        "isbn": "978-0-13-235088-4",
        "stock": 30,
    },
    {
        "title": "Design Patterns",
        "author_name": "Martin Fowler",
        "category": "Technology",
        "price": 520000,
        "description": "Giới thiệu các mẫu thiết kế phần mềm quan trọng và cách áp dụng trong thực tế.",
        "isbn": "978-0-20-163361-0",
        "stock": 25,
    },
    {
        "title": "Domain-Driven Design",
        "author_name": "Eric Evans",
        "category": "Technology",
        "price": 580000,
        "description": "Phương pháp tiếp cận thiết kế phần mềm phức tạp dựa trên domain knowledge.",
        "isbn": "978-0-32-112521-7",
        "stock": 20,
    },
    # Văn học nước ngoài
    {
        "title": "Harry Potter và Hòn Đá Phù Thủy",
        "author_name": "J.K. Rowling",
        "category": "Fiction",
        "price": 150000,
        "description": "Cuốn đầu tiên trong series Harry Potter, kể về cậu bé phù thủy và hành trình khám phá thế giới phép thuật.",
        "isbn": "978-604-1-12345-9",
        "stock": 150,
    },
    {
        "title": "1984",
        "author_name": "George Orwell",
        "category": "Fiction",
        "price": 120000,
        "description": "Tiểu thuyết dystopia kinh điển về một xã hội toàn trị với Big Brother theo dõi mọi người.",
        "isbn": "978-604-1-12346-0",
        "stock": 60,
    },
    # Sách Kinh doanh
    {
        "title": "Đắc Nhân Tâm",
        "author_name": "Dale Carnegie",
        "category": "Business",
        "price": 86000,
        "description": "Cuốn sách kinh điển về nghệ thuật giao tiếp và ứng xử với mọi người.",
        "isbn": "978-604-1-12346-1",
        "stock": 200,
    },
    {
        "title": "Nghĩ Giàu Làm Giàu",
        "author_name": "Napoleon Hill",
        "category": "Business",
        "price": 110000,
        "description": "13 nguyên tắc vàng để đạt được thành công và giàu có trong cuộc sống.",
        "isbn": "978-604-1-12346-2",
        "stock": 150,
    },
    {
        "title": "7 Thói Quen Hiệu Quả",
        "author_name": "Stephen Covey",
        "category": "Business",
        "price": 135000,
        "description": "Bảy thói quen giúp bạn thành công trong công việc và cuộc sống.",
        "isbn": "978-604-1-12346-3",
        "stock": 100,
    },
    # Sách Khoa học
    {
        "title": "Sapiens: Lược Sử Loài Người",
        "author_name": "Yuval Noah Harari",
        "category": "Science",
        "price": 189000,
        "description": "Lịch sử phát triển của loài người từ thời tiền sử đến hiện đại.",
        "isbn": "978-604-1-12346-4",
        "stock": 75,
    },
    {
        "title": "Cosmos",
        "author_name": "Carl Sagan",
        "category": "Science",
        "price": 220000,
        "description": "Hành trình khám phá vũ trụ bao la và vị trí của con người trong đó.",
        "isbn": "978-604-1-12346-5",
        "stock": 40,
    },
    # Thêm sách
    {
        "title": "Nhà Giả Kim",
        "author_name": "Paulo Coelho",
        "category": "Fiction",
        "price": 69000,
        "description": "Câu chuyện về chàng chăn cừu Santiago và hành trình theo đuổi giấc mơ.",
        "isbn": "978-604-1-12346-6",
        "stock": 180,
    },
    {
        "title": "Tuổi Trẻ Đáng Giá Bao Nhiêu",
        "author_name": "Rosie Nguyễn",
        "category": "Non-Fiction",
        "price": 76000,
        "description": "Những suy nghĩ và trải nghiệm về tuổi trẻ của tác giả Rosie Nguyễn.",
        "isbn": "978-604-1-12346-7",
        "stock": 120,
    },
    {
        "title": "Cà Phê Cùng Tony",
        "author_name": "Tony Buổi Sáng",
        "category": "Non-Fiction",
        "price": 72000,
        "description": "Những bài viết về cuộc sống, công việc và cách sống tích cực.",
        "isbn": "978-604-1-12346-8",
        "stock": 90,
    },
    {
        "title": "Sống Đơn Giản Cho Mình Thanh Thản",
        "author_name": "Shunmyo Masuno",
        "category": "Non-Fiction",
        "price": 79000,
        "description": "100 lời khuyên từ thiền sư Nhật Bản về nghệ thuật sống đơn giản.",
        "isbn": "978-604-1-12346-9",
        "stock": 85,
    },
    {
        "title": "Muôn Kiếp Nhân Sinh",
        "author_name": "Nguyên Phong",
        "category": "Non-Fiction",
        "price": 168000,
        "description": "Những câu chuyện về tiền kiếp và luân hồi đầy bí ẩn.",
        "isbn": "978-604-1-12347-0",
        "stock": 110,
    },
]

# Add missing authors first
missing_authors = [
    "Ngô Tất Tố",
    "Dale Carnegie",
    "Napoleon Hill",
    "Stephen Covey",
    "Yuval Noah Harari",
    "Carl Sagan",
    "Paulo Coelho",
    "Rosie Nguyễn",
    "Tony Buổi Sáng",
    "Shunmyo Masuno",
    "Nguyên Phong",
]

for author_name in missing_authors:
    if author_name not in authors:
        resp = requests.post(
            f"{CATALOG_SERVICE}/authors/",
            json={"name": author_name, "biography": f"Tác giả {author_name}"},
        )
        if resp.status_code == 201:
            data = resp.json()
            authors[author_name] = data["author_id"]
            print(f"✅ Added author: {author_name}")
        else:
            print(f"❌ Failed to add author {author_name}: {resp.text}")

# Add books
success = 0
for book in books:
    author_name = book.pop("author_name")
    category_name = book.pop("category")

    author_id = authors.get(author_name)
    category_id = categories.get(category_name)

    if author_id:
        book["author_id"] = author_id
    if category_id:
        book["category_id"] = category_id

    book["stock_quantity"] = book.pop("stock")

    resp = requests.post(f"{BOOK_SERVICE}/books/", json=book)
    if resp.status_code == 201:
        print(f"✅ Added: {book['title']}")
        success += 1
    else:
        print(f"❌ Failed: {book['title']} - {resp.text[:100]}")

print(f"\n📚 Added {success}/{len(books)} books successfully!")
