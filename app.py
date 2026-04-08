import streamlit as st
import pandas as pd
import random
import datetime
import database as db

# Thiết lập trang - Phải là lệnh đầu tiên
st.set_page_config(page_title="Shopee MVP Prototype", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

# SHPP-1: Giao diện Blue Pastel và Login flow
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

    /* Ô input tìm kiếm & chatbot */
    [data-testid="stTextInput"] > div > div {
        border-radius: 25px !important;
        background-color: #F1F3F4 !important;
    }
    [data-testid="stTextInput"] input {
        padding-left: 15px !important;
        padding-right: 15px !important;
        background-color: transparent !important;
    }
    [data-testid="stTextInput"] > div > div:focus-within {
        border: 2px solid #A7C7E7 !important;
        background-color: white !important;
    }
    
    /* Đầu trang (Header Logo) */
    .header-logo {
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: -1px;
        color: #202124;
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
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
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

if "user_role" not in st.session_state:
    st.session_state.user_role = "user"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if "cart" not in st.session_state:
    st.session_state.cart = {} # {product_id: quantity}

if "favorites" not in st.session_state:
    st.session_state.favorites = set() # Set of product_ids

if "active_category" not in st.session_state:
    st.session_state.active_category = "Tất cả"

# --- DATA LAYER ---
def fetch_products():
    return db.get_all_products()

if "products" not in st.session_state:
    st.session_state.products = fetch_products()

# --- HELPER FUNCTIONS ---
def format_currency_vnd(amount):
    return f"₫{amount:,.0f}"

def go_to_page(page_name):
    st.session_state.current_page = page_name

def set_category(cat):
    st.session_state.active_category = cat

# SHPP-3: Hàm xử lý thêm/xóa sản phẩm yêu thích (Database Sync)
def toggle_favorite(pid):
    if st.session_state.logged_in:
        added = db.toggle_favorite_db(st.session_state.username, pid)
        if added:
            st.session_state.favorites.add(pid)
            st.toast("Đã thêm vào mục yêu thích! ❤️")
        else:
            st.session_state.favorites.remove(pid)
            st.toast("Đã bỏ yêu thích.")
    else:
        st.toast("Bạn cần đăng nhập để lưu yêu thích!", icon="⚠️")

# SHPP-5: Quản lý logic Giỏ hàng.
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

# --- INITIAL DATA LOAD ON LOGIN ---
def load_user_data(username, role):
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.user_role = role
    st.session_state.favorites = db.get_favorites(username)
    st.session_state.cart = {} # clear cart cross user
    st.rerun()

# --- LOGIN AUTHENTICATION FLOW ---
if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; color: #202124;'>Welcome to DDK Store</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #6c757d;'>Đăng nhập hoặc đăng ký</p>", unsafe_allow_html=True)
            st.divider()
            
            tab_login, tab_reg = st.tabs(["Đăng nhập", "Đăng ký"])
            
            with tab_login:
                with st.form("login_form", border=False):
                    user_log = st.text_input("Tên đăng nhập", key="user_log_in")
                    pwd_log = st.text_input("Mật khẩu", type="password", key="pwd_log_in")
                    
                    if st.form_submit_button("Đăng nhập", type="primary", use_container_width=True):
                        if user_log and pwd_log:
                            auth = db.authenticate_user(user_log.strip(), pwd_log)
                            if auth["success"]:
                                load_user_data(user_log.strip(), auth["role"])
                            else:
                                st.error("Sai tên đăng nhập hoặc mật khẩu!")
                        else:
                            st.error("Vui lòng nhập đủ thông tin!")
            
            with tab_reg:
                with st.form("register_form", border=False):
                    user_reg = st.text_input("Tên đăng nhập mới", key="user_reg")
                    pwd_reg = st.text_input("Mật khẩu mới", type="password", key="pwd_reg")
                    
                    if st.form_submit_button("Đăng ký tài khoản", type="primary", use_container_width=True):
                        if user_reg and pwd_reg:
                            if db.register_user(user_reg.strip(), pwd_reg):
                                st.success("Tạo tài khoản thành công! Hãy đăng nhập lại.")
                            else:
                                st.error("Tên đăng nhập đã tồn tại!")
                        else:
                            st.error("Vui lòng nhập đủ thông tin!")

    st.stop()

# --- TOP HEADER MOCKUP ---
st.write("") # Dãn cách xíu

# Đưa tên shop lên trên cùng
st.markdown('<div class="header-logo" style="margin-bottom: 15px;">DDK Store</div>', unsafe_allow_html=True)

if st.session_state.user_role == "admin":
    c_search, c_greet, c_admin, c_out, c_ord, c_fav, c_cart = st.columns([3.5, 1.4, 1.3, 1.0, 1.3, 1.3, 1.3], gap="small", vertical_alignment="center")
else:
    c_search, c_greet, c_out, c_ord, c_fav, c_cart = st.columns([4.0, 1.5, 1.2, 1.2, 1.5, 1.5], gap="small", vertical_alignment="center")

# SHPP-4: Ô tìm kiếm sản phẩm thông minh trên Header
with c_search:
    product_names = [p["name"] for p in st.session_state.products]
    search_query = st.selectbox("Tìm kiếm", options=product_names, index=None, placeholder="🔍 Search for products...", label_visibility="collapsed")
with c_greet:
    is_premium = "👑" if st.session_state.user_role == "admin" else "👋"
    st.markdown(f"<div style='white-space: nowrap; font-size: 0.95rem; text-align: center;'>{is_premium} Hi, <b>{st.session_state.username}</b>!</div>", unsafe_allow_html=True)

if st.session_state.user_role == "admin":
    with c_admin:
        if st.button("⚙️ Admin", use_container_width=True):
            go_to_page("Admin")

with c_out:
    if st.button("Thoát", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_role = "user"
        st.session_state.current_page = "Home"
        st.rerun()
with c_ord:
    order_count = len(db.get_user_orders(st.session_state.username))
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
    
    # SHPP-2: Logic lọc sản phẩm Sidebar
    # 2. BỐ CỤC SIDEBAR (Bộ Lọc) & MAIN CONTENT (Thẻ Sản Phẩm)
    sidebar_col, main_col = st.columns([1.3, 3.7], gap="large")
    
    with sidebar_col:
        
        # --- CHATBOT MOCK ---
        with st.expander("💬 Chatbot DDK AI", expanded=False):
            st.caption("Hãy hỏi tôi về đơn hàng hoặc sản phẩm!")
            chat_input = st.text_input("Gửi tin nhắn", key="chat_input", label_visibility="collapsed", placeholder="Ví dụ: Lấy cho tôi bảng size")
            if st.button("Gửi", use_container_width=True):
                if chat_input:
                    ans = "Cảm ơn cậu đã quan tâm, DDK Store sẽ phản hồi lại sớm nhất!"
                    if "size" in chat_input.lower():
                        ans = "Đa số áo bên mình fit theo chuẩn Form Âu rộng rãi. Bạn có thể chọn lùi 1 size nếu muốn mặc ôm nhé!"
                    elif "ship" in chat_input.lower() or "giao" in chat_input.lower():
                        ans = "Thời gian giao hàng trung bình là 2-3 ngày làm việc đối với hỏa tốc (trong TP.HCM)."
                    elif "hoàn" in chat_input.lower() or "trả" in chat_input.lower():
                        ans = "Bên mình hỗ trợ hoàn đồ miễn phí trong 7 ngày đầu chừng nào tem mác còn nguyên. Bạn có muốn đổi trả đơn hàng gần nhất không?"
                    st.success(f"🤖 **AI:** {ans}")
        
        st.markdown('<br>', unsafe_allow_html=True)
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
        # SHPP-4: Xử lý logic lọc sản phẩm theo từ khóa tìm kiếm
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
                            
                    # SHPP-3: Hiển thị chi tiết sản phẩm và nút Thích
                    with st.expander("📝 Chi tiết sản phẩm"):
                        st.write(p['desc'])
                        
                        # --- AI RECOMMENDATION MOCK ---
                        st.markdown("**💡 Có thể bạn cũng thích:**")
                        related = [rp for rp in st.session_state.products if rp["category"] == p["category"] and rp["id"] != p["id"]]
                        if related:
                            for rp in related[:2]:  # Lấy 2 sản phẩm ngẫu nhiên cùng danh mục
                                st.caption(f"- {rp['name']} ({format_currency_vnd(rp['price'])})")
                        
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

# SHPP-5: Quản lý logic Giỏ hàng.
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
                # SHPP-6: Tính toán Voucher phức tạp và Phí vận chuyển.
                voucher_code = voucher.strip().upper()
                discount = 0
                shipping_fee = 20000
                if voucher_code == "SALE10":
                    discount = subtotal * 0.1
                    st.success("Áp dụng mã SALE10 thành công (Giảm 10%)")
                elif voucher_code == "FREESHIP":
                    discount = min(shipping_fee, 50000)
                    st.success("Áp dụng mã FREESHIP thành công")
                elif voucher_code == "DDKVIP" and st.session_state.user_role == "admin":
                    discount = subtotal * 0.5
                    st.success("Mã VIP của Admin (Giảm 50%!)")
                elif voucher_code:
                    st.error("Mã voucher không hợp lệ hoặc đã hết hạn.")
                
                total = subtotal + shipping_fee - discount
                
                st.write(f"Tiền hàng thu: {format_currency_vnd(subtotal)}")
                st.write(f"Phí vận chuyển: {format_currency_vnd(shipping_fee)}")
                if discount > 0:
                    st.write(f"Giảm giá (Voucher): -{format_currency_vnd(discount)}")
                    
                st.divider()
                st.markdown(f"**TỔNG TIỀN:** <br><span style='color: #A7C7E7; font-size: 2rem; font-weight: 800;'>{format_currency_vnd(total)}</span>", unsafe_allow_html=True)
                st.write("")
                # SHPP-7: Logic Thanh toán và hiệu ứng thành công.
                if st.button("XÁC NHẬN MUA", use_container_width=True, type="primary"):
                    order_id = f"ORD-{random.randint(1000, 9999)}"
                    db.save_order(order_id, st.session_state.username, st.session_state.cart, total)
                    st.session_state.products = fetch_products() # Update inventory locally
                    st.session_state.cart = {} # Làm rỗng luồng
                    st.success("🎉 Giao dịch thành công! Gói hàng của bạn đã được đóng gói.")
                    st.balloons()

# SHPP-8: Hiển thị lịch sử đơn hàng đã mua.
elif st.session_state.current_page == "Orders":
    st.button("← Tiếp tục Mua Sắm", on_click=lambda: go_to_page("Home"))
    st.markdown("<h2>📦 Lịch Sử Đơn Hàng</h2>", unsafe_allow_html=True)
    
    user_orders = db.get_user_orders(st.session_state.username)
    if not user_orders:
        st.info("Cậu chưa có đơn hàng nào cả. Trở về trang chủ rinh thêm đồ nhé!")
    else:
        for order in user_orders:
            with st.container(border=True):
                st.subheader(f"Mã đơn: {order['id']}")
                st.caption(f"Mua ngày: {order['order_date']}")
                st.markdown(f"**Trạng thái:** <span style='color: #28a745;'>{order['status']}</span>", unsafe_allow_html=True)
                st.divider()
                
                for pid, qty in order['items'].items():
                    p = get_product(pid)
                    if p:
                        st.write(f"- **{qty}x** {p['name']} ({format_currency_vnd(p['price'] * qty)})")
                
                st.markdown(f"#### Tổng thanh toán: <span style='color: #A7C7E7;'>{format_currency_vnd(order['total_amount'])}</span>", unsafe_allow_html=True)

elif st.session_state.current_page == "Admin":
    if st.session_state.user_role != "admin":
        st.error("Bạn không có quyền truy cập trang này!")
        st.stop()
        
    st.button("← Trở về Trang chủ", on_click=lambda: go_to_page("Home"))
    st.markdown("<h2>⚙️ Admin Dashboard</h2>", unsafe_allow_html=True)
    
    t_dash, t_orders = st.tabs(["📊 Thống kê", "📋 Quản lý Đơn hàng"])
    
    with t_dash:
        stats = db.get_summary_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng doanh thu (VNĐ)", format_currency_vnd(stats['revenue']))
        c2.metric("Tổng đơn hàng", stats['orders'])
        c3.metric("Tổng người dùng", stats['users'])
        
        st.info("Ở phiên bản sau, ta có thể tích hợp thư viện Plotly để vẽ biểu đồ doanh số theo tháng.")
        
    with t_orders:
        admin_orders = db.get_all_orders_admin()
        if not admin_orders:
            st.info("Chưa có đơn hàng nào trên hệ thống.")
        else:
            for o in admin_orders:
                with st.expander(f"Đơn {o['id']} - Khách: {o['username']} - {format_currency_vnd(o['total_amount'])} - {o['status']}"):
                    st.write(f"**Ngày mua:** {o['order_date']}")
                    
                    c_st1, c_st2 = st.columns([2,1])
                    with c_st1:
                        new_st = st.selectbox("Cập nhật trạng thái", 
                                            ["Đang xử lý", "Đã giao cho vận chuyển", "Giao thành công", "Đã Hủy"], 
                                            key=f"st_{o['id']}")
                    with c_st2:
                        st.write("") # padding
                        st.write("")
                        if st.button("Cập nhật", key=f"btn_{o['id']}", use_container_width=True):
                            db.update_order_status(o['id'], new_st)
                            st.success("Đã cập nhật trạng thái đơn hàng!")
                            st.rerun()
