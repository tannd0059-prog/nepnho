# -*- coding: utf-8 -*-
"""
Script to generate 3 separate responsive HTML templates:
1. desktop.html - Desktop-optimized UI (1280px+ layout, 4 columns, left filter sidebar, mega header)
2. tablet.html  - Tablet-optimized UI (768px-1024px layout, touch friendly, scrollable pills, 3 columns)
3. mobile.html  - Mobile-optimized UI (375px-430px smartphone layout, bottom navigation bar, 2 columns grid)
4. demo_3_devices.html - Interactive device switcher & side-by-side presentation preview
"""
import os
import json

BASE_DIR = r"c:\Users\tan\Documents\TMĐT\app"
DB_PATH = os.path.join(BASE_DIR, "nepnho_db.json")

with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

products = db.get("products", {})

def clean_img(url):
    if not url:
        return "images/ke_dung_my_pham.png"
    if url.startswith("/"):
        return url[1:]
    return url

# Common styles & colors
COMMON_CSS = """
:root {
    --bg-paper: #F7F4EE;
    --sage-green: #7D9D7C;
    --sage-dark: #658464;
    --earth-brown: #8A6F5A;
    --warm-accent: #E88D67;
    --text-dark: #2B2B2B;
    --text-muted: #6B7280;
    --card-bg: #FFFFFF;
}
* { box-sizing: border-box; }
body {
    background-color: var(--bg-paper);
    color: var(--text-dark);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    margin: 0;
    padding: 0;
}
.text-sage { color: var(--sage-green) !important; }
.bg-sage { background-color: var(--sage-green) !important; color: white !important; }
.btn-sage { background-color: var(--sage-green); color: white; border: none; font-weight: 600; border-radius: 8px; transition: 0.2s; }
.btn-sage:hover { background-color: var(--sage-dark); color: white; }
.price-tag { color: var(--warm-accent); font-weight: 700; }
.badge-atp { background-color: #E8F5E9; color: #2E7D32; font-size: 0.75rem; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
.badge-cat { background-color: #F1ECE1; color: var(--earth-brown); font-size: 0.72rem; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
"""

