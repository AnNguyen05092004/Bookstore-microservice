#!/usr/bin/env python3
"""
Seed Data Script - Chèn dữ liệu mẫu vào các microservices
Chạy: python seed_data.py
"""
import requests
import random
import hashlib

# Service URLs
CATALOG_URL = "http://localhost:8004"
BOOK_URL = "http://localhost:8005"
CUSTOMER_URL = "http://localhost:8001"
STAFF_URL = "http://localhost:8002"
CART_URL = "http://localhost:8006"
ORDER_URL = "http://localhost:8007"
PAY_URL = "http://localhost:8008"

# ============================================================
# DATA DEFINITIONS
# ============================================================

PUBLISHERS = [
    {
        "name": "NXB Kim Đồng",
        "description": "Nhà xuất bản sách thiếu nhi hàng đầu Việt Nam",
        "website": "https://nxbkimdong.com.vn",
    },
    {
        "name": "NXB Trẻ",
        "description": "Nhà xuất bản Trẻ TP.HCM",
        "website": "https://nxbtre.com.vn",
    },
    {
        "name": "NXB Tổng hợp TPHCM",
        "description": "Nhà xuất bản Tổng hợp Thành phố Hồ Chí Minh",
        "website": "https://nxbhcm.com.vn",
    },
    {
        "name": "NXB Hội Nhà Văn",
        "description": "Nhà xuất bản Hội Nhà Văn Việt Nam",
        "website": "https://nxbhoinhavan.com",
    },
    {
        "name": "NXB Giáo Dục",
        "description": "Nhà xuất bản Giáo dục Việt Nam",
        "website": "https://nxbgd.vn",
    },
    {
        "name": "Penguin Books",
        "description": "International publisher",
        "website": "https://penguin.com",
    },
    {
        "name": "O'Reilly Media",
        "description": "Technology and programming books",
        "website": "https://oreilly.com",
    },
    {
        "name": "Manning Publications",
        "description": "Software development books",
        "website": "https://manning.com",
    },
    {
        "name": "HarperCollins",
        "description": "Major English-language publisher",
        "website": "https://harpercollins.com",
    },
    {
        "name": "Bloomsbury Publishing",
        "description": "Independent worldwide publishing house",
        "website": "https://bloomsbury.com",
    },
]

AUTHORS = [
    {
        "name": "Nguyễn Nhật Ánh",
        "bio": "Nhà văn nổi tiếng với các tác phẩm về tuổi thơ Việt Nam",
        "nationality": "Vietnam",
    },
    {"name": "Tô Hoài", "bio": "Tác giả Dế Mèn Phiêu Lưu Ký", "nationality": "Vietnam"},
    {
        "name": "Nam Cao",
        "bio": "Nhà văn hiện thực phê phán nổi tiếng",
        "nationality": "Vietnam",
    },
    {
        "name": "Ngô Tất Tố",
        "bio": "Tác giả Tắt Đèn, nhà văn hiện thực",
        "nationality": "Vietnam",
    },
    {
        "name": "Nguyễn Du",
        "bio": "Đại thi hào dân tộc, tác giả Truyện Kiều",
        "nationality": "Vietnam",
    },
    {
        "name": "Vũ Trọng Phụng",
        "bio": "Ông vua phóng sự đất Bắc",
        "nationality": "Vietnam",
    },
    {
        "name": "Nguyễn Ngọc Tư",
        "bio": "Nhà văn miền Tây nổi tiếng",
        "nationality": "Vietnam",
    },
    {
        "name": "Nguyễn Huy Thiệp",
        "bio": "Nhà văn đổi mới văn học Việt Nam",
        "nationality": "Vietnam",
    },
    {
        "name": "Robert C. Martin",
        "bio": "Uncle Bob - Clean Code author",
        "nationality": "USA",
    },
    {
        "name": "Martin Fowler",
        "bio": "Software architecture expert",
        "nationality": "UK",
    },
    {"name": "Eric Evans", "bio": "Domain-Driven Design author", "nationality": "USA"},
    {"name": "J.K. Rowling", "bio": "Harry Potter series author", "nationality": "UK"},
    {
        "name": "George Orwell",
        "bio": "Author of 1984 and Animal Farm",
        "nationality": "UK",
    },
    {
        "name": "Haruki Murakami",
        "bio": "Nhà văn Nhật Bản nổi tiếng thế giới",
        "nationality": "Japan",
    },
    {"name": "Paulo Coelho", "bio": "Tác giả Nhà Giả Kim", "nationality": "Brazil"},
    {"name": "Dale Carnegie", "bio": "Tác giả Đắc Nhân Tâm", "nationality": "USA"},
    {
        "name": "Napoleon Hill",
        "bio": "Tác giả Think and Grow Rich",
        "nationality": "USA",
    },
    {
        "name": "Stephen Hawking",
        "bio": "Nhà vật lý lý thuyết thiên tài",
        "nationality": "UK",
    },
    {
        "name": "Yuval Noah Harari",
        "bio": "Tác giả Sapiens, nhà sử học",
        "nationality": "Israel",
    },
    {
        "name": "Daniel Kahneman",
        "bio": "Nhà tâm lý học đoạt giải Nobel",
        "nationality": "USA",
    },
    {
        "name": "Mark Manson",
        "bio": "Tác giả Nghệ Thuật Tinh Tế Của Việc Đếch Quan Tâm",
        "nationality": "USA",
    },
    {
        "name": "Robert Kiyosaki",
        "bio": "Tác giả Rich Dad Poor Dad",
        "nationality": "USA",
    },
    {
        "name": "Antoine de Saint-Exupéry",
        "bio": "Tác giả Hoàng Tử Bé",
        "nationality": "France",
    },
    {"name": "Fyodor Dostoevsky", "bio": "Đại văn hào Nga", "nationality": "Russia"},
    {
        "name": "Gabriel García Márquez",
        "bio": "Tác giả Trăm Năm Cô Đơn",
        "nationality": "Colombia",
    },
    {
        "name": "Thích Nhất Hạnh",
        "bio": "Thiền sư, nhà văn, nhà hoạt động hòa bình",
        "nationality": "Vietnam",
    },
    {
        "name": "Đặng Nhật Minh",
        "bio": "Nhà văn, đạo diễn phim nổi tiếng",
        "nationality": "Vietnam",
    },
    {
        "name": "Trần Đăng Khoa",
        "bio": "Nhà thơ thần đồng Việt Nam",
        "nationality": "Vietnam",
    },
    {
        "name": "Andrew Hunt",
        "bio": "Tác giả The Pragmatic Programmer",
        "nationality": "USA",
    },
    {"name": "Hector Garcia", "bio": "Tác giả Ikigai", "nationality": "Spain"},
]

