import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import urllib.parse 
from PIL import Image 

# ==========================================
# ⚙️ KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Executive Dashboard - Swasa Edition", layout="wide", page_icon="✨")

# ==========================================
# 🔒 SISTEM KEAMANAN (LOGIN USER & PASS)
# ==========================================
# Credential Baru
USER_RAHASIA = "mahesya13"
PASS_RAHASIA = "swasa226"

def check_login():
    """Memeriksa Username dan Password"""
    
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        # Tampilan Login Area
        st.markdown(
            """
            <style>
            .login-box {
                max-width: 400px; 
                margin: 100px auto; 
                padding: 30px; 
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                background-color: white;
                text-align: center;
            }
            .stTextInput > label {font-weight:bold; color:#2c3e50;}
            </style>
            """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("### 🔒 ACCESS RESTRICTED")
            st.info("Silakan Login untuk mengakses Dashboard Pabrik.")
            
            user_input = st.text_input("Username:", key="user_input")
            pass_input = st.text_input("Password:", type="password", key="pass_input")
            
            if st.button("LOGIN", type="primary"):
                if user_input == USER_RAHASIA and pass_input == PASS_RAHASIA:
                    st.session_state["logged_in"] = True
                    st.rerun() # Refresh halaman setelah login sukses
                else:
                    st.error("❌ Username atau Password Salah!")
            
        return False
    else:
        return True

# JIKA BELUM LOGIN, STOP DI SINI
if not check_login():
    st.stop()

# ==========================================
# 🚀 MULAI KONTEN DASHBOARD (SETELAH LOGIN)
# ==========================================

# CSS Styling Pro
st.markdown("""
<style>
    /* HEADER STYLING */
    .header-container { padding-top: 10px; padding-bottom: 20px; }
    .main-header {
        font-size: 42px; font-weight: 900; 
        background: linear-gradient(90deg, #005bea 0%, #00c6fb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: left; margin-bottom: 5px; line-height: 1.1;
        filter: drop-shadow(0px 0px 3px rgba(0, 198, 251, 0.3));
    }
    .sub-header { font-size: 18px; color: #546e7a; text-align: left; margin-bottom: 15px; font-weight: 500; }
    .dev-credit { font-size: 15px; color: #b0bec5; font-weight: 500; font-style: italic; text-align: left; margin-top: 10px; letter-spacing: 0.5px; }

    /* KPI CARD */
    .kpi-card {
        background: white; border-radius: 15px; padding: 20px; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-left: 5px solid #3498db;
        margin-bottom: 10px; transition: transform 0.3s, box-shadow 0.3s;
    }
    .kpi-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
    .kpi-title { font-size: 13px; color: #95a5a6; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-size: 26px; font-weight: 800; color: #2c3e50; margin-top: 8px; }
    .kpi-unit { font-size: 12px; color: #bdc3c7; font-weight: 500;}
    
    .border-prod { border-left-color: #005bea !important; }
    .border-qual { border-left-color: #00c6fb !important; }
    .border-chem { border-left-color: #ff9a44 !important; }
    .border-phys { border-left-color: #a18cd1 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SIDEBAR (PENGATURAN DATA BULANAN)
# ==========================================
with st.sidebar:
    st.title("🎛️ Control Panel")
    
    # --- FITUR UPLOAD LOGO ---
    with st.expander("🖼️ Logo Dashboard"):
        uploaded_file = st.file_uploader("Ganti Logo (PNG/JPG):", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    
    # --- PILIH SUMBER DATA (GANTI BULAN/TAHUN) ---
    st.header("📅 Pilih Data Bulan")
    
    default_id = "1yccpRefabM87-Ltzg0lbMHcsR2Qs6ZxPGd5A15jAHZ4"
    sheet_id = st.text_input("ID Google Sheet (File):", value=default_id, help="Ganti ID ini jika membuat File Excel Baru untuk Tahun Baru")

    # Mode Pemilihan Tab Sheet
    mode_input = st.radio("Metode Pilih Tab:", ["Pilih Bulan Otomatis", "Input Nama Manual"])
    
    if mode_input == "Pilih Bulan Otomatis":
        # Dropdown Bulan
        list_bulan = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
        pilih_bulan = st.selectbox("Pilih Bulan Laporan:", list_bulan, index=0)
        
        # Generator Nama Sheet Otomatis
        # Format sesuai Excel Bapak: "LAPORAN FP BE [BULAN]"
        sheet_name = f"LAPORAN FP BE {pilih_bulan}"
        st.info(f"Membaca Tab: **{sheet_name}**")
        
    else:
        # Input Manual (Jika format nama tab berubah, misal ada tahunnya)
        sheet_name = st.text_input("Ketik Nama Tab Persis:", value="LAPORAN FP BE JANUARY")

    st.divider()
    
    st.header("🎯 Target Setting")
    target_daily = st.number_input("Target Harian (Ton/Hari):", value=45.0, step=1.0)
    target_monthly = target_daily * 31
    st.caption(f"Target Bulanan: **{target_monthly:,.0f} Ton**")
    
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 REFRESH", type="primary"):
            st.cache_data.clear()
            st.rerun()
    with col_btn2:
        if st.button("🔒 LOGOUT"):
            del st.session_state["logged_in"]
            st.rerun()

# ==========================================
# 🖼️ HEADER SECTION
# ==========================================
st.markdown('<div class="header-container">', unsafe_allow_html=True)
col_logo, col_teks = st.columns([1.2, 5], gap="large")

with col_logo:
    try:
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
        else:
            try: st.image("image_0.png", use_container_width=True)
            except: 
                try: st.image("image_0.jpg", use_container_width=True)
                except: st.info("Logo Placeholder")
    except: st.error("Error Logo")
    st.markdown("""<style>[data-testid="stImage"] img {border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}</style>""", unsafe_allow_html=True)

with col_teks:
    st.markdown('<div class="main-header">FACTORY OPERATION DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Monitoring Data: <b>{sheet_name}</b> | Production, Quality & Efficiency</div>', unsafe_allow_html=True)
    st.markdown('<div class="dev-credit">✨ Created & Developer : Mahesya</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# ==========================================
# 📘 KAMUS SPEK
# ==========================================
KAMUS_SPEK_PH = {
    "Z 125":    [3.0, 5.0],
    "Z 211":    [3.5, 5.5],
    "Z 211 SC": [4.0, 7.0],
    "Z 221 S":  [4.0, 7.0],
    "Z 127":    [4.0, 7.0],
    "Z 301":    [4.0, 7.0] 
}

# ==========================================
# 2. MESIN PEMBACA DATA
# ==========================================
@st.cache_data
def load_data(id, sheet_name_input):
    if sheet_name_input:
        nama_sheet_aman = urllib.parse.quote(sheet_name_input)
        url = f'https://docs.google.com/spreadsheets/d/{id}/gviz/tq?tqx=out:csv&sheet={nama_sheet_aman}'
    else:
        url = f'https://docs.google.com/spreadsheets/d/{id}/export?format=csv'
        
    try:
        df = pd.read_csv(url, header=None, dtype=str, keep_default_na=False)
        
        header_row = -1
        for i in range(15):
            row_str = " ".join(df.iloc[i].astype(str).tolist()).upper()
            if "DATE" in row_str and "FLOW" in row_str:
                header_row = i
                break
        
        if header_row == -1:
            return None # Indikasi tab tidak ditemukan
            
        df_clean = df.iloc[header_row + 1:].copy()
        
        df_clean = df_clean.iloc[:, :14] 
        df_clean.columns = [
            "DATE", "FLOW", "MOIST_IN", "PRODUCT", "BATCH", 
            "MOIST_FINISH_PRODUCT", "PH", "DENSITY", "PARTICLE_SIZE", 
            "ACID_CONTENT", "ACIDITY", "SURFACE_AREA", 
            "BP_2_PERCENT", "STD_BP_2_PERCENT"
        ]
        
        df_clean = df_clean[~df_clean["DATE"].str.contains("Total|Average|Month", case=False, na=False)]
        df_clean = df_clean[df_clean["DATE"] != ""]
        
        numeric_cols = ["FLOW", "MOIST_IN", "BATCH", "MOIST_FINISH_PRODUCT", "PH", 
                        "DENSITY", "PARTICLE_SIZE", "ACID_CONTENT", "ACIDITY", 
                        "SURFACE_AREA"]
                        
        def clean_num(x):
            try: return float(str(x).replace(',', '.').strip())
            except: return 0.0

        for col in numeric_cols:
            df_clean[col] = df_clean[col].apply(clean_num)

        df_clean = df_clean[df_clean["BATCH"] > 0]
        return df_clean

    except Exception as e:
        return None

# ==========================================
# 3. DASHBOARD VISUALIZATION
# ==========================================
if sheet_id:
    df = load_data(sheet_id, sheet_name)
    
    if df is not None and not df.empty:
        
        # KPI Calculation
        total_prod_kg = df['BATCH'].sum()
        total_prod_ton = total_prod_kg / 1000
        total_flow = df['FLOW'].sum() 
        
        yield_prod = (total_prod_kg / total_flow * 100) if total_flow > 0 else 0
        losses = 100 - yield_prod
        achievement = (total_prod_ton / target_monthly * 100) if target_monthly > 0 else 0
        
        avg_density = df[df['DENSITY']>0]['DENSITY'].mean()
        avg_part_size = df[df['PARTICLE_SIZE']>0]['PARTICLE_SIZE'].mean()
        avg_surface = df[df['SURFACE_AREA']>0]['SURFACE_AREA'].mean()
        avg_min = df[df['MOIST_IN']>0]['MOIST_IN'].mean()
        avg_fp = df[df['MOIST_FINISH_PRODUCT']>0]['MOIST_FINISH_PRODUCT'].mean() 
        avg_ph = df[df['PH']>0]['PH'].mean()
        avg_acid = df[df['ACID_CONTENT']>0]['ACID_CONTENT'].mean()
        avg_acidity = df[df['ACIDITY']>0]['ACIDITY'].mean()

        # KPI GRID
        st.markdown("##### 🏗️ Production & Physical Properties")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(f'<div class="kpi-card border-prod"><div class="kpi-title">Total Production</div><div class="kpi-value">{total_prod_ton:,.1f}</div><div class="kpi-unit">Ton</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card border-prod"><div class="kpi-title">Total Flow</div><div class="kpi-value">{total_flow:,.0f}</div><div class="kpi-unit">Kg Input</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card border-phys"><div class="kpi-title">Avg Density</div><div class="kpi-value">{avg_density:.4f}</div><div class="kpi-unit">g/ml</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-card border-phys"><div class="kpi-title">Avg Particle Size</div><div class="kpi-value">{avg_part_size:.2f}</div><div class="kpi-unit">%</div></div>', unsafe_allow_html=True)
        c5.markdown(f'<div class="kpi-card border-phys"><div class="kpi-title">Avg Surface Area</div><div class="kpi-value">{avg_surface:,.0f}</div><div class="kpi-unit">m²/g</div></div>', unsafe_allow_html=True)
        
        st.markdown("##### 🧪 Chemical & Quality Control")
        c6, c7, c8, c9, c10 = st.columns(5)
        c6.markdown(f'<div class="kpi-card border-qual"><div class="kpi-title">Avg Moist Input</div><div class="kpi-value">{avg_min:.2f}</div><div class="kpi-unit">%</div></div>', unsafe_allow_html=True)
        c7.markdown(f'<div class="kpi-card border-qual"><div class="kpi-title">Avg Moist Finish Product</div><div class="kpi-value">{avg_fp:.2f}</div><div class="kpi-unit">%</div></div>', unsafe_allow_html=True)
        c8.markdown(f'<div class="kpi-card border-chem"><div class="kpi-title">Avg pH</div><div class="kpi-value">{avg_ph:.2f}</div><div class="kpi-unit">Scale</div></div>', unsafe_allow_html=True)
        c9.markdown(f'<div class="kpi-card border-chem"><div class="kpi-title">Avg Acid Content</div><div class="kpi-value">{avg_acid:.3f}</div><div class="kpi-unit">%</div></div>', unsafe_allow_html=True)
        c10.markdown(f'<div class="kpi-card border-chem"><div class="kpi-title">Avg Acidity</div><div class="kpi-value">{avg_acidity:.3f}</div><div class="kpi-unit">mgKOH/g</div></div>', unsafe_allow_html=True)
        
        st.divider()

        # CHARTS
        c_a, c_b = st.columns(2)
        with c_a:
            st.subheader("🥧 Product Composition")
            df_pie = df.groupby('PRODUCT')['BATCH'].sum().reset_index()
            fig_pie = px.pie(df_pie, values='BATCH', names='PRODUCT', hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c_b:
            st.subheader("📈 Moisture Trend (Input vs Finish Product)")
            fig_line = px.line(df, x='DATE', y=['MOIST_IN', 'MOIST_FINISH_PRODUCT'], markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

        st.divider()

        # EFFICIENCY
        st.subheader("🚀 Production Efficiency & Targets")
        ec1, ec2, ec3 = st.columns([1, 1, 2])
        with ec1:
            fig_yield = go.Figure(go.Indicator(mode = "gauge+number", value = yield_prod, title = {'text': "Yield Production (%)"}, gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#2ecc71"}, 'steps': [{'range': [0, 50], 'color': "#ff7675"}, {'range': [50, 80], 'color': "#ffeaa7"}], 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
            fig_yield.update_layout(height=300, margin=dict(t=50, b=10))
            st.plotly_chart(fig_yield, use_container_width=True)
        with ec2:
            fig_loss = go.Figure(go.Indicator(mode = "gauge+number", value = losses, title = {'text': "Losses (%)"}, gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#e74c3c"}, 'steps': [{'range': [0, 10], 'color': "#55efc4"}, {'range': [10, 30], 'color': "#ffeaa7"}], 'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 5}}))
            fig_loss.update_layout(height=300, margin=dict(t=50, b=10))
            st.plotly_chart(fig_loss, use_container_width=True)
        with ec3:
            fig_target = go.Figure()
            fig_target.add_trace(go.Bar(x=[total_prod_ton], y=['Achievement'], orientation='h', name='Actual', marker_color='#005bea', text=[f"{total_prod_ton:,.0f} T"], textposition='auto'))
            fig_target.add_trace(go.Bar(x=[target_monthly], y=['Achievement'], orientation='h', name='Monthly Target', marker_color='#ecf0f1', marker_line_color='#95a5a6', marker_line_width=2, opacity=0.6, text=[f"Target: {target_monthly:,.0f} T"], textposition='outside'))
            fig_target.update_layout(title=f"Target: {target_daily} T/Day × 31 Days = {target_monthly:,.0f} Ton", barmode='overlay', xaxis_title="Tonase", height=300, margin=dict(t=50, b=10))
            st.plotly_chart(fig_target, use_container_width=True)

        # TABLE
        st.divider()
        st.subheader(f"🚥 Detailed Log: {sheet_name}")
        def qc_logic(row):
            styles = [''] * len(row)
            prod = str(row['PRODUCT']).upper()
            m_in, m_fp, ph, dens, ps, acid_c, acidity, sa = row['MOIST_IN'], row['MOIST_FINISH_PRODUCT'], row['PH'], row['DENSITY'], row['PARTICLE_SIZE'], row['ACID_CONTENT'], row['ACIDITY'], row['SURFACE_AREA']
            GREEN, YELLOW, RED = 'background-color: #d4edda; color: #155724; font-weight: bold;', 'background-color: #fff3cd; color: #856404; font-weight: bold;', 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            
            if m_in >= 40.0: styles[2] = RED
            elif 38.0 <= m_in <= 39.9: styles[2] = YELLOW
            elif m_in > 0 and m_in <= 37.9: styles[2] = GREEN
            
            if m_fp >= 15.0: styles[5] = RED
            elif 13.1 <= m_fp <= 14.9: styles[5] = YELLOW
            elif 8.0 <= m_fp <= 13.0: styles[5] = GREEN
            elif m_fp > 0 and m_fp <= 7.9: styles[5] = YELLOW
            
            if prod:
                spek = None
                for k, v in KAMUS_SPEK_PH.items():
                    if k in prod: spek = v; break
                if spek and ph > 0:
                    if spek[0] <= ph <= spek[1]: styles[6] = GREEN
                    else: styles[6] = RED
            
            if dens >= 0.70: styles[7] = RED
            elif 0.621 <= dens <= 0.699: styles[7] = YELLOW
            elif dens > 0 and dens <= 0.620: styles[7] = GREEN
            
            if ps >= 90.0: styles[8] = YELLOW
            elif 80.0 <= ps <= 89.9: styles[8] = GREEN
            elif 75.1 <= ps <= 79.9: styles[8] = YELLOW
            elif ps > 0 and ps <= 75.0: styles[8] = RED
            
            if acid_c > 0:
                if acid_c > 0.5: styles[9] = RED
                else: styles[9] = GREEN
            
            if acidity > 0:
                if "211" in prod:
                    if acidity <= 2.0: styles[10] = GREEN
                    else: styles[10] = RED
                elif "125" in prod:
                    if acidity <= 4.0: styles[10] = GREEN
                    else: styles[10] = RED
            
            if sa > 0:
                if sa >= 275: styles[11] = GREEN
                elif sa <= 26.9: styles[11] = RED
            return styles

        st.dataframe(df.style.apply(qc_logic, axis=1).format({"FLOW": "{:,.0f}", "MOIST_IN": "{:.2f}%", "BATCH": "{:,.0f}", "MOIST_FINISH_PRODUCT": "{:.2f}%", "PH": "{:.2f}", "DENSITY": "{:.4f}", "PARTICLE_SIZE": "{:.2f}%", "ACID_CONTENT": "{:.3f}%", "ACIDITY": "{:.3f}", "SURFACE_AREA": "{:.0f}"}), use_container_width=True)
    
    else:
        # Tampilan Jika Tab Tidak Ditemukan
        st.warning(f"⚠️ Tab Excel bernama **'{sheet_name}'** tidak ditemukan!")
        st.info("Saran: Cek menu samping (Sidebar) > Pilih 'Metode Pilih Tab' > Ganti ke 'Input Nama Manual' jika nama tab di Excel berbeda (misal pakai tahun).")