# ==============================================================================
# 1. DESKTOP HTML
# ==============================================================================
def generate_desktop():
    product_cards_html = ""
    for pid, p in products.items():
        discount = int(((p['original_price'] - p['price']) / p['original_price']) * 100) if p.get('original_price', 0) > p['price'] else 0
        img_after = clean_img(p.get('after_img'))
        img_before = clean_img(p.get('before_img'))
        stock_atp = p.get('stock_physical', 50) - p.get('stock_committed', 0)
        
        product_cards_html += f"""
        <div class="desktop-card-col" data-cat="{p.get('category','')}" data-name="{p.get('name','').lower()}" data-price="{p.get('price', 0)}">
            <div class="desktop-card">
                <div class="card-img-wrap">
                    <span class="badge-discount">-{discount}%</span>
                    <span class="badge-cat-top">{p.get('category','')}</span>
                    <img id="img-{pid}" src="{img_after}" alt="{p.get('name','')}" class="product-thumb">
                    <div class="img-toggle-bar">
                        <button class="toggle-btn active" onclick="switchImg('{pid}', '{img_after}', this)">Sau khi xếp</button>
                        <button class="toggle-btn" onclick="switchImg('{pid}', '{img_before}', this)">Trước (Bừa)</button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="badge-atp">⚡ Sẵn giao: {stock_atp} món</span>
                        <span class="rating">⭐ 5.0 (48)</span>
                    </div>
                    <h3 class="product-title" title="{p.get('name','')}">{p.get('name','')}</h3>
                    <p class="product-desc">{p.get('description','')}</p>
                    <div class="card-footer-box">
                        <div>
                            <div class="price-val">{p.get('price', 0):,}đ</div>
                            <div class="price-old">{p.get('original_price', 0):,}đ</div>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-dark btn-sm rounded-3" onclick="addToCartMock('{p.get('name','')}')" title="Thêm giỏ hàng">🛒</button>
                            <button class="btn btn-sage btn-sm px-3" onclick="openDetailModal('{pid}')">Chi tiết</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

    # Categories list
    cats = sorted(list(set(p.get('category','') for p in products.values() if p.get('category'))))
    cat_filters = "".join([f'<label class="filter-check"><input type="checkbox" name="cat" value="{c}" onchange="filterProducts()"> <span>{c}</span></label>' for c in cats])

    # Products JSON for modal lookup
    products_json_str = json.dumps(products, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 Nếp Nhỏ — Desktop Interface (Giao diện Máy Tính)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        {COMMON_CSS}
        /* DESKTOP SPECIFIC STYLES */
        .desktop-container {{ max-width: 1360px; margin: 0 auto; padding: 0 20px; }}
        
        /* TOP BAR */
        .top-promo-bar {{ background: #2B2B2B; color: #E5E7EB; font-size: 0.8rem; padding: 8px 0; }}
        
        /* HEADER */
        .desktop-header {{ background: #FFFFFF; border-bottom: 2px solid var(--sage-green); padding: 14px 0; }}
        .brand-title {{ font-weight: 800; color: var(--earth-brown); font-size: 1.6rem; letter-spacing: -0.5px; text-decoration: none; }}
        .brand-subtitle {{ font-size: 0.78rem; color: #777; margin-top: -2px; }}
        .desktop-search-bar {{ max-width: 540px; position: relative; }}
        .desktop-search-input {{ border-radius: 30px; padding: 10px 20px 10px 42px; border: 1.5px solid #E2E8F0; background: #F8FAFC; width: 100%; outline: none; transition: 0.2s; }}
        .desktop-search-input:focus {{ border-color: var(--sage-green); background: #FFF; box-shadow: 0 0 0 4px rgba(125,157,124,0.15); }}
        .search-icon {{ position: absolute; left: 16px; top: 12px; color: #94A3B8; font-size: 1rem; }}
        
        /* MAIN NAV */
        .desktop-nav {{ background: #FFFFFF; border-bottom: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }}
        .nav-link-custom {{ color: #334155; font-weight: 600; font-size: 0.92rem; padding: 12px 16px !important; text-decoration: none; display: inline-block; transition: 0.2s; }}
        .nav-link-custom:hover, .nav-link-custom.active {{ color: var(--sage-green); border-bottom: 2px solid var(--sage-green); }}
        
        /* HERO BANNER */
        .hero-banner-desktop {{
            background: linear-gradient(135deg, #F1ECE1 0%, #E5DAC6 100%);
            border-radius: 20px;
            padding: 48px;
            margin: 24px 0 32px;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.04);
        }}
        .hero-title {{ font-size: 2.3rem; font-weight: 800; color: #1E293B; line-height: 1.25; }}
        .hero-badge {{ background: #DCFCE7; color: #15803D; font-weight: 700; font-size: 0.8rem; padding: 6px 14px; border-radius: 20px; display: inline-block; margin-bottom: 12px; }}
        
        /* COMMITMENT CARDS */
        .commit-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }}
        .commit-card {{ background: #FFFFFF; border-radius: 12px; padding: 16px 20px; display: flex; align-items: center; gap: 14px; border: 1px solid #E2E8F0; box-shadow: 0 2px 6px rgba(0,0,0,0.02); }}
        .commit-icon {{ font-size: 1.8rem; }}
        .commit-title {{ font-size: 0.88rem; font-weight: 700; color: #1E293B; margin-bottom: 2px; }}
        .commit-desc {{ font-size: 0.76rem; color: #64748B; margin: 0; }}
        
        /* STORE SECTION */
        .store-layout {{ display: grid; grid-template-columns: 260px 1fr; gap: 28px; }}
        
        /* SIDEBAR */
        .filter-sidebar {{ background: #FFFFFF; border-radius: 16px; padding: 22px; border: 1px solid #E2E8F0; height: fit-content; position: sticky; top: 20px; }}
        .filter-group-title {{ font-size: 0.95rem; font-weight: 700; color: #1E293B; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1.5px solid #F1F5F9; display: flex; justify-content: space-between; align-items: center; }}
        .filter-check {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-size: 0.86rem; color: #475569; cursor: pointer; }}
        .filter-check input {{ width: 16px; height: 16px; accent-color: var(--sage-green); }}
        
        /* PRODUCT GRID (4 COLUMNS DESKTOP) */
        .product-grid-desktop {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
        .desktop-card {{
            background: #FFFFFF;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #E8ECEF;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s;
            display: flex;
            flex-direction: column;
            height: 100%;
        }}
        .desktop-card:hover {{ transform: translateY(-6px); box-shadow: 0 12px 28px rgba(0,0,0,0.08); border-color: var(--sage-green); }}
        .card-img-wrap {{ position: relative; height: 210px; background: #FAF7F2; overflow: hidden; }}
        .product-thumb {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }}
        .desktop-card:hover .product-thumb {{ transform: scale(1.04); }}
        .badge-discount {{ position: absolute; top: 10px; left: 10px; background: #EF4444; color: white; font-weight: 700; font-size: 0.72rem; padding: 3px 8px; border-radius: 6px; z-index: 2; }}
        .badge-cat-top {{ position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.92); color: var(--earth-brown); font-size: 0.7rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; z-index: 2; backdrop-filter: blur(4px); }}
        
        .img-toggle-bar {{ position: absolute; bottom: 8px; left: 8px; right: 8px; display: flex; gap: 4px; background: rgba(0,0,0,0.55); backdrop-filter: blur(6px); border-radius: 8px; padding: 3px; z-index: 3; }}
        .toggle-btn {{ flex: 1; border: none; background: transparent; color: #FFF; font-size: 0.68rem; font-weight: 600; padding: 4px 0; border-radius: 6px; cursor: pointer; transition: 0.15s; }}
        .toggle-btn.active {{ background: #FFFFFF; color: #1E293B; }}
        
        .card-body {{ padding: 16px; display: flex; flex-direction: column; flex-grow: 1; }}
        .rating {{ font-size: 0.75rem; color: #64748B; }}
        .product-title {{ font-size: 0.92rem; font-weight: 700; color: #1E293B; margin: 4px 0 6px; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.7em; }}
        .product-desc {{ font-size: 0.78rem; color: #64748B; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 12px; }}
        .card-footer-box {{ margin-top: auto; padding-top: 12px; border-top: 1px solid #F1F5F9; display: flex; justify-content: space-between; align-items: center; }}
        .price-val {{ font-size: 1.15rem; font-weight: 800; color: var(--warm-accent); }}
        .price-old {{ font-size: 0.78rem; color: #94A3B8; text-decoration: line-through; }}
        
        /* FOOTER */
        .desktop-footer {{ background: #FFFFFF; border-top: 1px solid #E2E8F0; padding: 48px 0 24px; margin-top: 60px; }}
        .footer-col-title {{ font-size: 0.95rem; font-weight: 700; color: #1E293B; margin-bottom: 14px; }}
        .footer-link {{ color: #64748B; font-size: 0.84rem; text-decoration: none; margin-bottom: 8px; display: block; }}
        .footer-link:hover {{ color: var(--sage-green); }}

        /* DEVICE BADGE FLOATING */
        .device-indicator {{ position: fixed; bottom: 20px; left: 20px; background: #1E293B; color: #FFF; padding: 8px 16px; border-radius: 30px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 4px 14px rgba(0,0,0,0.2); z-index: 9999; display: flex; align-items: center; gap: 8px; }}
    </style>
</head>
<body>

    <!-- DEVICE INDICATOR -->
    <div class="device-indicator">
        <span>🖥️</span> Đang xem: <strong>Giao diện Desktop (&gt;1200px)</strong>
    </div>

    <!-- TOP BAR -->
    <div class="top-promo-bar">
        <div class="desktop-container d-flex justify-content-between align-items-center">
            <div>🌿 <strong>Nếp Nhỏ D2C:</strong> Gọn một góc, nhẹ cả ngày | Miễn phí giao hàng đơn từ 299.000đ</div>
            <div class="d-flex gap-3">
                <span>📍 Giao nhanh định vị GPS</span>
                <span>📞 Hotline: 0901.234.567</span>
                <span>⚙️ <a href="/admin" class="text-white text-decoration-none">Quản trị</a></span>
            </div>
        </div>
    </div>

    <!-- HEADER -->
    <header class="desktop-header">
        <div class="desktop-container d-flex justify-content-between align-items-center">
            <a href="desktop.html" class="d-flex align-items-center text-decoration-none">
                <div>
                    <div class="brand-title">🌿 NẾP NHỎ</div>
                    <div class="brand-subtitle">Gọn một góc, nhẹ cả ngày</div>
                </div>
            </a>
            
            <div class="desktop-search-bar flex-grow-1 mx-5">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="desktop-search-input" placeholder="Tìm kiếm kệ mỹ phẩm, gương LED, hộp gấp gọn, đèn chill..." onkeyup="filterProducts()">
            </div>
            
            <div class="d-flex align-items-center gap-3">
                <div class="d-flex align-items-center gap-2 px-3 py-2 bg-light rounded-pill border" style="font-size: 0.85rem;">
                    <span>📍</span>
                    <div>
                        <div style="font-size: 0.7rem; color: #888;">Giao đến:</div>
                        <strong style="color: #333;">Q.5, TP. Hồ Chí Minh</strong>
                    </div>
                </div>
                
                <a href="#cart" class="btn btn-outline-dark position-relative rounded-pill px-3 py-2" onclick="alert('Giỏ hàng hiện có 1 sản phẩm đã thêm!')">
                    🛒 <strong>Giỏ hàng</strong>
                    <span id="cartCountBadge" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">1</span>
                </a>
            </div>
        </div>
    </header>

    <!-- NAVIGATION MENU -->
    <nav class="desktop-nav">
        <div class="desktop-container d-flex gap-1">
            <a href="#" class="nav-link-custom active" onclick="filterByCat('all')">Tất cả sản phẩm</a>
            <a href="#" class="nav-link-custom" onclick="filterByCat('Làm đẹp & Bàn trang điểm')">Làm đẹp & Bàn phấn</a>
            <a href="#" class="nav-link-custom" onclick="filterByCat('Bàn học & Làm việc')">Bàn học & Làm việc</a>
            <a href="#" class="nav-link-custom" onclick="filterByCat('Tủ đồ & Quần áo')">Tủ đồ & Quần áo</a>
            <a href="#" class="nav-link-custom" onclick="filterByCat('Phòng ngủ & Decor chill')">Phòng ngủ & Decor chill</a>
            <a href="#" class="nav-link-custom" onclick="filterByCat('Combo giải pháp toàn diện')">Combo tiết kiệm</a>
            <span class="ms-auto d-flex align-items-center text-danger fw-bold fs-7 pe-2">⚡ FLASH SALE GIẢM ĐẾN 35%</span>
        </div>
    </nav>

    <!-- MAIN BODY -->
    <main class="desktop-container">
        
        <!-- HERO BANNER -->
        <section class="hero-banner-desktop">
            <div class="row align-items-center">
                <div class="col-lg-7">
                    <span class="hero-badge">✨ GIẢI PHÁP SẮP XẾP PHÒNG TRỌ & NHÀ PHỐ GỌN GÀNG</span>
                    <h1 class="hero-title mb-3">Biến Căn Phòng Bừa Bộn Thành Góc Chill Tinh Tế Trong 15 Phút</h1>
                    <p class="text-muted fs-6 mb-4" style="max-width: 580px;">
                        Bộ phụ kiện kệ mica 360°, hộp vải kháng bụi và các giải pháp decor chuẩn phong cách Hàn Quốc giúp bạn giải phóng 70% diện tích mặt bàn.
                    </p>
                    <div class="d-flex gap-3">
                        <a href="#storeSection" class="btn btn-sage px-4 py-2 fs-6 rounded-pill">Khám phá cửa hàng ngay ↓</a>
                        <button class="btn btn-outline-dark px-4 py-2 fs-6 rounded-pill" onclick="alert('Đã kích hoạt định vị GPS tự động cho đơn hàng!')">📍 Bắt tọa độ GPS giao hàng</button>
                    </div>
                </div>
                <div class="col-lg-5 text-center">
                    <div class="position-relative d-inline-block">
                        <img src="images/combo_neptro_neptu.png" alt="Combo Nếp Nhỏ" class="rounded-4 shadow-lg" style="max-height: 280px; width: auto; object-fit: cover;">
                        <div class="position-absolute bottom-0 start-0 m-3 bg-white p-2 px-3 rounded-pill shadow-sm border" style="font-size: 0.78rem; font-weight: 700; color: #16A34A;">
                            🌿 Đã phục vụ 1,500+ bạn trẻ
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- VALUE COMMITMENTS -->
        <div class="commit-grid">
            <div class="commit-card">
                <div class="commit-icon">🚀</div>
                <div>
                    <div class="commit-title">Giao nhanh định vị GPS</div>
                    <div class="commit-desc">Chính xác tận cổng phòng trọ</div>
                </div>
            </div>
            <div class="commit-card">
                <div class="commit-icon">🔄</div>
                <div>
                    <div class="commit-title">Đổi trả 7 ngày 1:1</div>
                    <div class="commit-desc">Miễn phí nếu vỡ hoặc lỗi mica</div>
                </div>
            </div>
            <div class="commit-card">
                <div class="commit-icon">💎</div>
                <div>
                    <div class="commit-title">Chất liệu cao cấp</div>
                    <div class="commit-desc">Mica acrylic, nắp tre tự nhiên</div>
                </div>
            </div>
            <div class="commit-card">
                <div class="commit-icon">💳</div>
                <div>
                    <div class="commit-title">VietQR thanh toán 1-chạm</div>
                    <div class="commit-desc">Tự động hủy sau 24h hoàn ATP</div>
                </div>
            </div>
        </div>

        <!-- STORE LAYOUT (SIDEBAR + 4 COLUMNS PRODUCT GRID) -->
        <div id="storeSection" class="store-layout">
            
            <!-- SIDEBAR FILTER -->
            <aside class="filter-sidebar">
                <div class="filter-group-title">
                    <span>DANH MỤC</span>
                    <small class="text-muted fw-normal">({len(products)} món)</small>
                </div>
                <div class="mb-4">
                    {cat_filters}
                </div>

                <div class="filter-group-title">
                    <span>KHOẢNG GIÁ</span>
                </div>
                <div class="mb-4">
                    <label class="filter-check"><input type="radio" name="priceRange" value="all" checked onchange="filterProducts()"> <span>Tất cả mức giá</span></label>
                    <label class="filter-check"><input type="radio" name="priceRange" value="under150" onchange="filterProducts()"> <span>Dưới 150.000đ</span></label>
                    <label class="filter-check"><input type="radio" name="priceRange" value="150to300" onchange="filterProducts()"> <span>150.000đ - 300.000đ</span></label>
                    <label class="filter-check"><input type="radio" name="priceRange" value="above300" onchange="filterProducts()"> <span>Trên 300.000đ</span></label>
                </div>

                <div class="filter-group-title">
                    <span>TỒN KHO THỰC TẾ (ATP)</span>
                </div>
                <div>
                    <label class="filter-check"><input type="checkbox" checked disabled> <span>Chỉ hiện sản phẩm sẵn sàng giao</span></label>
                </div>
            </aside>

            <!-- PRODUCT DISPLAY AREA -->
            <div>
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h2 class="fs-5 fw-bold text-dark m-0">Tất Cả Sản Phẩm Sẵn Sàng Giao (<span id="visibleCount">{len(products)}</span>)</h2>
                    <div class="d-flex align-items-center gap-2">
                        <span class="fs-7 text-muted">Sắp xếp:</span>
                        <select class="form-select form-select-sm" style="width: 170px;" onchange="sortProducts(this.value)">
                            <option value="featured">Nổi bật nhất</option>
                            <option value="price-asc">Giá: Thấp đến Cao</option>
                            <option value="price-desc">Giá: Cao đến Thấp</option>
                        </select>
                    </div>
                </div>

                <!-- 4 COLUMNS PRODUCT GRID -->
                <div class="product-grid-desktop" id="productGrid">
                    {product_cards_html}
                </div>
            </div>

        </div>

    </main>

    <!-- FOOTER -->
    <footer class="desktop-footer">
        <div class="desktop-container">
            <div class="row g-4">
                <div class="col-lg-4">
                    <div class="brand-title mb-2">🌿 NẾP NHỎ</div>
                    <p class="text-muted fs-7 mb-3">Thương hiệu D2C chuyên cung cấp các giải pháp sắp xếp bàn làm việc, góc làm đẹp và không gian phòng trọ gọn gàng, tiện nghi.</p>
                    <div class="fs-7 text-muted">📍 Kho trung tâm: Phường Phước Long B, Quận 9 (TP. Thủ Đức), TP. Hồ Chí Minh</div>
                    <div class="fs-7 text-muted">📞 Hỗ trợ khách hàng: 0901.234.567 (8h00 - 22h00)</div>
                </div>
                <div class="col-lg-2">
                    <div class="footer-col-title">VỀ NẾP NHỎ</div>
                    <a href="#" class="footer-link">Câu chuyện thương hiệu</a>
                    <a href="#" class="footer-link">Giải pháp sắp xếp phòng</a>
                    <a href="#" class="footer-link">Bộ kit làm đẹp bàn phấn</a>
                    <a href="#" class="footer-link">Tuyển dụng</a>
                </div>
                <div class="col-lg-3">
                    <div class="footer-col-title">CHÍNH SÁCH BÁN HÀNG</div>
                    <a href="#" class="footer-link">Chính sách vận chuyển GPS</a>
                    <a href="#" class="footer-link">Bảo hành vỡ hỏng 1 đổi 1</a>
                    <a href="#" class="footer-link">Chính sách thanh toán VietQR</a>
                    <a href="#" class="footer-link">Hướng dẫn tự hủy đơn sau 24h</a>
                </div>
                <div class="col-lg-3">
                    <div class="footer-col-title">THANH TOÁN TIỆN LỢI</div>
                    <div class="d-flex gap-2 mb-2">
                        <span class="badge bg-light text-dark border p-2">🏦 VietQR 1-Chạm</span>
                        <span class="badge bg-light text-dark border p-2">💵 Tiền mặt (COD)</span>
                    </div>
                    <div class="p-3 bg-light rounded-3 border fs-7 text-muted">
                        🔒 Hệ thống xác nhận thanh toán mã QR tự động cập nhật trạng thái đơn hàng tức thời.
                    </div>
                </div>
            </div>
            <div class="border-top mt-4 pt-3 text-center text-muted fs-7">
                © 2026 Nếp Nhỏ — Gọn một góc, nhẹ cả ngày.
            </div>
        </div>
    </footer>

    <!-- PRODUCT DETAIL MODAL -->
    <div class="modal fade" id="productModal" tabindex="-1">
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content rounded-4 border-0 overflow-hidden">
                <div class="modal-header border-0 bg-light p-4 pb-2">
                    <h5 class="modal-title fw-bold" id="modalTitle">Chi tiết sản phẩm</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4 pt-2">
                    <div class="row g-4">
                        <div class="col-md-6">
                            <div class="rounded-3 overflow-hidden border mb-2" style="height: 280px;">
                                <img id="modalMainImg" src="" class="w-100 h-100 object-fit-cover" alt="">
                            </div>
                            <div class="d-flex gap-2">
                                <button id="btnModalAfter" class="btn btn-sm btn-outline-dark flex-fill" onclick="setModalImg('after')">Ảnh Sau (Gọn gàng)</button>
                                <button id="btnModalBefore" class="btn btn-sm btn-outline-secondary flex-fill" onclick="setModalImg('before')">Ảnh Trước (Bừa bộn)</button>
                            </div>
                        </div>
                        <div class="col-md-6 d-flex flex-column">
                            <span class="badge bg-success bg-opacity-10 text-success p-2 mb-2 w-fit" id="modalCat"></span>
                            <div class="price-val fs-3 mb-1" id="modalPrice"></div>
                            <div class="text-muted fs-7 mb-3 text-decoration-line-through" id="modalOldPrice"></div>
                            <p class="text-muted fs-7 mb-3" id="modalDesc"></p>
                            
                            <div class="p-3 bg-light rounded-3 mb-3">
                                <strong class="fs-7 text-dark d-block mb-1">📦 Bộ kit bao gồm:</strong>
                                <ul class="m-0 ps-3 fs-7 text-muted" id="modalKitList"></ul>
                            </div>

                            <div class="mt-auto d-flex gap-2">
                                <button class="btn btn-outline-dark flex-fill py-2" onclick="addToCartModal()">🛒 Thêm vào giỏ</button>
                                <button class="btn btn-sage flex-fill py-2" onclick="alert('Chuyển hướng đến màn hình thanh toán VietQR!')">Mua ngay</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const productsData = {products_json_str};
        let currentModalPid = null;

        function switchImg(pid, src, btn) {{
            const img = document.getElementById('img-' + pid);
            if (img) img.src = src;
            const parent = btn.parentElement;
            parent.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }}

        function filterProducts() {{
            const search = document.getElementById('searchInput').value.toLowerCase().trim();
            const checkedCats = Array.from(document.querySelectorAll('input[name="cat"]:checked')).map(el => el.value);
            const priceVal = document.querySelector('input[name="priceRange"]:checked').value;
            
            let count = 0;
            document.querySelectorAll('.desktop-card-col').forEach(card => {{
                const name = card.getAttribute('data-name');
                const cat = card.getAttribute('data-cat');
                const price = parseInt(card.getAttribute('data-price')) || 0;

                let matchSearch = !search || name.includes(search);
                let matchCat = checkedCats.length === 0 || checkedCats.includes(cat);
                let matchPrice = true;
                if (priceVal === 'under150') matchPrice = price < 150000;
                else if (priceVal === '150to300') matchPrice = price >= 150000 && price <= 300000;
                else if (priceVal === 'above300') matchPrice = price > 300000;

                if (matchSearch && matchCat && matchPrice) {{
                    card.style.display = '';
                    count++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});
            document.getElementById('visibleCount').innerText = count;
        }}

        function filterByCat(catName) {{
            document.querySelectorAll('.nav-link-custom').forEach(l => l.classList.remove('active'));
            event.target.classList.add('active');
            
            document.querySelectorAll('input[name="cat"]').forEach(input => {{
                input.checked = (catName !== 'all' && input.value === catName);
            }});
            filterProducts();
        }}

        function sortProducts(type) {{
            const grid = document.getElementById('productGrid');
            const cards = Array.from(grid.children);
            cards.sort((a, b) => {{
                const priceA = parseInt(a.getAttribute('data-price')) || 0;
                const priceB = parseInt(b.getAttribute('data-price')) || 0;
                if (type === 'price-asc') return priceA - priceB;
                if (type === 'price-desc') return priceB - priceA;
                return 0;
            }});
            cards.forEach(card => grid.appendChild(card));
        }}

        let cartTotal = 1;
        function addToCartMock(name) {{
            cartTotal++;
            document.getElementById('cartCountBadge').innerText = cartTotal;
            alert('Đã thêm thành công: ' + name + ' vào giỏ hàng!');
        }}

        const modalEl = new bootstrap.Modal(document.getElementById('productModal'));
        function openDetailModal(pid) {{
            currentModalPid = pid;
            const p = productsData[pid];
            if (!p) return;
            document.getElementById('modalTitle').innerText = p.name;
            document.getElementById('modalCat').innerText = p.category;
            document.getElementById('modalPrice').innerText = p.price.toLocaleString() + 'đ';
            document.getElementById('modalOldPrice').innerText = p.original_price ? p.original_price.toLocaleString() + 'đ' : '';
            document.getElementById('modalDesc').innerText = p.description;
            
            const kitList = document.getElementById('modalKitList');
            kitList.innerHTML = '';
            (p.kit_components || []).forEach(item => {{
                const li = document.createElement('li');
                li.innerText = item;
                kitList.appendChild(li);
            }});
            
            setModalImg('after');
            modalEl.show();
        }}

        function setModalImg(type) {{
            if (!currentModalPid) return;
            const p = productsData[currentModalPid];
            const clean = (url) => url ? (url.startsWith('/') ? url.substring(1) : url) : '';
            const src = (type === 'after') ? clean(p.after_img) : clean(p.before_img);
            document.getElementById('modalMainImg').src = src;
            
            document.getElementById('btnModalAfter').className = (type === 'after') ? 'btn btn-sm btn-dark flex-fill' : 'btn btn-sm btn-outline-dark flex-fill';
            document.getElementById('btnModalBefore').className = (type === 'before') ? 'btn btn-sm btn-dark flex-fill' : 'btn btn-sm btn-outline-dark flex-fill';
        }}

        function addToCartModal() {{
            if (currentModalPid && productsData[currentModalPid]) {{
                addToCartMock(productsData[currentModalPid].name);
                modalEl.hide();
            }}
        }}
    </script>
</body>
</html>
"""
    return html