CATEGORIES = [
    {
        "name": "Văn học Việt Nam",
        "slug": "van-hoc-viet-nam",
        "description": "Tiểu thuyết, truyện ngắn, thơ Việt Nam",
    },
    {
        "name": "Văn học nước ngoài",
        "slug": "van-hoc-nuoc-ngoai",
        "description": "Tác phẩm văn học dịch từ nước ngoài",
    },
    {
        "name": "Công nghệ & Lập trình",
        "slug": "cong-nghe-lap-trinh",
        "description": "Sách về công nghệ, lập trình, phần mềm",
    },
    {
        "name": "Kinh tế & Kinh doanh",
        "slug": "kinh-te-kinh-doanh",
        "description": "Sách về kinh tế, tài chính, khởi nghiệp",
    },
    {
        "name": "Khoa học",
        "slug": "khoa-hoc",
        "description": "Sách khoa học tự nhiên và xã hội",
    },
    {
        "name": "Tâm lý & Kỹ năng sống",
        "slug": "tam-ly-ky-nang-song",
        "description": "Phát triển bản thân, tâm lý học",
    },
    {
        "name": "Thiếu nhi",
        "slug": "thieu-nhi",
        "description": "Sách dành cho thiếu nhi",
    },
    {
        "name": "Lịch sử & Văn hóa",
        "slug": "lich-su-van-hoa",
        "description": "Sách lịch sử, địa lý, văn hóa",
    },
    {
        "name": "Nghệ thuật & Thiết kế",
        "slug": "nghe-thuat-thiet-ke",
        "description": "Sách về nghệ thuật, thiết kế, nhiếp ảnh",
    },
    {
        "name": "Tôn giáo & Triết học",
        "slug": "ton-giao-triet-hoc",
        "description": "Sách về tôn giáo, triết học, tâm linh",
    },
]

TAGS = [
    {"name": "Bestseller", "slug": "bestseller"},
    {"name": "Sách mới", "slug": "sach-moi"},
    {"name": "Kinh điển", "slug": "kinh-dien"},
    {"name": "Giải thưởng", "slug": "giai-thuong"},
    {"name": "Lập trình", "slug": "lap-trinh"},
    {"name": "Self-help", "slug": "self-help"},
    {"name": "Thiếu nhi", "slug": "thieu-nhi-tag"},
    {"name": "Tiểu thuyết", "slug": "tieu-thuyet"},
]

