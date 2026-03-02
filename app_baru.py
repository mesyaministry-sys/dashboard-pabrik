import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import urllib.parse 
from PIL import Image 
import datetime
import calendar # <-- TAMBAHAN LIBRARY UNTUK MEMBACA JUMLAH HARI OTOMATIS
from fpdf import FPDF
import base64
import re

# ==========================================
# ⚙️ KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Executive Dashboard - Swasa Edition", layout="wide", page_icon="✨")

# ==========================================
# 🔒 SISTEM KEAMANAN (LOGIN USER & PASS)
# ==========================================
USER_RAHASIA = "mahesya13"
PASS_RAHASIA = "swasa226"

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.markdown("""<style>.login-box {max-width: 400px; margin: 100px auto; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); background-color: white; text-align: center;}</style>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("### 🔒 ACCESS RESTRICTED")
            st.info("Silakan Login untuk mengakses Dashboard Pabrik.")
            user_input = st.text_input("Username:", key="user_input")
            pass_input = st.text_input("Password:", type="password", key="pass_input")
            if st.button("LOGIN", type="primary"):
                if user_input == USER_RAHASIA and pass_input == PASS_RAHASIA:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("❌ Username atau Password Salah!")
        return False
    else:
        return True

if not check_login():
    st.stop()

# ==========================================
# 🚀 MULAI KONTEN DASHBOARD
# ==========================================

st.markdown("""
<style>
    /* --- 🛡️ HIDE STREAMLIT DEFAULT ELEMENTS (GITHUB ICON, MENU, FOOTER) --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    
    /* HEADER STYLING */
    .header-container { padding-top: 10px; padding-bottom: 20px; }
    .main-header { font-size: 42px; font-weight: 900; background: linear-gradient(90deg, #005bea 0%, #00c6fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: left; margin-bottom: 5px; line-height: 1.1; filter: drop-shadow(0px 0px 3px rgba(0, 198, 251, 0.3)); }
    .sub-header { font-size: 18px; color: #546e7a; text-align: left; margin-bottom: 15px; font-weight: 500; }
    .dev-credit { font-size: 15px; color: #b0bec5; font-weight: 500; font-style: italic; text-align: left; margin-top: 10px; letter-spacing: 0.5px; }
    
    /* KPI CARD */
    .kpi-card { background: white; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-left: 5px solid #3498db; margin-bottom: 10px; transition: transform 0.3s, box-shadow 0.3s; }
    .kpi-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
    .kpi-title { font-size: 13px; color: #95a5a6; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-size: 26px; font-weight: 800; color: #2c3e50; margin-top: 8px; }
    .kpi-unit { font-size: 12px; color: #bdc3c7; font-weight: 500;}
    
    .border-prod { border-left-color: #005bea !important; }
    .border-qual { border-left-color: #00c6fb !important; }
    .border-chem { border-left-color: #ff9a44 !important; }
    .border-phys { border-left-color: #a18cd1 !important; }
    
    .empty-state { text-align: center; padding: 40px; background-color: #f8f9fa; border: 2px dashed #d1d8e0; border-radius: 15px; color: #7f8c8d; }
    .forecast-box { padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SIDEBAR (MODIFIED FOR MULTI-MONTH ID)
# ==========================================
with st.sidebar:
    st.title("🎛️ Control Panel")
    with st.expander("🖼️ Logo Dashboard"):
        uploaded_file = st.file_uploader("Ganti Logo (PNG/JPG):", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    st.header("📅 Pilih Data Bulan")

    # -------------------------------------------------------------
    # 👇 TEMPAT MASUKKAN ID GOOGLE SHEET PER BULAN DI SINI 👇
    # -------------------------------------------------------------
    DATABASE_ID = {
        "JANUARY": "1yccpRefabM87-Ltzg0lbMHcsR2Qs6ZxPGd5A15jAHZ4", 
        "FEBRUARY": "1MHNmJpBXMHdgHdP85Wogm4olK1dgiIFTySpEzTrqzEg", 
        "MARCH": "1mpZKYjr775vZA3ooI6AY3AwDfxeuBs0X05yoXLfWdhE",    
        "APRIL": "",    
        "MAY": "",
        "JUNE": "",
        "JULY": "",
        "AUGUST": "",
        "SEPTEMBER": "",
        "OCTOBER": "",
        "NOVEMBER": "",
        "DECEMBER": ""
    }
    # -------------------------------------------------------------

    # Mapping nama bulan ke angka (untuk logika forecast)
    bulan_map = { "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4, "MAY": 5, "JUNE": 6, "JULY": 7, "AUGUST": 8, "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12 }
    list_bulan = list(bulan_map.keys())
    
    # 1. Pilih Bulan Dulu
    pilih_bulan = st.selectbox("Pilih Bulan Laporan:", list_bulan, index=0)

    # --- LOGIKA OTOMATIS HITUNG HARI PER BULAN ---
    tahun_sekarang = datetime.datetime.now().year
    bulan_angka = bulan_map[pilih_bulan]
    # calendar.monthrange mengembalikan tuple (hari_pertama, jumlah_hari)
    jumlah_hari_bulan_ini = calendar.monthrange(tahun_sekarang, bulan_angka)[1]
    # ---------------------------------------------

    # 2. Ambil ID berdasarkan bulan yang dipilih
    current_id = DATABASE_ID.get(pilih_bulan, "")
    
    # 3. Tampilkan di Text Input (Bisa diedit manual jika perlu)
    sheet_id = st.text_input("ID Google Sheet:", value=current_id)

    # 4. Setting Nama Tab/Sheet
    mode_input = st.radio("Metode Pilih Tab:", ["Pilih Bulan Otomatis", "Input Nama Manual"])
    target_month_idx = None 

    if mode_input == "Pilih Bulan Otomatis":
        # Otomatis membuat nama tab, misal: "LAPORAN FP BE FEBRUARY"
        sheet_name = f"LAPORAN FP BE {pilih_bulan}"
        target_month_idx = bulan_angka 
    else:
        sheet_name = st.text_input("Ketik Nama Tab Persis:", value=f"LAPORAN FP BE {pilih_bulan}")
        target_month_idx = bulan_angka 

    st.info(f"Target Tab: **{sheet_name}**")

    st.divider()
    st.header("🎯 Target Setting")
    target_daily = st.number_input("Target Harian (Ton/Hari):", value=45.0, step=1.0)
    
    # --- UPDATE: Target bulanan otomatis dikalikan jumlah hari akurat ---
    target_monthly = target_daily * jumlah_hari_bulan_ini
    st.caption(f"Target Bulanan ({jumlah_hari_bulan_ini} Hari): **{target_monthly:,.0f} Ton**")
    
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 REFRESH", type="primary"):
            st.cache_data.clear()
            st.rerun()
    with col_btn2:
        if st.button("🔒 LOGOUT"):
            st.session_state["logged_in"] = False
            st.rerun()

# ==========================================
# 🖼️ HEADER
# ==========================================
st.markdown('<div class="header-container">', unsafe_allow_html=True)
col_logo, col_teks = st.columns([1.2, 5], gap="large")
with col_logo:
    try:
        if uploaded_file: image = Image.open(uploaded_file); st.image(image, use_container_width=True)
        else:
            try: st.image("image_0.png", use_container_width=True)
            except: 
                try: st.image("image_0.jpg", use_container_width=True)
                except: st.info("Logo")
    except: st.error("Error Logo")
    st.markdown("""<style>[data-testid="stImage"] img {border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}</style>""", unsafe_allow_html=True)

with col_teks:
    st.markdown('<div class="main-header">FACTORY OPERATION DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Monitoring Data: <b>{sheet_name}</b> | Production, Quality & Efficiency</div>', unsafe_allow_html=True)
    st.markdown('<div class="dev-credit">✨ Created & Dev : Mahesya</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# ==========================================
# 📘 KAMUS SPEK
# ==========================================
KAMUS_SPEK_PH = { "Z 125": [3.0, 5.0], "Z 211": [3.5, 5.5], "Z 211 SC": [4.0, 7.0], "Z 221 S": [4.0, 7.0], "Z 127": [4.0, 7.0], "Z 301": [4.0, 7.0] }

# ==========================================
# 2. MESIN PEMBACA DATA
# ==========================================
@st.cache_data
def load_data(id, sheet_name_input, expected_month=None):
    if not id: return None # Cegah error jika ID kosong

    if sheet_name_input:
        nama_sheet_aman = urllib.parse.quote(sheet_name_input)
        url = f'https://docs.google.com/spreadsheets/d/{id}/gviz/tq?tqx=out:csv&sheet={nama_sheet_aman}'
    else:
        url = f'https://docs.google.com/spreadsheets/d/{id}/export?format=csv'
        
    try:
        df = pd.read_csv(url, header=None, dtype=str, keep_default_na=False)
        header_row = -1
        for i in range(min(20, len(df))): # Scan 20 baris pertama saja biar cepat
            row_str = " ".join(df.iloc[i].astype(str).tolist()).upper()
            if "DATE" in row_str and "FLOW" in row_str:
                header_row = i
                break
        
        if header_row == -1: return None 
        
        df_clean = df.iloc[header_row + 1:].copy()
        if df_clean.shape[1] < 14: return None # Cek kelengkapan kolom

        df_clean = df_clean.iloc[:, :14] 
        df_clean.columns = ["DATE", "FLOW", "MOIST_IN", "PRODUCT", "BATCH", "MOIST_FINISH_PRODUCT", "PH", "DENSITY", "PARTICLE_SIZE", "ACID_CONTENT", "ACIDITY", "SURFACE_AREA", "BP_2_PERCENT", "STD_BP_2_PERCENT"]
        
        df_clean = df_clean[~df_clean["DATE"].str.contains("Total|Average|Month", case=False, na=False)]
        df_clean = df_clean[df_clean["DATE"] != ""]
        
        if expected_month is not None and not df_clean.empty:
            try:
                sample_date_str = str(df_clean['DATE'].iloc[0])
                dt_sample = None
                try: dt_sample = pd.to_datetime(sample_date_str, format='%d-%b', errors='raise')
                except: dt_sample = pd.to_datetime(sample_date_str, errors='coerce')
                
                if pd.notnull(dt_sample):
                    # Logika check bulan (optional, di-bypass agar fleksibel)
                    pass 
            except: pass

        numeric_cols = ["FLOW", "MOIST_IN", "BATCH", "MOIST_FINISH_PRODUCT", "PH", "DENSITY", "PARTICLE_SIZE", "ACID_CONTENT", "ACIDITY", "SURFACE_AREA"]
        def clean_num(x):
            try: return float(str(x).replace(',', '.').strip())
            except: return 0.0
        for col in numeric_cols:
            df_clean[col] = df_clean[col].apply(clean_num)
        
        df_clean = df_clean[df_clean["BATCH"] > 0]
        return df_clean
    except:
        return None

# ==========================================
# 🧾 FUNGSI PDF GENERATOR
# ==========================================
def create_pdf(sheet_name, total_prod, achievement, messages, forecast_text):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, f'Executive Summary Report: {sheet_name}', 0, 1, 'C')
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, f'Generated by Mahesya System - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
            self.ln(5)

    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, '1. Production Summary', 1, 1, 'L', 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f'Total Production: {total_prod:,.1f} Ton', 0, 1)
    pdf.cell(0, 10, f'Target Achievement: {achievement:.1f} %', 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. Production Forecast (AI Prediction)', 1, 1, 'L', 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 10, forecast_text)
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '3. AI Analyst Findings (Anomalies)', 1, 1, 'L', 1)
    pdf.set_font('Arial', '', 11)
    if messages:
        for msg in messages:
            clean_msg = msg.replace('⚠️', '[WARNING]').replace('📉', '[DOWN]').replace('✅', '[OK]').replace('**', '')
            pdf.multi_cell(0, 10, f"- {clean_msg}")
    else:
        pdf.cell(0, 10, "No critical anomalies detected. Operation is stable.", 0, 1)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. DASHBOARD VISUALIZATION
# ==========================================
if sheet_id:
    df = load_data(sheet_id, sheet_name, target_month_idx)
    
    total_prod_ton = 0; total_flow = 0; yield_prod = 0; losses = 0; achievement = 0
    avg_density = 0; avg_part_size = 0; avg_surface = 0; avg_min = 0; avg_fp = 0
    avg_ph = 0; avg_acid = 0; avg_acidity = 0
    data_tersedia = False

    if df is not None and not df.empty:
        data_tersedia = True
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
    def fmt(val, dec=1): return f"{val:,.{dec}f}" if data_tersedia else "-"
    def fmt_int(val): return f"{val:,.0f}" if data_tersedia else "-"

    c1.markdown(f'<div class="kpi-card border-prod"><div class="kpi-title">Total Production</div><div class="kpi-value">{fmt(total_prod_ton)}</div><div class="kpi-unit">Ton</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card border-prod"><div class="kpi-title">Total Flow</div><div class="kpi-value">{fmt_int(total_flow)}</div><div class="kpi-unit">Kg Input</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card border-phys"><div class="kpi-title">Avg Density</div><div class="kpi-value">{fmt(avg_density, 4)}</div><div class="kpi-unit">g/ml</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card border-phys"><div class="kpi-title">Avg Particle Size</div><div class="kpi-value">{fmt(avg_part_size, 2)}</div><div class="kpi-unit">%</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi-card border-phys"><div class="kpi-title">Avg Surface Area</div><div class="kpi-value">{fmt_int(avg_surface)}</div><div class="kpi-unit">m²/g</div></div>', unsafe_allow_html=True)
    
    st.markdown("##### 🧪 Chemical & Quality Control")
    c6, c7, c8, c9, c10 = st.columns(5)
    c6.markdown(f'<div class="kpi-card border-qual"><div class="kpi-title">Avg Moist Input</div><div class="kpi-value">{fmt(avg_min, 2)}</div><div class="kpi-unit">%</div></div>', unsafe_allow_html=True)
    c7.markdown(f'<div class="kpi-card border-qual"><div class="kpi-title">Avg Moist Finish Product</div><div class="kpi-value">{fmt(avg_fp, 2)}</div><div class="kpi-unit">%</div></div>', unsafe_allow_html=True)
    c8.markdown(f'<div class="kpi-card border-chem"><div class="kpi-title">Avg pH</div><div class="kpi-value">{fmt(avg_ph, 2)}</div><div class="kpi-unit">Scale</div></div>', unsafe_allow_html=True)
    c9.markdown(f'<div class="kpi-card border-chem"><div class="kpi-title">Avg Acid Content</div><div class="kpi-value">{fmt(avg_acid, 3)}</div><div class="kpi-unit">%</div></div>', unsafe_allow_html=True)
    c10.markdown(f'<div class="kpi-card border-chem"><div class="kpi-title">Avg Acidity</div><div class="kpi-value">{fmt(avg_acidity, 3)}</div><div class="kpi-unit">mgKOH/g</div></div>', unsafe_allow_html=True)
    
    st.divider()

    # --- LOGIKA TAMPILAN GRAFIK & TABEL ---
    if data_tersedia:
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
        col_ai, col_forecast = st.columns(2)
        
        ai_messages = []
        df_high_moist = df[df['MOIST_FINISH_PRODUCT'] > 15.0]
        if not df_high_moist.empty:
            for index, row in df_high_moist.iterrows():
                ai_messages.append(f"⚠️ **Moisture Alert:** {row['MOIST_FINISH_PRODUCT']}% pada {row['DATE']}.")
        if yield_prod < 90.0: ai_messages.append(f"📉 **Yield Low:** {yield_prod:.1f}% (Target >90%).")

        with col_ai:
            st.subheader("🤖 AI Analyst")
            if ai_messages:
                st.markdown('<div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #e74c3c;">', unsafe_allow_html=True)
                for msg in ai_messages: st.markdown(f"- {msg}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.success("✅ Operational Status: Stable & Optimal.")

        forecast_msg = ""
        with col_forecast:
            st.subheader("🔮 Production Forecast")
            try:
                days_run = len(df['DATE'].unique())
                avg_daily_prod = total_prod_ton / days_run if days_run > 0 else 0
                
                # --- UPDATE: Ambil jumlah hari bulan dari variabel yang sudah dihitung ---
                total_days_in_month = jumlah_hari_bulan_ini 
                
                remaining_days = total_days_in_month - days_run
                if remaining_days < 0: remaining_days = 0
                
                projected_total = total_prod_ton + (avg_daily_prod * remaining_days)
                gap = projected_total - target_monthly
                
                if gap >= 0:
                    bg_color = "#2ecc71"
                    forecast_msg = f"🚀 **ON TRACK!** Dengan rata-rata **{avg_daily_prod:.1f} Ton/Hari**, estimasi total akhir bulan adalah **{projected_total:,.0f} Ton**.\n\nAnda akan melampaui target sebesar **+{gap:,.0f} Ton**."
                else:
                    bg_color = "#e74c3c"
                    shortfall = abs(gap)
                    req_rate = (target_monthly - total_prod_ton) / remaining_days if remaining_days > 0 else 0
                    forecast_msg = f"⚠️ **RISK OF MISSING TARGET.** Estimasi total hanya **{projected_total:,.0f} Ton** (Kurang {shortfall:,.0f} Ton).\n\nUntuk mengejar target, genjot produksi menjadi **{req_rate:.1f} Ton/Hari** untuk sisa {remaining_days} hari."

                st.markdown(f'<div class="forecast-box" style="background-color: {bg_color};">{forecast_msg}</div>', unsafe_allow_html=True)
            
            except Exception as e:
                st.warning("Data belum cukup untuk forecasting.")
                forecast_msg = "Data insufficient for forecasting."

        with st.sidebar:
            st.divider()
            st.markdown("### 📄 Export Report")
            if st.button("Generate PDF Report"):
                try:
                    pdf_bytes = create_pdf(sheet_name, total_prod_ton, achievement, ai_messages, forecast_msg.replace('**',''))
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Laporan_Pabrik_{sheet_name}.pdf" style="text-decoration:none;"><button style="width:100%; padding:10px; background-color:#e74c3c; color:white; border:none; border-radius:5px; cursor:pointer;">📥 DOWNLOAD PDF SEKARANG</button></a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("PDF Ready! Klik tombol merah di atas.")
                except Exception as e:
                    st.error(f"Gagal membuat PDF. Pastikan library 'fpdf' terinstall. Error: {e}")

        st.divider()
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
            
            # --- UPDATE: Teks pada judul grafik otomatis berubah mengikuti variabel ---
            fig_target.update_layout(title=f"Target: {target_daily} T/Day × {jumlah_hari_bulan_ini} Days = {target_monthly:,.0f} Ton", barmode='overlay', xaxis_title="Tonase", height=300, margin=dict(t=50, b=10))
            st.plotly_chart(fig_target, use_container_width=True)

    else:
        st.markdown(
            f"""
            <div class="empty-state">
                <h3 style="color:#bdc3c7;">Waiting for Data...</h3>
                <p>Grafik dan Analisa akan muncul otomatis setelah data bulan <b>{sheet_name.split(' ')[-1]}</b> tersedia.</p>
            </div>
            """, unsafe_allow_html=True
        )

    st.divider()
    st.subheader(f"🚥 Detailed Quality Control Log: {sheet_name}")
    
    if data_tersedia:
        df_display = df
    else:
        cols = ["DATE", "FLOW", "MOIST_IN", "PRODUCT", "BATCH", "MOIST_FINISH_PRODUCT", "PH", "DENSITY", "PARTICLE_SIZE", "ACID_CONTENT", "ACIDITY", "SURFACE_AREA", "BP_2_PERCENT", "STD_BP_2_PERCENT"]
        df_display = pd.DataFrame(columns=cols)

    def qc_logic(row):
        if not data_tersedia: return [''] * len(row)
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

    if data_tersedia:
        st.dataframe(df_display.style.apply(qc_logic, axis=1).format({"FLOW": "{:,.0f}", "MOIST_IN": "{:.2f}%", "BATCH": "{:,.0f}", "MOIST_FINISH_PRODUCT": "{:.2f}%", "PH": "{:.2f}", "DENSITY": "{:.4f}", "PARTICLE_SIZE": "{:.2f}%", "ACID_CONTENT": "{:.3f}%", "ACIDITY": "{:.3f}", "SURFACE_AREA": "{:.0f}"}), use_container_width=True)
    else:
        st.dataframe(df_display, use_container_width=True)
        st.caption("Data belum tersedia. Tabel di atas adalah template kolom yang akan diisi.")



