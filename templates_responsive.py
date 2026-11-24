# -*- coding: utf-8 -*-
"""
Responsive Storefront Templates for Nếp Nhỏ D2C
Includes 3 fully functional Jinja2 interfaces:
1. DESKTOP_TEMPLATE (1280px+ layout with left sidebar filters, 4-col grid, Before/After toggle, interactive detail)
2. TABLET_TEMPLATE  (768px-1024px touch-optimized layout, scrollable pills, 3-col grid, fixed bottom cart bar)
3. MOBILE_TEMPLATE  (375px-430px smartphone layout, status bar, story circles, flash sale timer, 2-col compact grid, bottom navigation bar, quick-buy sheet)
4. DEMO_SHOWCASE_TEMPLATE (Interactive Device Simulator with Desktop, iPad, iPhone, and Side-by-Side views)
"""

COMMON_HEADER_SNIPPET = """
{% if not is_embed %}
<div class="device-switcher-topbar">
    <div class="d-flex align-items-center gap-2">
        <span class="switcher-brand">🌿 NẾP NHỎ CHỌN GIAO DIỆN:</span>
        <span class="switcher-status">Đang xem: <strong>{{ current_mode_label }}</strong></span>
    </div>
    <div class="d-flex align-items-center gap-1">
        <a href="/desktop" class="switcher-btn {% if current_mode == 'desktop' %}active{% endif %}">🖥️ Desktop</a>
        <a href="/tablet" class="switcher-btn {% if current_mode == 'tablet' %}active{% endif %}">📱 Tablet</a>
        <a href="/mobile" class="switcher-btn {% if current_mode == 'mobile' %}active{% endif %}">📲 Mobile</a>
        <a href="/demo" class="switcher-btn btn-highlight {% if current_mode == 'demo' %}active{% endif %}">🔲 Xem Cả 3 (Simulator)</a>
    </div>
</div>
{% endif %}
"""

COMMON_JS_SNIPPET = """
<script>
function switchImg(pid, src, btn) {
    const img = document.getElementById('thumb-' + pid);
    if (img) img.src = src;
    if (btn && btn.parentElement) {
        btn.parentElement.querySelectorAll('button, span').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    }
}

function addCartAjax(pid, name, nextUrl) {
    const formData = new FormData();
    formData.append('product_id', pid);
    formData.append('qty', 1);
    formData.append('ajax', '1');

    fetch('/add-to-cart', {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            document.querySelectorAll('.live-cart-badge').forEach(el => {
                el.innerText = data.cart_count;
                el.style.display = data.cart_count > 0 ? '' : 'none';
            });
            document.querySelectorAll('.live-cart-subtotal').forEach(el => {
                el.innerText = (data.cart_subtotal || 0).toLocaleString() + 'đ';
            });
            showToast('🛒 ' + data.message);
            if (nextUrl) {
                window.location.href = nextUrl;
            }
        }
    })
    .catch(err => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/add-to-cart';
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'product_id';
        input.value = pid;
        form.appendChild(input);
        if (nextUrl) {
            const nextInput = document.createElement('input');
            nextInput.type = 'hidden';
            nextInput.name = 'next_url';
            nextInput.value = nextUrl;
            form.appendChild(nextInput);
        }
        document.body.appendChild(form);
        form.submit();
    });
}

function showToast(msg) {
    let toast = document.getElementById('nepnho-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'nepnho-toast';
        toast.style.cssText = 'position: fixed; bottom: 80px; right: 20px; z-index: 999999; background: #1E293B; color: #FFF; padding: 12px 20px; border-radius: 12px; font-size: 0.88rem; font-weight: 600; box-shadow: 0 8px 24px rgba(0,0,0,0.25); display: flex; align-items: center; gap: 8px; border-left: 4px solid #7D9D7C; transition: all 0.3s ease; opacity: 0; transform: translateY(20px);';
        document.body.appendChild(toast);
    }
    toast.innerHTML = msg;
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
    }, 2800);
}

function detectAndSaveLocation() {
    {% if not current_user %}
    alert("Vui lòng đăng nhập để hệ thống xác định và lưu vị trí giao hàng vào tài khoản của bạn!");
    window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname);
    return;
    {% endif %}

    if (!navigator.geolocation) {
        alert("Trình duyệt không hỗ trợ định vị GPS tự động!");
        return;
    }

    showToast("🛰️ Đang kết nối GPS định vị tọa độ giao hàng...");

    navigator.geolocation.getCurrentPosition(
        function(pos) {
            const lat = pos.coords.latitude.toFixed(6);
            const lng = pos.coords.longitude.toFixed(6);
            
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`)
            .then(res => res.json())
            .then(geo => {
                let addr = geo.display_name || `Tọa độ GPS: ${lat}, ${lng}`;
                saveLocationToDb(lat, lng, addr);
            })
            .catch(err => {
                saveLocationToDb(lat, lng, `Tọa độ GPS: ${lat}, ${lng}`);
            });
        },
        function(err) {
            let manualAddr = prompt("Không lấy được GPS tự động. Vui lòng nhập địa chỉ giao hàng của bạn (Kho xuất hàng: Quận 9):");
            if (manualAddr) {
                saveLocationToDb("", "", manualAddr);
            }
        },
        { enableHighAccuracy: true, timeout: 8000 }
    );
}

function saveLocationToDb(lat, lng, address) {
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
            showToast("✓ " + data.message);
            document.querySelectorAll('.live-delivery-loc').forEach(el => {
                el.innerText = data.address.length > 25 ? data.address.substring(0, 22) + '...' : data.address;
            });
            const cartDisplay = document.getElementById('cartLocDisplay');
            if (cartDisplay) {
                cartDisplay.innerHTML = '<strong>' + data.address + '</strong> <span class="badge bg-success bg-opacity-10 text-success ms-1">Đã lưu DB</span>';
            }
        } else {
            alert(data.message);
        }
    })
    .catch(e => {
        alert("Lỗi khi lưu vị trí vào database!");
    });
}
</script>
"""