# 100 books with realistic Vietnamese & international titles
BOOKS = [
    # Văn học Việt Nam (1-15)
    {
        "title": "Dế Mèn Phiêu Lưu Ký",
        "isbn": "9786041000001",
        "description": "Tác phẩm kinh điển của văn học thiếu nhi Việt Nam, kể về cuộc phiêu lưu của chú Dế Mèn qua nhiều vùng đất.",
        "price": "65000",
        "author_name": "Tô Hoài",
        "publisher_name": "NXB Kim Đồng",
        "pages": 200,
        "stock_quantity": 100,
        "status": "available",
    },
    {
        "title": "Cho Tôi Xin Một Vé Đi Tuổi Thơ",
        "isbn": "9786041000002",
        "description": "Câu chuyện xúc động về tuổi thơ hồn nhiên, trong sáng qua ngòi bút Nguyễn Nhật Ánh.",
        "price": "85000",
        "author_name": "Nguyễn Nhật Ánh",
        "publisher_name": "NXB Trẻ",
        "pages": 220,
        "stock_quantity": 80,
        "status": "available",
    },
    {
        "title": "Tắt Đèn",
        "isbn": "9786041000003",
        "description": "Tiểu thuyết hiện thực phê phán, phản ánh cuộc sống khổ cực của người nông dân Việt Nam.",
        "price": "55000",
        "author_name": "Ngô Tất Tố",
        "publisher_name": "NXB Hội Nhà Văn",
        "pages": 180,
        "stock_quantity": 45,
        "status": "available",
    },
    {
        "title": "Chí Phèo",
        "isbn": "9786041000004",
        "description": "Truyện ngắn xuất sắc về bi kịch của người nông dân bị tha hóa trong xã hội cũ.",
        "price": "48000",
        "author_name": "Nam Cao",
        "publisher_name": "NXB Hội Nhà Văn",
        "pages": 120,
        "stock_quantity": 70,
        "status": "available",
    },
    {
        "title": "Truyện Kiều",
        "isbn": "9786041000005",
        "description": "Kiệt tác văn học Việt Nam, truyện thơ Nôm nổi tiếng.",
        "price": "95000",
        "author_name": "Nguyễn Du",
        "publisher_name": "NXB Giáo Dục",
        "pages": 300,
        "stock_quantity": 60,
        "status": "available",
    },
    {
        "title": "Số Đỏ",
        "isbn": "9786041000006",
        "description": "Tiểu thuyết trào phúng nổi tiếng nhất văn học Việt Nam.",
        "price": "72000",
        "author_name": "Vũ Trọng Phụng",
        "publisher_name": "NXB Hội Nhà Văn",
        "pages": 280,
        "stock_quantity": 55,
        "status": "available",
    },
    {
        "title": "Cánh Đồng Bất Tận",
        "isbn": "9786041000007",
        "description": "Tập truyện ngắn đậm chất miền Tây sông nước.",
        "price": "78000",
        "author_name": "Nguyễn Ngọc Tư",
        "publisher_name": "NXB Trẻ",
        "pages": 200,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "Tướng Về Hưu",
        "isbn": "9786041000008",
        "description": "Truyện ngắn đặc sắc của văn học đổi mới.",
        "price": "62000",
        "author_name": "Nguyễn Huy Thiệp",
        "publisher_name": "NXB Hội Nhà Văn",
        "pages": 150,
        "stock_quantity": 35,
        "status": "available",
    },
    {
        "title": "Mắt Biếc",
        "isbn": "9786041000009",
        "description": "Câu chuyện tình yêu đầy cảm xúc thời học trò.",
        "price": "89000",
        "author_name": "Nguyễn Nhật Ánh",
        "publisher_name": "NXB Trẻ",
        "pages": 250,
        "stock_quantity": 90,
        "status": "available",
    },
    {
        "title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh",
        "isbn": "9786041000010",
        "description": "Câu chuyện về tuổi thơ ở làng quê miền Trung.",
        "price": "92000",
        "author_name": "Nguyễn Nhật Ánh",
        "publisher_name": "NXB Trẻ",
        "pages": 280,
        "stock_quantity": 85,
        "status": "available",
    },
    {
        "title": "Lão Hạc",
        "isbn": "9786041000011",
        "description": "Truyện ngắn cảm động về lão nông dân nghèo.",
        "price": "42000",
        "author_name": "Nam Cao",
        "publisher_name": "NXB Giáo Dục",
        "pages": 80,
        "stock_quantity": 60,
        "status": "available",
    },
    {
        "title": "Giông Tố",
        "isbn": "9786041000012",
        "description": "Tiểu thuyết phóng sự xuất sắc.",
        "price": "68000",
        "author_name": "Vũ Trọng Phụng",
        "publisher_name": "NXB Hội Nhà Văn",
        "pages": 320,
        "stock_quantity": 30,
        "status": "available",
    },
    {
        "title": "Kính Vạn Hoa",
        "isbn": "9786041000013",
        "description": "Bộ truyện thiếu nhi nổi tiếng nhất Việt Nam.",
        "price": "75000",
        "author_name": "Nguyễn Nhật Ánh",
        "publisher_name": "NXB Kim Đồng",
        "pages": 200,
        "stock_quantity": 120,
        "status": "available",
    },
    {
        "title": "Góc Sân Và Khoảng Trời",
        "isbn": "9786041000014",
        "description": "Tập thơ thiếu nhi nổi tiếng.",
        "price": "45000",
        "author_name": "Trần Đăng Khoa",
        "publisher_name": "NXB Kim Đồng",
        "pages": 100,
        "stock_quantity": 50,
        "status": "available",
    },
    {
        "title": "Gió Lạnh Đầu Mùa",
        "isbn": "9786041000015",
        "description": "Tập truyện ngắn kinh điển.",
        "price": "52000",
        "author_name": "Nguyễn Ngọc Tư",
        "publisher_name": "NXB Trẻ",
        "pages": 180,
        "stock_quantity": 40,
        "status": "available",
    },
    # Văn học nước ngoài (16-30)
    {
        "title": "Harry Potter và Hòn Đá Phù Thủy",
        "isbn": "9786041000016",
        "description": "Cuốn đầu tiên trong series Harry Potter huyền thoại.",
        "price": "125000",
        "author_name": "J.K. Rowling",
        "publisher_name": "NXB Trẻ",
        "pages": 332,
        "stock_quantity": 150,
        "status": "available",
    },
    {
        "title": "Harry Potter và Phòng Chứa Bí Mật",
        "isbn": "9786041000017",
        "description": "Cuốn thứ hai trong series Harry Potter.",
        "price": "135000",
        "author_name": "J.K. Rowling",
        "publisher_name": "NXB Trẻ",
        "pages": 360,
        "stock_quantity": 130,
        "status": "available",
    },
    {
        "title": "Harry Potter và Tên Tù Nhân Ngục Azkaban",
        "isbn": "9786041000018",
        "description": "Cuốn thứ ba trong series Harry Potter.",
        "price": "145000",
        "author_name": "J.K. Rowling",
        "publisher_name": "NXB Trẻ",
        "pages": 468,
        "stock_quantity": 110,
        "status": "available",
    },
    {
        "title": "1984",
        "isbn": "9786041000019",
        "description": "Tiểu thuyết phản địa đàng kinh điển về xã hội toàn trị.",
        "price": "98000",
        "author_name": "George Orwell",
        "publisher_name": "Penguin Books",
        "pages": 328,
        "stock_quantity": 60,
        "status": "available",
    },
    {
        "title": "Trại Súc Vật",
        "isbn": "9786041000020",
        "description": "Ngụ ngôn chính trị nổi tiếng.",
        "price": "78000",
        "author_name": "George Orwell",
        "publisher_name": "Penguin Books",
        "pages": 140,
        "stock_quantity": 55,
        "status": "available",
    },
    {
        "title": "Rừng Na Uy",
        "isbn": "9786041000021",
        "description": "Tiểu thuyết tình cảm nổi tiếng nhất của Murakami.",
        "price": "115000",
        "author_name": "Haruki Murakami",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 400,
        "stock_quantity": 70,
        "status": "available",
    },
    {
        "title": "Kafka Bên Bờ Biển",
        "isbn": "9786041000022",
        "description": "Tiểu thuyết siêu thực đầy mê hoặc.",
        "price": "128000",
        "author_name": "Haruki Murakami",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 480,
        "stock_quantity": 45,
        "status": "available",
    },
    {
        "title": "Nhà Giả Kim",
        "isbn": "9786041000023",
        "description": "Câu chuyện về hành trình theo đuổi giấc mơ.",
        "price": "69000",
        "author_name": "Paulo Coelho",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 228,
        "stock_quantity": 200,
        "status": "available",
    },
    {
        "title": "Hoàng Tử Bé",
        "isbn": "9786041000024",
        "description": "Tác phẩm kinh điển dành cho mọi lứa tuổi.",
        "price": "58000",
        "author_name": "Antoine de Saint-Exupéry",
        "publisher_name": "NXB Kim Đồng",
        "pages": 96,
        "stock_quantity": 180,
        "status": "available",
    },
    {
        "title": "Tội Ác Và Hình Phạt",
        "isbn": "9786041000025",
        "description": "Kiệt tác văn học Nga về tội lỗi và sự cứu rỗi.",
        "price": "145000",
        "author_name": "Fyodor Dostoevsky",
        "publisher_name": "NXB Hội Nhà Văn",
        "pages": 672,
        "stock_quantity": 30,
        "status": "available",
    },
    {
        "title": "Anh Em Nhà Karamazov",
        "isbn": "9786041000026",
        "description": "Tiểu thuyết triết học vĩ đại nhất của Dostoevsky.",
        "price": "168000",
        "author_name": "Fyodor Dostoevsky",
        "publisher_name": "NXB Hội Nhà Văn",
        "pages": 880,
        "stock_quantity": 25,
        "status": "available",
    },
    {
        "title": "Trăm Năm Cô Đơn",
        "isbn": "9786041000027",
        "description": "Kiệt tác văn học Mỹ Latinh, chủ nghĩa hiện thực huyền ảo.",
        "price": "138000",
        "author_name": "Gabriel García Márquez",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 450,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "Tình Yêu Thời Thổ Tả",
        "isbn": "9786041000028",
        "description": "Câu chuyện tình yêu kéo dài hơn nửa thế kỷ.",
        "price": "125000",
        "author_name": "Gabriel García Márquez",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 370,
        "stock_quantity": 35,
        "status": "available",
    },
    {
        "title": "1Q84 - Tập 1",
        "isbn": "9786041000029",
        "description": "Tiểu thuyết kỳ bí của Murakami.",
        "price": "155000",
        "author_name": "Haruki Murakami",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 500,
        "stock_quantity": 50,
        "status": "available",
    },
    {
        "title": "Biên Niên Ký Chim Vặn Dây Cót",
        "isbn": "9786041000030",
        "description": "Một trong những kiệt tác của Murakami.",
        "price": "165000",
        "author_name": "Haruki Murakami",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 600,
        "stock_quantity": 30,
        "status": "available",
    },
    # Công nghệ & Lập trình (31-50)
    {
        "title": "Clean Code",
        "isbn": "9786041000031",
        "description": "A Handbook of Agile Software Craftsmanship. Hướng dẫn viết code sạch.",
        "price": "450000",
        "author_name": "Robert C. Martin",
        "publisher_name": "O'Reilly Media",
        "pages": 464,
        "stock_quantity": 50,
        "status": "available",
    },
    {
        "title": "Clean Architecture",
        "isbn": "9786041000032",
        "description": "A Craftsman's Guide to Software Structure and Design.",
        "price": "480000",
        "author_name": "Robert C. Martin",
        "publisher_name": "O'Reilly Media",
        "pages": 432,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "The Clean Coder",
        "isbn": "9786041000033",
        "description": "A Code of Conduct for Professional Programmers.",
        "price": "420000",
        "author_name": "Robert C. Martin",
        "publisher_name": "O'Reilly Media",
        "pages": 256,
        "stock_quantity": 35,
        "status": "available",
    },
    {
        "title": "Design Patterns",
        "isbn": "9786041000034",
        "description": "Elements of Reusable Object-Oriented Software by Gang of Four.",
        "price": "520000",
        "author_name": "Eric Evans",
        "publisher_name": "O'Reilly Media",
        "pages": 395,
        "stock_quantity": 30,
        "status": "available",
    },
    {
        "title": "Domain-Driven Design",
        "isbn": "9786041000035",
        "description": "Tackling Complexity in the Heart of Software.",
        "price": "560000",
        "author_name": "Eric Evans",
        "publisher_name": "Manning Publications",
        "pages": 560,
        "stock_quantity": 25,
        "status": "available",
    },
    {
        "title": "Refactoring",
        "isbn": "9786041000036",
        "description": "Improving the Design of Existing Code.",
        "price": "490000",
        "author_name": "Martin Fowler",
        "publisher_name": "Manning Publications",
        "pages": 448,
        "stock_quantity": 35,
        "status": "available",
    },
    {
        "title": "Patterns of Enterprise Application Architecture",
        "isbn": "9786041000037",
        "description": "Hướng dẫn xây dựng ứng dụng doanh nghiệp.",
        "price": "530000",
        "author_name": "Martin Fowler",
        "publisher_name": "Manning Publications",
        "pages": 533,
        "stock_quantity": 20,
        "status": "available",
    },
    {
        "title": "The Pragmatic Programmer",
        "isbn": "9786041000038",
        "description": "Your Journey to Mastery, 20th Anniversary Edition.",
        "price": "470000",
        "author_name": "Andrew Hunt",
        "publisher_name": "O'Reilly Media",
        "pages": 352,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "Introduction to Algorithms",
        "isbn": "9786041000039",
        "description": "Sách giáo khoa kinh điển về thuật toán.",
        "price": "680000",
        "author_name": "Robert C. Martin",
        "publisher_name": "O'Reilly Media",
        "pages": 1292,
        "stock_quantity": 20,
        "status": "available",
    },
    {
        "title": "Code Complete",
        "isbn": "9786041000040",
        "description": "A Practical Handbook of Software Construction.",
        "price": "510000",
        "author_name": "Andrew Hunt",
        "publisher_name": "O'Reilly Media",
        "pages": 960,
        "stock_quantity": 25,
        "status": "available",
    },
    {
        "title": "Head First Design Patterns",
        "isbn": "9786041000041",
        "description": "Học Design Patterns một cách trực quan.",
        "price": "440000",
        "author_name": "Eric Evans",
        "publisher_name": "O'Reilly Media",
        "pages": 694,
        "stock_quantity": 45,
        "status": "available",
    },
    {
        "title": "Microservices Patterns",
        "isbn": "9786041000042",
        "description": "With Examples in Java - Kiến trúc Microservices.",
        "price": "520000",
        "author_name": "Martin Fowler",
        "publisher_name": "Manning Publications",
        "pages": 520,
        "stock_quantity": 30,
        "status": "available",
    },
    {
        "title": "Building Microservices",
        "isbn": "9786041000043",
        "description": "Designing Fine-Grained Systems.",
        "price": "480000",
        "author_name": "Martin Fowler",
        "publisher_name": "O'Reilly Media",
        "pages": 280,
        "stock_quantity": 35,
        "status": "available",
    },
    {
        "title": "Docker Deep Dive",
        "isbn": "9786041000044",
        "description": "Hướng dẫn toàn diện về Docker.",
        "price": "380000",
        "author_name": "Andrew Hunt",
        "publisher_name": "Manning Publications",
        "pages": 350,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "Kubernetes in Action",
        "isbn": "9786041000045",
        "description": "Triển khai ứng dụng container.",
        "price": "560000",
        "author_name": "Andrew Hunt",
        "publisher_name": "Manning Publications",
        "pages": 624,
        "stock_quantity": 25,
        "status": "available",
    },
    {
        "title": "Python Crash Course",
        "isbn": "9786041000046",
        "description": "A Hands-On Introduction to Programming.",
        "price": "420000",
        "author_name": "Eric Evans",
        "publisher_name": "O'Reilly Media",
        "pages": 544,
        "stock_quantity": 60,
        "status": "available",
    },
    {
        "title": "JavaScript: The Good Parts",
        "isbn": "9786041000047",
        "description": "Unearthing the Excellence in JavaScript.",
        "price": "280000",
        "author_name": "Robert C. Martin",
        "publisher_name": "O'Reilly Media",
        "pages": 176,
        "stock_quantity": 50,
        "status": "available",
    },
    {
        "title": "Learning React",
        "isbn": "9786041000048",
        "description": "Modern Patterns for Developing React Apps.",
        "price": "460000",
        "author_name": "Andrew Hunt",
        "publisher_name": "O'Reilly Media",
        "pages": 350,
        "stock_quantity": 55,
        "status": "available",
    },
    {
        "title": "System Design Interview",
        "isbn": "9786041000049",
        "description": "An Insider's Guide - Thiết kế hệ thống.",
        "price": "490000",
        "author_name": "Robert C. Martin",
        "publisher_name": "Manning Publications",
        "pages": 320,
        "stock_quantity": 45,
        "status": "available",
    },
    {
        "title": "Grokking Algorithms",
        "isbn": "9786041000050",
        "description": "Illustrated guide to algorithms.",
        "price": "350000",
        "author_name": "Andrew Hunt",
        "publisher_name": "Manning Publications",
        "pages": 256,
        "stock_quantity": 65,
        "status": "available",
    },
    # Kinh tế & Kinh doanh (51-65)
    {
        "title": "Đắc Nhân Tâm",
        "isbn": "9786041000051",
        "description": "How to Win Friends and Influence People - Nghệ thuật đối nhân xử thế.",
        "price": "86000",
        "author_name": "Dale Carnegie",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 320,
        "stock_quantity": 200,
        "status": "available",
    },
    {
        "title": "Quẳng Gánh Lo Đi Và Vui Sống",
        "isbn": "9786041000052",
        "description": "How to Stop Worrying and Start Living.",
        "price": "79000",
        "author_name": "Dale Carnegie",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 380,
        "stock_quantity": 150,
        "status": "available",
    },
    {
        "title": "Nghĩ Giàu Làm Giàu",
        "isbn": "9786041000053",
        "description": "Think and Grow Rich - Kinh điển về thành công.",
        "price": "92000",
        "author_name": "Napoleon Hill",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 300,
        "stock_quantity": 130,
        "status": "available",
    },
    {
        "title": "Cha Giàu Cha Nghèo",
        "isbn": "9786041000054",
        "description": "Rich Dad Poor Dad - Dạy con làm giàu.",
        "price": "108000",
        "author_name": "Robert Kiyosaki",
        "publisher_name": "NXB Trẻ",
        "pages": 336,
        "stock_quantity": 160,
        "status": "available",
    },
    {
        "title": "Cashflow Quadrant",
        "isbn": "9786041000055",
        "description": "Tứ trụ tài chính cá nhân.",
        "price": "118000",
        "author_name": "Robert Kiyosaki",
        "publisher_name": "NXB Trẻ",
        "pages": 380,
        "stock_quantity": 80,
        "status": "available",
    },
    {
        "title": "Chiến Lược Đại Dương Xanh",
        "isbn": "9786041000056",
        "description": "Blue Ocean Strategy - Tạo thị trường mới.",
        "price": "135000",
        "author_name": "Dale Carnegie",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 320,
        "stock_quantity": 60,
        "status": "available",
    },
    {
        "title": "Từ Tốt Đến Vĩ Đại",
        "isbn": "9786041000057",
        "description": "Good to Great - Nghiên cứu các công ty xuất sắc.",
        "price": "128000",
        "author_name": "Napoleon Hill",
        "publisher_name": "NXB Trẻ",
        "pages": 400,
        "stock_quantity": 55,
        "status": "available",
    },
    {
        "title": "Khởi Nghiệp Tinh Gọn",
        "isbn": "9786041000058",
        "description": "The Lean Startup - Phương pháp khởi nghiệp.",
        "price": "115000",
        "author_name": "Dale Carnegie",
        "publisher_name": "NXB Trẻ",
        "pages": 320,
        "stock_quantity": 70,
        "status": "available",
    },
    {
        "title": "Tư Duy Nhanh Và Chậm",
        "isbn": "9786041000059",
        "description": "Thinking, Fast and Slow - Hai hệ thống tư duy.",
        "price": "168000",
        "author_name": "Daniel Kahneman",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 500,
        "stock_quantity": 45,
        "status": "available",
    },
    {
        "title": "Nudge - Cú Hích",
        "isbn": "9786041000060",
        "description": "Improving Decisions About Health, Wealth, and Happiness.",
        "price": "125000",
        "author_name": "Daniel Kahneman",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 312,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "Dám Nghĩ Lớn",
        "isbn": "9786041000061",
        "description": "The Magic of Thinking Big.",
        "price": "89000",
        "author_name": "Napoleon Hill",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 300,
        "stock_quantity": 90,
        "status": "available",
    },
    {
        "title": "Bí Mật Tư Duy Triệu Phú",
        "isbn": "9786041000062",
        "description": "Secrets of the Millionaire Mind.",
        "price": "95000",
        "author_name": "Robert Kiyosaki",
        "publisher_name": "NXB Trẻ",
        "pages": 250,
        "stock_quantity": 75,
        "status": "available",
    },
    {
        "title": "Người Giàu Nhất Thành Babylon",
        "isbn": "9786041000063",
        "description": "The Richest Man in Babylon.",
        "price": "68000",
        "author_name": "Napoleon Hill",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 200,
        "stock_quantity": 100,
        "status": "available",
    },
    {
        "title": "Đầu Tư Tài Chính",
        "isbn": "9786041000064",
        "description": "Hướng dẫn đầu tư cho người mới bắt đầu.",
        "price": "145000",
        "author_name": "Robert Kiyosaki",
        "publisher_name": "NXB Trẻ",
        "pages": 420,
        "stock_quantity": 50,
        "status": "available",
    },
    {
        "title": "7 Thói Quen Hiệu Quả",
        "isbn": "9786041000065",
        "description": "The 7 Habits of Highly Effective People.",
        "price": "135000",
        "author_name": "Dale Carnegie",
        "publisher_name": "NXB Trẻ",
        "pages": 380,
        "stock_quantity": 85,
        "status": "available",
    },
    # Khoa học (66-75)
    {
        "title": "Lược Sử Thời Gian",
        "isbn": "9786041000066",
        "description": "A Brief History of Time - Vũ trụ qua góc nhìn khoa học.",
        "price": "125000",
        "author_name": "Stephen Hawking",
        "publisher_name": "NXB Trẻ",
        "pages": 256,
        "stock_quantity": 65,
        "status": "available",
    },
    {
        "title": "Vũ Trụ Trong Vỏ Hạt Dẻ",
        "isbn": "9786041000067",
        "description": "The Universe in a Nutshell.",
        "price": "145000",
        "author_name": "Stephen Hawking",
        "publisher_name": "NXB Trẻ",
        "pages": 224,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "Sapiens - Lược Sử Loài Người",
        "isbn": "9786041000068",
        "description": "A Brief History of Humankind.",
        "price": "189000",
        "author_name": "Yuval Noah Harari",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 498,
        "stock_quantity": 100,
        "status": "available",
    },
    {
        "title": "Homo Deus - Lược Sử Tương Lai",
        "isbn": "9786041000069",
        "description": "A Brief History of Tomorrow.",
        "price": "195000",
        "author_name": "Yuval Noah Harari",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 450,
        "stock_quantity": 70,
        "status": "available",
    },
    {
        "title": "21 Bài Học Cho Thế Kỷ 21",
        "isbn": "9786041000070",
        "description": "21 Lessons for the 21st Century.",
        "price": "175000",
        "author_name": "Yuval Noah Harari",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 400,
        "stock_quantity": 55,
        "status": "available",
    },
    {
        "title": "Cosmos - Vũ Trụ",
        "isbn": "9786041000071",
        "description": "Khám phá vũ trụ và vị trí của con người.",
        "price": "155000",
        "author_name": "Stephen Hawking",
        "publisher_name": "NXB Trẻ",
        "pages": 365,
        "stock_quantity": 35,
        "status": "available",
    },
    {
        "title": "Gene Ích Kỷ",
        "isbn": "9786041000072",
        "description": "The Selfish Gene - Lý thuyết tiến hóa.",
        "price": "135000",
        "author_name": "Stephen Hawking",
        "publisher_name": "NXB Trẻ",
        "pages": 360,
        "stock_quantity": 30,
        "status": "available",
    },
    {
        "title": "Thế Giới Phẳng",
        "isbn": "9786041000073",
        "description": "The World Is Flat - Toàn cầu hóa.",
        "price": "145000",
        "author_name": "Yuval Noah Harari",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 488,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "Outliers - Những Kẻ Xuất Chúng",
        "isbn": "9786041000074",
        "description": "The Story of Success.",
        "price": "115000",
        "author_name": "Daniel Kahneman",
        "publisher_name": "NXB Trẻ",
        "pages": 309,
        "stock_quantity": 60,
        "status": "available",
    },
    {
        "title": "Blink - Trong Chớp Mắt",
        "isbn": "9786041000075",
        "description": "The Power of Thinking Without Thinking.",
        "price": "105000",
        "author_name": "Daniel Kahneman",
        "publisher_name": "NXB Trẻ",
        "pages": 277,
        "stock_quantity": 50,
        "status": "available",
    },
    # Tâm lý & Kỹ năng sống (76-85)
    {
        "title": "Nghệ Thuật Tinh Tế Của Việc Đếch Quan Tâm",
        "isbn": "9786041000076",
        "description": "The Subtle Art of Not Giving a F*ck.",
        "price": "99000",
        "author_name": "Mark Manson",
        "publisher_name": "NXB Trẻ",
        "pages": 224,
        "stock_quantity": 180,
        "status": "available",
    },
    {
        "title": "Mọi Thứ Đều Tuyệt Vời",
        "isbn": "9786041000077",
        "description": "Everything Is F*cked: A Book About Hope.",
        "price": "105000",
        "author_name": "Mark Manson",
        "publisher_name": "NXB Trẻ",
        "pages": 256,
        "stock_quantity": 120,
        "status": "available",
    },
    {
        "title": "Ikigai - Bí Mật Sống Lâu",
        "isbn": "9786041000078",
        "description": "Bí mật sống trường thọ của người Nhật.",
        "price": "89000",
        "author_name": "Hector Garcia",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 208,
        "stock_quantity": 150,
        "status": "available",
    },
    {
        "title": "Sức Mạnh Của Thói Quen",
        "isbn": "9786041000079",
        "description": "The Power of Habit.",
        "price": "115000",
        "author_name": "Dale Carnegie",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 371,
        "stock_quantity": 80,
        "status": "available",
    },
    {
        "title": "Atomic Habits - Thay Đổi Tí Hon Hiệu Quả Bất Ngờ",
        "isbn": "9786041000080",
        "description": "An Easy & Proven Way to Build Good Habits.",
        "price": "135000",
        "author_name": "Mark Manson",
        "publisher_name": "NXB Trẻ",
        "pages": 320,
        "stock_quantity": 170,
        "status": "available",
    },
    {
        "title": "Đời Ngắn Đừng Ngủ Dài",
        "isbn": "9786041000081",
        "description": "Sống trọn vẹn từng khoảnh khắc.",
        "price": "75000",
        "author_name": "Dale Carnegie",
        "publisher_name": "NXB Trẻ",
        "pages": 200,
        "stock_quantity": 90,
        "status": "available",
    },
    {
        "title": "Dám Bị Ghét",
        "isbn": "9786041000082",
        "description": "The Courage to Be Disliked - Triết học Adler.",
        "price": "105000",
        "author_name": "Hector Garcia",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 280,
        "stock_quantity": 100,
        "status": "available",
    },
    {
        "title": "Mindset - Tâm Lý Học Thành Công",
        "isbn": "9786041000083",
        "description": "The New Psychology of Success.",
        "price": "115000",
        "author_name": "Daniel Kahneman",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 320,
        "stock_quantity": 70,
        "status": "available",
    },
    {
        "title": "EQ - Trí Tuệ Cảm Xúc",
        "isbn": "9786041000084",
        "description": "Emotional Intelligence.",
        "price": "125000",
        "author_name": "Daniel Kahneman",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 384,
        "stock_quantity": 60,
        "status": "available",
    },
    {
        "title": "Flow - Dòng Chảy",
        "isbn": "9786041000085",
        "description": "The Psychology of Optimal Experience.",
        "price": "135000",
        "author_name": "Daniel Kahneman",
        "publisher_name": "NXB Trẻ",
        "pages": 303,
        "stock_quantity": 45,
        "status": "available",
    },
    # Thiếu nhi (86-90)
    {
        "title": "Doraemon - Tập 1",
        "isbn": "9786041000086",
        "description": "Truyện tranh Doraemon kinh điển.",
        "price": "22000",
        "author_name": "Tô Hoài",
        "publisher_name": "NXB Kim Đồng",
        "pages": 180,
        "stock_quantity": 300,
        "status": "available",
    },
    {
        "title": "Conan - Tập 1",
        "isbn": "9786041000087",
        "description": "Thám tử lừng danh Conan.",
        "price": "25000",
        "author_name": "Tô Hoài",
        "publisher_name": "NXB Kim Đồng",
        "pages": 190,
        "stock_quantity": 250,
        "status": "available",
    },
    {
        "title": "Thám Tử Kỳ Tài - Tập 1",
        "isbn": "9786041000088",
        "description": "Truyện trinh thám thiếu nhi hấp dẫn.",
        "price": "35000",
        "author_name": "Nguyễn Nhật Ánh",
        "publisher_name": "NXB Kim Đồng",
        "pages": 150,
        "stock_quantity": 100,
        "status": "available",
    },
    {
        "title": "Totto-chan Bên Cửa Sổ",
        "isbn": "9786041000089",
        "description": "Câu chuyện về ngôi trường tiểu học đặc biệt.",
        "price": "68000",
        "author_name": "Tô Hoài",
        "publisher_name": "NXB Kim Đồng",
        "pages": 232,
        "stock_quantity": 120,
        "status": "available",
    },
    {
        "title": "Charlie Và Nhà Máy Sôcôla",
        "isbn": "9786041000090",
        "description": "Chuyến phiêu lưu kỳ diệu.",
        "price": "72000",
        "author_name": "Antoine de Saint-Exupéry",
        "publisher_name": "NXB Kim Đồng",
        "pages": 176,
        "stock_quantity": 80,
        "status": "available",
    },
    # Lịch sử & Văn hóa (91-95)
    {
        "title": "Việt Nam Sử Lược",
        "isbn": "9786041000091",
        "description": "Tổng quan lịch sử Việt Nam.",
        "price": "125000",
        "author_name": "Đặng Nhật Minh",
        "publisher_name": "NXB Giáo Dục",
        "pages": 680,
        "stock_quantity": 40,
        "status": "available",
    },
    {
        "title": "Đại Việt Sử Ký Toàn Thư",
        "isbn": "9786041000092",
        "description": "Bộ sử quan trọng nhất Việt Nam.",
        "price": "350000",
        "author_name": "Đặng Nhật Minh",
        "publisher_name": "NXB Giáo Dục",
        "pages": 1200,
        "stock_quantity": 15,
        "status": "available",
    },
    {
        "title": "Guns, Germs, and Steel",
        "isbn": "9786041000093",
        "description": "Súng, Vi Trùng Và Thép - Lịch sử văn minh.",
        "price": "175000",
        "author_name": "Yuval Noah Harari",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 480,
        "stock_quantity": 35,
        "status": "available",
    },
    {
        "title": "Nghìn Năm Văn Hiến",
        "isbn": "9786041000094",
        "description": "Di sản văn hóa Việt Nam.",
        "price": "145000",
        "author_name": "Đặng Nhật Minh",
        "publisher_name": "NXB Giáo Dục",
        "pages": 400,
        "stock_quantity": 30,
        "status": "available",
    },
    {
        "title": "Văn Minh Phương Đông",
        "isbn": "9786041000095",
        "description": "Khám phá nền văn minh phương Đông.",
        "price": "165000",
        "author_name": "Đặng Nhật Minh",
        "publisher_name": "NXB Giáo Dục",
        "pages": 520,
        "stock_quantity": 25,
        "status": "available",
    },
    # Tôn giáo & Triết học (96-100)
    {
        "title": "Đường Xưa Mây Trắng",
        "isbn": "9786041000096",
        "description": "Cuộc đời Đức Phật Thích Ca qua ngòi bút thiền sư.",
        "price": "135000",
        "author_name": "Thích Nhất Hạnh",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 600,
        "stock_quantity": 80,
        "status": "available",
    },
    {
        "title": "Phép Lạ Của Sự Tỉnh Thức",
        "isbn": "9786041000097",
        "description": "The Miracle of Mindfulness.",
        "price": "65000",
        "author_name": "Thích Nhất Hạnh",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 140,
        "stock_quantity": 100,
        "status": "available",
    },
    {
        "title": "An Lạc Từng Bước Chân",
        "isbn": "9786041000098",
        "description": "Peace Is Every Step.",
        "price": "72000",
        "author_name": "Thích Nhất Hạnh",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 160,
        "stock_quantity": 90,
        "status": "available",
    },
    {
        "title": "Triết Học Hiện Sinh",
        "isbn": "9786041000099",
        "description": "Nhập môn triết học hiện sinh phương Tây.",
        "price": "125000",
        "author_name": "Trần Đăng Khoa",
        "publisher_name": "NXB Giáo Dục",
        "pages": 350,
        "stock_quantity": 30,
        "status": "available",
    },
    {
        "title": "Siddhartha",
        "isbn": "9786041000100",
        "description": "Tiểu thuyết triết học kinh điển.",
        "price": "78000",
        "author_name": "Paulo Coelho",
        "publisher_name": "NXB Tổng hợp TPHCM",
        "pages": 152,
        "stock_quantity": 70,
        "status": "available",
    },
]

