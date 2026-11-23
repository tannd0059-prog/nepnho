import os
import json
import random
import string
import time
import re
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from templates_responsive import DESKTOP_TEMPLATE, TABLET_TEMPLATE, MOBILE_TEMPLATE, DEMO_SHOWCASE_TEMPLATE


app = Flask(__name__)
app.secret_key = "nepnho_d2c_full_system_key_2026"

DATA_FILE = "nepnho_db.json"

# ==============================================================================
# CẤU HÌNH TÀI KHOẢN NGÂN HÀNG THANH TOÁN (VIETQR TỰ ĐỘNG)
# ==============================================================================
DEFAULT_BANK_CONFIG = {
    "bank_code": "MB",
    "bank_name": "Ngân hàng TMCP Quân Đội (MBBank)",
    "account_number": "0368688548",
    "account_holder": "NGUYEN DUY TAN",
    "qr_template": "compact2"
}

# ==============================================================================
# DANH MỤC SẢN PHẨM: ĐỜI SỐNG, LÀM ĐẸP & SẮP XẾP PHÒNG GỌN GÀNG
# ==============================================================================
DEFAULT_PRODUCTS = {
    "NN-ROTATING-ORGANIZER": {
        "id": "NN-ROTATING-ORGANIZER",
        "name": "Kệ Đựng Mỹ Phẩm Xoay 360° Diamond Mica Đa Tầng",
        "price": 149000,
        "original_price": 199000,
        "category": "Làm đẹp & Bàn trang điểm",
        "description": "Thiết kế xoay 360 độ êm ái, sức chứa 30+ chai lọ skincare, toner, serum và 20 thỏi son. Giải phóng 70% mặt bàn trang điểm.",
        "kit_components": ["Trụ xoay mica acrylic kim cương", "4 khay ngăn điều chỉnh độ cao", "Khay nóc chia 16 ô son", "Vòng bi thép không gỉ trơn mượt"],
        "before_img": "/images/ke_dung_my_pham_before.png",
        "after_img": "/images/ke_dung_my_pham.png",
        "stock_physical": 65,
        "stock_committed": 3
    },
    "NN-LED-MIRROR": {
        "id": "NN-LED-MIRROR",
        "name": "Gương Trang Điểm Đèn LED Cảm Ứng 3 Màu + Khay Đựng Phụ Kiện",
        "price": 185000,
        "original_price": 245000,
        "category": "Làm đẹp & Bàn trang điểm",
        "description": "Mặt gương kính HD siêu nét chuẩn màu makeup. 3 màu đèn LED (Trắng - Tự nhiên - Vàng ấm). Chân đế tích hợp khay trang sức mini.",
        "kit_components": ["Gương xoay gập 90 độ mặt kính HD", "Dải đèn LED cảm ứng chạm", "Đế khay đựng nhẫn phụ kiện", "Cáp sạc Type-C pin 7 ngày"],
        "before_img": "/images/guong_trang_diem_led_before.png",
        "after_img": "/images/guong_trang_diem_led.png",
        "stock_physical": 45,
        "stock_committed": 2
    },
    "NN-COTTON-BOX": {
        "id": "NN-COTTON-BOX",
        "name": "Hộp Đựng Bông Tẩy Trang & Tăm Bông Nắp Gỗ Chống Bụi 2 Ngăn",
        "price": 69000,
        "original_price": 95000,
        "category": "Làm đẹp & Bàn trang điểm",
        "description": "Hộp mica acrylic trong suốt nắp gỗ tre tự nhiên kháng ẩm. Khe rút thông minh giúp lấy bông tẩy trang 1 giây mà không dính bụi.",
        "kit_components": ["Thân hộp mica kháng bụi 2 ngăn", "Nắp gỗ tre tự nhiên kín khí", "Khe rút bông tẩy trang lấy nhanh", "Ngăn tăm bông riêng biệt"],
        "before_img": "/images/hop_dung_bong_tay_trang_before.png",
        "after_img": "/images/hop_dung_bong_tay_trang.png",
        "stock_physical": 80,
        "stock_committed": 6
    },
    "NN-GOLD-TRAY": {
        "id": "NN-GOLD-TRAY",
        "name": "Khay Gương Viền Mạ Vàng Trưng Bày Nước Hoa & Son Phong Cách Bắc Âu",
        "price": 175000,
        "original_price": 230000,
        "category": "Làm đẹp & Bàn trang điểm",
        "description": "Khay gương tráng bạc phản chiếu ánh kim loại viền mạ vàng sang trọng. Biến góc bàn làm đẹp thành không gian check-in chuẩn spa.",
        "kit_components": ["Đáy gương pha lê tráng bạc", "Khung viền mạ tĩnh điện chống gỉ", "Chân đệm cao su chống trầy mặt bàn"],
        "before_img": "/images/khay_guong_before.png",
        "after_img": "/images/khay_guong.png",
        "stock_physical": 35,
        "stock_committed": 1
    },
    "NN-DRYER-HANGER": {
        "id": "NN-DRYER-HANGER",
        "name": "Giá Treo Máy Sấy Tóc & Lược Tạo Kiểu Dán Tường (Chịu Lực 5kg)",
        "price": 79000,
        "original_price": 110000,
        "category": "Làm đẹp & Bàn trang điểm",
        "description": "Dán tường siêu dính không cần khoan đục. Tích hợp móc cuộn dây điện máy sấy và cốc cắm lược chải tóc gọn gàng.",
        "kit_components": ["Giá đỡ máy sấy có viền silicone", "Cốc cắm lược có lỗ thoát nhiệt", "Móc gài phích cắm an toàn", "Miếng dán cường lực chịu 5kg"],
        "before_img": "/images/gia_treo_may_say_before.png",
        "after_img": "/images/gia_treo_may_say.png",
        "stock_physical": 55,
        "stock_committed": 2
    },
    "NN-STEEL-BOX": {
        "id": "NN-STEEL-BOX",
        "name": "Hộp Đựng Quần Áo Khung Thép Xếp Chồng Cửa Trong Suốt (66L)",
        "price": 129000,
        "original_price": 169000,
        "category": "Góc phòng gọn gàng",
        "description": "Lưu trữ chăn màn, ga gối, quần áo mùa đông. Khung thép mạ chịu tải 60kg xếp chồng nhiều tầng, mở lấy đồ cả nắp trên và cửa trước.",
        "kit_components": ["Khung thép mạ crom trợ lực chắc chắn", "Vải Oxford 600D chống ẩm", "Cửa nhựa PVC trong suốt", "Khóa kéo kép kim loại"],
        "before_img": "/images/hop_khung_quan_ao_before.png",
        "after_img": "/images/hop_khung_quan_ao.png",
        "stock_physical": 50,
        "stock_committed": 4
    },
    "NN-DIVIDER-BOX": {
        "id": "NN-DIVIDER-BOX",
        "name": "Set 3 Hộp Vải Chia Ngăn Đựng Đồ Lót, Tất & Khăn Lụa",
        "price": 89000,
        "original_price": 125000,
        "category": "Góc phòng gọn gàng",
        "description": "Bộ 3 kích cỡ (6 ngăn cho áo lót, 7 ngăn cho quần mỏng, 11 ngăn cho tất/phụ kiện). Xếp vừa khít ngăn kéo tủ đồ.",
        "kit_components": ["Hộp 6 ngăn cho áo ngực", "Hộp 7 ngăn cho quần lót", "Hộp 11 ngăn cho tất", "Chất liệu vải dệt thông thoáng kháng khuẩn"],
        "before_img": "/images/set_hop_3_ngan_before.png",
        "after_img": "/images/set_hop_3_ngan.png",
        "stock_physical": 70,
        "stock_committed": 5
    },
    "NN-SHOE-RACK": {
        "id": "NN-SHOE-RACK",
        "name": "Kệ Để Giày Dép Gấp Gọn Chữ X 5 Tầng Tiết Kiệm Không Gian",
        "price": 99000,
        "original_price": 139000,
        "category": "Góc phòng gọn gàng",
        "description": "Mở ra dùng ngay trong 5 giây không cần ốc vít. Bề rộng chỉ 26cm, tận dụng hoàn hảo khe hẹp sau cửa ra vào của phòng trọ nhỏ.",
        "kit_components": ["Khung nhựa PP nguyên sinh dẻo dai", "5 tầng kệ chứa tối đa 10 đôi giày", "Khớp gập module linh hoạt", "Gờ chắn chống rơi bụi"],
        "before_img": "/images/ke_de_giay_before.png",
        "after_img": "/images/ke_de_giay.png",
        "stock_physical": 40,
        "stock_committed": 3
    },
    "NN-CABLE-BOX": {
        "id": "NN-CABLE-BOX",
        "name": "Hộp Quản Lý Ổ Cắm & Giấu Dây Cáp Điện Nắp Gỗ Chống Cháy",
        "price": 115000,
        "original_price": 155000,
        "category": "Góc phòng gọn gàng",
        "description": "Gom gọn toàn bộ ổ cắm 6-8 lỗ và mớ dây sạc rườm rà dưới sàn. Nắp gỗ tự nhiên có rãnh làm giá đỡ điện thoại/ipad khi sạc an toàn.",
        "kit_components": ["Hộp nhựa ABS chống cháy cách điện", "Nắp gỗ tre tự nhiên có rãnh đỡ", "Khe tản nhiệt thông minh", "Khe luồn dây hai đầu"],
        "before_img": "/images/hop_dung_day_before.png",
        "after_img": "/images/hop_dung_day.png",
        "stock_physical": 60,
        "stock_committed": 2
    },
    "NN-AROMA-DIFFUSER": {
        "id": "NN-AROMA-DIFFUSER",
        "name": "Máy Xông Tinh Dầu Siêu Âm Phun Sương Vân Gỗ Đèn LED 7 Màu (500ml)",
        "price": 199000,
        "original_price": 270000,
        "category": "Đời sống & Thư giãn",
        "description": "Khuếch tán sương siêu mịn bù ẩm cho phòng điều hòa giúp dưỡng ẩm da khi ngủ. Kết hợp đèn LED 7 màu êm dịu thay thế đèn ngủ.",
        "kit_components": ["Máy khuếch tán dung tích 500ml", "Remote điều khiển từ xa", "Cảm biến tự ngắt khi cạn nước", "Tặng kèm tinh dầu 10ml"],
        "before_img": "/images/may_xong_before.png",
        "after_img": "/images/may_xong.png",
        "stock_physical": 50,
        "stock_committed": 3
    },
    "NN-SUNSET-LAMP": {
        "id": "NN-SUNSET-LAMP",
        "name": "Đèn Hoàng Hôn Sunset Lamp 16 Màu Kèm Remote Chill Phòng Ngủ",
        "price": 119000,
        "original_price": 165000,
        "category": "Đời sống & Thư giãn",
        "description": "Thấu kính pha lê xoay 360 độ tạo hiệu ứng hoàng hôn lãng mạn. Giúp góc phòng ngủ bừng sáng ấm cúng và là phụ kiện chụp ảnh makeup đỉnh cao.",
        "kit_components": ["Thấu kính pha lê truyền sáng quang học", "Cổ kim loại uốn cong 360 độ", "Remote điều khiển 24 phím 16 màu", "Đế kim loại tròn chống đổ"],
        "before_img": "/images/den_hoang_hon_before.png",
        "after_img": "/images/den_hoang_hon.png",
        "stock_physical": 45,
        "stock_committed": 1
    },
    "NN-RUG-ROUND": {
        "id": "NN-RUG-ROUND",
        "name": "Thảm Tròn Lông Cừu Nhân Tạo Êm Ái Trải Bàn Trang Điểm (D80cm)",
        "price": 85000,
        "original_price": 120000,
        "category": "Đời sống & Thư giãn",
        "description": "Thảm lông mềm mịn êm chân đường kính 80cm phong cách Bắc Âu. Đế chống trượt tuyệt đối, tạo điểm nhấn ấm cúng cho góc làm đẹp phòng trọ.",
        "kit_components": ["Lớp lông sợi microfiber mềm mịn", "Đế silicone hạt nổi chống trượt 100%", "Dễ dàng giặt máy hoặc vệ sinh"],
        "before_img": "/images/tham_long_before.png",
        "after_img": "/images/tham_long.png",
        "stock_physical": 40,
        "stock_committed": 2
    },
    "NN-DESK": {
        "id": "NN-DESK",
        "name": "Nếp Bàn — Desk Reset Kit",
        "price": 229000,
        "original_price": 279000,
        "category": "Bộ Kit Giải Pháp",
        "description": "Giải pháp gom dây cáp, phân khu vật dụng nhỏ và reset góc làm việc trong 15 phút.",
        "kit_components": ["Khay đựng vật dụng nhỏ", "Kẹp giữ dây cáp", "Hộp đựng dây sạc", "Bộ nhãn dán tối giản", "Khăn lau Microfiber"],
        "before_img": "/images/nep_ban_before.png",
        "after_img": "/images/nep_ban.png",
        "stock_physical": 50,
        "stock_committed": 5
    },
    "NN-CLOSET": {
        "id": "NN-CLOSET",
        "name": "Nếp Tủ — Closet Reset Kit",
        "price": 289000,
        "original_price": 339000,
        "category": "Bộ Kit Giải Pháp",
        "description": "Bộ túi gấp gọn phân loại tất, đồ lót, phụ kiện kèm túi thơm hút ẩm và checklist duy trì.",
        "kit_components": ["Túi gấp gọn đồ nhỏ", "Bộ phân loại vớ/đồ lót", "Bộ nhãn dán phân khu", "Túi thơm tự nhiên"],
        "before_img": "/images/nep_tu_before.png",
        "after_img": "/images/nep_tu.png",
        "stock_physical": 40,
        "stock_committed": 2
    },
    "NN-ROOM": {
        "id": "NN-ROOM",
        "name": "Nếp Trọ — Small Room Starter Kit",
        "price": 399000,
        "original_price": 459000,
        "category": "Bộ Kit Giải Pháp",
        "description": "Bộ móc dán tải trọng cao, túi treo đa năng và sơ đồ bố trí phòng 3 khu vực chuẩn gọn.",
        "kit_components": ["Móc dán tường siêu bám", "Túi treo đồ đa năng", "Kẹp phơi vật dụng gọn", "Hướng dẫn bố trí phòng 3 khu"],
        "before_img": "/images/nep_tro_before.png",
        "after_img": "/images/nep_tro.png",
        "stock_physical": 30,
        "stock_committed": 4
    },
    "NN-COMBO": {
        "id": "NN-COMBO",
        "name": "Combo Nếp Bàn + Nếp Tủ (Giảm 10%)",
        "price": 466000,
        "original_price": 518000,
        "category": "Bộ Kit Giải Pháp",
        "description": "Giải pháp toàn diện cho góc làm việc và tủ quần áo. Tiết kiệm ngay 10% khi mua kèm.",
        "kit_components": ["Trọn bộ Nếp Bàn", "Trọn bộ Nếp Tủ", "Thiệp chúc mừng viết tay cá nhân hóa"],
        "before_img": "/images/combo_neptro_neptu_before.png",
        "after_img": "/images/combo_neptro_neptu.png",
        "stock_physical": 20,
        "stock_committed": 1
    }
}

DEFAULT_USERS = {
    "admin@nepnho.vn": {
        "email": "admin@nepnho.vn",
        "password": generate_password_hash("admin123"),
        "fullname": "Quản Trị Viên Nếp Nhỏ",
        "phone": "0900000000",
        "address": "Kho Trung Tâm Nếp Nhỏ: Phường Phước Long B, Quận 9, TP. Thủ Đức, TP.HCM",
        "role": "admin"
    },
    "tan@gmail.com": {
        "email": "tan@gmail.com",
        "password": generate_password_hash("123"),
        "fullname": "Nguyễn Văn Tân",
        "phone": "0901234567",
        "address": "123 Nguyễn Văn Cừ, Phường 2, Quận 5, TP. Hồ Chí Minh",
        "role": "customer"
    }
}

def load_data():
    db = {"users": DEFAULT_USERS, "products": DEFAULT_PRODUCTS, "orders": {}, "bank_config": DEFAULT_BANK_CONFIG}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                db['users'] = loaded.get('users', DEFAULT_USERS)
                existing_products = loaded.get('products', {})
                for pid, pdata in DEFAULT_PRODUCTS.items():
                    if pid not in existing_products:
                        existing_products[pid] = pdata
                db['products'] = existing_products
                db['orders'] = loaded.get('orders', {})
                db['bank_config'] = loaded.get('bank_config', DEFAULT_BANK_CONFIG)
                return db
        except Exception:
            pass
    save_data(db)
    return db

def save_data(db):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

