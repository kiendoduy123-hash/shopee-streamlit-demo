import streamlit as st
import pandas as pd
import random
import datetime

# Thiết lập trang - Phải là lệnh đầu tiên
st.set_page_config(page_title="Shopee MVP Prototype", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Tổng quan Font & Nền */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'Inter', sans-serif;
    }
    
    /* Ẩn bớt thanh viền ngăn cách mặc định của Streamlit */
    hr {
        border-top: 1px solid #F1F3F4;
        margin: 1.5rem 0;
    }

    /* Bo góc 25px và Đổ bóng cho [st.container(border=True)] và Sidebar */
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stSidebar"] {
        border-radius: 25px !important;
        background-color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    /* Hiệu ứng di chuột nổi lơ lửng cho Thẻ sản phẩm */
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 20px rgba(167, 199, 231, 0.15) !important;
        border-color: #A7C7E7 !important;
    }

    /* Tuỳ chỉnh Nút Bấm: Bo tròn, đậm */
    .stButton > button {
        border-radius: 25px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease;
        width: 100%;
        border: 1px solid #E0E0E0;
        white-space: nowrap;
    }
    .stButton > button:hover {
        border-color: #A7C7E7 !important;
        background-color: rgba(167, 199, 231, 0.1) !important;
        color: #A7C7E7 !important;
    }

    /* Ô input tìm kiếm */
    [data-testid="stTextInput"] input {
        border-radius: 25px !important;
        background-color: #F1F3F4;
        border: none !important;
        padding-left: 1.5rem;
    }
    [data-testid="stTextInput"] input:focus {
        border: 2px solid #A7C7E7 !important;
        background-color: white;
        box-shadow: none !important;
    }
    
    /* Đầu trang (Header Logo) */
    .header-logo {
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: -1px;
        color: #202124;
        margin-top: -10px;
        white-space: nowrap;
    }
    
    /* Ảnh sản phẩm đồng nhất */
    [data-testid="stImage"] img {
        height: 200px !important;
        object-fit: cover !important;
        border-radius: 15px !important;
    }
    
    /* Đồng bộ chiều cao văn bản thẻ sản phẩm */
    .product-title {
        font-weight: 700;
        font-size: 1.05rem;
        min-height: 3.2rem;
        margin-bottom: 0.5rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .product-caption {
        font-size: 0.85rem;
        color: #6c757d;
        margin-top: 0.5rem;
        min-height: 1.5rem;
    }
    .product-rating {
        font-size: 0.9rem;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if "cart" not in st.session_state:
    st.session_state.cart = {} # {product_id: quantity}

if "orders" not in st.session_state:
    st.session_state.orders = []

if "favorites" not in st.session_state:
    st.session_state.favorites = set() # Set of product_ids

if "active_category" not in st.session_state:
    st.session_state.active_category = "Tất cả"

# --- MOCK DATA ---
if "products" not in st.session_state:
    st.session_state.products = [
        # Football
        {"id": 1, "name": "Áo đấu Arsenal 2026/27 (Concept)", "price": 1850000, "image": "https://picsum.photos/seed/football1/400/300", "desc": "Áo đấu mẫu concept mới nhất của pháo thủ.", "category": "Bóng đá", "tag": "Top Item", "brand": "Adidas"},
        {"id": 2, "name": "Áo khoác Chelsea Training", "price": 1200000, "image": "https://picsum.photos/seed/football2/400/300", "desc": "Áo khoác tập luyện chuyên nghiệp.", "category": "Bóng đá", "brand": "Nike"},
        {"id": 3, "name": "Bóng thi đấu Premier League Official", "price": 3500000, "image": "https://picsum.photos/seed/football3/400/300", "desc": "Bóng chính thức dùng trong Ngoại hạng Anh.", "category": "Bóng đá", "brand": "Nike"},
        {"id": 4, "name": "Khăn len cổ động Arsenal (Classic)", "price": 450000, "image": "https://picsum.photos/seed/football4/400/300", "desc": "Khăn len cổ điển giữ ấm mùa đông.", "category": "Bóng đá", "brand": "Premier League"},
        {"id": 5, "name": "Găng tay thủ môn chuyên nghiệp", "price": 2100000, "image": "https://picsum.photos/seed/football5/400/300", "desc": "Găng tay độ bám cao, bảo vệ ngón tay.", "category": "Bóng đá", "brand": "Adidas"},
        # Anime & Media
        {"id": 6, "name": "Đĩa than RADWIMPS - Album \"Yuushinron\"", "price": 1500000, "image": "https://picsum.photos/seed/anime1/400/300", "desc": "Đĩa than đặc biệt số lượng có hạn.", "category": "Anime & Giải trí", "tag": "Limited", "brand": "Khác"},
        {"id": 7, "name": "Mô hình Naruto Shippuden", "price": 850000, "image": "https://picsum.photos/seed/anime2/400/300", "desc": "Mô hình chi tiết cao vũ trụ Naruto.", "category": "Anime & Giải trí", "brand": "Khác"},
        {"id": 8, "name": "Sách ảnh (Artbook) Your Name", "price": 600000, "image": "https://picsum.photos/seed/anime3/400/300", "desc": "Artbook tuyệt đẹp từ Makoto Shinkai.", "category": "Anime & Giải trí", "brand": "Studio Ghibli"},
        {"id": 9, "name": "Gấu bông Totoro (Studio Ghibli)", "price": 350000, "image": "https://picsum.photos/seed/anime4/400/300", "desc": "Gấu bông mềm mịn chính hãng Ghibli.", "category": "Anime & Giải trí", "brand": "Studio Ghibli"},
        {"id": 10, "name": "Poster lụa Anime Theme Songs", "price": 250000, "image": "https://picsum.photos/seed/anime5/400/300", "desc": "Poster chất lượng cao về các bản nhạc Anime.", "category": "Anime & Giải trí", "brand": "Khác"},
        # Physics Gadgets
        {"id": 11, "name": "Con lắc Newton (Động năng)", "price": 280000, "image": "https://picsum.photos/seed/physics1/400/300", "desc": "Đồ chơi giải trí minh hoạ định luật vật lý.", "category": "Đồ chơi Vật lý", "brand": "Khác"},
        {"id": 12, "name": "Động cơ Stirling", "price": 1150000, "image": "https://picsum.photos/seed/physics2/400/300", "desc": "Mô hình động cơ nhiệt chạy bằng cồn.", "category": "Đồ chơi Vật lý", "tag": "Top Item", "brand": "Khác"},
        {"id": 13, "name": "Quả cầu lơ lửng từ tính", "price": 950000, "image": "https://picsum.photos/seed/physics3/400/300", "desc": "Quả cầu lơ lửng giữa không trung bằng từ trường.", "category": "Đồ chơi Vật lý", "brand": "Khác"},
        {"id": 14, "name": "Lăng kính thủy tinh quang học", "price": 180000, "image": "https://picsum.photos/seed/physics4/400/300", "desc": "Khối lăng kính phân tách ánh sáng trắng.", "category": "Đồ chơi Vật lý", "brand": "Khác"},
        {"id": 15, "name": "Con quay hồi chuyển kim loại", "price": 420000, "image": "https://picsum.photos/seed/physics5/400/300", "desc": "Con quay cân bằng cực kỳ chuẩn xác.", "category": "Đồ chơi Vật lý", "brand": "Khác"},
        # IT & Tech
        {"id": 16, "name": "Bàn phím cơ Blue Pastel", "price": 2500000, "image": "https://picsum.photos/seed/tech1/400/300", "desc": "Bàn phím cơ switch custom gõ êm ái.", "category": "Công nghệ & IT", "brand": "Khác"},
        {"id": 17, "name": "Linh vật Linux Tux", "price": 300000, "image": "https://picsum.photos/seed/tech2/400/300", "desc": "Thú nhồi bông chim cánh cụt cho Coder.", "category": "Công nghệ & IT", "brand": "Linux Foundation"},
        {"id": 18, "name": "Ổ cứng SSD di động 2TB", "price": 3200000, "image": "https://picsum.photos/seed/tech3/400/300", "desc": "Ổ cứng flash tốc độ flash siêu cao.", "category": "Công nghệ & IT", "brand": "Khác"},
        {"id": 19, "name": "Bộ kit Raspberry Pi 5", "price": 2800000, "image": "https://picsum.photos/seed/tech4/400/300", "desc": "Mạch máy tính mini dùng cho dự án IoT.", "category": "Công nghệ & IT", "tag": "Best Seller", "brand": "Khác"},
        {"id": 20, "name": "Chuột Ergonomic cho Coder", "price": 1400000, "image": "https://picsum.photos/seed/tech5/400/300", "desc": "Chuột chống mỏi tay khi sử dụng thời gian dài.", "category": "Công nghệ & IT", "brand": "Khác"},
        # Student Wellness
        {"id": 21, "name": "Tai nghe chống ồn", "price": 4500000, "image": "https://picsum.photos/seed/well1/400/300", "desc": "Headphones over-ear hoàn toàn tĩnh lặng.", "category": "Đời sống Học đường", "brand": "Khác"},
        {"id": 22, "name": "Đèn nhịp sinh học", "price": 750000, "image": "https://picsum.photos/seed/well2/400/300", "desc": "Đèn học tự đổi màu bảo vệ mắt và giấc ngủ.", "category": "Đời sống Học đường", "brand": "Khác"},
        {"id": 23, "name": "Sổ tay lập kế hoạch", "price": 220000, "image": "https://picsum.photos/seed/well3/400/300", "desc": "Sổ tay tối ưu năng suất học tập và tinh thần.", "category": "Đời sống Học đường", "tag": "For Students", "brand": "Khác"},
        {"id": 24, "name": "Máy xông tinh dầu", "price": 550000, "image": "https://picsum.photos/seed/well4/400/300", "desc": "Máy khuếch tán giải tỏa căng thẳng.", "category": "Đời sống Học đường", "brand": "Khác"},
        {"id": 25, "name": "Chăn trọng lực trợ ngủ", "price": 1250000, "image": "https://picsum.photos/seed/well5/400/300", "desc": "Weighted blanket cải thiện chất lượng giấc ngủ.", "category": "Đời sống Học đường", "brand": "Khác"}
    ]
    
    random.seed(42) # Giữ cho rating không thay đổi giữa các phiên rerun
    for p in st.session_state.products:
        p["rating"] = round(random.uniform(3.0, 5.0), 1)

# --- HELPER FUNCTIONS ---
def format_currency_vnd(amount):
    return f"₫{amount:,.0f}"

def go_to_page(page_name):
    st.session_state.current_page = page_name

def set_category(cat):
    st.session_state.active_category = cat

def toggle_favorite(pid):
    if pid in st.session_state.favorites:
        st.session_state.favorites.remove(pid)
        st.toast("Đã bỏ yêu thích.")
    else:
        st.session_state.favorites.add(pid)
        st.toast("Đã thêm vào mục yêu thích! ❤️")

def add_to_cart(pid, qty=1):
    if pid in st.session_state.cart:
        st.session_state.cart[pid] += qty
    else:
        st.session_state.cart[pid] = qty
    st.toast("Đã thêm vào giỏ hàng! 🛒")

def get_product(pid):
    for p in st.session_state.products:
        if p["id"] == pid:
            return p
    return None

# --- LOGIN AUTHENTICATION FLOW ---
if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; color: #202124;'>Welcome to DDK Store</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #6c757d;'>Please sign in to continue</p>", unsafe_allow_html=True)
            st.divider()
            
            user_input = st.text_input("Username", placeholder="Enter any username (e.g., Kien)")
            pwd_input = st.text_input("Password", type="password", placeholder="Mock password")
            
            if st.button("Login", type="primary", use_container_width=True):
                if user_input.strip() != "":
                    st.session_state.logged_in = True
                    st.session_state.username = user_input.strip()
                    st.rerun()
                else:
                    st.error("Please enter a username!")
    st.stop()

# --- TOP HEADER MOCKUP ---
st.write("") # Dãn cách xíu
c_logo, c_search, c_greet, c_out, c_ord, c_fav, c_cart = st.columns([1.5, 2.2, 1.5, 0.8, 1, 1.2, 1], gap="small")

with c_logo:
    st.markdown('<div class="header-logo">DDK Store</div>', unsafe_allow_html=True)
with c_search:
    product_names = [p["name"] for p in st.session_state.products]
    search_query = st.selectbox("Tìm kiếm", options=product_names, index=None, placeholder="🔍 Search for products...", label_visibility="collapsed")
with c_greet:
    is_premium = "👑" if st.session_state.username.lower() == "kien" else "👋"
    st.markdown(f"<div style='margin-top: 0.5rem; white-space: nowrap; font-size: 0.95rem;'>{is_premium} Hi, <b>{st.session_state.username}</b>!</div>", unsafe_allow_html=True)
with c_out:
    if st.button("Thoát", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.current_page = "Home"
        st.rerun()
with c_ord:
    order_count = len(st.session_state.orders)
    if st.button(f"📦 Đơn ({order_count})", use_container_width=True):
        go_to_page("Orders")
with c_fav:
    fav_count = len(st.session_state.favorites)
    if st.button(f"🤍 Thích ({fav_count})", use_container_width=True):
        go_to_page("Favorites")
with c_cart:
    cart_count = sum(st.session_state.cart.values())
    if st.button(f"🛒 Giỏ ({cart_count})", use_container_width=True):
        go_to_page("Cart")

st.markdown("<br>", unsafe_allow_html=True)

# --- NGỮ CẢNH THEO TRANG ---
if st.session_state.current_page == "Home":
    
    # 1. CATEGORY PILLS (Phân Loại)
    categories = ["Tất cả", "Bóng đá", "Anime & Giải trí", "Đồ chơi Vật lý", "Công nghệ & IT", "Đời sống Học đường"]
    pill_cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with pill_cols[i]:
            btn_type = "primary" if st.session_state.active_category == cat else "secondary"
            st.button(cat, key=f"cat_{cat}", use_container_width=True, type=btn_type, on_click=set_category, args=(cat,))
                
    st.divider()
    
    # 2. BỐ CỤC SIDEBAR (Bộ Lọc) & MAIN CONTENT (Thẻ Sản Phẩm)
    sidebar_col, main_col = st.columns([1, 4], gap="large")
    
    with sidebar_col:
        
        st.markdown('### Lọc Khoảng Giá')
        price_opts = list(range(0, 5100000, 100000))
        price_labels = [format_currency_vnd(x) for x in price_opts]
        price_range_label = st.select_slider("Giá", options=price_labels, value=(price_labels[0], price_labels[-1]), label_visibility="collapsed")
        price_range = (price_opts[price_labels.index(price_range_label[0])], price_opts[price_labels.index(price_range_label[1])])
        
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('### Đánh giá Sao')
        star_filter = st.selectbox("Sao", ["Tất cả", "⭐⭐⭐⭐", "⭐⭐⭐"], label_visibility="collapsed")
        
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('### Thương Hiệu')
        br_nike = st.checkbox("✔️ Nike")
        br_adidas = st.checkbox("👟 Adidas")
        br_pl = st.checkbox("⚽ Premier League")
        br_ghibli = st.checkbox("⛩️ Studio Ghibli")
        br_linux = st.checkbox("🐧 Linux Foundation")
        
        # Danh sách thương hiệu đang chọn
        selected_brands = set()
        if br_nike: selected_brands.add("Nike")
        if br_adidas: selected_brands.add("Adidas")
        if br_pl: selected_brands.add("Premier League")
        if br_ghibli: selected_brands.add("Studio Ghibli")
        if br_linux: selected_brands.add("Linux Foundation")
        
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('### Phương thức Giao hàng')
        st.radio("Giao hàng", ["🚚 Tiêu chuẩn", "🏠 Nhận tại cửa hàng"], label_visibility="collapsed")

    with main_col:
        min_star = 0.0
        if "⭐⭐⭐⭐" in star_filter:
            min_star = 4.0
        elif "⭐⭐⭐" in star_filter:
            min_star = 3.0
            
        # Bộ lọc dữ liệu áp dụng
        query_val = search_query.lower() if search_query else ""
        filtered = [p for p in st.session_state.products if 
                    (st.session_state.active_category == "Tất cả" or p["category"] == st.session_state.active_category) 
                    and (price_range[0] <= p["price"] <= price_range[1])
                    and (query_val in p["name"].lower())
                    and (p.get("rating", 0) >= min_star)
                    and (len(selected_brands) == 0 or p.get("brand") in selected_brands)]
        
        if not filtered:
            st.warning("Không tìm thấy sản phẩm nào phù hợp với bộ lọc hiện tại. Hãy trượt độ rộng mức giá ra nhé!")
            
        # Grid layout (Tránh lỗi vỡ khung, dùng 3 cột cố định)
        grid_cols = st.columns(3, gap="large")
        for idx, p in enumerate(filtered):
            with grid_cols[idx % 3]:
                # SỬ DỤNG LỚP WRAPPER container(border) để chống rò rỉ HTML và ôm trọn Thẻ
                with st.container(border=True):
                    # Ảnh từ MNative Render
                    st.image(p["image"], use_container_width=True)
                    
                    # Tag, tên và category bằng Markdown tĩnh (chống lỗi)
                    is_fav = p["id"] in st.session_state.favorites
                    heart = "❤️" if is_fav else "🤍"
                    
                    # Ép Text Render ngầm vào các cấu trúc Div có height cố định
                    tag_display = f"🚀 <b>{p['tag']}</b> |" if p.get("tag") else ""
                    st.markdown(f'<div class="product-caption">{tag_display} {p["category"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="product-title">{p["name"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="product-rating">⭐ {p.get("rating", 5.0)}/5.0</div>', unsafe_allow_html=True)
                    
                    # Nút chức năng trong cùng container
                    btn1, btn2 = st.columns([1, 1])
                    with btn1:
                        if st.button("🛒 Thêm", key=f"add_{p['id']}", use_container_width=True):
                            add_to_cart(p['id'])
                    with btn2:
                        if st.button(format_currency_vnd(p['price']), key=f"prc_{p['id']}", use_container_width=True, type="primary"):
                            pass
                            
                    with st.expander("📝 Chi tiết sản phẩm"):
                        st.write(p['desc'])
                        if st.button(f"Thích {heart}", key=f"fav_{p['id']}", use_container_width=True):
                            toggle_favorite(p['id'])
                            st.rerun()

elif st.session_state.current_page == "Favorites":
    st.button("← Tiếp tục Lựa Sản phẩm", on_click=lambda: go_to_page("Home"))
    st.markdown("<h2>🤍 Sản Phẩm Yêu Thích Của Tôi</h2>", unsafe_allow_html=True)
    
    if not st.session_state.favorites:
        st.info("Kho lưu trữ trống không. Cậu hãy lướt Cửa hàng ngắm nghía đồ nhé!")
    else:
        grid_cols = st.columns(4, gap="large")
        fav_list = [p for p in st.session_state.products if p["id"] in st.session_state.favorites]
        
        for idx, p in enumerate(fav_list):
            with grid_cols[idx % 4]:
                with st.container(border=True):
                    st.image(p["image"], use_container_width=True)
                    tag_display = f"🚀 <b>{p['tag']}</b> |" if p.get("tag") else ""
                    st.markdown(f'<div class="product-caption">{tag_display} {p["category"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="product-title">{p["name"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="product-rating">⭐ {p.get("rating", 5.0)}/5.0</div>', unsafe_allow_html=True)
                    
                    b1, b2 = st.columns([1, 1])
                    with b1:
                        if st.button("🛒 Thêm", key=f"fv_add_{p['id']}", use_container_width=True):
                            add_to_cart(p['id'])
                    with b2:
                        if st.button("💔 Bỏ thích", key=f"fv_rm_{p['id']}", use_container_width=True):
                            toggle_favorite(p['id'])
                            st.rerun()

elif st.session_state.current_page == "Cart":
    st.button("← Quay lại Lựa Sản phẩm", on_click=lambda: go_to_page("Home"))
    st.markdown("<h2>🛒 Giỏ Hàng & Quản Lý Đơn</h2>", unsafe_allow_html=True)
    
    if not st.session_state.cart:
        st.info("Giỏ hàng của cậu đang trống rỗng. Nhấn 'Quay lại' để shopping nha!")
    else:
        subtotal = 0
        for pid, qty in list(st.session_state.cart.items()):
            p = get_product(pid)
            if p:
                subtotal += p["price"] * qty
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1, 4, 1.5, 1])
                    with c1:
                        st.image(p["image"], use_container_width=True)
                    with c2:
                        st.markdown(f"**{p['name']}**")
                        st.caption(f"Đơn giá: {format_currency_vnd(p['price'])}")
                    with c3:
                        new_qty = st.number_input("Số lượng", min_value=1, max_value=99, value=qty, key=f"cart_qty_{pid}", label_visibility="collapsed")
                        st.session_state.cart[pid] = new_qty
                    with c4:
                        if st.button("🗑️ Bỏ", key=f"cart_rm_{pid}", use_container_width=True):
                            del st.session_state.cart[pid]
                            st.rerun()
                
        st.markdown(f"### Tạm tính: <span style='color: #A7C7E7;'>{format_currency_vnd(subtotal)}</span>", unsafe_allow_html=True)
        if st.button("Tiến Hành Lên Đơn (Checkout)", use_container_width=True, type="primary"):
            go_to_page("Checkout")
            st.rerun()

elif st.session_state.current_page == "Checkout":
    st.button("← Xem lại Giỏ", on_click=lambda: go_to_page("Cart"))
    st.markdown("<h2>💳 Xác Nhận & Thanh Toán</h2>", unsafe_allow_html=True)
    
    if not st.session_state.cart:
        st.warning("Không có sản phẩm nào để thanh toán cả.")
    else:
        colA, colB = st.columns([2, 1], gap="large")
        
        with colA:
            with st.container(border=True):
                st.subheader("1. Thông tin Vận chuyển")
                st.selectbox("Chọn địa chỉ lưu sẵn:", ["123 Nguyễn Huệ, Quận 1, TP.HCM", "Tuổi Trẻ Tower, Quận Cầu Giấy, HN", "Đà Nẵng"])
                st.radio("Đơn vị Giao hàng:", ["🚚 GHTK Tiêu chuẩn (₫20,000)", "🚀 Hoả tốc (₫50,000)"])
                
            with st.container(border=True):
                st.subheader("2. Hình thức Thanh toán")
                st.selectbox("Chọn phương thức:", ["Ví chuyển khoản (MoMo/ZaloPay)", "Thẻ Tín dụng / Ghi nợ", "Thanh toán lúc nhận (COD)"])
                voucher = st.text_input("Mã Voucher Giảm 10%", placeholder="Gõ SALE10")
        
        with colB:
            with st.container(border=True):
                st.subheader("Hoá Đơn Bán Lẻ")
                subtotal = sum((get_product(pid)["price"] * qty for pid, qty in st.session_state.cart.items()))
                discount = subtotal * 0.1 if voucher.strip().upper() == "SALE10" else 0
                shipping_fee = 20000 # Tạm fix vì tính logic đơn giản MVP
                
                total = subtotal + shipping_fee - discount
                
                st.write(f"Tiền hàng thu: {format_currency_vnd(subtotal)}")
                st.write(f"Phí vận chuyển: {format_currency_vnd(shipping_fee)}")
                if discount > 0:
                    st.write(f"Giảm giá (Voucher): -{format_currency_vnd(discount)}")
                    
                st.divider()
                st.markdown(f"**TỔNG TIỀN:** <br><span style='color: #A7C7E7; font-size: 2rem; font-weight: 800;'>{format_currency_vnd(total)}</span>", unsafe_allow_html=True)
                st.write("")
                if st.button("XÁC NHẬN MUA", use_container_width=True, type="primary"):
                    new_order = {
                        "id": f"ORD-{random.randint(1000, 9999)}",
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "items": dict(st.session_state.cart),
                        "total": total,
                        "status": "Đang xử lý"
                    }
                    st.session_state.orders.append(new_order)
                    st.session_state.cart = {} # Làm rỗng luồng
                    st.success("🎉 Giao dịch thành công! Gói hàng của bạn đã được đóng gói ảo.")
                    st.balloons()

elif st.session_state.current_page == "Orders":
    st.button("← Tiếp tục Mua Sắm", on_click=lambda: go_to_page("Home"))
    st.markdown("<h2>📦 Lịch Sử Đơn Hàng</h2>", unsafe_allow_html=True)
    
    if not st.session_state.orders:
        st.info("Cậu chưa có đơn hàng nào cả. Trở về trang chủ rinh thêm đồ nhé!")
    else:
        for order in reversed(st.session_state.orders): # Hiển thị đơn mới nhất lên đầu
            with st.container(border=True):
                st.subheader(f"Mã đơn: {order['id']}")
                st.caption(f"Mua ngày: {order['date']}")
                st.markdown(f"**Trạng thái:** <span style='color: #28a745;'>{order['status']}</span>", unsafe_allow_html=True)
                st.divider()
                
                for pid, qty in order['items'].items():
                    p = get_product(pid)
                    if p:
                        st.write(f"- **{qty}x** {p['name']} ({format_currency_vnd(p['price'] * qty)})")
                
                st.markdown(f"#### Tổng thanh toán: <span style='color: #A7C7E7;'>{format_currency_vnd(order['total'])}</span>", unsafe_allow_html=True)