CUSTOMERS = [
    {
        "username": "demouser",
        "email": "demo@bookstore.com",
        "password_hash": "demo123",
        "first_name": "Demo",
        "last_name": "User",
        "phone_number": "0999888777",
    },
    {
        "username": "nguyenvana",
        "email": "nguyen@example.com",
        "password_hash": "password123",
        "first_name": "Nguyễn",
        "last_name": "Văn A",
        "phone_number": "0901234567",
    },
    {
        "username": "tranthib",
        "email": "tran@example.com",
        "password_hash": "password123",
        "first_name": "Trần",
        "last_name": "Thị B",
        "phone_number": "0912345678",
    },
    {
        "username": "levanc",
        "email": "le@example.com",
        "password_hash": "password123",
        "first_name": "Lê",
        "last_name": "Văn C",
        "phone_number": "0923456789",
    },
    {
        "username": "phamthid",
        "email": "pham@example.com",
        "password_hash": "password123",
        "first_name": "Phạm",
        "last_name": "Thị D",
        "phone_number": "0934567890",
    },
]

STAFF = [
    {
        "email": "admin@bookstore.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "BookStore",
        "role": "admin",
        "department": "Management",
    },
    {
        "email": "manager@bookstore.com",
        "password": "manager123",
        "first_name": "Manager",
        "last_name": "BookStore",
        "role": "manager",
        "department": "Operations",
    },
    {
        "email": "staff@bookstore.com",
        "password": "staff123",
        "first_name": "Staff",
        "last_name": "BookStore",
        "role": "staff",
        "department": "Sales",
    },
    {
        "email": "warehouse@bookstore.com",
        "password": "warehouse123",
        "first_name": "Kho",
        "last_name": "Vận",
        "role": "warehouse",
        "department": "Warehouse",
    },
    {
        "email": "support@bookstore.com",
        "password": "support123",
        "first_name": "Hỗ Trợ",
        "last_name": "KH",
        "role": "support",
        "department": "Customer Support",
    },
]