DB = load_data()

# ==============================================================================
# HÀM TỰ ĐỘNG HỦY ĐƠN CHUYỂN KHOẢN SAU 24 GIỜ (HOÀN TRẢ TỒN KHO ATP)
# ==============================================================================
def check_and_cancel_expired_orders():
    now_ts = time.time()
    has_changes = False

    for oid, o in DB['orders'].items():
        if o.get('payment_method') == 'VIETQR' and o.get('payment_status') == 'Chờ thanh toán':
            expires_at = o.get('expires_at_timestamp')
            if not expires_at:
                try:
                    dt = datetime.strptime(o.get('created_at', ''), "%H:%M %d/%m/%Y")
                    expires_at = dt.timestamp() + (24 * 3600)
                    o['expires_at_timestamp'] = expires_at
                    has_changes = True
                except Exception:
                    continue

            if now_ts >= expires_at:
                o['status'] = 'Đã tự hủy (Quá hạn 24h)'
                o['payment_status'] = 'Đã hết hạn thanh toán'
                for item in o.get('items', []):
                    pid = item.get('id')
                    if pid in DB['products']:
                        DB['products'][pid]['stock_committed'] = max(
                            0, DB['products'][pid]['stock_committed'] - item.get('qty', 0)
                        )
                has_changes = True

    if has_changes:
        save_data(DB)

@app.before_request
def before_request_hook():
    check_and_cancel_expired_orders()