# ==============================================================================
# 2. TABLET HTML
# ==============================================================================
def generate_tablet():
    product_cards_html = ""
    for pid, p in products.items():
        discount = int(((p['original_price'] - p['price']) / p['original_price']) * 100) if p.get('original_price', 0) > p['price'] else 0
        img_after = clean_img(p.get('after_img'))
        img_before = clean_img(p.get('before_img'))
        stock_atp = p.get('stock_physical', 50) - p.get('stock_committed', 0)
        
        product_cards_html += f"""
        <div class="tablet-card" data-cat="{p.get('category','')}" data-name="{p.get('name','').lower()}">
            <div class="tablet-img-wrap">
                <span class="badge-discount">-{discount}%</span>
                <img id="tab-img-{pid}" src="{img_after}" alt="{p.get('name','')}" class="tablet-thumb">
                <div class="touch-before-after">
                    <button class="touch-btn active" onclick="switchTabletImg('{pid}', '{img_after}', this)">Sau</button>
                    <button class="touch-btn" onclick="switchTabletImg('{pid}', '{img_before}', this)">Trước</button>
                </div>
            </div>
            <div class="tablet-card-body">
                <span class="badge-cat mb-1 d-inline-block">{p.get('category','')}</span>
                <h4 class="tablet-title">{p.get('name','')}</h4>
                <div class="badge-atp mb-2">⚡ Sẵn giao: {stock_atp} món</div>
                <div class="d-flex justify-content-between align-items-center mt-auto pt-2 border-top">
                    <div>
                        <div class="price-val">{p.get('price', 0):,}đ</div>
                        <div class="price-old">{p.get('original_price', 0):,}đ</div>
                    </div>
                    <button class="btn btn-sage px-3 py-2" onclick="alert('Đã thêm {p.get('name','')} vào giỏ!')">🛒 Mua</button>
                </div>
            </div>
        </div>
        """

    cats = sorted(list(set(p.get('category','') for p in products.values() if p.get('category'))))
    cat_pills = '<button class="tab-pill active" onclick="filterTabletCat(\'all\', this)">Tất cả</button>' + "".join([f'<button class="tab-pill" onclick="filterTabletCat(\'{c}\', this)">{c}</button>' for c in cats])

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 Nếp Nhỏ — Tablet Interface (Giao diện Máy Tính Bảng 768px-1024px)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        {COMMON_CSS}
        /* TABLET OPTIMIZED CONTAINER */
        body {{ max-width: 900px; margin: 0 auto; background: #FAF8F5; }}
        .tablet-header {{ background: #FFFFFF; padding: 14px 20px; border-bottom: 2px solid var(--sage-green); position: sticky; top: 0; z-index: 100; }}
        .tablet-brand {{ font-weight: 800; font-size: 1.4rem; color: var(--earth-brown); text-decoration: none; }}
        
        /* TOUCH SCROLLABLE PILLS */
        .tablet-pills-bar {{ display: flex; gap: 8px; overflow-x: auto; padding: 12px 20px; background: #FFFFFF; border-bottom: 1px solid #E2E8F0; scrollbar-width: none; }}
        .tablet-pills-bar::-webkit-scrollbar {{ display: none; }}
        .tab-pill {{ white-space: nowrap; border: 1px solid #E2E8F0; background: #F8FAFC; padding: 8px 16px; border-radius: 20px; font-size: 0.84rem; font-weight: 600; color: #475569; cursor: pointer; transition: 0.2s; }}
        .tab-pill.active {{ background: var(--sage-green); color: #FFF; border-color: var(--sage-green); }}

        /* HERO TABLET */
        .tablet-hero {{ background: linear-gradient(135deg, #EFE7DA, #E3D6C1); border-radius: 16px; padding: 24px; margin: 16px 20px; }}
        
        /* 3 COLUMNS GRID TABLET */
        .tablet-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding: 0 20px 80px; }}
        @media (max-width: 768px) {{
            .tablet-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        .tablet-card {{ background: #FFFFFF; border-radius: 14px; border: 1px solid #E2E8F0; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 3px 10px rgba(0,0,0,0.03); }}
        .tablet-img-wrap {{ position: relative; height: 180px; background: #F1ECE1; }}
        .tablet-thumb {{ width: 100%; height: 100%; object-fit: cover; }}
        .badge-discount {{ position: absolute; top: 8px; left: 8px; background: #EF4444; color: #FFF; font-size: 0.7rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }}
        .touch-before-after {{ position: absolute; bottom: 6px; left: 6px; right: 6px; display: flex; gap: 4px; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); border-radius: 6px; padding: 2px; }}
        .touch-btn {{ flex: 1; border: none; background: transparent; color: #FFF; font-size: 0.65rem; font-weight: 600; padding: 4px 0; border-radius: 4px; }}
        .touch-btn.active {{ background: #FFF; color: #1E293B; }}
        .tablet-card-body {{ padding: 12px; display: flex; flex-direction: column; flex-grow: 1; }}
        .tablet-title {{ font-size: 0.85rem; font-weight: 700; color: #1E293B; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.6em; }}
        .price-val {{ font-size: 1.05rem; font-weight: 800; color: var(--warm-accent); }}
        .price-old {{ font-size: 0.72rem; color: #94A3B8; text-decoration: line-through; }}

        /* FLOATING TABLET BOTTOM BAR */
        .tablet-bottom-bar {{ position: fixed; bottom: 0; left: 0; right: 0; max-width: 900px; margin: 0 auto; background: #FFFFFF; border-top: 1px solid #CBD5E1; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 -4px 16px rgba(0,0,0,0.05); z-index: 100; }}
        .device-indicator {{ position: fixed; top: 70px; right: 20px; background: #1E293B; color: #FFF; padding: 6px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; z-index: 999; }}
    </style>
</head>
<body>

    <div class="device-indicator">📱 Giao diện Tablet (iPad 768px-1024px)</div>

    <!-- TABLET HEADER -->
    <header class="tablet-header d-flex justify-content-between align-items-center">
        <a href="tablet.html" class="tablet-brand">🌿 NẾP NHỎ</a>
        <div class="d-flex align-items-center gap-2 flex-grow-1 mx-3" style="max-width: 380px;">
            <input type="text" id="tabletSearch" class="form-control rounded-pill form-control-sm px-3" placeholder="🔍 Tìm kiếm sản phẩm..." onkeyup="filterTabletSearch()">
        </div>
        <div class="d-flex align-items-center gap-2">
            <span class="badge bg-light text-dark border p-2" style="font-size: 0.75rem;">📍 Q.5</span>
            <button class="btn btn-outline-dark btn-sm rounded-pill px-3" onclick="alert('Giỏ hàng có 1 sản phẩm')">🛒 (1)</button>
        </div>
    </header>

    <!-- HORIZONTAL SCROLLABLE PILLS -->
    <div class="tablet-pills-bar">
        {cat_pills}
    </div>

    <!-- TABLET HERO -->
    <div class="tablet-hero d-flex justify-content-between align-items-center">
        <div>
            <span class="badge bg-success bg-opacity-75 text-white px-2 py-1 rounded-pill mb-1" style="font-size: 0.7rem;">✨ Giao hàng chuẩn GPS</span>
            <h2 class="fs-4 fw-bold text-dark m-0">Gọn Một Góc, Nhẹ Cả Ngày</h2>
            <p class="text-muted fs-7 mt-1 mb-2">Trải nghiệm mua sắm tối ưu cảm ứng mượt mà trên iPad & Tablet.</p>
            <button class="btn btn-sage btn-sm px-3 py-2 rounded-pill" onclick="alert('Bật GPS thành công')">📍 Bắt GPS giao tận cửa</button>
        </div>
        <img src="images/ke_dung_my_pham.png" alt="Hero" style="height: 110px; width: auto; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    </div>

    <!-- TABLET GRID -->
    <div class="px-3 mb-2 d-flex justify-content-between align-items-center">
        <span class="fw-bold fs-6 text-dark">Sản Phẩm Khuyên Dùng</span>
        <span class="fs-7 text-muted">Vuốt để chọn Trước / Sau</span>
    </div>
    
    <div class="tablet-grid" id="tabletGrid">
        {product_cards_html}
    </div>

    <!-- TABLET BOTTOM BAR -->
    <div class="tablet-bottom-bar">
        <div class="d-flex align-items-center gap-2">
            <span class="fs-5">🛒</span>
            <div>
                <strong style="font-size: 0.85rem;">Giỏ hàng của bạn:</strong>
                <span class="text-muted fs-7">1 món • 149.000đ</span>
            </div>
        </div>
        <button class="btn btn-sage px-4 py-2" onclick="alert('Tiến hành chuyển hướng sang cổng VietQR...')">Tiến hành đặt hàng →</button>
    </div>

    <script>
        function switchTabletImg(pid, src, btn) {{
            const img = document.getElementById('tab-img-' + pid);
            if (img) img.src = src;
            const parent = btn.parentElement;
            parent.querySelectorAll('.touch-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }}

        function filterTabletCat(cat, btn) {{
            document.querySelectorAll('.tab-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            document.querySelectorAll('.tablet-card').forEach(card => {{
                const cardCat = card.getAttribute('data-cat');
                card.style.display = (cat === 'all' || cardCat === cat) ? '' : 'none';
            }});
        }}

        function filterTabletSearch() {{
            const s = document.getElementById('tabletSearch').value.toLowerCase().trim();
            document.querySelectorAll('.tablet-card').forEach(card => {{
                const name = card.getAttribute('data-name');
                card.style.display = (!s || name.includes(s)) ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>
"""
    return html

# ==============================================================================
# 3. MOBILE HTML
# ==============================================================================
def generate_mobile():
    product_cards_html = ""
    for pid, p in products.items():
        discount = int(((p['original_price'] - p['price']) / p['original_price']) * 100) if p.get('original_price', 0) > p['price'] else 0
        img_after = clean_img(p.get('after_img'))
        img_before = clean_img(p.get('before_img'))
        stock_atp = p.get('stock_physical', 50) - p.get('stock_committed', 0)

        product_cards_html += f"""
        <div class="mobile-card" data-cat="{p.get('category','')}" data-name="{p.get('name','').lower()}">
            <div class="mobile-thumb-wrap">
                <span class="mobile-discount">-{discount}%</span>
                <img id="mob-img-{pid}" src="{img_after}" alt="{p.get('name','')}" class="mobile-thumb">
                <div class="mobile-img-switch">
                    <span class="active" onclick="switchMobImg('{pid}', '{img_after}', this)">Sau</span>
                    <span onclick="switchMobImg('{pid}', '{img_before}', this)">Trước</span>
                </div>
            </div>
            <div class="mobile-card-content">
                <h4 class="mobile-title">{p.get('name','')}</h4>
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="price-val fs-6">{p.get('price', 0):,}đ</span>
                    <span class="mobile-atp-tag">Sẵn {stock_atp}</span>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="price-old">{p.get('original_price', 0):,}đ</span>
                    <button class="mobile-buy-btn" onclick="openMobSheet('{p.get('name','')}', '{p.get('price', 0):,}đ', '{img_after}')">🛒 Mua</button>
                </div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>🌿 Nếp Nhỏ — Mobile App Interface (Giao diện Điện Thoại 375px-430px)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        {COMMON_CSS}
        /* MOBILE APP CONTAINER */
        body {{
            max-width: 430px;
            margin: 0 auto;
            background: #F7F5F0;
            padding-bottom: 74px; /* Space for bottom nav */
            box-shadow: 0 0 30px rgba(0,0,0,0.1);
            min-height: 100vh;
            position: relative;
        }}
        
        /* PHONE STATUS BAR SIMULATION */
        .phone-status-bar {{
            background: #FFFFFF;
            padding: 8px 16px 4px;
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            font-weight: 700;
            color: #1E293B;
            border-bottom: 1px solid #F1F5F9;
        }}

        /* APP HEADER */
        .mobile-header {{
            background: #FFFFFF;
            padding: 10px 14px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }}
        .mobile-search-pill {{
            background: #F1F5F9;
            border-radius: 20px;
            padding: 6px 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            color: #64748B;
        }}
        .mobile-search-input {{
            border: none;
            background: transparent;
            outline: none;
            width: 100%;
            font-size: 0.8rem;
        }}
        
        /* GPS STRIP */
        .mobile-gps-strip {{
            background: #ECFDF5;
            color: #065F46;
            font-size: 0.72rem;
            padding: 6px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #A7F3D0;
        }}

        /* CATEGORY STORIES / CIRCLES */
        .story-circles-wrap {{
            display: flex;
            gap: 12px;
            overflow-x: auto;
            padding: 14px 14px 6px;
            scrollbar-width: none;
        }}
        .story-circles-wrap::-webkit-scrollbar {{ display: none; }}
        .story-item {{ display: flex; flex-direction: column; align-items: center; min-width: 62px; text-decoration: none; }}
        .story-circle {{
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: #FFFFFF;
            border: 2px solid var(--sage-green);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
            margin-bottom: 4px;
        }}
        .story-label {{ font-size: 0.68rem; font-weight: 600; color: #334155; text-align: center; line-height: 1.2; }}

        /* MOBILE BANNER */
        .mobile-banner {{
            margin: 10px 14px;
            border-radius: 14px;
            background: linear-gradient(135deg, #7D9D7C, #5C7A5B);
            color: #FFF;
            padding: 16px;
            position: relative;
            overflow: hidden;
        }}
        .mobile-banner-title {{ font-size: 1.05rem; font-weight: 800; margin-bottom: 4px; }}
        .mobile-banner-desc {{ font-size: 0.75rem; opacity: 0.9; margin-bottom: 10px; }}

        /* FLASH SALE TICKER */
        .mobile-flash-bar {{
            margin: 6px 14px 10px;
            background: #FEF2F2;
            border: 1px solid #FCA5A5;
            border-radius: 10px;
            padding: 8px 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            font-weight: 700;
            color: #DC2626;
        }}
        .countdown-box {{ background: #DC2626; color: #FFF; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; }}

        /* 2 COLUMNS MOBILE GRID */
        .mobile-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            padding: 0 14px;
        }}
        .mobile-card {{
            background: #FFFFFF;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #E8ECEF;
            display: flex;
            flex-direction: column;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }}
        .mobile-thumb-wrap {{ position: relative; height: 140px; background: #F1ECE1; }}
        .mobile-thumb {{ width: 100%; height: 100%; object-fit: cover; }}
        .mobile-discount {{ position: absolute; top: 6px; left: 6px; background: #EF4444; color: #FFF; font-size: 0.65rem; font-weight: 700; padding: 2px 5px; border-radius: 4px; }}
        .mobile-img-switch {{
            position: absolute;
            bottom: 4px;
            left: 4px;
            right: 4px;
            display: flex;
            background: rgba(0,0,0,0.6);
            border-radius: 4px;
            padding: 1px;
        }}
        .mobile-img-switch span {{
            flex: 1;
            text-align: center;
            color: #FFF;
            font-size: 0.6rem;
            padding: 2px 0;
            cursor: pointer;
            border-radius: 3px;
        }}
        .mobile-img-switch span.active {{ background: #FFF; color: #1E293B; font-weight: 700; }}
        .mobile-card-content {{ padding: 10px; display: flex; flex-direction: column; flex-grow: 1; }}
        .mobile-title {{ font-size: 0.78rem; font-weight: 700; color: #1E293B; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.6em; line-height: 1.3; }}
        .mobile-atp-tag {{ font-size: 0.65rem; background: #E8F5E9; color: #2E7D32; padding: 1px 4px; border-radius: 4px; font-weight: 600; }}
        .mobile-buy-btn {{ background: var(--sage-green); color: #FFF; border: none; font-size: 0.72rem; font-weight: 700; padding: 4px 8px; border-radius: 6px; }}
        .price-old {{ font-size: 0.7rem; color: #94A3B8; text-decoration: line-through; }}

        /* FIXED BOTTOM NAVIGATION BAR */
        .mobile-bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 430px;
            background: #FFFFFF;
            border-top: 1px solid #E2E8F0;
            display: flex;
            justify-content: space-around;
            padding: 8px 0;
            z-index: 1000;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.06);
        }}
        .nav-tab-item {{ display: flex; flex-direction: column; align-items: center; text-decoration: none; color: #64748B; font-size: 0.65rem; font-weight: 600; }}
        .nav-tab-item.active {{ color: var(--sage-green); font-weight: 700; }}
        .nav-tab-icon {{ font-size: 1.25rem; margin-bottom: 1px; position: relative; }}
        .badge-cart-mob {{ position: absolute; top: -4px; right: -8px; background: #EF4444; color: #FFF; font-size: 0.58rem; padding: 1px 4px; border-radius: 10px; font-weight: 700; }}

        /* BOTTOM SHEET DIALOG */
        .bottom-sheet-overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 2000; display: none; align-items: flex-end; justify-content: center; }}
        .bottom-sheet-overlay.active {{ display: flex; }}
        .bottom-sheet-box {{ background: #FFFFFF; width: 100%; max-width: 430px; border-radius: 20px 20px 0 0; padding: 20px; animation: slideUp 0.3s ease; }}
        @keyframes slideUp {{ from {{ transform: translateY(100%); }} to {{ transform: translateY(0); }} }}

        .device-indicator {{ position: fixed; top: 38px; right: 10px; background: #1E293B; color: #FFF; padding: 4px 10px; border-radius: 14px; font-size: 0.68rem; font-weight: 600; z-index: 999; }}
    </style>
</head>
<body>

    <!-- DEVICE INDICATOR -->
    <div class="device-indicator">📲 Giao diện Mobile (375px-430px)</div>

    <!-- PHONE STATUS BAR -->
    <div class="phone-status-bar">
        <span>09:41</span>
        <span>5G 📶 • 100% 🔋</span>
    </div>

    <!-- APP HEADER -->
    <header class="mobile-header">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="fw-bold fs-6 text-dark">🌿 NẾP NHỎ D2C</span>
            <div class="d-flex gap-2">
                <span class="fs-6" onclick="alert('Không có thông báo mới!')">🔔</span>
                <span class="fs-6" onclick="alert('Đã đồng bộ đơn hàng với số điện thoại!')">💬</span>
            </div>
        </div>
        <div class="mobile-search-pill">
            <span>🔍</span>
            <input type="text" id="mobSearch" class="mobile-search-input" placeholder="Tìm kệ mỹ phẩm, gương LED, đèn chill..." onkeyup="filterMob()">
        </div>
    </header>

    <!-- GPS STRIP -->
    <div class="mobile-gps-strip">
        <span>📍 Giao tận nơi: <strong>123 Nguyễn Văn Cừ, Q.5, TP.HCM</strong></span>
        <span class="fw-bold" onclick="alert('Đã cập nhật tọa độ GPS chính xác!')">Đổi GPS</span>
    </div>

    <!-- CATEGORY STORIES HORIZONTAL -->
    <div class="story-circles-wrap">
        <div class="story-item" onclick="filterMobCat('all')">
            <div class="story-circle">✨</div>
            <div class="story-label">Tất cả</div>
        </div>
        <div class="story-item" onclick="filterMobCat('Làm đẹp & Bàn trang điểm')">
            <div class="story-circle">💄</div>
            <div class="story-label">Bàn phấn</div>
        </div>
        <div class="story-item" onclick="filterMobCat('Bàn học & Làm việc')">
            <div class="story-circle">💻</div>
            <div class="story-label">Bàn học</div>
        </div>
        <div class="story-item" onclick="filterMobCat('Tủ đồ & Quần áo')">
            <div class="story-circle">👗</div>
            <div class="story-label">Tủ đồ</div>
        </div>
        <div class="story-item" onclick="filterMobCat('Phòng ngủ & Decor chill')">
            <div class="story-circle">🌙</div>
            <div class="story-label">Decor chill</div>
        </div>
        <div class="story-item" onclick="filterMobCat('Combo giải pháp toàn diện')">
            <div class="story-circle">🎁</div>
            <div class="story-label">Combo</div>
        </div>
    </div>

    <!-- MOBILE BANNER -->
    <div class="mobile-banner">
        <div class="mobile-banner-title">GỌN GÀNG GÓC PHÒNG TRỌ</div>
        <div class="mobile-banner-desc">Giải phóng 70% mặt bàn với bộ kệ mica cao cấp.</div>
        <button class="btn btn-light btn-sm rounded-pill px-3 py-1 fw-bold fs-7" onclick="alert('Mã NEPNHO20 giảm 20k đã áp dụng!')">Lấy mã giảm 20K</button>
    </div>

    <!-- FLASH SALE BAR -->
    <div class="mobile-flash-bar">
        <span>⚡ FLASH SALE HÔM NAY</span>
        <div class="d-flex align-items-center gap-1">
            <span>Kết thúc sau:</span>
            <span class="countdown-box">02</span>:
            <span class="countdown-box">45</span>:
            <span class="countdown-box">18</span>
        </div>
    </div>

    <!-- 2 COLUMNS PRODUCT GRID -->
    <div class="mobile-grid" id="mobileGrid">
        {product_cards_html}
    </div>

    <!-- FIXED BOTTOM NAVIGATION BAR -->
    <nav class="mobile-bottom-nav">
        <a href="mobile.html" class="nav-tab-item active">
            <span class="nav-tab-icon">🏠</span>
            <span>Trang chủ</span>
        </a>
        <a href="#category" class="nav-tab-item" onclick="alert('Chuyển tới danh mục sản phẩm')">
            <span class="nav-tab-icon">📑</span>
            <span>Danh mục</span>
        </a>
        <a href="#sale" class="nav-tab-item" onclick="alert('Khám phá mã giảm giá Flash Sale')">
            <span class="nav-tab-icon">⚡</span>
            <span>Ưu đãi</span>
        </a>
        <a href="#cart" class="nav-tab-item" onclick="alert('Mở giỏ hàng di động')">
            <span class="nav-tab-icon">🛒<span class="badge-cart-mob" id="mobBadge">1</span></span>
            <span>Giỏ hàng</span>
        </a>
        <a href="#user" class="nav-tab-item" onclick="alert('Trang cá nhân & Lịch sử đơn hàng')">
            <span class="nav-tab-icon">👤</span>
            <span>Tôi</span>
        </a>
    </nav>

    <!-- BOTTOM SHEET FOR QUICK BUY -->
    <div class="bottom-sheet-overlay" id="bottomSheet" onclick="closeMobSheet(event)">
        <div class="bottom-sheet-box" onclick="event.stopPropagation()">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold m-0 fs-6" id="sheetTitle">Mua hàng</h5>
                <button class="btn-close btn-sm" onclick="closeMobSheetDirect()"></button>
            </div>
            <div class="d-flex gap-3 mb-3">
                <img id="sheetImg" src="" style="width: 70px; height: 70px; object-fit: cover; border-radius: 8px;" alt="">
                <div>
                    <div class="price-val fs-5" id="sheetPrice"></div>
                    <span class="badge bg-success bg-opacity-10 text-success fs-7">Sẵn sàng giao tận cửa</span>
                </div>
            </div>
            <button class="btn btn-sage w-100 py-2 fw-bold mb-2" onclick="confirmMobBuy()">Xác nhận mua ngay (VietQR 1-Chạm)</button>
            <button class="btn btn-outline-dark w-100 py-2 fs-7" onclick="closeMobSheetDirect()">Để xem thêm</button>
        </div>
    </div>

    <script>
        function switchMobImg(pid, src, span) {{
            const img = document.getElementById('mob-img-' + pid);
            if (img) img.src = src;
            const parent = span.parentElement;
            parent.querySelectorAll('span').forEach(s => s.classList.remove('active'));
            span.classList.add('active');
        }}

        function filterMobCat(cat) {{
            document.querySelectorAll('.mobile-card').forEach(card => {{
                const cardCat = card.getAttribute('data-cat');
                card.style.display = (cat === 'all' || cardCat === cat) ? '' : 'none';
            }});
        }}

        function filterMob() {{
            const s = document.getElementById('mobSearch').value.toLowerCase().trim();
            document.querySelectorAll('.mobile-card').forEach(card => {{
                const name = card.getAttribute('data-name');
                card.style.display = (!s || name.includes(s)) ? '' : 'none';
            }});
        }}

        function openMobSheet(name, price, img) {{
            document.getElementById('sheetTitle').innerText = name;
            document.getElementById('sheetPrice').innerText = price;
            document.getElementById('sheetImg').src = img;
            document.getElementById('bottomSheet').classList.add('active');
        }}

        function closeMobSheet(e) {{
            document.getElementById('bottomSheet').classList.remove('active');
        }}

        function closeMobSheetDirect() {{
            document.getElementById('bottomSheet').classList.remove('active');
        }}

        let mobCart = 1;
        function confirmMobBuy() {{
            mobCart++;
            document.getElementById('mobBadge').innerText = mobCart;
            alert('Đã tạo đơn hàng thành công! Vui lòng quét mã VietQR tự động.');
            closeMobSheetDirect();
        }}
    </script>
</body>
</html>
"""
    return html

# ==============================================================================
# 4. MASTER DEMO 3 DEVICES HTML (Interactive Device Switcher & Mockups)
# ==============================================================================
def generate_master_demo():
    html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 Nếp Nhỏ — Bộ Trình Diễn 3 Giao Diện: Desktop • Tablet • Mobile</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bar-bg: #1E293B;
            --accent: #7D9D7C;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0F172A; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }
        
        /* TOP CONTROLLER BAR */
        .showcase-nav {
            background: var(--bar-bg);
            color: #FFFFFF;
            padding: 10px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            z-index: 100;
        }
        .showcase-brand { font-weight: 800; font-size: 1.15rem; color: #FFF; display: flex; align-items: center; gap: 8px; }
        .mode-btn-group { display: flex; background: #0F172A; padding: 4px; border-radius: 10px; border: 1px solid #334155; }
        .mode-btn {
            background: transparent;
            color: #94A3B8;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .mode-btn:hover { color: #FFF; }
        .mode-btn.active { background: var(--accent); color: #FFF; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }

        /* VIEWPORT WRAPPER */
        .viewport-wrapper {
            flex-grow: 1;
            background: #0B1120;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
            padding: 20px;
        }

        /* DEVICE FRAMES */
        .device-frame {
            background: #FFFFFF;
            box-shadow: 0 25px 60px rgba(0,0,0,0.5);
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        /* 1. DESKTOP MODE */
        .mode-desktop-view {
            width: 100%;
            height: 100%;
            border-radius: 8px;
            border: 1px solid #334155;
        }

        /* 2. TABLET MODE (IPAD) */
        .mode-tablet-view {
            width: 820px;
            height: 92vh;
            border-radius: 28px;
            border: 12px solid #1E293B;
            box-shadow: 0 0 0 2px #475569;
        }

        /* 3. MOBILE MODE (IPHONE) */
        .mode-mobile-view {
            width: 410px;
            height: 92vh;
            border-radius: 44px;
            border: 12px solid #1E293B;
            box-shadow: 0 0 0 2px #475569;
            position: relative;
        }
        .notch-bar {
            width: 120px;
            height: 24px;
            background: #1E293B;
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            border-bottom-left-radius: 14px;
            border-bottom-right-radius: 14px;
            z-index: 10;
        }

        /* 4. ALL 3 SIDE-BY-SIDE MODE */
        .mode-all-view {
            display: flex;
            gap: 24px;
            align-items: flex-start;
            height: 94%;
            width: 100%;
            justify-content: center;
        }
        .side-col {
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100%;
        }
        .side-title {
            color: #94A3B8;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .side-frame-desktop {
            width: 620px;
            height: 88%;
            border-radius: 12px;
            border: 8px solid #1E293B;
        }
        .side-frame-tablet {
            width: 440px;
            height: 88%;
            border-radius: 20px;
            border: 8px solid #1E293B;
        }
        .side-frame-mobile {
            width: 320px;
            height: 88%;
            border-radius: 28px;
            border: 8px solid #1E293B;
        }

        iframe {
            width: 100%;
            height: 100%;
            border: none;
            background: #FFFFFF;
        }
    </style>
</head>
<body>

    <!-- TOP CONTROL BAR -->
    <div class="showcase-nav">
        <div class="showcase-brand">
            <span>🌿</span>
            <span>NẾP NHỎ D2C • BỘ 3 GIAO DIỆN TMĐT</span>
        </div>

        <div class="mode-btn-group">
            <button class="mode-btn active" onclick="setMode('desktop')">
                <span>🖥️</span> Desktop (&gt;1200px)
            </button>
            <button class="mode-btn" onclick="setMode('tablet')">
                <span>📱</span> Tablet (iPad)
            </button>
            <button class="mode-btn" onclick="setMode('mobile')">
                <span>📲</span> Mobile (iPhone)
            </button>
            <button class="mode-btn" onclick="setMode('all')">
                <span>🔲</span> Xem cả 3 cùng lúc (Side-by-Side)
            </button>
        </div>

        <div class="d-flex gap-2">
            <a href="desktop.html" target="_blank" class="btn btn-sm btn-outline-light">Mở Desktop ↗</a>
            <a href="tablet.html" target="_blank" class="btn btn-sm btn-outline-light">Mở Tablet ↗</a>
            <a href="mobile.html" target="_blank" class="btn btn-sm btn-outline-light">Mở Mobile ↗</a>
        </div>
    </div>

    <!-- MAIN VIEWPORT CONTAINER -->
    <div class="viewport-wrapper" id="viewport">
        <!-- Rendered via JS -->
    </div>

    <script>
        const viewport = document.getElementById('viewport');

        function setMode(mode) {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            event.target.closest('.mode-btn').classList.add('active');

            if (mode === 'desktop') {
                viewport.innerHTML = `
                    <div class="device-frame mode-desktop-view">
                        <iframe src="desktop.html"></iframe>
                    </div>
                `;
            } else if (mode === 'tablet') {
                viewport.innerHTML = `
                    <div class="device-frame mode-tablet-view">
                        <iframe src="tablet.html"></iframe>
                    </div>
                `;
            } else if (mode === 'mobile') {
                viewport.innerHTML = `
                    <div class="device-frame mode-mobile-view">
                        <div class="notch-bar"></div>
                        <iframe src="mobile.html"></iframe>
                    </div>
                `;
            } else if (mode === 'all') {
                viewport.innerHTML = `
                    <div class="mode-all-view">
                        <div class="side-col">
                            <div class="side-title">🖥️ 1. Giao diện Desktop (1440 x 900)</div>
                            <div class="device-frame side-frame-desktop">
                                <iframe src="desktop.html"></iframe>
                            </div>
                        </div>
                        <div class="side-col">
                            <div class="side-title">📱 2. Giao diện Tablet (820 x 1180)</div>
                            <div class="device-frame side-frame-tablet">
                                <iframe src="tablet.html"></iframe>
                            </div>
                        </div>
                        <div class="side-col">
                            <div class="side-title">📲 3. Giao diện Mobile (393 x 852)</div>
                            <div class="device-frame side-frame-mobile">
                                <iframe src="mobile.html"></iframe>
                            </div>
                        </div>
                    </div>
                `;
            }
        }

        // Initialize with Desktop view
        setMode('desktop');
    </script>
</body>
</html>
"""
    return html

def main():
    desktop_html = generate_desktop()
    with open(os.path.join(BASE_DIR, "desktop.html"), "w", encoding="utf-8") as f:
        f.write(desktop_html)
    print("Generated desktop.html")

    tablet_html = generate_tablet()
    with open(os.path.join(BASE_DIR, "tablet.html"), "w", encoding="utf-8") as f:
        f.write(tablet_html)
    print("Generated tablet.html")

    mobile_html = generate_mobile()
    with open(os.path.join(BASE_DIR, "mobile.html"), "w", encoding="utf-8") as f:
        f.write(mobile_html)
    print("Generated mobile.html")

    master_html = generate_master_demo()
    with open(os.path.join(BASE_DIR, "demo_3_devices.html"), "w", encoding="utf-8") as f:
        f.write(master_html)
    print("Generated demo_3_devices.html")

if __name__ == "__main__":
    main()