# ============================================================
# SEED FUNCTIONS
# ============================================================


def seed_entity(url, items, label, id_field=None):
    """Generic seed function for any entity."""
    ids = []
    for item in items:
        try:
            resp = requests.post(url, json=item, timeout=10)
            if resp.status_code == 201:
                if id_field:
                    ids.append(resp.json().get(id_field))
                name = (
                    item.get("name")
                    or item.get("title")
                    or item.get("email")
                    or str(item)[:40]
                )
                print(f"  ✅ {label}: {name}")
            else:
                name = item.get("name") or item.get("title") or item.get("email") or ""
                print(f"  ⚠️ {label} {name}: {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    return ids


def enrich_books_with_refs(catalog_url, books):
    """Attach category_id/author_id/publisher_id and normalize payload keys."""
    category_ranges = [
        ("van-hoc-viet-nam", 1, 15),
        ("van-hoc-nuoc-ngoai", 16, 30),
        ("cong-nghe-lap-trinh", 31, 50),
        ("kinh-te-kinh-doanh", 51, 65),
        ("khoa-hoc", 66, 75),
        ("tam-ly-ky-nang-song", 76, 85),
        ("thieu-nhi", 86, 90),
        ("lich-su-van-hoa", 91, 95),
        ("ton-giao-triet-hoc", 96, 100),
    ]

    try:
        cat_resp = requests.get(f"{catalog_url}/categories/", timeout=10)
        author_resp = requests.get(f"{catalog_url}/authors/", timeout=10)
        pub_resp = requests.get(f"{catalog_url}/publishers/", timeout=10)
        categories = cat_resp.json() if cat_resp.status_code == 200 else []
        authors = author_resp.json() if author_resp.status_code == 200 else []
        publishers = pub_resp.json() if pub_resp.status_code == 200 else []
    except Exception as exc:
        print(f"  ⚠️ Cannot fetch catalog refs for books: {exc}")
        return books

    slug_to_id = {c.get("slug"): c.get("category_id") for c in categories}
    name_to_id = {a.get("name"): a.get("author_id") for a in authors}
    publisher_name_to_id = {p.get("name"): p.get("publisher_id") for p in publishers}

    idx_to_category = {}
    for slug, start, end in category_ranges:
        cat_id = slug_to_id.get(slug)
        if not cat_id:
            continue
        for i in range(start - 1, end):
            idx_to_category[i] = cat_id

    enriched = []
    for idx, book in enumerate(books):
        b = dict(book)
        b["category_id"] = idx_to_category.get(idx)
        b["author_id"] = name_to_id.get(book.get("author_name"))
        b["publisher_id"] = publisher_name_to_id.get(book.get("publisher_name"))

        # Normalize fields for book-service serializers
        if "pages" in b and "page_count" not in b:
            b["page_count"] = b.get("pages")
        b.pop("pages", None)
        b.pop("author_name", None)
        b.pop("publisher_name", None)

        enriched.append(b)

    return enriched


def seed_books_upsert(book_url, books_payload):
    """
    Upsert books by ISBN:
    - POST for new ISBN
    - PUT partial update for existing ISBN (to backfill missing author/publisher/category refs)
    """
    print(f"\n📖 Seeding Book Service ({len(books_payload)} books)...")

    try:
        existing_resp = requests.get(book_url, timeout=15)
        existing_books = (
            existing_resp.json()
            if existing_resp.status_code == 200
            and isinstance(existing_resp.json(), list)
            else []
        )
    except Exception as exc:
        print(f"  ⚠️ Cannot fetch existing books for upsert: {exc}")
        existing_books = []

    isbn_to_id = {
        str(b.get("isbn") or "").strip(): b.get("book_id")
        for b in existing_books
        if str(b.get("isbn") or "").strip() and b.get("book_id")
    }

    create_fields = {
        "title",
        "isbn",
        "isbn13",
        "description",
        "short_description",
        "price",
        "original_price",
        "cost_price",
        "stock_quantity",
        "page_count",
        "weight_grams",
        "dimensions",
        "language",
        "format",
        "publish_year",
        "publish_date",
        "edition",
        "status",
        "is_featured",
        "is_bestseller",
        "cover_image_url",
        "author_id",
        "publisher_id",
        "category_id",
    }
    update_fields = {
        "title",
        "description",
        "short_description",
        "price",
        "original_price",
        "stock_quantity",
        "status",
        "is_featured",
        "is_bestseller",
        "cover_image_url",
        "author_id",
        "publisher_id",
        "category_id",
    }

    for item in books_payload:
        title = item.get("title") or "(No title)"
        isbn = str(item.get("isbn") or "").strip()

        try:
            if isbn and isbn in isbn_to_id:
                book_id = isbn_to_id[isbn]
                payload = {k: v for k, v in item.items() if k in update_fields}
                resp = requests.put(
                    f"{book_url}{book_id}/",
                    json=payload,
                    timeout=12,
                )
                if resp.status_code == 200:
                    print(f"  ♻️ Book updated: {title}")
                else:
                    print(
                        f"  ⚠️ Book update {title}: {resp.status_code} - {resp.text[:100]}"
                    )
            else:
                payload = {k: v for k, v in item.items() if k in create_fields}
                resp = requests.post(book_url, json=payload, timeout=12)
                if resp.status_code == 201:
                    created = resp.json()
                    if isbn and created.get("book_id"):
                        isbn_to_id[isbn] = created["book_id"]
                    print(f"  ✅ Book: {title}")
                else:
                    print(f"  ⚠️ Book {title}: {resp.status_code} - {resp.text[:100]}")
        except Exception as exc:
            print(f"  ❌ Book {title}: {exc}")


def _safe_get_list(url, label):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
    except Exception as exc:
        print(f"  ⚠️ Cannot fetch {label}: {exc}")
    return []


def _random_address():
    addresses = [
        "12 Nguyen Trai, District 1, HCMC",
        "88 Tran Hung Dao, District 5, HCMC",
        "102 Le Loi, District 1, HCMC",
        "45 Phan Dinh Phung, District 3, HCMC",
        "160 Vo Thi Sau, District 3, HCMC",
        "25 Le Duan, District 1, HCMC",
    ]
    return random.choice(addresses)


def seed_orders(order_count=50, completed_ratio=0.7):
    print(f"\n🧾 Seeding Order Service ({order_count} orders)...")

    customers = _safe_get_list(f"{CUSTOMER_URL}/customers/", "customers")
    books = _safe_get_list(f"{BOOK_URL}/books/", "books")

    if not customers or not books:
        print("  ⚠️ Missing customers or books. Skip seeding orders.")
        return 0

    created = 0
    active_statuses = ["pending", "confirmed", "processing", "shipped", "cancelled"]

    for _ in range(order_count):
        customer = random.choice(customers)
        customer_id = customer.get("customer_id")
        if not customer_id:
            continue

        item_count = random.randint(1, 4)
        chosen_books = random.sample(books, k=min(item_count, len(books)))
        added = 0

        for book in chosen_books:
            book_id = book.get("book_id")
            if not book_id:
                continue
            payload = {"book_id": book_id, "quantity": random.randint(1, 2)}
            try:
                resp = requests.post(
                    f"{CART_URL}/carts/{customer_id}/items/",
                    json=payload,
                    timeout=10,
                )
                if resp.status_code in (200, 201):
                    added += 1
            except Exception:
                continue

        if added == 0:
            continue

        order_payload = {
            "customer_id": customer_id,
            "shipping_address": _random_address(),
            "billing_address": _random_address(),
            "shipping_method": random.choice(["standard", "express"]),
            "payment_method": random.choice(["cod", "card", "bank"]),
            "notes": "Seeded order",
        }

        try:
            resp = requests.post(f"{ORDER_URL}/orders/", json=order_payload, timeout=10)
            if resp.status_code != 201:
                print(f"  ⚠️ Order create failed: {resp.status_code} - {resp.text[:80]}")
                continue

            order_data = resp.json()
            order_id = order_data.get("order_id")
            payment_id = order_data.get("payment_id")

            if order_id:
                if random.random() < completed_ratio and payment_id:
                    try:
                        requests.post(
                            f"{PAY_URL}/payments/{payment_id}/process/",
                            timeout=10,
                        )
                        requests.put(
                            f"{ORDER_URL}/orders/{order_id}/",
                            json={"status": "delivered"},
                            timeout=10,
                        )
                    except Exception:
                        pass
                else:
                    target_status = random.choice(active_statuses)
                    if target_status != order_data.get("status"):
                        requests.put(
                            f"{ORDER_URL}/orders/{order_id}/",
                            json={"status": target_status},
                            timeout=10,
                        )
            created += 1
        except Exception as exc:
            print(f"  ❌ Order create error: {exc}")

    print(f"  ✅ Created {created} orders")
    return created


def main():
    print("=" * 60)
    print("🚀 BookStore Microservices - Seed Data (Comprehensive)")
    print("=" * 60)

    # Check if services are running
    try:
        resp = requests.get("http://localhost:8000/health/", timeout=5)
        if resp.status_code != 200:
            print("❌ Services not running! Please run: docker-compose up")
            return
    except:
        print("❌ Cannot connect to services! Please run: docker-compose up")
        return

    # 1. Catalog: Publishers, Authors, Categories, Tags
    print("\n📦 Seeding Catalog Service (Publishers, Authors, Categories, Tags)...")
    seed_entity(f"{CATALOG_URL}/publishers/", PUBLISHERS, "Publisher", "publisher_id")
    seed_entity(f"{CATALOG_URL}/authors/", AUTHORS, "Author", "author_id")
    seed_entity(f"{CATALOG_URL}/categories/", CATEGORIES, "Category", "category_id")
    seed_entity(f"{CATALOG_URL}/tags/", TAGS, "Tag")

    # 2. Books
    books_payload = enrich_books_with_refs(CATALOG_URL, BOOKS)
    seed_books_upsert(f"{BOOK_URL}/books/", books_payload)

    # 3. Customers
    print(f"\n👤 Seeding Customer Service ({len(CUSTOMERS)} customers)...")
    seed_entity(f"{CUSTOMER_URL}/customers/", CUSTOMERS, "Customer", "customer_id")

    # 4. Staff
    print(f"\n👔 Seeding Staff Service ({len(STAFF)} staff)...")
    seed_entity(f"{STAFF_URL}/staff/", STAFF, "Staff", "staff_id")

    # 5. Orders
    orders_created = seed_orders(50)

    # Summary
    print("\n" + "=" * 60)
    print("✅ Seed Data Complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  📚 Books: {len(BOOKS)}")
    print(f"  ✍️  Authors: {len(AUTHORS)}")
    print(f"  📂 Categories: {len(CATEGORIES)}")
    print(f"  🏷️  Tags: {len(TAGS)}")
    print(f"  🏢 Publishers: {len(PUBLISHERS)}")
    print(f"  👤 Customers: {len(CUSTOMERS)}")
    print(f"  👔 Staff: {len(STAFF)}")
    print(f"  🧾 Orders: {orders_created}")
    print(f"\n📝 Customer Login:")
    print(f"  Email: demo@bookstore.com / Password: demo123")
    print(f"\n📝 Staff Login:")
    print(f"  Admin:     admin@bookstore.com / admin123")
    print(f"  Manager:   manager@bookstore.com / manager123")
    print(f"  Staff:     staff@bookstore.com / staff123")
    print(f"  Warehouse: warehouse@bookstore.com / warehouse123")
    print(f"  Support:   support@bookstore.com / support123")
    print(f"\n🌐 Access: http://localhost:8000")
    print(f"🔧 Staff:  http://localhost:8000/staff/login/")
    print("=" * 60)


if __name__ == "__main__":
    main()