# ==============================================================================
# MASTER HTML TEMPLATE
# ==============================================================================
BASE_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nếp Nhỏ — Gọn một góc, nhẹ cả ngày | Đời sống & Làm đẹp</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --bg-paper: #F7F4EE; --sage-green: #7D9D7C; --earth-brown: #8A6F5A; --warm-accent: #E88D67; --text-dark: #2B2B2B; }
        body { background-color: var(--bg-paper); color: var(--text-dark); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        .navbar-nepnho { background-color: #FFFFFF; border-bottom: 2px solid var(--sage-green); }
        .brand-title { font-weight: 800; color: var(--earth-brown); letter-spacing: -0.5px; }
        .btn-sage { background-color: var(--sage-green); color: white; font-weight: 600; border: none; }
        .btn-sage:hover { background-color: #6C8B6B; color: white; }
        .card-kit { border: none; border-radius: 14px; background: #FFFFFF; box-shadow: 0 4px 14px rgba(0,0,0,0.04); transition: transform 0.2s, box-shadow 0.2s; }
        .card-kit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
        .price-tag { color: var(--warm-accent); font-weight: 700; font-size: 1.15rem; }
        .badge-atp { background-color: #E8F5E9; color: #2E7D32; font-size: 0.75rem; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
        .copy-toast { position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: none; }
        
        /* GPS & ADDRESS STYLING */
        .gps-box { background: #F0FDF4; border: 1.5px dashed #16A34A; border-radius: 12px; }
        .gps-badge { background-color: #DCFCE7; color: #15803D; font-weight: 600; }

        /* ANIMATED CHECKMARK & STEPPER */
        .success-checkmark-box { width: 80px; height: 80px; margin: 0 auto 16px; position: relative; }
        .checkmark-svg { width: 80px; height: 80px; border-radius: 50%; display: block; stroke-width: 3.5; stroke: #198754; stroke-miterlimit: 10; margin: 0 auto; box-shadow: inset 0px 0px 0px #198754; animation: fill-check .4s ease-in-out .4s forwards, scale-check .3s ease-in-out .9s both; }
        .checkmark-circle { stroke-dasharray: 166; stroke-dashoffset: 166; stroke-width: 3.5; stroke-miterlimit: 10; stroke: #198754; fill: none; animation: stroke-check .6s cubic-bezier(0.65, 0, 0.45, 1) forwards; }
        .checkmark-check { transform-origin: 50% 50%; stroke-dasharray: 48; stroke-dashoffset: 48; stroke-width: 4; stroke: #198754; animation: stroke-check .35s cubic-bezier(0.65, 0, 0.45, 1) .7s forwards; }
        @keyframes stroke-check { 100% { stroke-dashoffset: 0; } }
        @keyframes scale-check { 0%, 100% { transform: none; } 50% { transform: scale3d(1.12, 1.12, 1); } }
        @keyframes fill-check { 100% { box-shadow: inset 0px 0px 0px 40px rgba(25, 135, 84, 0.12); } }

        .order-stepper { display: flex; justify-content: space-between; position: relative; margin: 25px 0 30px; }
        .order-stepper::before { content: ''; position: absolute; top: 22px; left: 10%; right: 10%; height: 3px; background: #E2E8F0; z-index: 1; }
        .order-stepper-bar { position: absolute; top: 22px; left: 10%; height: 3px; background: #198754; z-index: 2; transition: width 0.6s ease; }
        .stepper-step { position: relative; z-index: 3; text-align: center; flex: 1; }
        .stepper-icon { width: 44px; height: 44px; border-radius: 50%; background: #FFFFFF; border: 3px solid #CBD5E1; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-size: 16px; font-weight: bold; color: #64748B; }
        .stepper-step.completed .stepper-icon { border-color: #198754; background: #198754; color: #FFFFFF; }
        .stepper-step.active .stepper-icon { border-color: #198754; background: #FFFFFF; color: #198754; box-shadow: 0 0 0 5px rgba(25, 135, 84, 0.2); }
        .stepper-title { font-size: 0.82rem; color: #64748B; font-weight: 600; }
        .stepper-step.completed .stepper-title, .stepper-step.active .stepper-title { color: #198754; font-weight: 700; }
        .stepper-desc { font-size: 0.72rem; color: #94A3B8; }

        .e-receipt-card { background: #FFFFFF; border-radius: 18px; border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 10px 30px rgba(0,0,0,0.04); }
        .dashed-divider { border-top: 2px dashed #E2E8F0; margin: 16px 0; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-nepnho sticky-top py-2 shadow-sm">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="/">
                <div>
                    <span class="brand-title fs-4">🌿 NẾP NHỎ</span>
                    <div style="font-size: 0.78rem; color: #777;">Gọn một góc, nhẹ cả ngày</div>
                </div>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto ms-lg-4">
                    <li class="nav-item"><a class="nav-link fw-bold text-dark" href="/">Trang chủ</a></li>
                    <li class="nav-item"><a class="nav-link text-muted" href="/#products-section">Cửa hàng</a></li>
                    <li class="nav-item"><a class="nav-link fw-bold text-success" href="/demo" target="_blank">📱 Xem 3 Giao Diện</a></li>
                    {% if current_user and current_user.get('role') == 'admin' %}
                    <li class="nav-item"><a class="nav-link fw-bold text-danger" href="/admin">⚙️ QUẢN TRỊ ADMIN</a></li>
                    {% endif %}
                </ul>
                <div class="d-flex align-items-center gap-2">
                    <a href="/cart" class="btn btn-outline-dark position-relative me-2">
                        🛒 Giỏ hàng
                        {% if cart_count > 0 %}
                        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                            {{ cart_count }}
                        </span>
                        {% endif %}
                    </a>
                    {% if current_user %}
                    <div class="dropdown">
                        <button class="btn btn-sage dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            👤 {{ current_user['fullname'] }}
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end shadow">
                            <li><a class="dropdown-item" href="/profile">Trang cá nhân & Đơn hàng</a></li>
                            {% if current_user.get('role') == 'admin' %}
                            <li><a class="dropdown-item text-danger fw-bold" href="/admin">⚙️ Trang Quản Trị Admin</a></li>
                            {% endif %}
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="/logout">Đăng xuất</a></li>
                        </ul>
                    </div>
                    {% else %}
                    <a href="/login" class="btn btn-outline-secondary">Đăng nhập</a>
                    <a href="/register" class="btn btn-sage">Đăng ký</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    <div class="container mt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <main class="container my-4">
        {% block content %}{% endblock %}
    </main>

    <footer class="text-center py-4 mt-5 border-top bg-white">
        <div class="container">
            <p class="mb-1 fw-bold text-muted">🌿 NẾP NHỎ — Hệ thống TMĐT D2C Giải Pháp Sắp Xếp & Đời Sống</p>
            <div class="small text-muted mb-2">Hỗ trợ giao hàng qua GPS & Tự động hủy đơn chuyển khoản sau 24h</div>
            <small class="text-muted">Thanh toán VietQR liên ngân hàng 24/7</small>
        </div>
    </footer>
    
    <div id="copyToast" class="toast align-items-center text-bg-dark border-0 copy-toast" role="alert">
        <div class="d-flex">
            <div class="toast-body fw-bold">📋 Đã sao chép vào bộ nhớ tạm!</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    function copyToClipboard(text, btnElement) {
        if (!navigator.clipboard) {
            let textArea = document.createElement("textarea");
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("copy");
            document.body.removeChild(textArea);
            return;
        }
        navigator.clipboard.writeText(text).then(() => {
            let toastEl = document.getElementById('copyToast');
            if (toastEl) new bootstrap.Toast(toastEl, { delay: 2000 }).show();
            if (btnElement) {
                let old = btnElement.innerHTML;
                btnElement.innerHTML = '✓ Đã chép!';
                setTimeout(() => { btnElement.innerHTML = old; }, 2000);
            }
        });
    }
    </script>
</body>
</html>
"""

# ==============================================================================
# STOREFRONT TEMPLATES
# ==============================================================================
INDEX_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="p-4 p-md-5 mb-4 rounded-4 text-center shadow-sm" style="background: linear-gradient(135deg, #EFE8DC 0%, #E2D7C3 100%);">
    <span class="badge bg-success bg-opacity-75 text-white px-3 py-2 rounded-pill mb-2 fs-7">✨ Định vị GPS giao hàng tận cửa</span>
    <h1 class="fw-bold text-dark mb-2 display-6">Biến Căn Phòng Trở Nên Gọn Gàng & Thăng Hạng Góc Làm Đẹp</h1>
    <p class="lead text-muted fs-6 mb-4 mx-auto" style="max-width: 680px;">
        Bộ phụ kiện bàn trang điểm, hộp sắp xếp đồ đạc thông minh và các giải pháp decor chill giúp căn phòng luôn ngăn nắp, thoáng đãng.
    </p>
    <div class="row justify-content-center">
        <div class="col-md-7 col-lg-6">
            <div class="input-group shadow-sm bg-white rounded-pill p-1 border">
                <span class="input-group-text bg-transparent border-0 fs-5 ps-3">🔍</span>
                <input type="text" id="liveSearchInput" class="form-control border-0 shadow-none" placeholder="Tìm kiếm kệ mỹ phẩm, gương LED, hộp đựng..." onkeyup="filterStorefront()">
                <button class="btn btn-sage rounded-pill px-4" type="button" onclick="filterStorefront()">Tìm kiếm</button>
            </div>
        </div>
    </div>
</div>

<div id="products-section" class="mb-3">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <h4 class="fw-bold mb-0 text-dark">Tất Cả Sản Phẩm ({{ products|length }} món sẵn sàng giao)</h4>
        <span class="badge bg-info bg-opacity-10 text-primary border border-primary p-2">📍 Đã hỗ trợ bắt tọa độ GPS giao hàng</span>
    </div>
</div>

<div class="row g-4" id="productGrid">
    {% for pid, p in products.items() %}
    <div class="col-12 col-sm-6 col-lg-3 product-card-col" data-category="{{ p['category'] }}" data-name="{{ p['name'] | lower }}">
        <div class="card card-kit h-100 p-3 position-relative d-flex flex-column">
            <span class="badge position-absolute top-0 end-0 m-3 bg-white text-dark shadow-sm border" style="font-size: 0.72rem; z-index: 2;">
                {{ p['category'] }}
            </span>
            <div class="overflow-hidden rounded-3 mb-3 position-relative" style="height: 190px; background-color: #f1ede5;">
                <img src="{{ p['after_img'] }}" class="w-100 h-100 object-fit-cover rounded-3" alt="{{ p['name'] }}" loading="lazy">
            </div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge-atp">Sẵn sàng giao: {{ p['stock_physical'] - p['stock_committed'] }} món</span>
                {% if p['original_price'] > p['price'] %}
                <span class="badge bg-danger bg-opacity-10 text-danger fw-bold" style="font-size: 0.72rem;">
                    -{{ ((p['original_price'] - p['price']) / p['original_price'] * 100) | round | int }}%
                </span>
                {% endif %}
            </div>
            <h5 class="fw-bold fs-6 mb-1 text-dark text-truncate">{{ p['name'] }}</h5>
            <p class="text-muted small mb-3 flex-grow-1" style="height: 38px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                {{ p['description'] }}
            </p>
            <div class="d-flex justify-content-between align-items-center mt-auto pt-2 border-top">
                <span class="price-tag">{{ "{:,}".format(p['price']) }}đ</span>
                <div class="d-flex gap-1">
                    <form action="/add-to-cart" method="POST" class="m-0">
                        <input type="hidden" name="product_id" value="{{ p['id'] }}">
                        <button type="submit" class="btn btn-sm btn-outline-dark">🛒</button>
                    </form>
                    <a href="/product/{{ p['id'] }}" class="btn btn-sm btn-sage">Chi tiết</a>
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<script>
function filterStorefront() {
    let s = document.getElementById('liveSearchInput').value.toLowerCase().trim();
    document.querySelectorAll('.product-card-col').forEach(card => {
        let name = card.getAttribute('data-name') || '';
        card.style.display = (!s || name.includes(s)) ? '' : 'none';
    });
}
</script>
""")

PRODUCT_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="row g-4 bg-white p-4 rounded-4 shadow-sm">
    <div class="col-md-6">
        <div class="row g-2">
            <div class="col-6 text-center">
                <span class="badge bg-secondary mb-1">TRƯỚC KHI DÙNG</span>
                <img src="{{ product['before_img'] }}" class="img-fluid rounded border" style="height: 240px; object-fit: cover; width: 100%;" alt="Trước">
            </div>
            <div class="col-6 text-center">
                <span class="badge bg-success mb-1">SAU KHI GỌN GÀNG</span>
                <img src="{{ product['after_img'] }}" class="img-fluid rounded border" style="height: 240px; object-fit: cover; width: 100%;" alt="Sau">
            </div>
        </div>
    </div>
    <div class="col-md-6 d-flex flex-column">
        <span class="badge bg-warning text-dark mb-2 align-self-start">{{ product['category'] }}</span>
        <h2 class="fw-bold mb-2 text-dark">{{ product['name'] }}</h2>
        <div class="mb-3 d-flex align-items-center gap-2">
            <span class="fs-3 fw-bold text-danger">{{ "{:,}".format(product['price']) }}đ</span>
            <span class="badge bg-success ms-auto">ATP Khả dụng: {{ product['stock_physical'] - product['stock_committed'] }}</span>
        </div>
        <p class="text-secondary fs-6 mb-3">{{ product['description'] }}</p>
        <div class="p-3 mb-3 bg-light rounded-3 border">
            <h6 class="fw-bold mb-2 text-dark">📦 Thành phần nổi bật:</h6>
            <ul class="mb-0 ps-3 small text-secondary">
                {% for comp in product['kit_components'] %}
                <li class="py-1"><strong>✓</strong> {{ comp }}</li>
                {% endfor %}
            </ul>
        </div>
        <form action="/add-to-cart" method="POST" class="mt-auto">
            <input type="hidden" name="product_id" value="{{ product['id'] }}">
            <button type="submit" class="btn btn-sage btn-lg w-100 py-3 fs-6 shadow-sm">
                🛒 Thêm vào giỏ hàng ngay
            </button>
        </form>
    </div>
</div>
""")

CART_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<h4 class="fw-bold mb-3 text-dark">🛒 Giỏ Hàng Của Bạn</h4>

<!-- KHỐI VỊ TRÍ GIAO HÀNG & KHO XUẤT HÀNG -->
<div class="card p-3 mb-4 border-0 shadow-sm bg-white rounded-4 border-start border-success border-4">
    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
        <div>
            <div class="fw-bold text-dark d-flex align-items-center gap-2">
                <span>📍</span> Vị Trí Giao Hàng Của Bạn:
            </div>
            <div class="small mt-1 text-secondary" id="cartLocDisplay">
                {% if user_info and user_info.get('address') %}
                    <strong class="text-dark">{{ user_info.get('address') }}</strong>
                    {% if user_info.get('gps_lat') and user_info.get('gps_lng') %}
                    <span class="badge bg-success bg-opacity-10 text-success ms-1">GPS: {{ user_info.get('gps_lat') }}, {{ user_info.get('gps_lng') }}</span>
                    {% endif %}
                {% else %}
                    <span class="text-danger fw-bold">Chưa xác định tọa độ GPS giao hàng</span>
                {% endif %}
            </div>
            <div class="small text-muted mt-1" style="font-size: 0.76rem;">
                🏢 Kho xuất phát: <strong>Kho Trung Tâm Quận 9 (Phường Phước Long B, TP. Thủ Đức, TP.HCM)</strong>
            </div>
        </div>
        <button type="button" class="btn btn-sm btn-outline-success fw-bold px-3 py-2 shadow-sm rounded-pill" onclick="detectAndSaveLocation()">
            📍 Bắt vị trí GPS & Lưu
        </button>
    </div>
</div>

<div class="row g-4">
    <div class="col-md-8">
        <div class="card p-3 border-0 shadow-sm bg-white rounded-3">
            <table class="table align-middle">
                <thead><tr><th>Sản phẩm</th><th>Đơn giá</th><th>Số lượng</th><th>Thành tiền</th><th>Xóa</th></tr></thead>
                <tbody>
                    {% for item in cart %}
                    <tr>
                        <td class="fw-bold">{{ item['name'] }}</td>
                        <td>{{ "{:,}".format(item['price']) }}đ</td>
                        <td>
                            <form action="/update-cart" method="POST" class="d-flex align-items-center">
                                <input type="hidden" name="product_id" value="{{ item['id'] }}">
                                <input type="number" name="qty" value="{{ item['qty'] }}" min="1" class="form-control form-control-sm me-1" style="width: 60px;">
                                <button type="submit" class="btn btn-sm btn-outline-secondary">Lưu</button>
                            </form>
                        </td>
                        <td class="fw-bold text-danger">{{ "{:,}".format(item['price'] * item['qty']) }}đ</td>
                        <td><a href="/remove-cart/{{ item['id'] }}" class="btn btn-sm btn-outline-danger">✕</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
                <a href="/" class="btn btn-outline-dark">← Mua thêm</a>
                <span class="fs-5 fw-bold">Tổng tiền: <span class="text-danger">{{ "{:,}".format(subtotal) }}đ</span></span>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card p-3 border-0 shadow-sm bg-white rounded-3">
            <h5 class="fw-bold mb-3">Tóm Tắt</h5>
            <div class="d-flex justify-content-between mb-2"><span>Tạm tính:</span><span>{{ "{:,}".format(subtotal) }}đ</span></div>
            <div class="d-flex justify-content-between mb-2"><span>Phí ship:</span><span class="text-success fw-bold">0đ (Freeship từ Kho Q9)</span></div>
            <hr>
            <div class="d-flex justify-content-between fs-5 fw-bold mb-3"><span>Tổng:</span><span class="text-danger">{{ "{:,}".format(subtotal) }}đ</span></div>
            <a href="/checkout" class="btn btn-sage btn-lg w-100 py-2 fs-6">Đi Đến Bước Đặt Hàng & Giao Đến</a>
        </div>
    </div>
</div>

<script>
function detectAndSaveLocation() {
    if (!navigator.geolocation) {
        alert("Trình duyệt không hỗ trợ định vị GPS tự động!");
        return;
    }
    const cartDisplay = document.getElementById('cartLocDisplay');
    if (cartDisplay) cartDisplay.innerHTML = '<span class="text-primary">🛰️ Đang kết nối GPS...</span>';

    navigator.geolocation.getCurrentPosition(
        function(pos) {
            const lat = pos.coords.latitude.toFixed(6);
            const lng = pos.coords.longitude.toFixed(6);
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`)
            .then(res => res.json())
            .then(geo => {
                let addr = geo.display_name || `Tọa độ GPS: ${lat}, ${lng}`;
                postLocationUpdate(lat, lng, addr);
            })
            .catch(err => {
                postLocationUpdate(lat, lng, `Tọa độ GPS: ${lat}, ${lng}`);
            });
        },
        function(err) {
            let manualAddr = prompt("Không lấy được GPS tự động. Nhập địa chỉ giao hàng của bạn (Kho xuất hàng: Quận 9):");
            if (manualAddr) {
                postLocationUpdate("", "", manualAddr);
            }
        },
        { enableHighAccuracy: true, timeout: 8000 }
    );
}

function postLocationUpdate(lat, lng, address) {
    const fd = new FormData();
    fd.append('lat', lat);
    fd.append('lng', lng);
    fd.append('address', address);

    fetch('/api/update-location', {
        method: 'POST',
        body: fd
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert("✓ " + data.message);
            const cartDisplay = document.getElementById('cartLocDisplay');
            if (cartDisplay) {
                cartDisplay.innerHTML = '<strong class="text-dark">' + data.address + '</strong> <span class="badge bg-success bg-opacity-10 text-success ms-1">Đã lưu DB</span>';
            }
        } else {
            alert(data.message);
        }
    });
}
</script>
""")

# ==============================================================================
# TRANG CHECKOUT: SELECT KHU VỰC & ĐỊNH VỊ GPS VỊ TRÍ GIAO HÀNG
# ==============================================================================
CHECKOUT_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="row g-4">
    <div class="col-md-7">
        <div class="card p-4 border-0 shadow-sm bg-white rounded-4">
            <h4 class="fw-bold mb-3 text-dark d-flex align-items-center gap-2">
                <span>📍</span> Địa Chỉ Nhận Hàng & Định Vị GPS
            </h4>
            
            <!-- KHỐI ĐỊNH VỊ GPS VÀ HỖ TRỢ KHI KHÔNG BẬT GPS -->
            <div class="gps-box p-3 mb-4 border rounded-3 bg-light">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
                    <div class="fw-bold text-success d-flex align-items-center gap-2">
                        <span class="fs-5">🛰️</span> TỌA ĐỘ GPS GIAO HÀNG CHO SHIPPER
                    </div>
                    <div class="d-flex gap-2 flex-wrap">
                        <button type="button" class="btn btn-success btn-sm fw-bold px-3 shadow-sm" id="btnGetGPS" onclick="fetchGPSLocation()">
                            📍 1. Bật GPS vệ tinh
                        </button>
                        <button type="button" class="btn btn-outline-primary btn-sm fw-bold px-2" id="btnGetIP" onclick="fetchIPLocation()">
                            🌐 2. Định vị qua IP Mạng (Khi tắt GPS)
                        </button>
                    </div>
                </div>
                <div class="small text-muted" id="gpsStatusText">
                    💡 <strong>Không cần mở GPS:</strong> Bạn chỉ cần chọn Tỉnh, Quận, Phường và nhập Tên đường ở bên dưới — Hệ thống sẽ <strong>tự động chuyển địa chỉ thành tọa độ GPS</strong> chính xác ghim trên bản đồ cho Shipper!
                </div>
                <div id="gpsResultBadge" class="mt-2 d-none">
                    <span class="badge p-2 fs-7 border border-success bg-white text-success d-inline-flex align-items-center gap-2">
                        <span id="gpsSourceLabel">✓ Đã khóa tọa độ GPS:</span>
                        <strong id="gpsCoordsText">0.0, 0.0</strong>
                    </span>
                    <a href="#" id="gpsMapPreviewLink" target="_blank" class="btn btn-sm btn-outline-success ms-2 py-0 fw-bold">🗺️ Xem trên Google Maps ↗</a>
                </div>
            </div>

            <form action="/process-order" method="POST" id="checkoutForm">
                <!-- HIDDEN INPUTS LƯU TỌA ĐỘ GPS -->
                <input type="hidden" name="geo_lat" id="geo_lat" value="">
                <input type="hidden" name="geo_lng" id="geo_lng" value="">

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold small">Họ và tên người nhận *</label>
                        <input type="text" name="fullname" class="form-control" required value="{{ user_info['fullname'] }}" placeholder="Nguyễn Văn A">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold small">Số điện thoại *</label>
                        <input type="tel" name="phone" class="form-control" required value="{{ user_info['phone'] }}" placeholder="0901234567">
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold small">Email nhận thông báo *</label>
                    <input type="email" name="email" class="form-control" required value="{{ user_info['email'] }}" placeholder="email@example.com">
                </div>

                <!-- SELECT PHÂN CẤP KHU VỰC HÀNH CHÍNH (TOÀN QUỐC 63 TỈNH THÀNH) -->
                <div class="d-flex justify-content-between align-items-center mt-3 mb-2 flex-wrap gap-1">
                    <h6 class="fw-bold text-dark m-0">🏙️ Khu Vực Giao Hàng Toàn Quốc</h6>
                    <button type="button" class="btn btn-link btn-sm p-0 text-decoration-none small text-success fw-bold" onclick="geocodeCurrentAddress()">
                        🔍 Tự động tạo GPS từ địa chỉ bên dưới ↗
                    </button>
                </div>
                <div class="row g-2 mb-3">
                    <div class="col-md-4">
                        <label class="form-label small text-muted">1. Tỉnh / Thành phố *</label>
                        <select name="province" id="selectProvince" class="form-select form-select-sm" required onchange="handleProvinceChange()">
                            <option value="">-- Chọn Tỉnh/TP --</option>
                            <option value="Hồ Chí Minh" selected>TP. Hồ Chí Minh (Kho Quận 9)</option>
                            <option value="Hà Nội">TP. Hà Nội</option>
                            <option value="Đà Nẵng">TP. Đà Nẵng</option>
                            <option value="Bình Dương">Bình Dương</option>
                            <option value="Đồng Nai">Đồng Nai</option>
                            <option value="Cần Thơ">TP. Cần Thơ</option>
                            <option value="Hải Phòng">TP. Hải Phòng</option>
                            <option value="Bà Rịa - Vũng Tàu">Bà Rịa - Vũng Tàu</option>
                            <option value="An Giang">An Giang</option>
                            <option value="Bắc Giang">Bắc Giang</option>
                            <option value="Bắc Kạn">Bắc Kạn</option>
                            <option value="Bạc Liêu">Bạc Liêu</option>
                            <option value="Bắc Ninh">Bắc Ninh</option>
                            <option value="Bến Tre">Bến Tre</option>
                            <option value="Bình Định">Bình Định</option>
                            <option value="Bình Phước">Bình Phước</option>
                            <option value="Bình Thuận">Bình Thuận</option>
                            <option value="Cà Mau">Cà Mau</option>
                            <option value="Cao Bằng">Cao Bằng</option>
                            <option value="Đắk Lắk">Đắk Lắk</option>
                            <option value="Đắk Nông">Đắk Nông</option>
                            <option value="Điện Biên">Điện Biên</option>
                            <option value="Đồng Tháp">Đồng Tháp</option>
                            <option value="Gia Lai">Gia Lai</option>
                            <option value="Hà Giang">Hà Giang</option>
                            <option value="Hà Nam">Hà Nam</option>
                            <option value="Hà Tĩnh">Hà Tĩnh</option>
                            <option value="Hải Dương">Hải Dương</option>
                            <option value="Hậu Giang">Hậu Giang</option>
                            <option value="Hòa Bình">Hòa Bình</option>
                            <option value="Hưng Yên">Hưng Yên</option>
                            <option value="Khánh Hòa">Khánh Hòa</option>
                            <option value="Kiên Giang">Kiên Giang</option>
                            <option value="Kon Tum">Kon Tum</option>
                            <option value="Lai Châu">Lai Châu</option>
                            <option value="Lâm Đồng">Lâm Đồng</option>
                            <option value="Lạng Sơn">Lạng Sơn</option>
                            <option value="Lào Cai">Lào Cai</option>
                            <option value="Long An">Long An</option>
                            <option value="Nam Định">Nam Định</option>
                            <option value="Nghệ An">Nghệ An</option>
                            <option value="Ninh Bình">Ninh Bình</option>
                            <option value="Ninh Thuận">Ninh Thuận</option>
                            <option value="Phú Thọ">Phú Thọ</option>
                            <option value="Phú Yên">Phú Yên</option>
                            <option value="Quảng Bình">Quảng Bình</option>
                            <option value="Quảng Nam">Quảng Nam</option>
                            <option value="Quảng Ngãi">Quảng Ngãi</option>
                            <option value="Quảng Ninh">Quảng Ninh</option>
                            <option value="Quảng Trị">Quảng Trị</option>
                            <option value="Sóc Trăng">Sóc Trăng</option>
                            <option value="Sơn La">Sơn La</option>
                            <option value="Tây Ninh">Tây Ninh</option>
                            <option value="Thái Bình">Thái Bình</option>
                            <option value="Thái Nguyên">Thái Nguyên</option>
                            <option value="Thanh Hóa">Thanh Hóa</option>
                            <option value="Thừa Thiên Huế">Thừa Thiên Huế</option>
                            <option value="Tiền Giang">Tiền Giang</option>
                            <option value="Trà Vinh">Trà Vinh</option>
                            <option value="Tuyên Quang">Tuyên Quang</option>
                            <option value="Vĩnh Long">Vĩnh Long</option>
                            <option value="Vĩnh Phúc">Vĩnh Phúc</option>
                            <option value="Yên Bái">Yên Bái</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label small text-muted">2. Quận / Huyện *</label>
                        <select name="district" id="selectDistrict" class="form-select form-select-sm" required onchange="handleDistrictChange()">
                            <option value="">-- Chọn Quận/Huyện --</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label small text-muted">3. Phường / Xã *</label>
                        <select name="ward" id="selectWard" class="form-select form-select-sm" required onchange="handleWardChange()">
                            <option value="">-- Chọn Phường/Xã --</option>
                        </select>
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold small">Số nhà, Tên tòa nhà / Tên đường cụ thể *</label>
                    <input type="text" name="street_address" id="street_address" class="form-control" required placeholder="Ví dụ: 18 đường 297, Phước Long B, Phòng 302..." value="{{ user_info.get('street_address', '') }}" onblur="handleStreetBlur()">
                    <div class="form-text small text-muted">Ghi rõ số phòng/tầng nếu ở chung cư, ký túc xá hoặc phòng trọ. Hệ thống sẽ tự động tạo tọa độ GPS từ địa chỉ này.</div>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold small">Ghi chú cho Shipper (Tùy chọn)</label>
                    <input type="text" name="notes" class="form-control form-control-sm" placeholder="Ví dụ: Gọi trước khi giao 15p, để ở sảnh bảo vệ...">
                </div>

                <!-- ĐƠN VỊ VẬN CHUYỂN ĐỐI TÁC -->
                <h5 class="fw-bold mt-4 mb-1 text-dark">🚚 Gợi Ý Đơn Vị Vận Chuyển Đối Tác</h5>
                <p class="small text-muted mb-3">Đơn hàng xuất kho trực tiếp từ: <strong>Kho Trung Tâm Quận 9 (Phường Phước Long B, TP. Thủ Đức, TP.HCM)</strong></p>
                
                <div class="row g-2 mb-4">
                    <!-- GHN -->
                    <div class="col-md-6">
                        <label class="carrier-card d-flex align-items-center gap-3 p-3 border rounded-3 bg-white h-100 border-success" style="cursor: pointer;">
                            <input type="radio" name="shipping_carrier" value="Giao Hàng Nhanh (GHN Express)" checked onchange="selectCarrier(this)" class="form-check-input mt-0">
                            <div class="flex-grow-1">
                                <div class="d-flex justify-content-between align-items-center">
                                    <strong class="text-dark" style="font-size: 0.88rem;">🚚 GHN Express</strong>
                                    <span class="badge bg-success bg-opacity-10 text-success fw-bold">Freeship 0đ</span>
                                </div>
                                <div class="small text-muted mt-1" style="font-size: 0.74rem;">Đối tác chính. Giao 24h nội thành HCM, 2-3 ngày toàn quốc. Tích hợp định vị GPS.</div>
                            </div>
                        </label>
                    </div>

                    <!-- GHTK -->
                    <div class="col-md-6">
                        <label class="carrier-card d-flex align-items-center gap-3 p-3 border rounded-3 bg-white h-100" style="cursor: pointer;">
                            <input type="radio" name="shipping_carrier" value="Giao Hàng Tiết Kiệm (GHTK)" onchange="selectCarrier(this)" class="form-check-input mt-0">
                            <div class="flex-grow-1">
                                <div class="d-flex justify-content-between align-items-center">
                                    <strong class="text-dark" style="font-size: 0.88rem;">⚡ GHTK</strong>
                                    <span class="badge bg-success bg-opacity-10 text-success fw-bold">Freeship 0đ</span>
                                </div>
                                <div class="small text-muted mt-1" style="font-size: 0.74rem;">Chuyên đơn D2C, gọi hẹn giờ trước khi giao, hỗ trợ đồng kiểm.</div>
                            </div>
                        </label>
                    </div>

                    <!-- Viettel Post -->
                    <div class="col-md-6">
                        <label class="carrier-card d-flex align-items-center gap-3 p-3 border rounded-3 bg-white h-100" style="cursor: pointer;">
                            <input type="radio" name="shipping_carrier" value="Viettel Post" onchange="selectCarrier(this)" class="form-check-input mt-0">
                            <div class="flex-grow-1">
                                <div class="d-flex justify-content-between align-items-center">
                                    <strong class="text-dark" style="font-size: 0.88rem;">🦅 Viettel Post</strong>
                                    <span class="badge bg-success bg-opacity-10 text-success fw-bold">Freeship 0đ</span>
                                </div>
                                <div class="small text-muted mt-1" style="font-size: 0.74rem;">Mạng lưới phủ 100% huyện xã toàn quốc, vùng sâu vùng xa an tâm.</div>
                            </div>
                        </label>
                    </div>

                    <!-- AhaMove Hỏa Tốc -->
                    <div class="col-md-6">
                        <label class="carrier-card d-flex align-items-center gap-3 p-3 border rounded-3 bg-white h-100" style="cursor: pointer;">
                            <input type="radio" name="shipping_carrier" value="Hỏa Tốc 1-2H (AhaMove / GrabExpress)" onchange="selectCarrier(this)" class="form-check-input mt-0">
                            <div class="flex-grow-1">
                                <div class="d-flex justify-content-between align-items-center">
                                    <strong class="text-dark" style="font-size: 0.88rem;">🛵 Hỏa Tốc 1-2H (AhaMove)</strong>
                                    <span class="badge bg-warning bg-opacity-10 text-warning-emphasis fw-bold">+15.000đ</span>
                                </div>
                                <div class="small text-muted mt-1" style="font-size: 0.74rem;">Giao siêu tốc từ Kho Q9 tận phòng trọ/nhà riêng trong 1 - 2 giờ (TP.HCM).</div>
                            </div>
                        </label>
                    </div>
                </div>

                <!-- PHƯƠNG THỨC THANH TOÁN -->
                <h5 class="fw-bold mt-4 mb-2 text-dark">Phương Thức Thanh Toán</h5>
                
                <div class="form-check p-3 border rounded-3 mb-2 bg-light border-success">
                    <input class="form-check-input ms-0 me-2" type="radio" name="payment_method" id="pay_qr" value="VIETQR" checked onchange="toggleQRPaymentPreview(true)">
                    <label class="form-check-label fw-bold text-success" for="pay_qr">
                        ⚡ Chuyển khoản VietQR (Giữ đơn 24h — Khớp đơn sang Đang chuẩn bị)
                    </label>
                    <div class="small text-muted mt-1 ps-4">
                        Quét mã VietQR bằng App Ngân hàng bất kỳ (MBBank, Vietcombank, Techcombank, MoMo...).
                    </div>

                    <!-- MÃ QR THANH TOÁN VIETQR TRỰC TIẾP TRÊN TRANG CHECKOUT -->
                    <div id="checkoutQRPreviewBox" class="mt-3 p-3 bg-white border rounded-3 text-center shadow-sm">
                        <div class="d-inline-flex align-items-center gap-2 px-3 py-1 bg-success bg-opacity-10 text-success rounded-pill small fw-bold mb-2">
                            <span>⚡ Quét Mã QR VietQR NAPAS 24/7 Ngay Tại Đây</span>
                        </div>
                        <div class="my-2">
                            <img id="checkoutQRImg" 
                                 src="https://img.vietqr.io/image/{{ bank_config['bank_code'] }}-{{ bank_config['account_number'] }}-compact2.png?amount={{ subtotal }}&addInfo=NEPNHO%20DAT%20HANG&accountName={{ bank_config['account_holder'] | urlencode }}" 
                                 class="img-fluid rounded border shadow-sm mx-auto" 
                                 style="max-height: 230px;" 
                                 alt="Mã QR Thanh Toán VietQR">
                        </div>
                        <div class="small text-muted mt-2">
                            <strong>{{ bank_config['bank_name'] }}</strong> | STK: <strong class="text-primary">{{ bank_config['account_number'] }}</strong> | Chủ TK: <strong>{{ bank_config['account_holder'] }}</strong>
                        </div>
                        <div class="alert alert-info py-2 px-3 mt-2 mb-0 small text-start">
                            ℹ️ <strong>Mẹo:</strong> Bạn có thể quét mã QR ngay bây giờ hoặc bấm nút <strong>"Xác Nhận Đặt Hàng"</strong> bên dưới — Hệ thống sẽ tạo mã QR riêng khớp đúng Mã Đơn Hàng và tự động nhảy khi nhận tiền!
                        </div>
                    </div>
                </div>

                <div class="form-check p-3 border rounded-3 mb-4 bg-light">
                    <input class="form-check-input ms-0 me-2" type="radio" name="payment_method" id="pay_cod" value="COD" onchange="toggleQRPaymentPreview(false)">
                    <label class="form-check-label fw-bold text-dark" for="pay_cod">
                        📦 Thanh toán khi nhận hàng (COD)
                    </label>
                </div>

                <button type="submit" class="btn btn-sage btn-lg w-100 py-3 fs-6 shadow-sm fw-bold">
                    ✓ Xác Nhận Đặt Hàng Ngay
                </button>
            </form>
        </div>
    </div>

    <!-- TÓM TẮT ĐƠN HÀNG -->
    <div class="col-md-5">
        <div class="card p-3 border-0 shadow-sm bg-white rounded-4 sticky-top" style="top: 85px;">
            <h5 class="fw-bold mb-3 text-dark">Đơn Hàng ({{ cart|length }} món)</h5>
            <div class="overflow-auto pe-1" style="max-height: 280px;">
                {% for item in cart %}
                <div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom">
                    <div>
                        <div class="fw-bold small text-dark">{{ item['name'] }}</div>
                        <div class="text-muted small">Số lượng: x{{ item['qty'] }}</div>
                    </div>
                    <span class="fw-bold text-danger">{{ "{:,}".format(item['price'] * item['qty']) }}đ</span>
                </div>
                {% endfor %}
            </div>
            
            <div class="mt-3 pt-2">
                <input type="hidden" id="subtotalValue" value="{{ subtotal }}">
                <div class="d-flex justify-content-between mb-1 small"><span class="text-muted">Tiền hàng:</span><span>{{ "{:,}".format(subtotal) }}đ</span></div>
                <div class="d-flex justify-content-between mb-1 small"><span class="text-muted">Đơn vị vận chuyển:</span><strong id="carrierSelectedText" class="text-dark">GHN Express</strong></div>
                <div class="d-flex justify-content-between mb-2 small"><span class="text-muted">Phí vận chuyển:</span><span id="shipFeeText" class="text-success fw-bold">0đ (Freeship)</span></div>
                <hr class="my-2">
                <div class="d-flex justify-content-between fs-5 fw-bold">
                    <span>Tổng thanh toán:</span>
                    <span class="text-danger" id="totalPaymentText">{{ "{:,}".format(subtotal) }}đ</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// DỮ LIỆU ĐỊA CHÍNH KHU VỰC MẪU (VIETNAM ADMINISTRATIVE DATA)
const REGION_DATA = {
    "Hồ Chí Minh": {
        "Quận 9 (Kho Trung Tâm)": ["Phường Phước Long B (Kho Nếp Nhỏ)", "Phường Phước Long A", "Phường Tăng Nhơn Phú A", "Phường Tăng Nhơn Phú B", "Phường Hiệp Phú", "Phường Long Thạnh Mỹ"],
        "Quận 1": ["Phường Bến Nghé", "Phường Bến Thành", "Phường Cầu Kho", "Phường Đa Kao", "Phường Tân Định"],
        "Quận 5": ["Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5", "Phường 7", "Phường 10"],
        "Quận 7": ["Phường Tân Phong", "Phường Tân Phú", "Phường Phú Mỹ", "Phường Tân Hưng"],
        "Quận Bình Thạnh": ["Phường 25", "Phường 26", "Phường 19", "Phường 21", "Phường 15"],
        "TP. Thủ Đức": ["Phường Linh Trung", "Phường Hiệp Phú", "Phường Thảo Điền", "Phường An Phú"]
    },
    "Hà Nội": {
        "Quận Cầu Giấy": ["Phường Dịch Vọng", "Phường Quan Hoa", "Phường Mai Dịch", "Phường Nghĩa Đô"],
        "Quận Đống Đa": ["Phường Ô Chợ Dừa", "Phường Láng Hạ", "Phường Kim Liên", "Phường Văn Miếu"],
        "Quận Hoàn Kiếm": ["Phường Hàng Trống", "Phường Tràng Tiền", "Phường Hàng Bạc"]
    },
    "Đà Nẵng": {
        "Quận Hải Châu": ["Phường Thạch Thang", "Phường Hải Châu 1", "Phường Bình Thuận"],
        "Quận Sơn Trà": ["Phường An Hải Bắc", "Phường Phước Mỹ"]
    },
    "Bình Dương": {
        "TP. Thủ Dầu Một": ["Phường Phú Hòa", "Phường Phú Lợi", "Phường Hiệp Thành"],
        "TP. Dĩ An": ["Phường Dĩ An", "Phường Đông Hòa", "Phường Tân Đông Hiệp"]
    },
    "Đồng Nai": {
        "TP. Biên Hòa": ["Phường Tân Phong", "Phường Quyết Thắng", "Phường Trảng Dài"]
    },
    "Cần Thơ": {
        "Quận Ninh Kiều": ["Phường An Khánh", "Phường Xuân Khánh", "Phường Hưng Lợi"]
    },
    "Hải Phòng": {
        "Quận Hồng Bàng": ["Phường Hoàng Văn Thụ", "Phường Minh Khai"]
    },
    "Khác": {
        "Khu vực khác": ["Trung tâm"]
    }
};

function selectCarrier(radio) {
    document.querySelectorAll('.carrier-card').forEach(card => {
        card.classList.remove('border-success', 'bg-success-subtle');
    });
    let card = radio.closest('.carrier-card');
    if (card) {
        card.classList.add('border-success');
    }
    let val = radio.value;
    let subtotal = parseInt(document.getElementById('subtotalValue').value) || 0;
    let shipFee = 0;
    let carrierName = 'GHN Express';

    if (val.includes('Hỏa Tốc') || val.includes('AhaMove')) {
        shipFee = 15000;
        carrierName = 'AhaMove Hỏa Tốc (1-2h)';
        document.getElementById('shipFeeText').innerHTML = '<span class="text-warning-emphasis fw-bold">+15.000đ</span>';
    } else if (val.includes('GHTK')) {
        carrierName = 'GHTK Tiết Kiệm';
        document.getElementById('shipFeeText').innerHTML = '<span class="text-success fw-bold">0đ (Freeship)</span>';
    } else if (val.includes('Viettel')) {
        carrierName = 'Viettel Post';
        document.getElementById('shipFeeText').innerHTML = '<span class="text-success fw-bold">0đ (Freeship)</span>';
    } else {
        carrierName = 'GHN Express';
        document.getElementById('shipFeeText').innerHTML = '<span class="text-success fw-bold">0đ (Freeship)</span>';
    }

    document.getElementById('carrierSelectedText').innerText = carrierName;
    let total = subtotal + shipFee;
    document.getElementById('totalPaymentText').innerText = total.toLocaleString('vi-VN') + 'đ';
}

function handleProvinceChange() {
    let province = document.getElementById('selectProvince').value;
    let distSelect = document.getElementById('selectDistrict');
    let wardSelect = document.getElementById('selectWard');
    
    distSelect.innerHTML = '<option value="">-- Chọn Quận/Huyện --</option>';
    wardSelect.innerHTML = '<option value="">-- Chọn Phường/Xã --</option>';

    if (province && REGION_DATA[province]) {
        for (let dist in REGION_DATA[province]) {
            distSelect.innerHTML += `<option value="${dist}">${dist}</option>`;
        }
    }
}

function handleDistrictChange() {
    let province = document.getElementById('selectProvince').value;
    let dist = document.getElementById('selectDistrict').value;
    let wardSelect = document.getElementById('selectWard');
    
    wardSelect.innerHTML = '<option value="">-- Chọn Phường/Xã --</option>';

    if (province && dist && REGION_DATA[province] && REGION_DATA[province][dist]) {
        REGION_DATA[province][dist].forEach(w => {
            wardSelect.innerHTML += `<option value="${w}">${w}</option>`;
        });
    }
}

function handleWardChange() {
    geocodeCurrentAddress();
}

function handleStreetBlur() {
    geocodeCurrentAddress();
}

function toggleQRPaymentPreview(show) {
    let box = document.getElementById('checkoutQRPreviewBox');
    if (box) {
        box.style.display = show ? 'block' : 'none';
    }
}

// Khởi tạo mặc định Quận/Huyện cho TP.HCM khi tải trang
window.addEventListener('DOMContentLoaded', () => {
    handleProvinceChange();
});

// HÀM BÓC TÁCH CẤP ĐỊA CHÍNH VIỆT NAM CHUẨN XÁC TỪ DỮ LIỆU NOMINATIM
function parseVnAddressNominatim(data) {
    let addr = data.address || {};
    let dispParts = (data.display_name || '').split(',').map(s => s.trim());
    
    // 1. TỈNH / THÀNH PHỐ
    let prov = addr.city || addr.state || addr.province || '';
    if (!prov) {
        for (let p of dispParts) {
            if (/Hồ Chí Minh|Hà Nội|Đà Nẵng|Bình Dương|Đồng Nai|Cần Thơ|Hải Phòng/i.test(p)) {
                prov = p; break;
            }
        }
    }
    if (!prov) prov = 'Hồ Chí Minh';

    // 2. PHƯỜNG / XÃ (Ward): BẮT BUỘC là cấp Phường/Xã (Tuyệt đối không lấy Khu phố làm Phường!)
    let ward = '';
    let checkWards = [addr.ward, addr.suburb, addr.quarter, addr.village];
    for (let w of checkWards) {
        if (w && /^(Phường|Xã|Thị trấn)\b/i.test(w)) {
            ward = w;
            break;
        }
    }
    if (!ward) {
        for (let p of dispParts) {
            if (/^(Phường|Xã|Thị trấn)\b/i.test(p)) {
                ward = p;
                break;
            }
        }
    }
    if (!ward && addr.suburb && !/^(Quận|Huyện|Thành phố|TP[.])\b/i.test(addr.suburb)) {
        ward = addr.suburb.startsWith('Phường') ? addr.suburb : ('Phường ' + addr.suburb);
    }

    // 3. QUẬN / HUYỆN (District): BẮT BUỘC là Quận/Huyện (TUYỆT ĐỐI không lấy chuỗi có chữ "Phường"!)
    let dist = '';
    let checkDists = [addr.city_district, addr.district, addr.county, addr.town];
    for (let d of checkDists) {
        if (d && !/^(Phường|Xã|Thị trấn)\b/i.test(d)) {
            dist = d;
            break;
        }
    }
    if (!dist) {
        for (let p of dispParts) {
            if (/^(Quận|Huyện|Thị xã|TP[.]|Thành phố Thủ Đức)\b/i.test(p) && !/^(Phường|Xã)\b/i.test(p)) {
                dist = p;
                break;
            }
        }
    }

    // Phục hồi Quận/Huyện chính xác nếu Nominatim chỉ trả về Phường mà thiếu Quận
    let combinedText = (ward + ' ' + (data.display_name || '')).toLowerCase();
    if (!dist || /^(Phường|Xã)\b/i.test(dist)) {
        if (/phước long|tăng nhơn phú|hiệp phú|long thạnh mỹ|long phước|long trường|phú hữu|tân phú/i.test(combinedText)) {
            dist = "Quận 9 (Kho Trung Tâm)";
            if (!ward || ward === 'Phường Phước Long') ward = 'Phường Phước Long B (Kho Nếp Nhỏ)';
        } else if (/bến nghé|bến thành|đa kao|tân định|cầu kho/i.test(combinedText)) {
            dist = "Quận 1";
        } else if (/linh trung|linh tây|linh chiểu|tam bình|thảo điền|an phú/i.test(combinedText)) {
            dist = "TP. Thủ Đức";
        } else if (/bình thạnh/i.test(combinedText)) {
            dist = "Quận Bình Thạnh";
        } else if (/quận 5|chợ lớn/i.test(combinedText)) {
            dist = "Quận 5";
        } else if (/quận 7|tân phong|phú mỹ/i.test(combinedText)) {
            dist = "Quận 7";
        } else {
            dist = "Quận 9 (Kho Trung Tâm)";
        }
    }

    // 4. SỐ NHÀ, TÊN ĐƯỜNG: Khu phố 19, Tổ, Ấp đưa vào đây, không để ở Phường!
    let road = addr.road || '';
    let houseNum = addr.house_number || '';
    let subUnit = '';
    if (addr.neighbourhood && /^(Khu phố|Ấp|Tổ|Thôn|Xóm)\b/i.test(addr.neighbourhood)) {
        subUnit = addr.neighbourhood;
    }
    for (let p of dispParts) {
        if (/^(Khu phố|Ấp|Tổ|Thôn|Xóm)\b/i.test(p) && !subUnit) {
            subUnit = p;
        }
    }

    let streetParts = [];
    if (houseNum) streetParts.push(houseNum);
    if (road) streetParts.push(road);
    if (subUnit && !road.includes(subUnit)) streetParts.push(subUnit);

    let street = streetParts.join(', ');
    if (!street) {
        street = dispParts.slice(0, 2).filter(p => !p.includes(prov) && !p.includes(dist) && !p.includes(ward)).join(', ');
    }

    return { prov, dist, ward, street };
}

// HÀM ÁP DỤNG ĐỊA CHỈ & QUẬN/HUYỆN/PHƯỜNG VÀO FORM RÕ RÀNG KHÔNG GỘP
function applyLocationToForm(provinceName, districtName, wardName, streetName, lat, lng) {
    let provSelect = document.getElementById('selectProvince');
    let distSelect = document.getElementById('selectDistrict');
    let wardSelect = document.getElementById('selectWard');
    let streetInput = document.getElementById('street_address');

    // 1. Tự động chọn Tỉnh/Thành phố
    if (provinceName) {
        let cleanProv = provinceName.replace(/Thành phố|Tỉnh|TP[.]/gi, '').trim().toLowerCase();
        for (let i = 0; i < provSelect.options.length; i++) {
            let optClean = provSelect.options[i].text.replace(/Thành phố|Tỉnh|TP[.]/gi, '').trim().toLowerCase();
            if (cleanProv.includes(optClean) || optClean.includes(cleanProv)) {
                provSelect.selectedIndex = i;
                handleProvinceChange();
                break;
            }
        }
    }

    // 2. Tự động gán đúng Quận/Huyện (TUYỆT ĐỐI KHÔNG GỘP PHƯỜNG VÀO ĐÂY)
    if (districtName) {
        let foundDist = false;
        let cleanDist = districtName.replace(/Quận|Huyện|Thành phố|Thị xã|TP[.]/gi, '').trim().toLowerCase();
        
        for (let i = 0; i < distSelect.options.length; i++) {
            let optClean = distSelect.options[i].text.replace(/Quận|Huyện|Thành phố|Thị xã|TP[.]/gi, '').trim().toLowerCase();
            if (cleanDist.includes(optClean) || optClean.includes(cleanDist) || distSelect.options[i].value.toLowerCase().includes(cleanDist)) {
                distSelect.selectedIndex = i;
                foundDist = true;
                handleDistrictChange();
                break;
            }
        }
        if (!foundDist) {
            let newDistOption = new Option(districtName, districtName, true, true);
            distSelect.add(newDistOption);
            distSelect.value = districtName;
            handleDistrictChange();
        }
    }

    // 3. Tự động gán đúng Phường/Xã
    if (wardName) {
        let foundWard = false;
        let cleanWard = wardName.replace(/Phường|Xã|Thị trấn/gi, '').trim().toLowerCase();
        
        for (let i = 0; i < wardSelect.options.length; i++) {
            let optClean = wardSelect.options[i].text.replace(/Phường|Xã|Thị trấn/gi, '').trim().toLowerCase();
            if (cleanWard.includes(optClean) || optClean.includes(cleanWard)) {
                wardSelect.selectedIndex = i;
                foundWard = true;
                break;
            }
        }
        if (!foundWard) {
            let newWardOption = new Option(wardName, wardName, true, true);
            wardSelect.add(newWardOption);
            wardSelect.value = wardName;
        }
    }

    // 4. Cập nhật Số nhà / Tên đường (kèm Khu phố nếu có)
    if (streetName && (!streetInput.value || streetInput.value.trim() === '')) {
        streetInput.value = streetName;
    }

    // 5. Tự động lưu địa chỉ và tọa độ GPS vào cơ sở dữ liệu
    let fullAddr = `${streetInput.value || streetName || ''}, ${wardSelect.value || ''}, ${distSelect.value || ''}, ${provSelect.value || ''}`.replace(/^, |, $/g, '');
    let formData = new FormData();
    formData.append('lat', lat);
    formData.append('lng', lng);
    formData.append('address', fullAddr);

    fetch('/api/update-location', {
        method: 'POST',
        body: formData
    }).catch(e => console.log('Auto save location error:', e));
}

// TÍNH NĂNG 1: ĐỊNH VỊ QUA IP MẠNG / WIFI (KHI KHÁCH KHÔNG BẬT GPS)
function fetchIPLocation() {
    let statusText = document.getElementById('gpsStatusText');
    let btn = document.getElementById('btnGetIP');
    if (btn) btn.disabled = true;
    statusText.innerHTML = '<span class="text-primary">⏳ Đang tự động định vị qua địa chỉ IP mạng Internet / Wifi (không cần mở GPS)...</span>';

    fetch('https://ipapi.co/json/')
        .then(res => res.json())
        .then(data => {
            if (btn) btn.disabled = false;
            let lat = data.latitude ? parseFloat(data.latitude).toFixed(6) : '10.824120';
            let lng = data.longitude ? parseFloat(data.longitude).toFixed(6) : '106.770976';
            let city = data.city || data.region || 'Hồ Chí Minh';

            document.getElementById('geo_lat').value = lat;
            document.getElementById('geo_lng').value = lng;
            document.getElementById('gpsCoordsText').innerText = `${lat}, ${lng}`;
            document.getElementById('gpsMapPreviewLink').href = `https://www.google.com/maps?q=${lat},${lng}`;
            document.getElementById('gpsResultBadge').classList.remove('d-none');
            document.getElementById('gpsSourceLabel').innerText = '🌐 Đã định vị qua IP mạng:';

            // Tự động khớp Tỉnh/Thành phố
            let provSelect = document.getElementById('selectProvince');
            let cleanCity = city.toLowerCase();
            for (let i = 0; i < provSelect.options.length; i++) {
                let optText = provSelect.options[i].text.toLowerCase();
                if (optText.includes('hồ chí minh') && (cleanCity.includes('ho chi minh') || cleanCity.includes('hcm') || cleanCity.includes('saigon'))) {
                    provSelect.selectedIndex = i;
                    handleProvinceChange();
                    break;
                } else if (cleanCity.includes(optText) || optText.includes(cleanCity)) {
                    provSelect.selectedIndex = i;
                    handleProvinceChange();
                    break;
                }
            }
            statusText.innerHTML = `<span class="text-success fw-bold">✓ Đã định vị qua IP mạng: ${city} (${lat}, ${lng}). Bạn chỉ cần chọn Quận & Phường bên dưới!</span>`;
        })
        .catch(() => {
            if (btn) btn.disabled = false;
            fetch('https://freeipapi.com/api/json')
                .then(r => r.json())
                .then(d => {
                    let lat = d.latitude ? parseFloat(d.latitude).toFixed(6) : '10.824120';
                    let lng = d.longitude ? parseFloat(d.longitude).toFixed(6) : '106.770976';
                    document.getElementById('geo_lat').value = lat;
                    document.getElementById('geo_lng').value = lng;
                    document.getElementById('gpsCoordsText').innerText = `${lat}, ${lng}`;
                    document.getElementById('gpsMapPreviewLink').href = `https://www.google.com/maps?q=${lat},${lng}`;
                    document.getElementById('gpsResultBadge').classList.remove('d-none');
                    document.getElementById('gpsSourceLabel').innerText = '🌐 Đã định vị qua IP mạng:';
                    statusText.innerHTML = `<span class="text-success fw-bold">✓ Đã định vị qua IP mạng: ${d.cityName || 'TP. Hồ Chí Minh'}. Vui lòng chọn Quận/Phường bên dưới!</span>`;
                })
                .catch(() => {
                    statusText.innerHTML = '<span class="text-info">💡 Bạn chỉ cần chọn Quận & Phường ở dưới — Hệ thống sẽ tự động ghim tọa độ GPS cho Shipper!</span>';
                });
        });
}

// TÍNH NĂNG 2: TỰ ĐỘNG CHUYỂN ĐỊA CHỈ THÀNH TỌA ĐỘ GPS (KHI KHÔNG MỞ GPS)
function geocodeCurrentAddress() {
    let provSelect = document.getElementById('selectProvince');
    let distSelect = document.getElementById('selectDistrict');
    let wardSelect = document.getElementById('selectWard');
    let streetInput = document.getElementById('street_address');

    let prov = provSelect.value ? provSelect.options[provSelect.selectedIndex].text.split('(')[0].trim() : '';
    let dist = distSelect.value ? distSelect.options[distSelect.selectedIndex].text.split('(')[0].trim() : '';
    let ward = wardSelect.value ? wardSelect.options[wardSelect.selectedIndex].text.split('(')[0].trim() : '';
    let street = streetInput.value.trim();

    if (!prov || (!dist && !ward && !street)) return;

    let queryAddress = [street, ward, dist, prov, 'Việt Nam'].filter(Boolean).join(', ');
    let statusText = document.getElementById('gpsStatusText');

    statusText.innerHTML = '<span class="text-primary">⏳ Đang tự động chuyển địa chỉ thành tọa độ GPS vệ tinh...</span>';

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryAddress)}&countrycodes=vn&limit=1`)
        .then(res => res.json())
        .then(results => {
            if (results && results.length > 0) {
                let lat = parseFloat(results[0].lat).toFixed(6);
                let lng = parseFloat(results[0].lon).toFixed(6);
                
                document.getElementById('geo_lat').value = lat;
                document.getElementById('geo_lng').value = lng;
                document.getElementById('gpsCoordsText').innerText = `${lat}, ${lng}`;
                document.getElementById('gpsMapPreviewLink').href = `https://www.google.com/maps?q=${lat},${lng}`;
                document.getElementById('gpsResultBadge').classList.remove('d-none');
                document.getElementById('gpsSourceLabel').innerText = '✓ Đã tạo GPS từ địa chỉ:';

                statusText.innerHTML = `<span class="text-success fw-bold">✓ Đã định vị vệ tinh thành công từ địa chỉ: ${lat}, ${lng}</span>`;

                let fullAddr = `${street}, ${ward}, ${dist}, ${prov}`.replace(/^, |, $/g, '');
                let formData = new FormData();
                formData.append('lat', lat);
                formData.append('lng', lng);
                formData.append('address', fullAddr);
                fetch('/api/update-location', { method: 'POST', body: formData }).catch(e => {});
            } else {
                let broadQuery = [ward, dist, prov, 'Việt Nam'].filter(Boolean).join(', ');
                fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(broadQuery)}&countrycodes=vn&limit=1`)
                    .then(r => r.json())
                    .then(resBroad => {
                        if (resBroad && resBroad.length > 0) {
                            let lat = parseFloat(resBroad[0].lat).toFixed(6);
                            let lng = parseFloat(resBroad[0].lon).toFixed(6);
                            document.getElementById('geo_lat').value = lat;
                            document.getElementById('geo_lng').value = lng;
                            document.getElementById('gpsCoordsText').innerText = `${lat}, ${lng}`;
                            document.getElementById('gpsMapPreviewLink').href = `https://www.google.com/maps?q=${lat},${lng}`;
                            document.getElementById('gpsResultBadge').classList.remove('d-none');
                            document.getElementById('gpsSourceLabel').innerText = '✓ Đã tạo GPS khu vực:';
                            statusText.innerHTML = `<span class="text-success">✓ Đã định vị khu vực ${ward}, ${dist} (${lat}, ${lng})</span>`;
                        }
                    });
            }
        })
        .catch(err => console.log('Geocoding error:', err));
}

// TÍNH NĂNG 3: BẬT GPS VỆ TINH TRỰC TIẾP (KÈM BÓC TÁCH CHUẨN XÁC)
function fetchGPSLocation() {
    let statusText = document.getElementById('gpsStatusText');
    let btn = document.getElementById('btnGetGPS');

    if (!navigator.geolocation) {
        statusText.innerHTML = '<span class="text-danger">⚠️ Trình duyệt không hỗ trợ GPS, đang chuyển sang định vị IP...</span>';
        fetchIPLocation();
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '⏳ Đang định vị vệ tinh...';
    statusText.innerText = 'Đang nhận diện vị trí GPS của bạn (vui lòng Cho phép / Allow truy cập vị trí)...';

    navigator.geolocation.getCurrentPosition(
        (position) => {
            let lat = position.coords.latitude.toFixed(6);
            let lng = position.coords.longitude.toFixed(6);
            
            document.getElementById('geo_lat').value = lat;
            document.getElementById('geo_lng').value = lng;

            document.getElementById('gpsCoordsText').innerText = `${lat}, ${lng}`;
            document.getElementById('gpsMapPreviewLink').href = `https://www.google.com/maps?q=${lat},${lng}`;
            document.getElementById('gpsResultBadge').classList.remove('d-none');
            document.getElementById('gpsSourceLabel').innerText = '✓ Đã khóa tọa độ GPS:';
            
            statusText.innerHTML = '<span class="text-success fw-bold">✓ Định vị GPS thành công! Đang bóc tách Tỉnh / Quận / Phường rõ ràng...</span>';
            btn.innerHTML = '✓ Đã nhận diện GPS';
            btn.classList.replace('btn-success', 'btn-outline-success');

            // Reverse Geocoding chuẩn xác bằng OpenStreetMap Nominatim
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`)
                .then(res => res.json())
                .then(data => {
                    if (data) {
                        let parsed = parseVnAddressNominatim(data);
                        applyLocationToForm(parsed.prov, parsed.dist, parsed.ward, parsed.street, lat, lng);
                        statusText.innerHTML = `<span class="text-success fw-bold">✓ Đã xác định: ${parsed.ward}, ${parsed.dist}, ${parsed.prov} (${lat}, ${lng})</span>`;
                    }
                })
                .catch(() => {
                    statusText.innerHTML = '<span class="text-success">✓ Đã khóa tọa độ GPS cho Shipper!</span>';
                });
        },
        (error) => {
            btn.disabled = false;
            btn.innerHTML = '📍 Thử lại GPS vệ tinh';
            let msg = 'Thiết bị chưa bật GPS hoặc bạn đã từ chối quyền. ';
            statusText.innerHTML = `<span class="text-warning">⚠️ ${msg} Đang tự động chuyển sang định vị qua IP mạng...</span>`;
            // TỰ ĐỘNG FALLBACK SANG IP MẠNG KHI TẮT GPS!
            setTimeout(fetchIPLocation, 500);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
}
</script>
""")

# ==============================================================================
# CỔNG THANH TOÁN VIETQR (ĐẾM LÙI 24H & CHUYỂN TRẠNG THÁI)
# ==============================================================================
PAYMENT_GATEWAY_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="row justify-content-center">
    <div class="col-lg-8 col-xl-7">
        <div class="card p-4 p-md-5 border-0 shadow-sm bg-white rounded-4 text-center">
            {% if is_expired %}
            <div class="alert alert-danger p-4 rounded-4 shadow-sm">
                <div class="fs-1 mb-2">⚠️</div>
                <h4 class="fw-bold text-danger">Đơn hàng #{{ order['id'] }} đã bị TỰ HỦY!</h4>
                <p class="mb-3">Đã quá thời hạn 24 giờ kể từ lúc tạo đơn chưa nhận được chuyển khoản. Tồn kho đã được hoàn lại.</p>
                <a href="/" class="btn btn-sage">Đặt hàng lại</a>
            </div>
            {% else %}
            <div class="d-inline-flex align-items-center justify-content-center gap-2 px-3 py-1 bg-warning bg-opacity-10 text-dark border border-warning rounded-pill mb-3 mx-auto small fw-bold">
                ⏳ ĐANG CHỜ THANH TOÁN CHUYỂN KHOẢN (24 GIỜ)
            </div>
            <h3 class="fw-bold text-dark mb-1">Cổng Thanh Toán VietQR Tự Động</h3>
            <p class="text-muted small mb-3">Mã đơn: <strong class="text-primary fs-6">#{{ order['id'] }}</strong> | Quét mã bằng App Ngân hàng</p>

            <div class="bg-light p-3 rounded-3 d-inline-flex flex-column align-items-center gap-1 mb-3 border">
                <div class="text-muted small">Thời gian còn lại để chuyển khoản:</div>
                <div class="badge bg-danger fs-5 font-monospace px-3 py-2" id="countdown24h">Đang tính...</div>
            </div>

            <!-- TRẠNG THÁI REAL-TIME TỰ ĐỘNG LẮNG NGHE BIẾN ĐỘNG TÀI KHOẢN -->
            <div id="paymentStatusBox" class="my-3">
                <div class="d-inline-flex align-items-center gap-2 px-3 py-2 bg-primary bg-opacity-10 text-primary border border-primary rounded-pill small fw-bold">
                    <span class="spinner-grow spinner-grow-sm text-primary" role="status"></span>
                    <span>Đang chờ chuyển khoản... Hệ thống tự động kiểm tra mỗi 2 giây</span>
                </div>
            </div>

            <div class="card p-3 my-2 border shadow-sm mx-auto" style="max-width: 380px; border-radius: 16px;">
                <span class="badge bg-success-subtle text-success border border-success px-2 py-1 small mb-2">⚡ VietQR Chuẩn NAPAS 24/7</span>
                <img src="https://img.vietqr.io/image/{{ bank_config['bank_code'] }}-{{ bank_config['account_number'] }}-{{ bank_config.get('qr_template', 'compact2') }}.png?amount={{ order['total'] }}&addInfo=NEPNHO%20{{ order['id'] }}&accountName={{ bank_config['account_holder'] | urlencode }}" 
                     class="img-fluid rounded border my-2 mx-auto" style="max-height: 270px;" alt="VietQR">
            </div>

            <div class="small text-start bg-light p-3 rounded-3 mt-3 border mx-auto" style="max-width: 480px;">
                <div class="d-flex justify-content-between py-1 border-bottom"><span class="text-muted">Ngân hàng:</span><strong>{{ bank_config['bank_name'] }}</strong></div>
                <div class="d-flex justify-content-between py-1 border-bottom"><span class="text-muted">STK:</span><strong class="text-primary">{{ bank_config['account_number'] }}</strong></div>
                <div class="d-flex justify-content-between py-1 border-bottom"><span class="text-muted">Chủ TK:</span><strong>{{ bank_config['account_holder'] }}</strong></div>
                <div class="d-flex justify-content-between py-1 border-bottom"><span class="text-muted">Đơn vị vận chuyển:</span><strong class="text-dark">🚚 {{ order.get('shipping_carrier', 'GHN Express') }}</strong></div>
                <div class="d-flex justify-content-between py-1 border-bottom"><span class="text-muted">Số tiền:</span><strong class="text-danger">{{ "{:,}".format(order['total']) }}đ</strong></div>
                <div class="d-flex justify-content-between py-1"><span class="text-muted">Nội dung:</span><strong class="bg-warning px-2 rounded">NEPNHO {{ order['id'] }}</strong></div>
            </div>

            <div class="mt-4 mx-auto" style="max-width: 480px;">
                <form action="/confirm-payment/{{ order['id'] }}" method="POST">
                    <button type="submit" class="btn btn-success btn-lg w-100 py-3 fs-6 shadow fw-bold">
                        ✅ TÔI ĐÃ HOÀN TẤT CHUYỂN KHOẢN (BẤM THỦ CÔNG)
                    </button>
                </form>
                <div class="text-muted small mt-2">Hệ thống sẽ tự động chuyển trang khi tài khoản nhận tiền hoặc bạn bấm xác nhận.</div>
            </div>

            <!-- NÚT MÔ PHỎNG DÀNH CHO DEMO / CHẤM ĐỒ ÁN -->
            <div class="mt-3 p-3 bg-light rounded-3 border border-dashed mx-auto text-center" style="max-width: 480px;">
                <div class="small text-muted mb-2">⚡ <strong>Chế độ Demo / Test:</strong> Mô phỏng App MBBank của Admin nhận được tiền (nghe chuông Ting Ting và tự động chuyển trang):</div>
                <button type="button" class="btn btn-sm btn-outline-success fw-bold px-3 py-1" onclick="simulateBankTransfer()">
                    💸 Thử Ngay: Giả Lập Ngân Hàng Báo Có Tiền (Ting Ting) ↗
                </button>
            </div>
            {% endif %}
        </div>
    </div>
</div>

<script>
{% if not is_expired %}
let expiresAt = {{ order.get('expires_at_timestamp', 0) * 1000 }};
let timerDisplay = document.getElementById('countdown24h');
function updateTimer() {
    let distance = expiresAt - new Date().getTime();
    if (distance <= 0) {
        timerDisplay.innerText = "00:00:00 (Hết hạn)";
        window.location.reload();
        return;
    }
    let h = Math.floor(distance / (1000 * 60 * 60)).toString().padStart(2, '0');
    let m = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)).toString().padStart(2, '0');
    let s = Math.floor((distance % (1000 * 60)) / 1000).toString().padStart(2, '0');
    timerDisplay.innerText = `${h}h ${m}m ${s}s`;
}
updateTimer();
setInterval(updateTimer, 1000);

// Phát âm thanh chuông "Ting Ting" ngân hàng bằng Web Audio API
function playTingTingSound() {
    try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        const now = ctx.currentTime;
        
        // Ting 1 (1318.5 Hz)
        const osc1 = ctx.createOscillator();
        const gain1 = ctx.createGain();
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(1318.5, now);
        gain1.gain.setValueAtTime(0.35, now);
        gain1.gain.exponentialRampToValueAtTime(0.0001, now + 0.4);
        osc1.connect(gain1);
        gain1.connect(ctx.destination);
        osc1.start(now);
        osc1.stop(now + 0.4);

        // Ting 2 (1975.5 Hz)
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(1975.5, now + 0.12);
        gain2.gain.setValueAtTime(0.45, now + 0.12);
        gain2.gain.exponentialRampToValueAtTime(0.0001, now + 0.7);
        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        osc2.start(now + 0.12);
        osc2.stop(now + 0.7);
    } catch(e) {
        console.log('Web Audio blocked or not supported:', e);
    }
}

// REAL-TIME AUTO CHECKING (TỰ ĐỘNG NHẬN DIỆN VÀ CHUYỂN HƯỚNG KHI NHẬN ĐƯỢC TIỀN)
let isRedirecting = false;

function checkPaymentStatus() {
    if (isRedirecting) return;
    fetch('/api/check-payment/{{ order["id"] }}')
        .then(res => res.json())
        .then(data => {
            if (data.is_paid && !isRedirecting) {
                isRedirecting = true;
                playTingTingSound();
                let statusBox = document.getElementById('paymentStatusBox');
                if (statusBox) {
                    statusBox.innerHTML = `
                        <div class="alert alert-success p-3 rounded-4 shadow-sm fw-bold">
                            🎉 <strong>TING TING! TÀI KHOẢN ADMIN ĐÃ NHẬN TIỀN THÀNH CÔNG!</strong><br>
                            <span class="small font-monospace">Hệ thống đang tự động chuyển sang trang biên lai đơn hàng...</span>
                        </div>
                    `;
                }
                setTimeout(() => {
                    window.location.href = '/payment-success/{{ order["id"] }}';
                }, 1200);
            }
        })
        .catch(err => console.log('Checking payment...', err));
}

// Kiểm tra ngầm mỗi 2 giây
let checkInterval = setInterval(checkPaymentStatus, 2000);

// Nút bấm giả lập biến động số dư ngân hàng (Dành cho demo)
function simulateBankTransfer() {
    fetch('/api/simulate-bank-transfer/{{ order["id"] }}', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                checkPaymentStatus();
            }
        });
}
{% endif %}
</script>
""")

# ==============================================================================
# MÀN HÌNH XÁC NHẬN ĐƠN HÀNG & THÔNG TIN GPS CHO SHIPPER
# ==============================================================================
PAYMENT_SUCCESS_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="row justify-content-center">
    <div class="col-lg-10 col-xl-9">
        <div class="e-receipt-card p-4 p-md-5 mb-4 text-center">
            
            <div class="success-checkmark-box">
                <svg class="checkmark-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                    <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                    <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
                </svg>
            </div>

            <span class="badge bg-success bg-opacity-10 text-success fs-6 px-3 py-2 rounded-pill mb-2 fw-bold">
                ✓ XÁC NHẬN THÀNH CÔNG
            </span>
            
            <h2 class="fw-bold text-dark mb-1">Đơn Hàng #{{ order['id'] }} Đang Được Chuẩn Bị!</h2>
            <p class="text-muted fs-6 mb-4">Cảm ơn <strong>{{ order['fullname'] }}</strong>! Kiện hàng đang được bộ phận kho đóng gói.</p>

            <!-- STEPPER TIẾN TRÌNH -->
            <div class="order-stepper">
                <div class="order-stepper-bar" style="width: 45%;"></div>
                <div class="stepper-step completed"><div class="stepper-icon">🛒</div><div class="stepper-title">Đặt Hàng</div></div>
                <div class="stepper-step completed"><div class="stepper-icon">💳</div><div class="stepper-title">Thanh Toán</div></div>
                <div class="stepper-step active"><div class="stepper-icon">📦</div><div class="stepper-title">Đang Chuẩn Bị</div></div>
                <div class="stepper-step"><div class="stepper-icon">🚚</div><div class="stepper-title">Giao Hàng</div></div>
                <div class="stepper-step"><div class="stepper-icon">🏠</div><div class="stepper-title">Nhận Hàng</div></div>
            </div>

            <!-- CHI TIẾT ĐỊA CHỈ & TỌA ĐỘ GPS -->
            <div class="row g-4 text-start">
                <div class="col-md-6">
                    <div class="card h-100 p-3 border-0 bg-light rounded-3">
                        <h6 class="fw-bold text-dark mb-3">📍 ĐỊA CHỈ GIAO HÀNG & ĐỊNH VỊ GPS</h6>
                        <div class="mb-2"><span class="text-muted small">Người nhận:</span> <strong class="text-dark">{{ order['fullname'] }} ({{ order['phone'] }})</strong></div>
                        <div class="mb-2"><span class="text-muted small">Địa chỉ chi tiết:</span> <div class="text-dark fw-bold small">{{ order['address'] }}</div></div>
                        <div class="mb-2"><span class="text-muted small">Khu vực:</span> <span class="badge bg-secondary">{{ order.get('ward', '') }}, {{ order.get('district', '') }}, {{ order.get('province', '') }}</span></div>
                        
                        {% if order.get('geo_lat') and order.get('geo_lng') %}
                        <div class="p-2 mt-2 bg-success bg-opacity-10 border border-success rounded-3 small">
                            <div class="fw-bold text-success mb-1">🛰️ Tọa độ GPS đã khóa:</div>
                            <code>{{ order['geo_lat'] }}, {{ order['geo_lng'] }}</code>
                            <div class="mt-1">
                                <a href="https://www.google.com/maps?q={{ order['geo_lat'] }},{{ order['geo_lng'] }}" target="_blank" class="btn btn-sm btn-success py-1 px-2 fw-bold" style="font-size: 0.75rem;">
                                    🗺️ Mở chỉ đường Google Maps
                                </a>
                            </div>
                        </div>
                        {% endif %}
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card h-100 p-3 border-0 bg-light rounded-3">
                        <h6 class="fw-bold text-dark mb-3">🧾 BIÊN LAI THANH TOÁN</h6>
                        <div class="d-flex justify-content-between mb-2 small"><span class="text-muted">Phương thức:</span><span class="badge bg-success">{{ order['payment_method'] }}</span></div>
                        <div class="d-flex justify-content-between mb-2 small"><span class="text-muted">Đơn vị vận chuyển:</span><strong class="text-dark">🚚 {{ order.get('shipping_carrier', 'GHN Express') }}</strong></div>
                        <div class="d-flex justify-content-between mb-2 small"><span class="text-muted">Trạng thái xử lý:</span><span class="badge bg-warning text-dark">{{ order['status'] }}</span></div>
                        <div class="d-flex justify-content-between mb-2 small"><span class="text-muted">Thời gian đặt:</span><span>{{ order['created_at'] }}</span></div>
                        <hr class="my-2">
                        <div class="d-flex justify-content-between fs-5 fw-bold"><span>Tổng tiền:</span><span class="text-danger">{{ "{:,}".format(order['total']) }}đ</span></div>
                    </div>
                </div>
            </div>

            <div class="d-flex flex-wrap gap-2 justify-content-center mt-4">
                <a href="/order-status/{{ order['id'] }}" class="btn btn-outline-dark px-4 py-2 fw-bold">📦 Theo Dõi Đơn Hàng (OMS)</a>
                <a href="/" class="btn btn-sage px-4 py-2 fw-bold">🛍️ Tiếp Tục Mua Sắm</a>
            </div>
        </div>
    </div>
</div>

<script>
window.addEventListener('DOMContentLoaded', () => {
    if (typeof confetti === 'function') confetti({ particleCount: 70, spread: 60, origin: { y: 0.6 } });
});
</script>
""")

# ==============================================================================
# HÀNH TRÌNH ĐƠN HÀNG (OMS TRACKING CÓ GPS)
# ==============================================================================
TRACKING_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="card p-4 mx-auto shadow-sm bg-white rounded-4" style="max-width: 680px;">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="fw-bold mb-0 text-dark">Hệ Thống Quản Lý Đơn Hàng (OMS)</h4>
        <span class="badge bg-warning text-dark fs-6">{{ order['status'] }}</span>
    </div>
    
    <div class="card p-3 bg-light border-0 rounded-3 mb-3">
        <div class="row">
            <div class="col-sm-6 mb-1"><strong>Mã đơn:</strong> #{{ order['id'] }}</div>
            <div class="col-sm-6 mb-1"><strong>Khách hàng:</strong> {{ order['fullname'] }} ({{ order['phone'] }})</div>
            <div class="col-12 mt-1"><strong>Địa chỉ giao hàng:</strong> {{ order['address'] }}</div>
            <div class="col-12 mt-1"><strong>Đơn vị vận chuyển:</strong> <span class="badge bg-primary">🚚 {{ order.get('shipping_carrier', 'GHN Express') }}</span></div>
            {% if order.get('geo_lat') and order.get('geo_lng') %}
            <div class="col-12 mt-2">
                <span class="badge bg-success">📍 GPS: {{ order['geo_lat'] }}, {{ order['geo_lng'] }}</span>
                <a href="https://www.google.com/maps?q={{ order['geo_lat'] }},{{ order['geo_lng'] }}" target="_blank" class="small text-success ms-2 fw-bold text-decoration-none">
                    🗺️ Xem vị trí trên Google Maps ↗
                </a>
            </div>
            {% endif %}
        </div>
    </div>

    <h6 class="fw-bold mb-2">Hành trình xử lý:</h6>
    <div class="list-group my-2 small">
        <div class="list-group-item list-group-item-success">✅ 1. Đặt hàng thành công — {{ order['created_at'] }}</div>
        <div class="list-group-item {% if order['status'] in ['Đơn hàng đang được chuẩn bị', 'Đã bàn giao 3PL (GHTK/GHN)', 'Giao thành công (POD)'] %}list-group-item-success fw-bold{% else %}text-muted{% endif %}">
            📦 2. Đơn hàng đang được chuẩn bị (Pick & Pack)
        </div>
        <div class="list-group-item {% if order['status'] in ['Đã bàn giao 3PL (GHTK/GHN)', 'Giao thành công (POD)'] %}list-group-item-success{% else %}text-muted{% endif %}">
            🚚 3. Đã bàn giao đơn vị vận chuyển 3PL
        </div>
        <div class="list-group-item {% if order['status'] == 'Giao thành công (POD)' %}list-group-item-success{% else %}text-muted{% endif %}">
            🏠 4. Giao hàng thành công (POD)
        </div>
    </div>

    <div class="text-center mt-3">
        <a href="/" class="btn btn-outline-dark">← Quay về Trang chủ</a>
    </div>
</div>
""")

AUTH_TEMPLATE_CONTENT = """
<div class="row justify-content-center my-4">
    <div class="col-md-6 col-lg-5">
        <div class="card border-0 shadow-lg bg-white rounded-4 overflow-hidden">
            <!-- HEADER BRAND -->
            <div class="p-4 text-center pb-3" style="background: linear-gradient(135deg, #F7F4EE 0%, #EFE8DC 100%);">
                <span class="fs-1">🌿</span>
                <h4 class="fw-bold text-dark mb-0">NẾP NHỎ D2C</h4>
                <div class="small text-muted">Gọn một góc, nhẹ cả ngày</div>
            </div>

            <!-- TABS SWITCHER -->
            <div class="d-flex border-bottom bg-light">
                <button type="button" id="tabLoginBtn" class="btn w-50 py-3 fw-bold rounded-0 {% if active_tab != 'register' %}btn-white text-success border-bottom border-3 border-success bg-white{% else %}text-muted{% endif %}" onclick="switchAuthTab('login')">
                    🔐 Đăng Nhập
                </button>
                <button type="button" id="tabRegisterBtn" class="btn w-50 py-3 fw-bold rounded-0 {% if active_tab == 'register' %}btn-white text-success border-bottom border-3 border-success bg-white{% else %}text-muted{% endif %}" onclick="switchAuthTab('register')">
                    📝 Đăng Ký Tài Khoản
                </button>
            </div>

            <div class="p-4">
                <!-- FORM ĐĂNG NHẬP -->
                <div id="authLoginForm" style="{% if active_tab == 'register' %}display: none;{% endif %}">
                    <form action="/login" method="POST">
                        <input type="hidden" name="next" value="{{ next_url or '/' }}">
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">Email đăng nhập *</label>
                            <input type="email" id="loginEmail" name="email" class="form-control form-control-lg fs-6" required placeholder="admin@nepnho.vn">
                        </div>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <label class="form-label small fw-bold text-dark mb-0">Mật khẩu *</label>
                                <span class="small text-muted" style="cursor: pointer;" onclick="togglePasswordVisibility('loginPass')">👁️ Hiện/Ẩn</span>
                            </div>
                            <input type="password" id="loginPass" name="password" class="form-control form-control-lg fs-6" required placeholder="••••••••">
                        </div>
                        <button type="submit" class="btn btn-sage w-100 py-2 fs-6 fw-bold shadow-sm mb-3">
                            ✓ Đăng Nhập Vào Hệ Thống
                        </button>
                    </form>

                    <!-- HỘP ĐIỀN NHANH TÀI KHOẢN ADMIN / DEMO -->
                    <div class="p-3 bg-light rounded-3 border mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="small fw-bold text-dark">⚡ Tài Khoản Quản Trị Viên (Demo):</span>
                            <span class="badge bg-success bg-opacity-10 text-success">Admin</span>
                        </div>
                        <div class="small text-muted mb-2 font-monospace">admin@nepnho.vn | admin123</div>
                        <button type="button" class="btn btn-sm btn-outline-dark w-100 fw-bold" onclick="fillAdminDemo()">
                            👉 Bấm để Tự Điền Tài Khoản Admin Demo
                        </button>
                    </div>

                    <div class="text-center small text-muted">
                        Chưa có tài khoản? <a href="javascript:void(0)" onclick="switchAuthTab('register')" class="text-success fw-bold text-decoration-none">Đăng ký thành viên mới ngay →</a>
                    </div>
                </div>

                <!-- FORM ĐĂNG KÝ -->
                <div id="authRegisterForm" style="{% if active_tab != 'register' %}display: none;{% endif %}">
                    <form action="/register" method="POST">
                        <input type="hidden" name="next" value="{{ next_url or '/' }}">
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">Họ và tên quý khách *</label>
                            <input type="text" name="fullname" class="form-control" required placeholder="Ví dụ: Nguyễn Văn A">
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label small fw-bold text-dark">Email liên hệ *</label>
                                <input type="email" name="email" class="form-control" required placeholder="email@gmail.com">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label small fw-bold text-dark">Số điện thoại *</label>
                                <input type="tel" name="phone" class="form-control" required placeholder="0901234567">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">Địa chỉ giao hàng (Tùy chọn)</label>
                            <input type="text" name="address" class="form-control" placeholder="Số nhà, tên đường, Phường, Quận...">
                            <div class="form-text" style="font-size: 0.75rem;">Hệ thống sẽ tự động bắt tọa độ GPS vệ tinh khi đặt hàng để gửi cho shipper.</div>
                        </div>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <label class="form-label small fw-bold text-dark mb-0">Mật khẩu khởi tạo *</label>
                                <span class="small text-muted" style="cursor: pointer;" onclick="togglePasswordVisibility('regPass')">👁️ Hiện/Ẩn</span>
                            </div>
                            <input type="password" id="regPass" name="password" class="form-control" required placeholder="Tối thiểu 6 ký tự">
                        </div>
                        <button type="submit" class="btn btn-sage w-100 py-2 fs-6 fw-bold shadow-sm mb-3">
                            ✓ Hoàn Tất Đăng Ký Tài Khoản
                        </button>
                    </form>

                    <div class="text-center small text-muted">
                        Đã có tài khoản rồi? <a href="javascript:void(0)" onclick="switchAuthTab('login')" class="text-success fw-bold text-decoration-none">Đăng nhập ngay tại đây ←</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function switchAuthTab(tab) {
    const loginForm = document.getElementById('authLoginForm');
    const regForm = document.getElementById('authRegisterForm');
    const tabLoginBtn = document.getElementById('tabLoginBtn');
    const tabRegBtn = document.getElementById('tabRegisterBtn');

    if (tab === 'register') {
        if (loginForm) loginForm.style.display = 'none';
        if (regForm) regForm.style.display = 'block';
        if (tabRegBtn) tabRegBtn.className = 'btn w-50 py-3 fw-bold rounded-0 btn-white text-success border-bottom border-3 border-success bg-white';
        if (tabLoginBtn) tabLoginBtn.className = 'btn w-50 py-3 fw-bold rounded-0 text-muted';
        if (window.history && window.history.pushState) {
            window.history.pushState({}, '', '/register');
        }
    } else {
        if (loginForm) loginForm.style.display = 'block';
        if (regForm) regForm.style.display = 'none';
        if (tabLoginBtn) tabLoginBtn.className = 'btn w-50 py-3 fw-bold rounded-0 btn-white text-success border-bottom border-3 border-success bg-white';
        if (tabRegBtn) tabRegBtn.className = 'btn w-50 py-3 fw-bold rounded-0 text-muted';
        if (window.history && window.history.pushState) {
            window.history.pushState({}, '', '/login');
        }
    }
}

function fillAdminDemo() {
    const em = document.getElementById('loginEmail');
    const pw = document.getElementById('loginPass');
    if (em) em.value = 'admin@nepnho.vn';
    if (pw) pw.value = 'admin123';
}

function togglePasswordVisibility(id) {
    const input = document.getElementById(id);
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}
</script>
"""

LOGIN_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", AUTH_TEMPLATE_CONTENT)
REGISTER_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", AUTH_TEMPLATE_CONTENT)

PROFILE_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="row g-4">
    <div class="col-md-4">
        <div class="card border-0 shadow-sm p-4 bg-white rounded-4">
            <div class="text-center mb-3"><div class="fs-1">👤</div><h5 class="fw-bold mb-0">{{ user['fullname'] }}</h5></div>
            <div class="small mb-2"><strong>Email:</strong> {{ user['email'] }}</div>
            <div class="small mb-3"><strong>Điện thoại:</strong> {{ user['phone'] }}</div>
            <a href="/logout" class="btn btn-outline-danger btn-sm w-100">Đăng xuất</a>
        </div>
    </div>
    <div class="col-md-8">
        <div class="card border-0 shadow-sm p-4 bg-white rounded-4">
            <h5 class="fw-bold mb-3">Lịch Sử Đơn Hàng Của Bạn</h5>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead><tr><th>Mã đơn</th><th>Ngày đặt</th><th>Tổng tiền</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
                    <tbody>
                        {% for oid, order in my_orders.items() %}
                        <tr>
                            <td class="fw-bold">#{{ order['id'] }}</td>
                            <td class="small">{{ order['created_at'] }}</td>
                            <td class="text-danger fw-bold">{{ "{:,}".format(order['total']) }}đ</td>
                            <td><span class="badge bg-warning text-dark">{{ order['status'] }}</span></td>
                            <td><a href="/order-status/{{ order['id'] }}" class="btn btn-sm btn-outline-dark">Xem OMS</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
""")

# ==============================================================================
# BẢNG QUẢN TRỊ ADMIN (HIỂN THỊ LINK BẢN ĐỒ GOOGLE MAPS CHO SHIPPER)
# ==============================================================================
ADMIN_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="d-flex justify-content-between align-items-center mb-4">
    <h3 class="fw-bold text-danger mb-0">⚙️ BẢNG QUẢN TRỊ ADMIN — NẾP NHỎ D2C</h3>
    <span class="badge bg-dark fs-6 px-3 py-2">Quyền: Quản trị viên</span>
</div>

<div class="row g-3 mb-4">
    <div class="col-md-4">
        <div class="card p-3 bg-white border-start border-4 border-primary shadow-sm rounded-3">
            <div class="text-muted small">Tổng Đơn Hàng</div>
            <div class="fs-3 fw-bold">{{ orders|length }} đơn</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card p-3 bg-white border-start border-4 border-success shadow-sm rounded-3">
            <div class="text-muted small">Doanh Thu Thu Được</div>
            <div class="fs-3 fw-bold text-success">{{ "{:,}".format(total_revenue) }}đ</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card p-3 bg-white border-start border-4 border-warning shadow-sm rounded-3">
            <div class="text-muted small">Sản Phẩm Trong Kho</div>
            <div class="fs-3 fw-bold text-warning">{{ products|length }} SKU</div>
        </div>
    </div>
</div>

<!-- QUẢN LÝ ĐƠN HÀNG KÈM GPS VÀ ĐIỀU HƯỚNG SHIPPER -->
<div class="card p-3 border-0 shadow-sm bg-white mb-4 rounded-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="fw-bold mb-0 text-dark">📦 Quản Lý Đơn Hàng (OMS) & Tọa Độ Giao Hàng GPS</h5>
        <span class="text-muted small">Bấm 'Google Maps' để mở ứng dụng dẫn đường bưu tá</span>
    </div>
    <div class="table-responsive">
        <table class="table table-hover align-middle">
            <thead>
                <tr>
                    <th>Mã Đơn</th>
                    <th>Khách Hàng / SĐT</th>
                    <th>Địa Chỉ & Tọa Độ GPS</th>
                    <th>Tổng Tiền</th>
                    <th>Trạng Thái OMS</th>
                    <th>Cập Nhật</th>
                </tr>
            </thead>
            <tbody>
                {% for oid, o in orders.items() %}
                <tr>
                    <td class="fw-bold">#{{ o['id'] }}</td>
                    <td>
                        <div class="fw-bold">{{ o['fullname'] }}</div>
                        <div class="text-muted small">{{ o['phone'] }}</div>
                        <div class="badge bg-light text-dark border mt-1" style="font-size: 0.68rem;">🚚 {{ o.get('shipping_carrier', 'GHN') }}</div>
                    </td>
                    <td>
                        <div class="small fw-bold text-dark">{{ o['address'] }}</div>
                        {% if o.get('geo_lat') and o.get('geo_lng') %}
                        <div class="mt-1">
                            <a href="https://www.google.com/maps?q={{ o['geo_lat'] }},{{ o['geo_lng'] }}" target="_blank" class="btn btn-sm btn-outline-success py-0 px-2 fw-bold" style="font-size: 0.72rem;">
                                📍 Bản đồ: {{ o['geo_lat'] }}, {{ o['geo_lng'] }} ↗
                            </a>
                        </div>
                        {% else %}
                        <span class="badge bg-light text-muted border" style="font-size: 0.7rem;">Không có GPS</span>
                        {% endif %}
                    </td>
                    <td class="fw-bold text-danger">{{ "{:,}".format(o['total']) }}đ</td>
                    <td>
                        {% if 'chuẩn bị' in o['status'] %}
                        <span class="badge bg-warning text-dark">{{ o['status'] }}</span>
                        {% elif 'Đã tự hủy' in o['status'] %}
                        <span class="badge bg-danger">{{ o['status'] }}</span>
                        {% else %}
                        <span class="badge bg-info text-dark">{{ o['status'] }}</span>
                        {% endif %}
                    </td>
                    <td>
                        <form action="/admin/update-order-status" method="POST" class="d-flex">
                            <input type="hidden" name="order_id" value="{{ o['id'] }}">
                            <select name="status" class="form-select form-select-sm me-1" style="width: 200px;">
                                <option value="Chờ thanh toán VietQR" {% if o['status']=='Chờ thanh toán VietQR' %}selected{% endif %}>Chờ thanh toán VietQR</option>
                                <option value="Chờ xác nhận (COD)" {% if o['status']=='Chờ xác nhận (COD)' %}selected{% endif %}>Chờ xác nhận (COD)</option>
                                <option value="Đơn hàng đang được chuẩn bị" {% if o['status']=='Đơn hàng đang được chuẩn bị' %}selected{% endif %}>📦 Đang chuẩn bị hàng</option>
                                <option value="Đã bàn giao 3PL (GHTK/GHN)" {% if o['status']=='Đã bàn giao 3PL (GHTK/GHN)' %}selected{% endif %}>🚚 Đang giao 3PL</option>
                                <option value="Giao thành công (POD)" {% if o['status']=='Giao thành công (POD)' %}selected{% endif %}>🏠 Giao thành công</option>
                                <option value="Đã tự hủy (Quá hạn 24h)" {% if o['status']=='Đã tự hủy (Quá hạn 24h)' %}selected{% endif %}>❌ Đã tự hủy (24h)</option>
                            </select>
                            <button type="submit" class="btn btn-sm btn-primary">Lưu</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
""")

# ==============================================================================
# CONTROLLERS & ROUTES (XỬ LÝ NGHIỆP VỤ)
# ==============================================================================

@app.context_processor
def inject_global_vars():
    user = session.get('user')
    cart = session.get('cart', [])
    cart_count = sum(item['qty'] for item in cart)
    cart_subtotal = sum(item['price'] * item['qty'] for item in cart)
    bank_config = DB.get('bank_config', DEFAULT_BANK_CONFIG)
    return dict(current_user=user, cart_count=cart_count, cart_subtotal=cart_subtotal, bank_config=bank_config)

@app.route('/')
def index():
    view = request.args.get('view')
    is_embed = request.args.get('embed') == '1'
    if view == 'tablet':
        return render_template_string(TABLET_TEMPLATE, products=DB['products'], current_mode='tablet', current_mode_label='Tablet (768px-1024px)', is_embed=is_embed)
    elif view == 'mobile':
        return render_template_string(MOBILE_TEMPLATE, products=DB['products'], current_mode='mobile', current_mode_label='Mobile App (375px-430px)', is_embed=is_embed)
    elif view in ('demo', 'preview'):
        return render_template_string(DEMO_SHOWCASE_TEMPLATE, products=DB['products'], current_mode='demo', current_mode_label='Bộ 3 Giao Diện Simulator', is_embed=is_embed)
    else:
        return render_template_string(DESKTOP_TEMPLATE, products=DB['products'], current_mode='desktop', current_mode_label='Desktop (>1200px)', is_embed=is_embed)

@app.route('/product/<pid>')
def product_detail(pid):
    product = DB['products'].get(pid)
    if not product:
        flash("Sản phẩm không tồn tại!", "danger")
        return redirect('/')
    return render_template_string(PRODUCT_HTML, product=product)

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next') or '/'
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = DB['users'].get(email)
        if user and check_password_hash(user['password'], password):
            session['user'] = user
            flash(f"Chào mừng {user['fullname']}!", "success")
            return redirect(next_url)
        flash("Email hoặc mật khẩu không đúng!", "danger")
    return render_template_string(LOGIN_HTML, next_url=next_url, active_tab='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    next_url = request.args.get('next') or request.form.get('next') or '/'
    if request.method == 'POST':
        email = request.form.get('email')
        if email in DB['users']:
            flash("Email đã tồn tại!", "warning")
            return redirect(f'/register?next={next_url}')
        new_user = {
            'email': email,
            'password': generate_password_hash(request.form.get('password')),
            'fullname': request.form.get('fullname'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'role': 'customer'
        }
        DB['users'][email] = new_user
        save_data(DB)
        session['user'] = new_user
        flash(f"Chúc mừng {new_user['fullname']} đã đăng ký thành công!", "success")
        return redirect(next_url)
    return render_template_string(REGISTER_HTML, next_url=next_url, active_tab='register')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect('/login')
    my_orders = {oid: o for oid, o in DB['orders'].items() if o.get('email') == user['email']}
    return render_template_string(PROFILE_HTML, user=user, my_orders=my_orders)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    pid = request.form.get('product_id')
    qty = int(request.form.get('qty', 1))
    next_url = request.form.get('next_url')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('ajax') == '1'
    product = DB['products'].get(pid)
    if product:
        cart = session.get('cart', [])
        found = False
        for item in cart:
            if item['id'] == pid:
                item['qty'] += qty
                found = True
                break
        if not found:
            cart.append({'id': product['id'], 'name': product['name'], 'price': product['price'], 'qty': qty, 'img': product.get('after_img', '')})
        session['cart'] = cart
        flash(f"Đã thêm '{product['name']}' vào giỏ hàng!", "success")
        if is_ajax:
            return jsonify({
                'status': 'success',
                'message': f"Đã thêm '{product['name']}' vào giỏ hàng!",
                'cart_count': sum(i['qty'] for i in cart),
                'cart_subtotal': sum(i['price'] * i['qty'] for i in cart),
                'product_name': product['name']
            })
    if next_url:
        return redirect(next_url)
    return redirect('/cart')

@app.route('/cart')
def view_cart():
    user = session.get('user')
    if not user:
        flash("Vui lòng đăng nhập để xem giỏ hàng và đồng bộ vị trí giao hàng!", "warning")
        return redirect(url_for('login', next='/cart'))
    cart = session.get('cart', [])
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    return render_template_string(CART_HTML, cart=cart, subtotal=subtotal, user_info=user)

@app.route('/update-cart', methods=['POST'])
def update_cart():
    pid = request.form.get('product_id')
    qty = int(request.form.get('qty', 1))
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == pid:
            if qty > 0:
                item['qty'] = qty
            break
    session['cart'] = cart
    return redirect('/cart')

@app.route('/remove-cart/<pid>')
def remove_cart(pid):
    cart = [i for i in session.get('cart', []) if i['id'] != pid]
    session['cart'] = cart
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    user = session.get('user')
    if not user:
        flash("Vui lòng đăng nhập để xác nhận địa chỉ và vị trí giao hàng!", "warning")
        return redirect(url_for('login', next='/checkout'))
    cart = session.get('cart', [])
    if not cart:
        flash("Giỏ hàng của bạn đang trống!", "info")
        return redirect('/')
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    return render_template_string(CHECKOUT_HTML, cart=cart, subtotal=subtotal, user_info=user)

@app.route('/api/update-location', methods=['POST'])
def update_location():
    user = session.get('user')
    if not user:
        return jsonify({'status': 'error', 'message': 'Vui lòng đăng nhập để lưu vị trí giao hàng!'}), 401
    
    email = user.get('email')
    lat = request.form.get('lat')
    lng = request.form.get('lng')
    address = request.form.get('address')
    
    if not address and lat and lng:
        address = f"Tọa độ GPS: {float(lat):.5f}, {float(lng):.5f}"
    
    if email in DB['users']:
        if lat and lng:
            DB['users'][email]['gps_lat'] = lat
            DB['users'][email]['gps_lng'] = lng
        if address:
            DB['users'][email]['address'] = address
        save_data(DB)
        session['user'] = DB['users'][email]
        return jsonify({
            'status': 'success',
            'message': 'Đã xác định vị trí và lưu vào database thành công!',
            'address': session['user'].get('address'),
            'gps_lat': session['user'].get('gps_lat'),
            'gps_lng': session['user'].get('gps_lng')
        })
    return jsonify({'status': 'error', 'message': 'Không tìm thấy người dùng'}), 404

@app.route('/process-order', methods=['POST'])
def process_order():
    user = session.get('user')
    if not user:
        flash("Vui lòng đăng nhập để đặt hàng!", "warning")
        return redirect(url_for('login', next='/checkout'))
    cart = session.get('cart', [])
    if not cart:
        return redirect('/')
    
    order_id = ''.join(random.choices(string.digits, k=6))
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    payment_method = request.form.get('payment_method', 'VIETQR')
    shipping_carrier = request.form.get('shipping_carrier', 'Giao Hàng Nhanh (GHN Express)')
    shipping_fee = 15000 if ('Hỏa Tốc' in shipping_carrier or 'AhaMove' in shipping_carrier) else 0
    final_total = subtotal + shipping_fee
    
    # THU THẬP THÔNG TIN ĐỊA CHỈ KHU VỰC VÀ TỌA ĐỘ GPS
    province = request.form.get('province', '').strip()
    district = request.form.get('district', '').strip()
    ward = request.form.get('ward', '').strip()
    street_address = request.form.get('street_address', '').strip()
    geo_lat = request.form.get('geo_lat', '').strip()
    geo_lng = request.form.get('geo_lng', '').strip()
    
    full_address = f"{street_address}, {ward}, {district}, {province}".strip(', ')

    # CẬP NHẬT VÀ LƯU VỊ TRÍ VÀO TÀI KHOẢN NGƯỜI DÙNG TRONG DATABASE
    user_email = user.get('email')
    if user_email and user_email in DB['users']:
        if full_address:
            DB['users'][user_email]['address'] = full_address
        if geo_lat and geo_lng:
            DB['users'][user_email]['gps_lat'] = geo_lat
            DB['users'][user_email]['gps_lng'] = geo_lng
        if request.form.get('phone'):
            DB['users'][user_email]['phone'] = request.form.get('phone')
        session['user'] = DB['users'][user_email]
    
    now_dt = datetime.now()
    now_ts = now_dt.timestamp()
    expires_at_ts = now_ts + (24 * 3600)  # Tự động hủy sau 24h
    
    order = {
        'id': order_id,
        'fullname': request.form.get('fullname'),
        'phone': request.form.get('phone'),
        'email': user_email,
        'province': province,
        'district': district,
        'ward': ward,
        'street_address': street_address,
        'address': full_address,
        'geo_lat': geo_lat,
        'geo_lng': geo_lng,
        'warehouse_location': 'Kho Trung Tâm Quận 9 (TP. Thủ Đức, TP.HCM)',
        'payment_method': payment_method,
        'shipping_carrier': shipping_carrier,
        'shipping_fee': shipping_fee,
        'subtotal': subtotal,
        'payment_status': 'Chờ thanh toán' if payment_method == 'VIETQR' else 'COD (Chưa thu)',
        'total': final_total,
        'items': cart,
        'status': 'Chờ thanh toán VietQR' if payment_method == 'VIETQR' else 'Chờ xác nhận (COD)',
        'created_at': now_dt.strftime("%H:%M %d/%m/%Y"),
        'created_timestamp': now_ts,
        'expires_at_timestamp': expires_at_ts,
        'paid_at': ''
    }
    
    # Khóa giữ tồn kho ATP
    for item in cart:
        pid = item['id']
        if pid in DB['products']:
            DB['products'][pid]['stock_committed'] += item['qty']

    DB['orders'][order_id] = order
    save_data(DB)
    session['cart'] = []
    
    if payment_method == 'VIETQR':
        return redirect(f'/payment/{order_id}')
    else:
        return redirect(f'/payment-success/{order_id}')

@app.route('/payment/<order_id>')
def payment_gateway(order_id):
    order = DB['orders'].get(order_id)
    if not order:
        return redirect('/')
    if order.get('payment_status') == 'Đã thanh toán':
        return redirect(f'/payment-success/{order_id}')

    is_expired = False
    if order.get('status') == 'Đã tự hủy (Quá hạn 24h)' or time.time() >= order.get('expires_at_timestamp', 0):
        is_expired = True

    return render_template_string(PAYMENT_GATEWAY_HTML, order=order, is_expired=is_expired)

@app.route('/confirm-payment/<order_id>', methods=['POST', 'GET'])
def confirm_payment(order_id):
    order = DB['orders'].get(order_id)
    if not order:
        return redirect('/')
        
    if order.get('status') == 'Đã tự hủy (Quá hạn 24h)' or time.time() >= order.get('expires_at_timestamp', 0):
        flash("Đơn hàng đã quá hạn 24h và đã tự hủy!", "danger")
        return redirect(f'/payment/{order_id}')
        
    # CHUYỂN NGAY SANG: ĐƠN HÀNG ĐANG ĐƯỢC CHUẨN BỊ
    order['status'] = 'Đơn hàng đang được chuẩn bị'
    order['payment_status'] = 'Đã thanh toán'
    order['paid_at'] = datetime.now().strftime("%H:%M %d/%m/%Y")
    save_data(DB)
    
    flash("Thanh toán thành công! Đơn hàng đang được chuẩn bị tại kho.", "success")
    return redirect(f'/payment-success/{order_id}')

@app.route('/payment-success/<order_id>')
def payment_success(order_id):
    order = DB['orders'].get(order_id)
    if not order:
        return redirect('/')
    return render_template_string(PAYMENT_SUCCESS_HTML, order=order)

# ==============================================================================
# HỆ THỐNG TỰ ĐỘNG KHỚP THANH TOÁN VIETQR REAL-TIME (SEPAY / CASSO / WEBHOOK)
# ==============================================================================

@app.route('/api/check-payment/<order_id>')
def api_check_payment(order_id):
    """API để Frontend tự động Long-poll / Kiểm tra trạng thái thanh toán mỗi 2s"""
    order = DB['orders'].get(order_id)
    if not order:
        return jsonify({'status': 'not_found', 'is_paid': False}), 404
    
    is_paid = (order.get('payment_status') == 'Đã thanh toán')
    return jsonify({
        'order_id': order_id,
        'is_paid': is_paid,
        'status': order.get('status', ''),
        'payment_status': order.get('payment_status', '')
    })

@app.route('/api/simulate-bank-transfer/<order_id>', methods=['POST', 'GET'])
def api_simulate_bank_transfer(order_id):
    """Mô phỏng tài khoản MBBank của Admin nhận biến động số dư đúng mã đơn"""
    order = DB['orders'].get(order_id)
    if not order:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy đơn hàng'}), 404
    
    order['status'] = 'Đơn hàng đang được chuẩn bị'
    order['payment_status'] = 'Đã thanh toán'
    order['paid_at'] = datetime.now().strftime("%H:%M %d/%m/%Y")
    save_data(DB)
    return jsonify({
        'status': 'success',
        'message': f"Đã nhận biến động số dư ngân hàng cho đơn #{order_id} (+{order['total']:,}đ)!",
        'order_id': order_id,
        'is_paid': True
    })

@app.route('/webhook/bank-transfer', methods=['POST'])
def webhook_bank_transfer():
    """
    Webhook tiếp nhận biến động số dư tự động từ dịch vụ ngân hàng (SePay / Casso / MBBank / Techcombank)
    Khi tiền vào tài khoản ngân hàng thật của Admin, SePay/Casso sẽ gọi URL này.
    Ví dụ nội dung: 'NEPNHO 123456'
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({'status': 'error', 'message': 'Không có dữ liệu'}), 400

    content = str(data.get('content') or data.get('description') or data.get('code') or '')
    amount = float(data.get('transferAmount') or data.get('amount') or 0)
    
    # Tìm mã đơn 6 chữ số trong nội dung chuyển khoản
    match = re.search(r'NEPNHO\s*([0-9]{6})', content, re.IGNORECASE) or re.search(r'\b([0-9]{6})\b', content)
    if match:
        order_id = match.group(1)
        order = DB['orders'].get(order_id)
        if order and order.get('payment_status') != 'Đã thanh toán':
            order['status'] = 'Đơn hàng đang được chuẩn bị'
            order['payment_status'] = 'Đã thanh toán'
            order['paid_at'] = datetime.now().strftime("%H:%M %d/%m/%Y")
            order['bank_ref'] = data.get('referenceCode', '')
            save_data(DB)
            return jsonify({
                'status': 'success',
                'message': f"Đã tự động khớp đơn hàng #{order_id} thành công!",
                'order_id': order_id
            })

    return jsonify({'status': 'ignored', 'message': 'Không tìm thấy mã đơn hợp lệ'}), 200

@app.route('/order-status/<order_id>')
def order_status(order_id):
    order = DB['orders'].get(order_id)
    if not order:
        return redirect('/')
    return render_template_string(TRACKING_HTML, order=order)

@app.route('/admin')
def admin_dashboard():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect('/login')
    total_revenue = sum(o['total'] for o in DB['orders'].values() if o.get('payment_status') == 'Đã thanh toán')
    return render_template_string(ADMIN_HTML, orders=DB['orders'], products=DB['products'], total_revenue=total_revenue, bank_config=DB.get('bank_config', DEFAULT_BANK_CONFIG))

@app.route('/admin/update-order-status', methods=['POST'])
def admin_update_order():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect('/')
    oid = request.form.get('order_id')
    status = request.form.get('status')
    if oid in DB['orders']:
        old_status = DB['orders'][oid]['status']
        DB['orders'][oid]['status'] = status
        if status in ['Đơn hàng đang được chuẩn bị', 'Đã bàn giao 3PL (GHTK/GHN)', 'Giao thành công (POD)']:
            DB['orders'][oid]['payment_status'] = 'Đã thanh toán'
            if not DB['orders'][oid].get('paid_at'):
                DB['orders'][oid]['paid_at'] = datetime.now().strftime("%H:%M %d/%m/%Y")
        if status == 'Đã tự hủy (Quá hạn 24h)' and old_status != 'Đã tự hủy (Quá hạn 24h)':
            for item in DB['orders'][oid].get('items', []):
                pid = item.get('id')
                if pid in DB['products']:
                    DB['products'][pid]['stock_committed'] = max(0, DB['products'][pid]['stock_committed'] - item.get('qty', 0))
        save_data(DB)
        flash(f"Đã cập nhật đơn #{oid} thành '{status}'!", "success")
    return redirect('/admin')

@app.route('/images/<path:filename>')
def serve_images(filename):
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
    return send_from_directory(images_dir, filename)

@app.route('/desktop')
def serve_desktop():
    is_embed = request.args.get('embed') == '1'
    return render_template_string(DESKTOP_TEMPLATE, products=DB['products'], current_mode='desktop', current_mode_label='Desktop (>1200px)', is_embed=is_embed)

@app.route('/tablet')
def serve_tablet():
    is_embed = request.args.get('embed') == '1'
    return render_template_string(TABLET_TEMPLATE, products=DB['products'], current_mode='tablet', current_mode_label='Tablet (768px-1024px)', is_embed=is_embed)

@app.route('/mobile')
def serve_mobile():
    is_embed = request.args.get('embed') == '1'
    return render_template_string(MOBILE_TEMPLATE, products=DB['products'], current_mode='mobile', current_mode_label='Mobile App (375px-430px)', is_embed=is_embed)

@app.route('/demo')
@app.route('/preview')
def serve_demo():
    is_embed = request.args.get('embed') == '1'
    return render_template_string(DEMO_SHOWCASE_TEMPLATE, products=DB['products'], current_mode='demo', current_mode_label='Bộ 3 Giao Diện Simulator', is_embed=is_embed)

def start_live_server_tunnel():
    # Khi chạy trên Render hoặc môi trường Cloud, Render đã cung cấp HTTPS domain riêng
    if os.environ.get('RENDER') or os.environ.get('PORT'):
        return

    app_dir = os.path.dirname(os.path.abspath(__file__))
    cloudflared_path = os.path.join(app_dir, "cloudflared.exe")
    if not os.path.exists(cloudflared_path):
        return

    import atexit
    import subprocess
    log_path = os.path.join(app_dir, "cloudflared.log")

    while True:
        log_file = open(log_path, "w", encoding='utf-8')
        proc = subprocess.Popen(
            [cloudflared_path, "tunnel", "--url", "http://127.0.0.1:5000"],
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        atexit.register(lambda: proc.terminate())

        found_url = False
        for _ in range(40):
            time.sleep(0.5)
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        match = re.search(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com', content)
                        if match:
                            url = match.group(0)
                            print("\n" + "="*68, flush=True)
                            print("🌐 LIVE SERVER TOÀN CẦU ĐÃ KẾT NỐI (4G/KHÁC MẠNG ĐỀU VÀO ĐƯỢC):", flush=True)
                            print(f"👉 Link Online: {url}", flush=True)
                            print(f"👉 Bản Mobile:  {url}/mobile", flush=True)
                            print(f"👉 Đăng nhập:   {url}/login", flush=True)
                            print(f"👉 Đăng ký:     {url}/register", flush=True)
                            print("="*68 + "\n", flush=True)
                            found_url = True
                            break
                except Exception:
                    pass
        if found_url:
            proc.wait()
        time.sleep(2)

if __name__ == '__main__':
    import socket
    import threading

    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    print("====================================================================")
    print("🚀 NẾP NHỎ D2C: ĐANG KHỞI ĐỘNG CHẠY SONG SONG LOCALHOST & LIVE SERVER")
    print("====================================================================")
    print("💻 1. Localhost (máy tính này):     http://localhost:5000")
    print(f"📱 2. Mạng Wi-Fi (chung mạng):       http://{local_ip}:5000")
    print("🌐 3. Live Server (khác mạng / 4G): Đang tạo link bên dưới...")
    print("====================================================================", flush=True)

    # Khởi động Live Server Cloudflare tự động chạy song song
    threading.Thread(target=start_live_server_tunnel, daemon=True).start()

    # Flask chạy đồng thời trên Localhost, Mạng LAN và Render Cloud (qua biến môi trường PORT)
    server_port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=server_port, debug=False)