# ==============================================================================
# 1. DESKTOP TEMPLATE
# ==============================================================================
DESKTOP_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 Nếp Nhỏ — Desktop Storefront (Giao diện Máy Tính)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-paper: #F7F4EE;
            --sage-green: #7D9D7C;
            --sage-dark: #658464;
            --earth-brown: #8A6F5A;
            --warm-accent: #E88D67;
            --text-dark: #2B2B2B;
        }
        * { box-sizing: border-box; }
        body { background-color: var(--bg-paper); color: var(--text-dark); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; }
        
        /* SWITCHER TOPBAR */
        .device-switcher-topbar { background: #1E293B; color: #FFF; padding: 6px 20px; font-size: 0.8rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 99999; border-bottom: 1px solid #334155; }
        .switcher-brand { color: #7D9D7C; font-weight: 700; letter-spacing: 0.5px; }
        .switcher-status { color: #CBD5E1; }
        .switcher-btn { color: #CBD5E1; text-decoration: none; padding: 3px 10px; border-radius: 6px; font-size: 0.76rem; font-weight: 600; border: 1px solid #475569; transition: 0.15s; }
        .switcher-btn:hover { background: #334155; color: #FFF; }
        .switcher-btn.active { background: var(--sage-green); color: #FFF; border-color: var(--sage-green); }
        .switcher-btn.btn-highlight { border-color: #F59E0B; color: #FCD34D; }
        .switcher-btn.btn-highlight:hover, .switcher-btn.btn-highlight.active { background: #F59E0B; color: #1E293B; }

        .desktop-container { max-width: 1360px; margin: 0 auto; padding: 0 20px; }
        
        /* TOP PROMO */
        .top-promo { background: #2B2B2B; color: #E5E7EB; font-size: 0.78rem; padding: 7px 0; }
        
        /* HEADER */
        .desktop-header { background: #FFFFFF; border-bottom: 2px solid var(--sage-green); padding: 14px 0; }
        .brand-title { font-weight: 800; color: var(--earth-brown); font-size: 1.6rem; letter-spacing: -0.5px; text-decoration: none; }
        .brand-subtitle { font-size: 0.76rem; color: #777; margin-top: -3px; }
        .desktop-search-input { border-radius: 30px; padding: 10px 20px 10px 42px; border: 1.5px solid #E2E8F0; background: #F8FAFC; width: 100%; outline: none; transition: 0.2s; }
        .desktop-search-input:focus { border-color: var(--sage-green); background: #FFF; box-shadow: 0 0 0 4px rgba(125,157,124,0.15); }

        /* NAV */
        .desktop-nav { background: #FFFFFF; border-bottom: 1px solid #E2E8F0; box-shadow: 0 2px 6px rgba(0,0,0,0.02); }
        .nav-link-custom { color: #334155; font-weight: 600; font-size: 0.9rem; padding: 12px 14px !important; text-decoration: none; display: inline-block; transition: 0.2s; cursor: pointer; }
        .nav-link-custom:hover, .nav-link-custom.active { color: var(--sage-green); border-bottom: 2px solid var(--sage-green); }

        /* HERO */
        .hero-banner { background: linear-gradient(135deg, #F1ECE1 0%, #E5DAC6 100%); border-radius: 20px; padding: 44px; margin: 24px 0 28px; border: 1px solid rgba(0,0,0,0.04); }
        .hero-title { font-size: 2.2rem; font-weight: 800; color: #1E293B; line-height: 1.25; }
        .hero-badge { background: #DCFCE7; color: #15803D; font-weight: 700; font-size: 0.8rem; padding: 6px 14px; border-radius: 20px; display: inline-block; margin-bottom: 12px; }

        /* COMMIT CARDS */
        .commit-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
        .commit-card { background: #FFFFFF; border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; gap: 12px; border: 1px solid #E2E8F0; }

        /* STORE LAYOUT */
        .store-layout { display: grid; grid-template-columns: 260px 1fr; gap: 26px; }
        .filter-sidebar { background: #FFFFFF; border-radius: 16px; padding: 20px; border: 1px solid #E2E8F0; height: fit-content; position: sticky; top: 70px; }
        .filter-group-title { font-size: 0.92rem; font-weight: 700; color: #1E293B; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1.5px solid #F1F5F9; }
        .filter-check { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 0.85rem; color: #475569; cursor: pointer; }
        .filter-check input { width: 16px; height: 16px; accent-color: var(--sage-green); }

        /* PRODUCT GRID (4 COLS) */
        .product-grid-desktop { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
        .desktop-card { background: #FFFFFF; border-radius: 14px; overflow: hidden; border: 1px solid #E8ECEF; box-shadow: 0 4px 12px rgba(0,0,0,0.03); transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; height: 100%; }
        .desktop-card:hover { transform: translateY(-5px); box-shadow: 0 10px 24px rgba(0,0,0,0.08); border-color: var(--sage-green); }
        .card-img-wrap { position: relative; height: 195px; background: #FAF7F2; overflow: hidden; }
        .product-thumb { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
        .badge-discount { position: absolute; top: 10px; left: 10px; background: #EF4444; color: white; font-weight: 700; font-size: 0.72rem; padding: 3px 8px; border-radius: 6px; z-index: 2; }
        .badge-cat-top { position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.92); color: var(--earth-brown); font-size: 0.68rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; z-index: 2; backdrop-filter: blur(4px); }

        /* TOGGLE BEFORE / AFTER */
        .img-toggle-bar { position: absolute; bottom: 8px; left: 8px; right: 8px; display: flex; gap: 4px; background: rgba(0,0,0,0.6); backdrop-filter: blur(6px); border-radius: 8px; padding: 3px; z-index: 3; }
        .toggle-btn { flex: 1; border: none; background: transparent; color: #FFF; font-size: 0.66rem; font-weight: 600; padding: 3px 0; border-radius: 5px; cursor: pointer; transition: 0.15s; }
        .toggle-btn.active { background: #FFFFFF; color: #1E293B; }

        .card-body-custom { padding: 14px; display: flex; flex-direction: column; flex-grow: 1; }
        .badge-atp { background-color: #E8F5E9; color: #2E7D32; font-size: 0.72rem; padding: 3px 6px; border-radius: 6px; font-weight: 600; }
        .product-title { font-size: 0.9rem; font-weight: 700; color: #1E293B; margin: 4px 0 6px; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.7em; }
        .product-desc { font-size: 0.76rem; color: #64748B; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 10px; }
        .card-footer-box { margin-top: auto; padding-top: 10px; border-top: 1px solid #F1F5F9; display: flex; justify-content: space-between; align-items: center; }
        .price-val { font-size: 1.15rem; font-weight: 800; color: var(--warm-accent); }
        .price-old { font-size: 0.76rem; color: #94A3B8; text-decoration: line-through; }
        .btn-sage { background-color: var(--sage-green); color: white; border: none; font-weight: 600; border-radius: 6px; }
        .btn-sage:hover { background-color: var(--sage-dark); color: white; }

        .desktop-footer { background: #FFFFFF; border-top: 1px solid #E2E8F0; padding: 40px 0 20px; margin-top: 50px; font-size: 0.84rem; }
    </style>
</head>
<body>

    """ + COMMON_HEADER_SNIPPET + """

    <!-- TOP PROMO -->
    <div class="top-promo">
        <div class="desktop-container d-flex justify-content-between align-items-center">
            <div>🌿 <strong>Nếp Nhỏ D2C:</strong> Gọn một góc, nhẹ cả ngày | Miễn phí giao hàng đơn từ 299.000đ</div>
            <div class="d-flex gap-3">
                <span>📍 Giao nhanh định vị GPS</span>
                <span>📞 Hotline: 0901.234.567</span>
                <span>⚙️ <a href="/admin" class="text-white text-decoration-none">Quản trị</a></span>
            </div>
        </div>
    </div>

    <!-- MAIN HEADER -->
    <header class="desktop-header">
        <div class="desktop-container d-flex justify-content-between align-items-center">
            <a href="/desktop" class="d-flex align-items-center text-decoration-none">
                <div>
                    <div class="brand-title">🌿 NẾP NHỎ</div>
                    <div class="brand-subtitle">Gọn một góc, nhẹ cả ngày</div>
                </div>
            </a>
            
            <div class="desktop-search-bar flex-grow-1 mx-5 position-relative">
                <span style="position: absolute; left: 16px; top: 11px; color: #94A3B8;">🔍</span>
                <input type="text" id="desktopSearch" class="desktop-search-input" placeholder="Tìm kiếm kệ mỹ phẩm, gương LED, hộp gấp gọn, đèn chill..." onkeyup="filterDesktop()">
            </div>
            
            <div class="d-flex align-items-center gap-3">
                <div class="d-flex align-items-center gap-2 px-3 py-2 bg-light rounded-pill border" style="font-size: 0.85rem; cursor: pointer;" onclick="detectAndSaveLocation()" title="Nhấn để định vị GPS & lưu vị trí">
                    <span>📍</span>
                    <div>
                        <div style="font-size: 0.68rem; color: #888;">Giao đến:</div>
                        <strong style="color: #333;" class="live-delivery-loc">
                            {% if current_user and current_user.get('address') %}
                                {{ current_user.get('address') | truncate(22) }}
                            {% else %}
                                Nhấn để định vị GPS
                            {% endif %}
                        </strong>
                    </div>
                </div>
                
                <a href="/cart" class="btn btn-outline-dark position-relative rounded-pill px-3 py-2">
                    🛒 <strong>Giỏ hàng</strong>
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger live-cart-badge" {% if cart_count == 0 %}style="display:none;"{% endif %}>{{ cart_count }}</span>
                </a>

                {% if current_user %}
                <div class="d-flex align-items-center gap-2">
                    <a href="/profile" class="btn btn-light border rounded-pill px-3 py-2 text-dark text-decoration-none" style="font-size: 0.85rem;" title="Xem thông tin cá nhân & đơn hàng">
                        👤 <strong>{{ current_user['fullname'] }}</strong>
                    </a>
                    {% if current_user.get('role') == 'admin' %}
                    <a href="/admin" class="btn btn-outline-primary rounded-pill px-3 py-2 fw-bold text-decoration-none" style="font-size: 0.85rem;" title="Trang quản trị">
                        ⚙️ Quản Trị
                    </a>
                    {% endif %}
                    <a href="/logout" class="btn btn-outline-danger rounded-pill px-3 py-2 fw-bold text-decoration-none" style="font-size: 0.85rem;" title="Bấm để đăng xuất">
                        🚪 Đăng xuất
                    </a>
                </div>
                {% else %}
                <div class="d-flex align-items-center gap-2">
                    <a href="/login" class="btn btn-outline-dark rounded-pill px-3 py-2 fw-bold" style="font-size: 0.85rem;">Đăng nhập</a>
                    <a href="/register" class="btn btn-sage rounded-pill px-3 py-2 fw-bold" style="font-size: 0.85rem;">Đăng ký</a>
                </div>
                {% endif %}
            </div>
        </div>
    </header>

    <!-- NAV BAR -->
    <nav class="desktop-nav">
        <div class="desktop-container d-flex gap-1">
            <a class="nav-link-custom active" onclick="filterByCat('all')">Tất cả sản phẩm</a>
            <a class="nav-link-custom" onclick="filterByCat('Làm đẹp & Bàn trang điểm')">Làm đẹp & Bàn phấn</a>
            <a class="nav-link-custom" onclick="filterByCat('Bàn học & Làm việc')">Bàn học & Làm việc</a>
            <a class="nav-link-custom" onclick="filterByCat('Tủ đồ & Quần áo')">Tủ đồ & Quần áo</a>
            <a class="nav-link-custom" onclick="filterByCat('Phòng ngủ & Decor chill')">Phòng ngủ & Decor chill</a>
            <a class="nav-link-custom" onclick="filterByCat('Combo giải pháp toàn diện')">Combo tiết kiệm</a>
            <span class="ms-auto d-flex align-items-center text-danger fw-bold fs-7 pe-2">⚡ FLASH SALE GIẢM ĐẾN 35%</span>
        </div>
    </nav>

    <!-- MAIN BODY -->
    <main class="desktop-container">
        
        <!-- HERO -->
        <section class="hero-banner">
            <div class="row align-items-center">
                <div class="col-lg-7">
                    <span class="hero-badge">✨ GIẢI PHÁP SẮP XẾP PHÒNG TRỌ & NHÀ PHỐ GỌN GÀNG</span>
                    <h1 class="hero-title mb-3">Biến Căn Phòng Bừa Bộn Thành Góc Chill Tinh Tế Trong 15 Phút</h1>
                    <p class="text-muted fs-6 mb-4" style="max-width: 580px;">
                        Bộ phụ kiện kệ mica 360°, hộp vải kháng bụi và các giải pháp decor chuẩn phong cách Hàn Quốc giúp bạn giải phóng 70% diện tích mặt bàn.
                    </p>
                    <div class="d-flex gap-3">
                        <a href="#storeSection" class="btn btn-sage px-4 py-2 fs-6 rounded-pill">Khám phá cửa hàng ngay ↓</a>
                        <a href="/checkout" class="btn btn-outline-dark px-4 py-2 fs-6 rounded-pill">💳 Đặt hàng nhanh (VietQR)</a>
                    </div>
                </div>
                <div class="col-lg-5 text-center">
                    <img src="/images/combo_neptro_neptu.png" alt="Combo Nếp Nhỏ" class="rounded-4 shadow-lg" style="max-height: 270px; width: auto; object-fit: cover;">
                </div>
            </div>
        </section>

        <!-- 4 COMMITMENTS -->
        <div class="commit-grid">
            <div class="commit-card">
                <div style="font-size: 1.8rem;">🚀</div>
                <div>
                    <strong style="font-size: 0.88rem; display: block;">Giao nhanh định vị GPS</strong>
                    <span style="font-size: 0.75rem; color: #64748B;">Chính xác tận cổng phòng trọ</span>
                </div>
            </div>
            <div class="commit-card">
                <div style="font-size: 1.8rem;">🔄</div>
                <div>
                    <strong style="font-size: 0.88rem; display: block;">Đổi trả 7 ngày 1:1</strong>
                    <span style="font-size: 0.75rem; color: #64748B;">Miễn phí nếu vỡ hoặc lỗi mica</span>
                </div>
            </div>
            <div class="commit-card">
                <div style="font-size: 1.8rem;">💎</div>
                <div>
                    <strong style="font-size: 0.88rem; display: block;">Chất liệu cao cấp</strong>
                    <span style="font-size: 0.75rem; color: #64748B;">Mica acrylic, nắp tre tự nhiên</span>
                </div>
            </div>
            <div class="commit-card">
                <div style="font-size: 1.8rem;">💳</div>
                <div>
                    <strong style="font-size: 0.88rem; display: block;">VietQR thanh toán 1-chạm</strong>
                    <span style="font-size: 0.75rem; color: #64748B;">Tự động hủy sau 24h hoàn ATP</span>
                </div>
            </div>
        </div>

        <!-- STORE SECTION -->
        <div id="storeSection" class="store-layout">
            
            <!-- SIDEBAR -->
            <aside class="filter-sidebar">
                <div class="filter-group-title d-flex justify-content-between">
                    <span>DANH MỤC</span>
                    <small class="text-muted fw-normal">({{ products|length }} món)</small>
                </div>
                <div class="mb-4">
                    {% set categories = [] %}
                    {% for p in products.values() %}
                        {% if p.get('category') and p.get('category') not in categories %}
                            {% set _ = categories.append(p.get('category')) %}
                            <label class="filter-check">
                                <input type="checkbox" name="cat" value="{{ p.get('category') }}" onchange="filterDesktop()">
                                <span>{{ p.get('category') }}</span>
                            </label>
                        {% endif %}
                    {% endfor %}
                </div>

                <div class="filter-group-title">KHOẢNG GIÁ</div>
                <div class="mb-4">
                    <label class="filter-check"><input type="radio" name="priceRange" value="all" checked onchange="filterDesktop()"> <span>Tất cả mức giá</span></label>
                    <label class="filter-check"><input type="radio" name="priceRange" value="under150" onchange="filterDesktop()"> <span>Dưới 150.000đ</span></label>
                    <label class="filter-check"><input type="radio" name="priceRange" value="150to300" onchange="filterDesktop()"> <span>150.000đ - 300.000đ</span></label>
                    <label class="filter-check"><input type="radio" name="priceRange" value="above300" onchange="filterDesktop()"> <span>Trên 300.000đ</span></label>
                </div>

                <div class="filter-group-title">TỒN KHO THỰC TẾ (ATP)</div>
                <div>
                    <label class="filter-check"><input type="checkbox" checked disabled> <span>Chỉ hiện sản phẩm sẵn sàng giao</span></label>
                </div>
            </aside>

            <!-- PRODUCTS (4 COLS) -->
            <div>
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h2 class="fs-5 fw-bold text-dark m-0">Tất Cả Sản Phẩm Sẵn Sàng Giao (<span id="visibleCount">{{ products|length }}</span>)</h2>
                    <div class="d-flex align-items-center gap-2">
                        <span class="fs-7 text-muted">Sắp xếp:</span>
                        <select class="form-select form-select-sm" style="width: 170px;" onchange="sortDesktop(this.value)">
                            <option value="featured">Nổi bật nhất</option>
                            <option value="price-asc">Giá: Thấp đến Cao</option>
                            <option value="price-desc">Giá: Cao đến Thấp</option>
                        </select>
                    </div>
                </div>

                <div class="product-grid-desktop" id="productGrid">
                    {% for pid, p in products.items() %}
                    {% set discount = (((p['original_price'] - p['price']) / p['original_price'] * 100) | round | int) if p.get('original_price', 0) > p['price'] else 0 %}
                    <div class="desktop-card-col" data-cat="{{ p.get('category','') }}" data-name="{{ p.get('name','').lower() }}" data-price="{{ p.get('price', 0) }}">
                        <div class="desktop-card">
                            <div class="card-img-wrap">
                                {% if discount > 0 %}
                                <span class="badge-discount">-{{ discount }}%</span>
                                {% endif %}
                                <span class="badge-cat-top">{{ p.get('category','') }}</span>
                                <img id="thumb-{{ pid }}" src="{{ p['after_img'] }}" alt="{{ p['name'] }}" class="product-thumb">
                                <div class="img-toggle-bar">
                                    <button type="button" class="toggle-btn active" onclick="switchImg('{{ pid }}', '{{ p['after_img'] }}', this)">Sau khi xếp</button>
                                    <button type="button" class="toggle-btn" onclick="switchImg('{{ pid }}', '{{ p['before_img'] }}', this)">Trước (Bừa)</button>
                                </div>
                            </div>
                            <div class="card-body-custom">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <span class="badge-atp">⚡ Sẵn giao: {{ p['stock_physical'] - p['stock_committed'] }} món</span>
                                    <span style="font-size: 0.75rem; color: #64748B;">⭐ 5.0 (48)</span>
                                </div>
                                <h3 class="product-title" title="{{ p['name'] }}">{{ p['name'] }}</h3>
                                <p class="product-desc">{{ p['description'] }}</p>
                                <div class="card-footer-box">
                                    <div>
                                        <div class="price-val">{{ "{:,}".format(p['price']) }}đ</div>
                                        {% if p.get('original_price') %}
                                        <div class="price-old">{{ "{:,}".format(p['original_price']) }}đ</div>
                                        {% endif %}
                                    </div>
                                    <div class="d-flex gap-1">
                                        <button type="button" class="btn btn-outline-dark btn-sm rounded-3 px-2" onclick="addCartAjax('{{ pid }}', '{{ p['name'] }}')" title="Thêm giỏ hàng">🛒</button>
                                        <a href="/product/{{ pid }}" class="btn btn-sage btn-sm px-3">Chi tiết</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
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
                    <div class="fw-bold mb-2 text-dark">VỀ NẾP NHỎ</div>
                    <div class="mb-1"><a href="#" class="text-muted text-decoration-none">Câu chuyện thương hiệu</a></div>
                    <div class="mb-1"><a href="#" class="text-muted text-decoration-none">Giải pháp sắp xếp phòng</a></div>
                    <div class="mb-1"><a href="#" class="text-muted text-decoration-none">Bộ kit làm đẹp bàn phấn</a></div>
                </div>
                <div class="col-lg-3">
                    <div class="fw-bold mb-2 text-dark">CHÍNH SÁCH BÁN HÀNG</div>
                    <div class="mb-1"><a href="#" class="text-muted text-decoration-none">Chính sách vận chuyển GPS</a></div>
                    <div class="mb-1"><a href="#" class="text-muted text-decoration-none">Bảo hành vỡ hỏng 1 đổi 1</a></div>
                    <div class="mb-1"><a href="#" class="text-muted text-decoration-none">Chính sách thanh toán VietQR</a></div>
                </div>
                <div class="col-lg-3">
                    <div class="fw-bold mb-2 text-dark">THANH TOÁN TIỆN LỢI</div>
                    <div class="d-flex gap-2 mb-2">
                        <span class="badge bg-light text-dark border p-2">🏦 VietQR 1-Chạm</span>
                        <span class="badge bg-light text-dark border p-2">💵 Tiền mặt (COD)</span>
                    </div>
                    <div class="p-2 bg-light rounded-3 border fs-7 text-muted">
                        🔒 Hệ thống xác nhận thanh toán mã QR tự động cập nhật trạng thái đơn hàng tức thời.
                    </div>
                </div>
            </div>
            <div class="border-top mt-4 pt-3 text-center text-muted fs-7">
                © 2026 Nếp Nhỏ — Gọn một góc, nhẹ cả ngày.
            </div>
        </div>
    </footer>

    """ + COMMON_JS_SNIPPET + """
    <script>
        function filterDesktop() {
            const search = document.getElementById('desktopSearch').value.toLowerCase().trim();
            const checkedCats = Array.from(document.querySelectorAll('input[name="cat"]:checked')).map(el => el.value);
            const priceVal = document.querySelector('input[name="priceRange"]:checked').value;
            
            let count = 0;
            document.querySelectorAll('.desktop-card-col').forEach(card => {
                const name = card.getAttribute('data-name');
                const cat = card.getAttribute('data-cat');
                const price = parseInt(card.getAttribute('data-price')) || 0;

                let matchSearch = !search || name.includes(search);
                let matchCat = checkedCats.length === 0 || checkedCats.includes(cat);
                let matchPrice = true;
                if (priceVal === 'under150') matchPrice = price < 150000;
                else if (priceVal === '150to300') matchPrice = price >= 150000 && price <= 300000;
                else if (priceVal === 'above300') matchPrice = price > 300000;

                if (matchSearch && matchCat && matchPrice) {
                    card.style.display = '';
                    count++;
                } else {
                    card.style.display = 'none';
                }
            });
            document.getElementById('visibleCount').innerText = count;
        }

        function filterByCat(catName) {
            document.querySelectorAll('.nav-link-custom').forEach(l => l.classList.remove('active'));
            event.target.classList.add('active');
            
            document.querySelectorAll('input[name="cat"]').forEach(input => {
                input.checked = (catName !== 'all' && input.value === catName);
            });
            filterDesktop();
        }

        function sortDesktop(type) {
            const grid = document.getElementById('productGrid');
            const cards = Array.from(grid.children);
            cards.sort((a, b) => {
                const priceA = parseInt(a.getAttribute('data-price')) || 0;
                const priceB = parseInt(b.getAttribute('data-price')) || 0;
                if (type === 'price-asc') return priceA - priceB;
                if (type === 'price-desc') return priceB - priceA;
                return 0;
            });
            cards.forEach(card => grid.appendChild(card));
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ==============================================================================
# 2. TABLET TEMPLATE
# ==============================================================================
TABLET_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 Nếp Nhỏ — Tablet Storefront (Giao diện Máy Tính Bảng 768px-1024px)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-paper: #F7F4EE;
            --sage-green: #7D9D7C;
            --sage-dark: #658464;
            --earth-brown: #8A6F5A;
            --warm-accent: #E88D67;
            --text-dark: #2B2B2B;
        }
        * { box-sizing: border-box; }
        body { max-width: 900px; margin: 0 auto; background: #FAF8F5; color: var(--text-dark); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding-bottom: 80px; }
        
        .device-switcher-topbar { background: #1E293B; color: #FFF; padding: 6px 16px; font-size: 0.78rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 99999; }
        .switcher-brand { color: #7D9D7C; font-weight: 700; }
        .switcher-btn { color: #CBD5E1; text-decoration: none; padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; border: 1px solid #475569; }
        .switcher-btn.active { background: var(--sage-green); color: #FFF; border-color: var(--sage-green); }

        .tablet-header { background: #FFFFFF; padding: 12px 20px; border-bottom: 2px solid var(--sage-green); position: sticky; top: 35px; z-index: 100; }
        .tablet-brand { font-weight: 800; font-size: 1.4rem; color: var(--earth-brown); text-decoration: none; }
        
        /* TOUCH PILLS */
        .tablet-pills-bar { display: flex; gap: 8px; overflow-x: auto; padding: 12px 20px; background: #FFFFFF; border-bottom: 1px solid #E2E8F0; scrollbar-width: none; }
        .tablet-pills-bar::-webkit-scrollbar { display: none; }
        .tab-pill { white-space: nowrap; border: 1px solid #E2E8F0; background: #F8FAFC; padding: 8px 16px; border-radius: 20px; font-size: 0.84rem; font-weight: 600; color: #475569; cursor: pointer; transition: 0.2s; }
        .tab-pill.active { background: var(--sage-green); color: #FFF; border-color: var(--sage-green); }

        .tablet-hero { background: linear-gradient(135deg, #EFE7DA, #E3D6C1); border-radius: 16px; padding: 22px; margin: 16px 20px; }
        
        /* 3 COLS GRID */
        .tablet-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; padding: 0 20px; }
        @media (max-width: 768px) {
            .tablet-grid { grid-template-columns: repeat(2, 1fr); }
        }
        .tablet-card { background: #FFFFFF; border-radius: 14px; border: 1px solid #E2E8F0; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 3px 10px rgba(0,0,0,0.03); }
        .tablet-img-wrap { position: relative; height: 175px; background: #F1ECE1; }
        .tablet-thumb { width: 100%; height: 100%; object-fit: cover; }
        .badge-discount { position: absolute; top: 8px; left: 8px; background: #EF4444; color: #FFF; font-size: 0.7rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
        
        .touch-before-after { position: absolute; bottom: 6px; left: 6px; right: 6px; display: flex; gap: 4px; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); border-radius: 6px; padding: 2px; }
        .touch-btn { flex: 1; border: none; background: transparent; color: #FFF; font-size: 0.65rem; font-weight: 600; padding: 4px 0; border-radius: 4px; }
        .touch-btn.active { background: #FFF; color: #1E293B; }
        
        .tablet-card-body { padding: 12px; display: flex; flex-direction: column; flex-grow: 1; }
        .tablet-title { font-size: 0.85rem; font-weight: 700; color: #1E293B; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.6em; }
        .price-val { font-size: 1.05rem; font-weight: 800; color: var(--warm-accent); }
        .price-old { font-size: 0.72rem; color: #94A3B8; text-decoration: line-through; }
        .btn-sage { background-color: var(--sage-green); color: white; border: none; font-weight: 600; border-radius: 8px; }
        .btn-sage:hover { background-color: var(--sage-dark); color: white; }

        /* FIXED BOTTOM BAR TABLET */
        .tablet-bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; max-width: 900px; margin: 0 auto; background: #FFFFFF; border-top: 1px solid #CBD5E1; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 -4px 16px rgba(0,0,0,0.06); z-index: 100; }
    </style>
</head>
<body>

    """ + COMMON_HEADER_SNIPPET + """

    <header class="tablet-header d-flex justify-content-between align-items-center">
        <a href="/tablet" class="tablet-brand">🌿 NẾP NHỎ</a>
        <div class="d-flex align-items-center gap-2 flex-grow-1 mx-3" style="max-width: 360px;">
            <input type="text" id="tabletSearch" class="form-control rounded-pill form-control-sm px-3" placeholder="🔍 Tìm kiếm sản phẩm..." onkeyup="filterTabletSearch()">
        </div>
        <div class="d-flex align-items-center gap-2">
            <span class="badge bg-light text-dark border p-2" style="font-size: 0.75rem; cursor: pointer;" onclick="detectAndSaveLocation()" title="Nhấn để định vị GPS & lưu vị trí">📍 <span class="live-delivery-loc">{% if current_user and current_user.get('address') %}{{ current_user.get('address') | truncate(14) }}{% else %}Định vị GPS{% endif %}</span></span>
            <a href="/cart" class="btn btn-outline-dark btn-sm rounded-pill px-3 position-relative">
                🛒 Giỏ (<span class="live-cart-badge">{{ cart_count }}</span>)
            </a>
            {% if current_user %}
            <a href="/profile" class="btn btn-light btn-sm border rounded-pill px-2 py-1 text-dark text-decoration-none" title="Trang cá nhân">
                👤 <strong style="font-size: 0.76rem;">{{ current_user['fullname'] | truncate(12) }}</strong>
            </a>
            {% if current_user.get('role') == 'admin' %}
            <a href="/admin" class="btn btn-outline-primary btn-sm rounded-pill px-2 py-1" style="font-size: 0.72rem; font-weight: 600;">⚙️ Admin</a>
            {% endif %}
            <a href="/logout" class="btn btn-outline-danger btn-sm rounded-pill px-2 py-1" style="font-size: 0.72rem; font-weight: 600;">🚪 Đăng xuất</a>
            {% else %}
            <a href="/login" class="btn btn-outline-dark btn-sm rounded-pill px-2 py-1" style="font-size: 0.75rem; font-weight: 600;">Đăng nhập</a>
            <a href="/register" class="btn btn-sage btn-sm rounded-pill px-2 py-1" style="font-size: 0.75rem; font-weight: 600;">Đăng ký</a>
            {% endif %}
        </div>
    </header>

    <!-- HORIZONTAL PILLS -->
    <div class="tablet-pills-bar">
        <button class="tab-pill active" onclick="filterTabletCat('all', this)">Tất cả</button>
        {% set categories = [] %}
        {% for p in products.values() %}
            {% if p.get('category') and p.get('category') not in categories %}
                {% set _ = categories.append(p.get('category')) %}
                <button class="tab-pill" onclick="filterTabletCat('{{ p.get('category') }}', this)">{{ p.get('category') }}</button>
            {% endif %}
        {% endfor %}
    </div>

    <!-- TABLET HERO -->
    <div class="tablet-hero d-flex justify-content-between align-items-center">
        <div>
            <span class="badge bg-success bg-opacity-75 text-white px-2 py-1 rounded-pill mb-1" style="font-size: 0.7rem;">✨ Giao hàng chuẩn GPS</span>
            <h2 class="fs-4 fw-bold text-dark m-0">Gọn Một Góc, Nhẹ Cả Ngày</h2>
            <p class="text-muted fs-7 mt-1 mb-2">Trải nghiệm mua sắm tối ưu cảm ứng mượt mà trên iPad & Tablet.</p>
            <a href="/checkout" class="btn btn-sage btn-sm px-3 py-2 rounded-pill">📍 Đặt hàng ngay (VietQR)</a>
        </div>
        <img src="/images/ke_dung_my_pham.png" alt="Hero" style="height: 105px; width: auto; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    </div>

    <div class="px-3 mb-2 d-flex justify-content-between align-items-center">
        <span class="fw-bold fs-6 text-dark">Sản Phẩm Khuyên Dùng ({{ products|length }} món)</span>
        <span class="fs-7 text-muted">Chạm để chọn Trước / Sau</span>
    </div>

    <!-- TABLET GRID -->
    <div class="tablet-grid" id="tabletGrid">
        {% for pid, p in products.items() %}
        {% set discount = (((p['original_price'] - p['price']) / p['original_price'] * 100) | round | int) if p.get('original_price', 0) > p['price'] else 0 %}
        <div class="tablet-card" data-cat="{{ p.get('category','') }}" data-name="{{ p.get('name','').lower() }}">
            <div class="tablet-img-wrap">
                {% if discount > 0 %}
                <span class="badge-discount">-{{ discount }}%</span>
                {% endif %}
                <img id="thumb-{{ pid }}" src="{{ p['after_img'] }}" alt="{{ p['name'] }}" class="tablet-thumb">
                <div class="touch-before-after">
                    <button type="button" class="touch-btn active" onclick="switchImg('{{ pid }}', '{{ p['after_img'] }}', this)">Sau</button>
                    <button type="button" class="touch-btn" onclick="switchImg('{{ pid }}', '{{ p['before_img'] }}', this)">Trước</button>
                </div>
            </div>
            <div class="tablet-card-body">
                <span class="badge bg-light text-secondary border align-self-start mb-1" style="font-size: 0.68rem;">{{ p.get('category','') }}</span>
                <h4 class="tablet-title"><a href="/product/{{ pid }}" class="text-dark text-decoration-none">{{ p['name'] }}</a></h4>
                <div class="badge bg-success bg-opacity-10 text-success align-self-start mb-2" style="font-size: 0.7rem;">⚡ Sẵn giao: {{ p['stock_physical'] - p['stock_committed'] }} món</div>
                <div class="d-flex justify-content-between align-items-center mt-auto pt-2 border-top">
                    <div>
                        <div class="price-val">{{ "{:,}".format(p['price']) }}đ</div>
                        {% if p.get('original_price') %}
                        <div class="price-old">{{ "{:,}".format(p['original_price']) }}đ</div>
                        {% endif %}
                    </div>
                    <div class="d-flex gap-1">
                        <button type="button" class="btn btn-outline-dark btn-sm px-2" onclick="addCartAjax('{{ pid }}', '{{ p['name'] }}')" title="Thêm vào giỏ">🛒</button>
                        <a href="/product/{{ pid }}" class="btn btn-sage btn-sm px-3">Xem</a>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- TABLET FIXED BOTTOM BAR -->
    <div class="tablet-bottom-bar">
        <div class="d-flex align-items-center gap-2">
            <span class="fs-4">🛒</span>
            <div>
                <strong style="font-size: 0.85rem;">Giỏ hàng của bạn:</strong>
                <span class="text-muted fs-7"><span class="live-cart-badge">{{ cart_count }}</span> món • <strong class="live-cart-subtotal">{{ "{:,}".format(cart_subtotal) }}đ</strong></span>
            </div>
        </div>
        <div class="d-flex gap-2">
            <a href="/cart" class="btn btn-outline-dark btn-sm px-3 py-2">Xem giỏ hàng</a>
            <a href="/checkout" class="btn btn-sage px-4 py-2">Tiến hành đặt hàng →</a>
        </div>
    </div>

    """ + COMMON_JS_SNIPPET + """
    <script>
        function filterTabletCat(cat, btn) {
            document.querySelectorAll('.tab-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            document.querySelectorAll('.tablet-card').forEach(card => {
                const cardCat = card.getAttribute('data-cat');
                card.style.display = (cat === 'all' || cardCat === cat) ? '' : 'none';
            });
        }

        function filterTabletSearch() {
            const s = document.getElementById('tabletSearch').value.toLowerCase().trim();
            document.querySelectorAll('.tablet-card').forEach(card => {
                const name = card.getAttribute('data-name');
                card.style.display = (!s || name.includes(s)) ? '' : 'none';
            });
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ==============================================================================
# 3. MOBILE TEMPLATE
# ==============================================================================
MOBILE_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>🌿 Nếp Nhỏ — Mobile App Storefront (Giao diện Điện Thoại 375px-430px)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-paper: #F7F4EE;
            --sage-green: #7D9D7C;
            --sage-dark: #658464;
            --earth-brown: #8A6F5A;
            --warm-accent: #E88D67;
            --text-dark: #2B2B2B;
        }
        * { box-sizing: border-box; }
        body {
            max-width: 430px;
            margin: 0 auto;
            background: #F7F5F0;
            padding-bottom: 74px;
            min-height: 100vh;
            position: relative;
            box-shadow: 0 0 30px rgba(0,0,0,0.08);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        
        .device-switcher-topbar { background: #1E293B; color: #FFF; padding: 5px 12px; font-size: 0.72rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 99999; }
        .switcher-brand { color: #7D9D7C; font-weight: 700; }
        .switcher-btn { color: #CBD5E1; text-decoration: none; padding: 2px 6px; border-radius: 4px; font-size: 0.68rem; font-weight: 600; border: 1px solid #475569; }
        .switcher-btn.active { background: var(--sage-green); color: #FFF; border-color: var(--sage-green); }

        .phone-status-bar { background: #FFFFFF; padding: 6px 14px 4px; display: flex; justify-content: space-between; font-size: 0.72rem; font-weight: 700; color: #1E293B; border-bottom: 1px solid #F1F5F9; }
        
        .mobile-header { background: #FFFFFF; padding: 8px 12px; position: sticky; top: 28px; z-index: 100; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
        .mobile-search-pill { background: #F1F5F9; border-radius: 20px; padding: 6px 14px; display: flex; align-items: center; gap: 8px; font-size: 0.8rem; }
        .mobile-search-input { border: none; background: transparent; outline: none; width: 100%; font-size: 0.8rem; }
        
        .mobile-gps-strip { background: #ECFDF5; color: #065F46; font-size: 0.7rem; padding: 5px 12px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #A7F3D0; }

        /* STORIES HORIZONTAL */
        .story-circles-wrap { display: flex; gap: 10px; overflow-x: auto; padding: 12px 12px 4px; scrollbar-width: none; }
        .story-circles-wrap::-webkit-scrollbar { display: none; }
        .story-item { display: flex; flex-direction: column; align-items: center; min-width: 58px; cursor: pointer; }
        .story-circle { width: 48px; height: 48px; border-radius: 50%; background: #FFFFFF; border: 2px solid var(--sage-green); display: flex; align-items: center; justify-content: center; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 3px; }
        .story-label { font-size: 0.65rem; font-weight: 600; color: #334155; text-align: center; }

        .mobile-banner { margin: 8px 12px; border-radius: 12px; background: linear-gradient(135deg, #7D9D7C, #5C7A5B); color: #FFF; padding: 14px; }
        .mobile-banner-title { font-size: 1rem; font-weight: 800; margin-bottom: 2px; }
        .mobile-banner-desc { font-size: 0.72rem; opacity: 0.9; margin-bottom: 8px; }

        .mobile-flash-bar { margin: 4px 12px 8px; background: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 8px; padding: 6px 10px; display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; font-weight: 700; color: #DC2626; }
        .countdown-box { background: #DC2626; color: #FFF; padding: 1px 5px; border-radius: 3px; font-size: 0.68rem; }

        /* 2 COLS MOBILE GRID */
        .mobile-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; padding: 0 12px; }
        .mobile-card { background: #FFFFFF; border-radius: 12px; overflow: hidden; border: 1px solid #E8ECEF; display: flex; flex-direction: column; }
        .mobile-thumb-wrap { position: relative; height: 135px; background: #F1ECE1; }
        .mobile-thumb { width: 100%; height: 100%; object-fit: cover; }
        .mobile-discount { position: absolute; top: 6px; left: 6px; background: #EF4444; color: #FFF; font-size: 0.65rem; font-weight: 700; padding: 2px 5px; border-radius: 4px; }
        .mobile-img-switch { position: absolute; bottom: 4px; left: 4px; right: 4px; display: flex; background: rgba(0,0,0,0.6); border-radius: 4px; padding: 1px; }
        .mobile-img-switch span { flex: 1; text-align: center; color: #FFF; font-size: 0.6rem; padding: 2px 0; cursor: pointer; border-radius: 3px; }
        .mobile-img-switch span.active { background: #FFF; color: #1E293B; font-weight: 700; }
        
        .mobile-card-content { padding: 8px; display: flex; flex-direction: column; flex-grow: 1; }
        .mobile-title { font-size: 0.76rem; font-weight: 700; color: #1E293B; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.6em; line-height: 1.3; }
        .price-val { font-size: 0.92rem; font-weight: 800; color: var(--warm-accent); }
        .price-old { font-size: 0.68rem; color: #94A3B8; text-decoration: line-through; }
        .mobile-buy-btn { background: var(--sage-green); color: #FFF; border: none; font-size: 0.7rem; font-weight: 700; padding: 4px 8px; border-radius: 6px; cursor: pointer; }

        /* FIXED BOTTOM NAV */
        .mobile-bottom-nav { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 430px; background: #FFFFFF; border-top: 1px solid #E2E8F0; display: flex; justify-content: space-around; padding: 6px 0; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); }
        .nav-tab-item { display: flex; flex-direction: column; align-items: center; text-decoration: none; color: #64748B; font-size: 0.65rem; font-weight: 600; }
        .nav-tab-item.active { color: var(--sage-green); font-weight: 700; }
        .nav-tab-icon { font-size: 1.25rem; margin-bottom: 1px; position: relative; }
        .badge-cart-mob { position: absolute; top: -4px; right: -8px; background: #EF4444; color: #FFF; font-size: 0.58rem; padding: 1px 4px; border-radius: 10px; font-weight: 700; }

        /* BOTTOM SHEET */
        .bottom-sheet-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 2000; display: none; align-items: flex-end; justify-content: center; }
        .bottom-sheet-overlay.active { display: flex; }
        .bottom-sheet-box { background: #FFFFFF; width: 100%; max-width: 430px; border-radius: 20px 20px 0 0; padding: 18px; animation: slideUp 0.25s ease; }
        @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
    </style>
</head>
<body>

    """ + COMMON_HEADER_SNIPPET + """

    <!-- STATUS BAR -->
    <div class="phone-status-bar">
        <span>09:41</span>
        <span>5G 📶 • 100% 🔋</span>
    </div>

    <!-- HEADER -->
    <header class="mobile-header">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="fw-bold fs-6 text-dark">🌿 NẾP NHỎ D2C</span>
            <div class="d-flex align-items-center gap-2">
                <a href="/cart" class="text-decoration-none text-dark fs-6 position-relative me-1">
                    🛒<span class="badge-cart-mob live-cart-badge" {% if cart_count == 0 %}style="display:none;"{% endif %}>{{ cart_count }}</span>
                </a>
                {% if current_user %}
                <a href="/profile" class="badge bg-light text-dark border text-decoration-none px-2 py-1" style="font-size: 0.72rem;">
                    👤 {{ current_user['fullname'] | truncate(10) }}
                </a>
                {% if current_user.get('role') == 'admin' %}
                <a href="/admin" class="badge bg-primary text-white text-decoration-none px-2 py-1" style="font-size: 0.72rem;">
                    ⚙️ Admin
                </a>
                {% endif %}
                <a href="/logout" class="badge bg-danger bg-opacity-10 text-danger border border-danger text-decoration-none px-2 py-1" style="font-size: 0.72rem; font-weight: 700;">
                    Đăng xuất
                </a>
                {% else %}
                <a href="/login" class="badge bg-success bg-opacity-10 text-success border border-success text-decoration-none px-2 py-1" style="font-size: 0.72rem; font-weight: 700;">
                    Đăng nhập / Đăng ký
                </a>
                {% endif %}
            </div>
        </div>
        <div class="mobile-search-pill">
            <span>🔍</span>
            <input type="text" id="mobSearch" class="mobile-search-input" placeholder="Tìm kệ mỹ phẩm, gương LED, đèn chill..." onkeyup="filterMob()">
        </div>
    </header>

    <!-- GPS -->
    <div class="mobile-gps-strip">
        <span>📍 Giao tận nơi: <strong class="live-delivery-loc">{% if current_user and current_user.get('address') %}{{ current_user.get('address') | truncate(24) }}{% else %}Nhấn để định vị GPS{% endif %}</strong></span>
        <span class="fw-bold text-success" style="cursor:pointer;" onclick="detectAndSaveLocation()">Định vị GPS ✓</span>
    </div>

    <!-- STORIES -->
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
        <a href="/checkout" class="btn btn-light btn-sm rounded-pill px-3 py-1 fw-bold fs-7 text-dark text-decoration-none">Đặt hàng VietQR</a>
    </div>

    <!-- FLASH SALE -->
    <div class="mobile-flash-bar">
        <span>⚡ FLASH SALE HÔM NAY</span>
        <div class="d-flex align-items-center gap-1">
            <span>Kết thúc:</span>
            <span class="countdown-box" id="ch-h">02</span>:
            <span class="countdown-box" id="ch-m">45</span>:
            <span class="countdown-box" id="ch-s">18</span>
        </div>
    </div>

    <!-- 2 COLS GRID -->
    <div class="mobile-grid" id="mobileGrid">
        {% for pid, p in products.items() %}
        {% set discount = (((p['original_price'] - p['price']) / p['original_price'] * 100) | round | int) if p.get('original_price', 0) > p['price'] else 0 %}
        <div class="mobile-card" data-cat="{{ p.get('category','') }}" data-name="{{ p.get('name','').lower() }}">
            <div class="mobile-thumb-wrap">
                {% if discount > 0 %}
                <span class="mobile-discount">-{{ discount }}%</span>
                {% endif %}
                <img id="thumb-{{ pid }}" src="{{ p['after_img'] }}" alt="{{ p['name'] }}" class="mobile-thumb">
                <div class="mobile-img-switch">
                    <span class="active" onclick="switchImg('{{ pid }}', '{{ p['after_img'] }}', this)">Sau</span>
                    <span onclick="switchImg('{{ pid }}', '{{ p['before_img'] }}', this)">Trước</span>
                </div>
            </div>
            <div class="mobile-card-content">
                <h4 class="mobile-title"><a href="/product/{{ pid }}" class="text-dark text-decoration-none">{{ p['name'] }}</a></h4>
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="price-val">{{ "{:,}".format(p['price']) }}đ</span>
                    <span class="badge bg-success bg-opacity-10 text-success p-1" style="font-size: 0.62rem;">Sẵn {{ p['stock_physical'] - p['stock_committed'] }}</span>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                    {% if p.get('original_price') %}
                    <span class="price-old">{{ "{:,}".format(p['original_price']) }}đ</span>
                    {% else %}
                    <span></span>
                    {% endif %}
                    <button type="button" class="mobile-buy-btn" onclick="openMobSheet('{{ pid }}', '{{ p['name'] }}', '{{ "{:,}".format(p['price']) }}đ', '{{ p['after_img'] }}')">🛒 Mua</button>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- FIXED BOTTOM NAV -->
    <nav class="mobile-bottom-nav">
        <a href="/mobile" class="nav-tab-item active">
            <span class="nav-tab-icon">🏠</span>
            <span>Trang chủ</span>
        </a>
        <a href="#category" class="nav-tab-item" onclick="window.scrollTo({top: 150, behavior: 'smooth'})">
            <span class="nav-tab-icon">📑</span>
            <span>Danh mục</span>
        </a>
        <a href="/checkout" class="nav-tab-item">
            <span class="nav-tab-icon">⚡</span>
            <span>Thanh toán</span>
        </a>
        <a href="/cart" class="nav-tab-item">
            <span class="nav-tab-icon">🛒<span class="badge-cart-mob live-cart-badge" {% if cart_count == 0 %}style="display:none;"{% endif %}>{{ cart_count }}</span></span>
            <span>Giỏ hàng</span>
        </a>
        {% if current_user %}
        <a href="/profile" class="nav-tab-item">
            <span class="nav-tab-icon">👤</span>
            <span>Tài khoản</span>
        </a>
        <a href="/logout" class="nav-tab-item text-danger">
            <span class="nav-tab-icon">🚪</span>
            <span>Đăng xuất</span>
        </a>
        {% else %}
        <a href="/login" class="nav-tab-item">
            <span class="nav-tab-icon">🔐</span>
            <span>Đăng nhập</span>
        </a>
        {% endif %}
    </nav>

    <!-- BOTTOM SHEET -->
    <div class="bottom-sheet-overlay" id="bottomSheet" onclick="closeMobSheet(event)">
        <div class="bottom-sheet-box" onclick="event.stopPropagation()">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="fw-bold m-0 fs-6" id="sheetTitle">Mua hàng</h5>
                <button type="button" class="btn-close btn-sm" onclick="closeMobSheetDirect()"></button>
            </div>
            <div class="d-flex gap-3 mb-3">
                <img id="sheetImg" src="" style="width: 65px; height: 65px; object-fit: cover; border-radius: 8px;" alt="">
                <div>
                    <div class="price-val fs-5" id="sheetPrice"></div>
                    <span class="badge bg-success bg-opacity-10 text-success fs-7">Sẵn sàng giao tận cửa</span>
                </div>
            </div>
            <div class="d-flex gap-2">
                <button type="button" class="btn btn-outline-dark flex-fill py-2 fs-7" id="sheetBtnAdd">🛒 Thêm vào giỏ</button>
                <button type="button" class="btn btn-sage flex-fill py-2 fw-bold fs-7" id="sheetBtnBuy">Mua ngay (VietQR)</button>
            </div>
        </div>
    </div>

    """ + COMMON_JS_SNIPPET + """
    <script>
        function filterMobCat(cat) {
            document.querySelectorAll('.mobile-card').forEach(card => {
                const cardCat = card.getAttribute('data-cat');
                card.style.display = (cat === 'all' || cardCat === cat) ? '' : 'none';
            });
        }

        function filterMob() {
            const s = document.getElementById('mobSearch').value.toLowerCase().trim();
            document.querySelectorAll('.mobile-card').forEach(card => {
                const name = card.getAttribute('data-name');
                card.style.display = (!s || name.includes(s)) ? '' : 'none';
            });
        }

        let currentMobPid = null;
        function openMobSheet(pid, name, price, img) {
            currentMobPid = pid;
            document.getElementById('sheetTitle').innerText = name;
            document.getElementById('sheetPrice').innerText = price;
            document.getElementById('sheetImg').src = img;
            
            document.getElementById('sheetBtnAdd').onclick = function() {
                addCartAjax(pid, name);
                closeMobSheetDirect();
            };
            document.getElementById('sheetBtnBuy').onclick = function() {
                addCartAjax(pid, name, '/checkout');
            };

            document.getElementById('bottomSheet').classList.add('active');
        }

        function closeMobSheet(e) {
            document.getElementById('bottomSheet').classList.remove('active');
        }

        function closeMobSheetDirect() {
            document.getElementById('bottomSheet').classList.remove('active');
        }

        // Live countdown timer simulation
        setInterval(() => {
            const elS = document.getElementById('ch-s');
            if (!elS) return;
            let s = parseInt(elS.innerText) - 1;
            if (s < 0) s = 59;
            elS.innerText = s < 10 ? '0' + s : s;
        }, 1000);
    </script>
</body>
</html>
"""

# ==============================================================================
# 4. MASTER DEMO SHOWCASE TEMPLATE
# ==============================================================================
DEMO_SHOWCASE_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 Nếp Nhỏ — Bộ Trình Diễn 3 Giao Diện Hoạt Động Thật (Desktop • Tablet • Mobile)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bar-bg: #1E293B;
            --accent: #7D9D7C;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0B1120; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }
        
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

        .viewport-wrapper {
            flex-grow: 1;
            background: #0B1120;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
            padding: 16px;
        }

        .device-frame {
            background: #FFFFFF;
            box-shadow: 0 25px 60px rgba(0,0,0,0.55);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .mode-desktop-view {
            width: 100%;
            height: 100%;
            border-radius: 8px;
            border: 1px solid #334155;
        }

        .mode-tablet-view {
            width: 820px;
            height: 92vh;
            border-radius: 26px;
            border: 12px solid #1E293B;
            box-shadow: 0 0 0 2px #475569;
        }

        .mode-mobile-view {
            width: 410px;
            height: 92vh;
            border-radius: 42px;
            border: 12px solid #1E293B;
            box-shadow: 0 0 0 2px #475569;
            position: relative;
        }
        .notch-bar {
            width: 120px;
            height: 22px;
            background: #1E293B;
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
            z-index: 10;
        }

        .mode-all-view {
            display: flex;
            gap: 20px;
            align-items: flex-start;
            height: 95%;
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
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .side-frame-desktop {
            width: 620px;
            height: 88%;
            border-radius: 10px;
            border: 8px solid #1E293B;
        }
        .side-frame-tablet {
            width: 440px;
            height: 88%;
            border-radius: 18px;
            border: 8px solid #1E293B;
        }
        .side-frame-mobile {
            width: 320px;
            height: 88%;
            border-radius: 26px;
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

    <div class="showcase-nav">
        <div class="showcase-brand">
            <span>🌿</span>
            <span>NẾP NHỎ D2C • BỘ 3 GIAO DIỆN TMĐT FLASK</span>
        </div>

        <div class="mode-btn-group">
            <button class="mode-btn active" onclick="setMode('desktop')">
                <span>🖥️</span> Desktop
            </button>
            <button class="mode-btn" onclick="setMode('tablet')">
                <span>📱</span> Tablet (iPad)
            </button>
            <button class="mode-btn" onclick="setMode('mobile')">
                <span>📲</span> Mobile (iPhone)
            </button>
            <button class="mode-btn" onclick="setMode('all')">
                <span>🔲</span> Xem Cả 3 Cùng Lúc (Side-by-Side)
            </button>
        </div>

        <div class="d-flex gap-2">
            <a href="/desktop" target="_blank" class="btn btn-sm btn-outline-light">Mở Desktop ↗</a>
            <a href="/tablet" target="_blank" class="btn btn-sm btn-outline-light">Mở Tablet ↗</a>
            <a href="/mobile" target="_blank" class="btn btn-sm btn-outline-light">Mở Mobile ↗</a>
        </div>
    </div>

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
                        <iframe src="/desktop?embed=1"></iframe>
                    </div>
                `;
            } else if (mode === 'tablet') {
                viewport.innerHTML = `
                    <div class="device-frame mode-tablet-view">
                        <iframe src="/tablet?embed=1"></iframe>
                    </div>
                `;
            } else if (mode === 'mobile') {
                viewport.innerHTML = `
                    <div class="device-frame mode-mobile-view">
                        <div class="notch-bar"></div>
                        <iframe src="/mobile?embed=1"></iframe>
                    </div>
                `;
            } else if (mode === 'all') {
                viewport.innerHTML = `
                    <div class="mode-all-view">
                        <div class="side-col">
                            <div class="side-title">🖥️ 1. Giao diện Desktop (1440 x 900)</div>
                            <div class="device-frame side-frame-desktop">
                                <iframe src="/desktop?embed=1"></iframe>
                            </div>
                        </div>
                        <div class="side-col">
                            <div class="side-title">📱 2. Giao diện Tablet (820 x 1180)</div>
                            <div class="device-frame side-frame-tablet">
                                <iframe src="/tablet?embed=1"></iframe>
                            </div>
                        </div>
                        <div class="side-col">
                            <div class="side-title">📲 3. Giao diện Mobile (393 x 852)</div>
                            <div class="device-frame side-frame-mobile">
                                <iframe src="/mobile?embed=1"></iframe>
                            </div>
                        </div>
                    </div>
                `;
            }
        }

        setMode('desktop');
    </script>
</body>
</html>
"""
