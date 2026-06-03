import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
# IMPORT BASIS PENGETAHUAN DARI pakar.py
# ══════════════════════════════════════════════════════════════════
from pakar import hipotesis, gejala_dict, rules, cf_user_options, THRESHOLD

# ══════════════════════════════════════════════════════════════════
# KONFIGURASI HALAMAN
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="DermaScan — Deteksi Bahan Kosmetik Berbahaya",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
# DATA EDUKASI BAHAN BERBAHAYA (dari jurnal & knowledge base)
# ══════════════════════════════════════════════════════════════════
info_bahan = {
    "P001": {
        "nama": "Hidroquinone",
        "warna": "#e74c3c",
        "kadar_max": "0,2% – 2%",
        "definisi": "Senyawa kimia yang digunakan sebagai agen pemutih kulit dengan cara menghambat produksi melanin.",
        "dampak": ["Sensasi terbakar pada kulit", "Kulit terasa kering dan kemerahan", "Pada penggunaan jangka panjang dapat menyebabkan Ochronosis (kulit menghitam permanen)", "Berisiko karsinogenik"],
        "pencegahan": "Hindari produk dengan kadar hidroquinone di atas 2%. Gunakan hanya atas rekomendasi dokter dermatologi.",
        "penanganan": "Hentikan pemakaian segera, konsultasikan ke dokter kulit, gunakan pelembap untuk meredakan iritasi.",
    },
    "P002": {
        "nama": "Asam Retinoat",
        "warna": "#e67e22",
        "kadar_max": "< 0,025%",
        "definisi": "Derivat vitamin A yang digunakan untuk perawatan jerawat dan penuaan dini, namun berbahaya jika tidak diawasi medis.",
        "dampak": ["Kulit kering dan bersisik parah", "Sensasi tersengat dan terbakar", "Kulit sangat sensitif terhadap cahaya matahari", "Teratogenik (berbahaya bagi janin)"],
        "pencegahan": "Hanya digunakan atas resep dokter. Wajib menggunakan tabir surya saat beraktivitas di luar.",
        "penanganan": "Kurangi frekuensi pemakaian, gunakan pelembap, hindari paparan sinar matahari langsung.",
    },
    "P003": {
        "nama": "Merkuri (Mercury)",
        "warna": "#8e44ad",
        "kadar_max": "DILARANG (0%)",
        "definisi": "Logam berat yang dilarang keras dalam produk kosmetik karena toksisitas tinggi terhadap sistem saraf dan ginjal.",
        "dampak": ["Bintik hitam muncul di kulit", "Kulit memerah hingga melepuh", "Sesak napas (efek sistemik)", "Kerusakan ginjal dan sistem saraf permanen"],
        "pencegahan": "Periksa label produk. Kosmetik legal TIDAK boleh mengandung merkuri. Pilih produk yang terdaftar BPOM.",
        "penanganan": "SEGERA hentikan pemakaian dan pergi ke IGD rumah sakit. Keracunan merkuri memerlukan penanganan medis darurat.",
    },
    "P004": {
        "nama": "Resorcinol",
        "warna": "#c0392b",
        "kadar_max": "< 1%",
        "definisi": "Senyawa organik yang digunakan sebagai antiseptik dan agen pengelupas kulit, namun berisiko tinggi pada dosis tidak tepat.",
        "dampak": ["Kulit tampak kebiruan/kemerahan", "Ruam dan breakout parah", "Perubahan warna kulit tidak merata", "Potensi toksisitas sistemik"],
        "pencegahan": "Hindari penggunaan mandiri tanpa resep. Kadar aman maksimum sangat rendah.",
        "penanganan": "Hentikan pemakaian, bersihkan area yang terkena dengan air mengalir, konsultasikan ke dokter.",
    },
    "P005": {
        "nama": "Klorin (Chlorine)",
        "warna": "#27ae60",
        "kadar_max": "DILARANG dalam kosmetik",
        "definisi": "Zat kimia oksidator kuat. Keberadaannya dalam kosmetik menunjukkan produk tidak layak konsumsi.",
        "dampak": ["Kulit terasa kering", "Perubahan warna kulit menjadi merah/biru", "Iritasi dan ruam kemerahan", "Kerusakan lapisan pelindung kulit"],
        "pencegahan": "Pastikan kosmetik memiliki sertifikasi BPOM. Jangan gunakan produk tanpa label yang jelas.",
        "penanganan": "Bilas area yang terkena dengan air bersih selama 15 menit, hindari menggosok kulit, segera konsultasikan ke dokter.",
    },
    "P006": {
        "nama": "Arbutin",
        "warna": "#16a085",
        "kadar_max": "0,2% – 2% (alpha arbutin)",
        "definisi": "Senyawa glikosida alami yang dapat menghambat tirosinase. Pada kadar tinggi berpotensi melepas hidroquinone.",
        "dampak": ["Ruam kemerahan", "Breakout mendadak", "Bercak pigmentasi tidak merata", "Reaksi alergi pada kulit sensitif"],
        "pencegahan": "Lakukan patch test sebelum penggunaan. Perhatikan kadar dalam formula produk.",
        "penanganan": "Hentikan jika muncul reaksi, kompres dingin untuk meredakan kemerahan, konsultasi ke dokter kulit.",
    },
    "P007": {
        "nama": "Kojic Acid",
        "warna": "#d35400",
        "kadar_max": "< 1%",
        "definisi": "Asam organik hasil fermentasi jamur yang menghambat produksi melanin. Efektif namun berpotensi iritatif.",
        "dampak": ["Sensasi terbakar", "Ruam merah", "Pembengkakan area pemakaian", "Nyeri pada kulit", "Foto-sensitif"],
        "pencegahan": "Gunakan produk dengan kadar ≤1%. Selalu sertakan tabir surya dalam rutinitas.",
        "penanganan": "Hentikan pemakaian segera saat muncul pembengkakan, minum antihistamin jika diperlukan, kunjungi dokter.",
    },
    "P008": {
        "nama": "Tretinoin",
        "warna": "#2980b9",
        "kadar_max": "Hanya dengan resep dokter",
        "definisi": "Bentuk aktif vitamin A (retinoid) yang digunakan untuk jerawat dan anti-aging. Wajib pengawasan dokter.",
        "dampak": ["Kulit bengkak disertai memar dan kering", "Sensasi menyengat parah", "Memperburuk luka jerawat", "Meninggalkan bekas belang", "Kulit sangat kering dan mengelupas"],
        "pencegahan": "Gunakan hanya berdasarkan resep dokter. Mulai dari dosis rendah dan tingkatkan bertahap.",
        "penanganan": "Kurangi frekuensi pemakaian, gunakan emolien tebal, hindari eksfoliasi tambahan.",
    },
    "P009": {
        "nama": "Benzoyl Peroxide",
        "warna": "#8e44ad",
        "kadar_max": "2,5% – 10%",
        "definisi": "Agen antibakteri untuk jerawat. Sangat efektif namun iritatif pada kulit sensitif atau penggunaan berlebihan.",
        "dampak": ["Sensasi terbakar", "Ruam merah", "Kulit gatal dan bengkak", "Kulit melepuh atau terbakar parah", "Kulit sangat kering hingga mengelupas"],
        "pencegahan": "Mulai dengan konsentrasi 2,5%. Hindari area mata dan bibir. Jangan kombinasikan dengan retinoid tanpa panduan dokter.",
        "penanganan": "Kurangi frekuensi penggunaan, gunakan pelembap barrier repair, kompres dingin untuk pembengkakan.",
    },
    "P010": {
        "nama": "Arsenic (Arsen)",
        "warna": "#7f8c8d",
        "kadar_max": "DILARANG KERAS",
        "definisi": "Metaloid beracun yang DILARANG dalam semua produk kosmetik karena bersifat karsinogenik kuat.",
        "dampak": ["Ruam merah pada kulit", "Tumbuhnya kutil abnormal", "Perubahan pigmentasi", "Lesi kulit", "Peningkatan risiko kanker kulit"],
        "pencegahan": "Beli hanya kosmetik berlabel BPOM resmi. Hindari produk impor ilegal tanpa sertifikasi.",
        "penanganan": "SEGERA ke dokter atau IGD. Keracunan arsen adalah kondisi darurat medis yang serius.",
    },
    "P011": {
        "nama": "AHA (Alpha Hydroxy Acid)",
        "warna": "#f39c12",
        "kadar_max": "≤ 10% (OTC), ≤ 30% (profesional)",
        "definisi": "Asam buah (glikolat, laktat, sitrat) yang berfungsi sebagai eksfolian kimia untuk mencerahkan dan meremajakan kulit.",
        "dampak": ["Kulit sangat sensitif terhadap sinar matahari", "Rasa gatal dan sensasi terbakar", "Kulit mengelupas", "Kulit terasa panas berlebihan"],
        "pencegahan": "Wajib sunscreen SPF 30+ setiap hari. Jangan gunakan saat kulit sedang iritasi atau luka.",
        "penanganan": "Kurangi konsentrasi, tingkatkan pelembap, gunakan sunscreen ekstra, hindari paparan sinar matahari langsung.",
    },
    "P012": {
        "nama": "Sodium Laureth Sulfate (SLS)",
        "warna": "#1abc9c",
        "kadar_max": "Bervariasi, hindari pada kulit sensitif",
        "definisi": "Surfaktan deterjen yang digunakan dalam sabun dan shampoo. Dapat mengganggu barier kulit dan memicu iritasi.",
        "dampak": ["Kulit terasa gatal", "Kulit kering", "Ruam merah", "Kulit mengelupas", "Kulit terasa panas"],
        "pencegahan": "Pilih produk berlabel 'SLS-free' untuk kulit sensitif. Batasi waktu paparan saat mandi.",
        "penanganan": "Ganti produk dengan formula lembut, gunakan pelembap setelah mandi, konsultasi dokter jika iritasi persisten.",
    },
    "P013": {
        "nama": "Steroid (Kortikosteroid)",
        "warna": "#e74c3c",
        "kadar_max": "Hanya dengan resep dokter",
        "definisi": "Hormon sintetis yang digunakan untuk menekan inflamasi. Penyalahgunaan dalam kosmetik menyebabkan steroid skin abuse.",
        "dampak": ["Kulit wajah sangat sensitif", "Muncul beruntusan", "Kulit mudah memar", "Urat/garis pembuluh darah terlihat", "Kulit menipis dan rapuh", "Tumbuh rambut halus tidak wajar di wajah"],
        "pencegahan": "Jangan gunakan krim steroid untuk kecantikan tanpa resep dokter. Waspadai krim yang memberikan hasil 'terlalu cepat'.",
        "penanganan": "Penghentian steroid harus bertahap (tapering) di bawah pengawasan dokter. Jangan hentikan tiba-tiba.",
    },
}

# ══════════════════════════════════════════════════════════════════
# CSS KUSTOM — TEMA MEDIS MODERN
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@700;900&display=swap');

/* Reset & Base */
* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #f0f4f8 0%, #e8f4f8 50%, #f5f0fb 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
}
[data-testid="stSidebar"] * { color: #e0e8ef !important; }
[data-testid="stSidebar"] .stRadio label { color: #c8d8e4 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 { color: #ffffff !important; }

/* Header Banner */
.hero-banner {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    color: white;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(15,32,39,0.3);
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(44,83,100,0.6) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-banner h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    margin: 0 0 0.5rem;
    font-weight: 900;
    letter-spacing: -0.5px;
}
.hero-banner p {
    font-size: 1rem;
    opacity: 0.8;
    margin: 0;
    line-height: 1.6;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 50px;
    padding: 0.3rem 1rem;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* Cards */
.ds-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.ds-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}
.ds-card-accent {
    border-left: 4px solid #2c5364;
}
.ds-card-danger {
    border-left: 4px solid #e74c3c;
    background: linear-gradient(to right, #fff5f5, white);
}
.ds-card-success {
    border-left: 4px solid #27ae60;
    background: linear-gradient(to right, #f0faf5, white);
}
.ds-card-warning {
    border-left: 4px solid #f39c12;
    background: linear-gradient(to right, #fffbf0, white);
}
.ds-card-info {
    border-left: 4px solid #3498db;
    background: linear-gradient(to right, #f0f8ff, white);
}

/* Stat Cards */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: white;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.07);
    text-align: center;
}
.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 900;
    color: #2c5364;
    line-height: 1;
}
.stat-label {
    font-size: 0.78rem;
    color: #7f8c8d;
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Pertanyaan konsultasi */
.question-box {
    background: white;
    border-radius: 20px;
    padding: 2rem 2.5rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.08);
    border: 1px solid rgba(44,83,100,0.1);
    margin-bottom: 1.5rem;
}
.question-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #2c5364;
    margin-bottom: 0.8rem;
}
.question-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: #1a2533;
    line-height: 1.5;
    margin-bottom: 0;
}

/* Hipotesis badge */
.hypo-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #eef3f7;
    border: 1px solid #d0dde6;
    border-radius: 50px;
    padding: 0.3rem 0.9rem;
    font-size: 0.82rem;
    color: #2c5364;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Hasil diagnosa */
.result-main {
    background: linear-gradient(135deg, #0f2027 0%, #2c5364 100%);
    border-radius: 20px;
    padding: 2.5rem;
    color: white;
    margin-bottom: 1.5rem;
    text-align: center;
}
.result-bahan {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 900;
    margin: 0.5rem 0;
}
.result-cf {
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1;
    color: #64d8cb;
}
.result-label {
    font-size: 0.8rem;
    opacity: 0.7;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Rank items */
.rank-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: white;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 0.7rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid #eee;
}
.rank-medal { font-size: 1.4rem; }
.rank-name { font-weight: 600; color: #1a2533; flex: 1; }
.rank-cf { font-weight: 800; font-size: 1.1rem; color: #2c5364; }

/* Tag gejala */
.symptom-tag {
    display: inline-block;
    background: #eef3f7;
    border: 1px solid #c8d8e4;
    border-radius: 50px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    color: #2c5364;
    margin: 0.2rem;
    font-weight: 500;
}
.symptom-tag-active {
    background: #2c5364;
    border-color: #2c5364;
    color: white;
}

/* Info bahan card */
.bahan-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border-top: 4px solid #2c5364;
    transition: transform 0.2s;
}
.bahan-card:hover { transform: translateY(-3px); }

/* Timeline */
.timeline-item {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    align-items: flex-start;
}
.timeline-dot {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #2c5364;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.timeline-content {
    background: white;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    flex: 1;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    font-size: 0.9rem;
    color: #1a2533;
}

/* Footer */
.ds-footer {
    text-align: center;
    color: #95a5a6;
    font-size: 0.78rem;
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 1px solid #e8edf2;
}

/* Warning box */
.warn-box {
    background: #fff8e1;
    border: 1px solid #ffd54f;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: #5d4037;
    margin: 1rem 0;
}

/* Info box */
.info-box {
    background: #e3f2fd;
    border: 1px solid #90caf9;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: #1565c0;
    margin: 1rem 0;
}

/* Override Streamlit button */
.stButton > button {
    background: linear-gradient(135deg, #203a43, #2c5364) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(44,83,100,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(44,83,100,0.4) !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #2c5364, #64d8cb) !important;
    border-radius: 10px;
}

/* Sidebar nav */
.nav-item {
    padding: 0.6rem 1rem;
    border-radius: 10px;
    margin-bottom: 0.3rem;
    cursor: pointer;
    transition: background 0.2s;
    color: #c8d8e4;
    font-size: 0.92rem;
}
.nav-item:hover { background: rgba(255,255,255,0.1); }
.nav-item-active {
    background: rgba(255,255,255,0.15) !important;
    border-left: 3px solid #64d8cb;
    color: white !important;
    font-weight: 600;
}

/* Riwayat table */
.riwayat-row {
    background: white;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.5rem;
    display: flex;
    gap: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    font-size: 0.88rem;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGASI
# ══════════════════════════════════════════════════════════════════
RIWAYAT_FILE = "riwayat_konsultasi.json"

def load_riwayat():
    if os.path.exists(RIWAYAT_FILE):
        with open(RIWAYAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_riwayat(data):
    riwayat = load_riwayat()
    riwayat.append(data)
    with open(RIWAYAT_FILE, "w", encoding="utf-8") as f:
        json.dump(riwayat, f, ensure_ascii=False, indent=2)

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.2rem 0 0.5rem;">
        <div style="font-size:2.5rem; margin-bottom:0.3rem;">🔬</div>
        <div style="font-family:'Playfair Display',serif; font-size:1.3rem; font-weight:900; color:white;">DermaScan</div>
        <div style="font-size:0.72rem; color:#8fb8c8; letter-spacing:1.5px; text-transform:uppercase;">Expert System v1.0</div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1); margin: 1rem 0;">
    """, unsafe_allow_html=True)

    menu_options = [
        ("🏠", "Beranda"),
        ("👤", "Data Pengguna"),
        ("🩺", "Konsultasi"),
        ("📊", "Hasil Diagnosa"),
        ("📚", "Info Bahan"),
        ("📋", "Riwayat"),
        ("ℹ️", "Tentang Sistem"),
    ]

    if "halaman" not in st.session_state:
        st.session_state.halaman = "Beranda"

    for icon, label in menu_options:
        is_active = st.session_state.halaman == label
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.halaman = label
            st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin:1rem 0;'>", unsafe_allow_html=True)

    # Info pengguna di sidebar
    if st.session_state.get("user_nama"):
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1); border-radius:10px; padding:0.8rem; font-size:0.85rem;">
            <div style="color:#8fb8c8; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">Pengguna Aktif</div>
            <div style="color:white; font-weight:600;">👤 {st.session_state.user_nama}</div>
            <div style="color:#8fb8c8; font-size:0.78rem;">{st.session_state.get('user_jk','')}, {st.session_state.get('user_umur','')} tahun</div>
        </div>
        """, unsafe_allow_html=True)

    # Status konsultasi
    if st.session_state.get("is_done"):
        st.markdown("""
        <div style="background:rgba(100,216,203,0.15); border:1px solid rgba(100,216,203,0.3); border-radius:10px; padding:0.7rem; margin-top:0.8rem; font-size:0.82rem; color:#64d8cb; text-align:center;">
            ✅ Diagnosa Selesai
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="color:#4a6878; font-size:0.72rem; text-align:center; margin-top:2rem; line-height:1.6;">
        Backward Chaining + Certainty Factor<br>
        Berdasarkan Jurnal FORISTEK Vol.13 No.1
    </div>
    """, unsafe_allow_html=True)

halaman = st.session_state.halaman

# ══════════════════════════════════════════════════════════════════
# HALAMAN 1: BERANDA
# ══════════════════════════════════════════════════════════════════
if halaman == "Beranda":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">🔬 Sistem Pakar Kosmetik</div>
        <h1>DermaScan</h1>
        <p>Platform diagnosa mandiri efek samping bahan berbahaya dalam kosmetik berbasis kecerdasan buatan.<br>
        Didukung metode Backward Chaining & Certainty Factor.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">13</div>
            <div class="stat-label">Bahan Berbahaya Terdeteksi</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">37</div>
            <div class="stat-label">Gejala dalam Basis Data</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">90%</div>
            <div class="stat-label">Akurasi Sistem (20 sampel)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("""
        <div class="ds-card ds-card-accent">
            <h3 style="color:#1a2533; margin-top:0;">🎯 Tujuan Sistem</h3>
            <p style="color:#555; line-height:1.7;">
            DermaScan dirancang untuk membantu masyarakat, khususnya wanita, dalam melakukan 
            <strong>self-assessment</strong> mandiri terhadap kemungkinan efek samping bahan berbahaya 
            pada kosmetik yang mereka gunakan.<br><br>
            Sistem ini menggunakan metode <strong>Backward Chaining</strong> untuk menelusuri hipotesis 
            dari bahan berbahaya ke gejala yang dirasakan, dikombinasikan dengan <strong>Certainty Factor (CF)</strong> 
            untuk mengukur tingkat keyakinan diagnosis.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ds-card">
            <h3 style="color:#1a2533; margin-top:0;">📋 Cara Penggunaan</h3>
        </div>
        """, unsafe_allow_html=True)

        steps = [
            ("Isi Data Pengguna", "Masukkan nama, umur, dan jenis kelamin Anda di halaman 'Data Pengguna' sebelum memulai konsultasi."),
            ("Mulai Konsultasi", "Jawab setiap pertanyaan gejala dengan tingkat keyakinan Anda. Sistem akan mengevaluasi satu per satu hipotesis bahan berbahaya."),
            ("Lihat Hasil Diagnosa", "Setelah selesai, sistem menampilkan bahan berbahaya yang paling terindikasi beserta persentase keyakinannya."),
            ("Pelajari Informasi Bahan", "Cek halaman 'Info Bahan' untuk informasi lengkap tentang bahaya, pencegahan, dan penanganan setiap bahan."),
        ]
        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot">{i}</div>
                <div class="timeline-content">
                    <strong>{title}</strong><br>
                    <span style="color:#666; font-size:0.85rem;">{desc}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="ds-card" style="background:linear-gradient(135deg,#fff8f0,white);">
            <h3 style="color:#1a2533; margin-top:0;">⚠️ Bahan yang Dideteksi</h3>
        """, unsafe_allow_html=True)
        for kode, nama in hipotesis.items():
            info = info_bahan.get(kode, {})
            emoji = info.get("emoji", "🔸")
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.7rem; padding:0.4rem 0; border-bottom:1px solid #f0f0f0;">
                <span style="font-size:1.1rem;">{emoji}</span>
                <span style="font-size:0.88rem; color:#333; font-weight:500;">{nama}</span>
                <span style="font-size:0.72rem; color:#999; margin-left:auto;">{kode}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="warn-box">
            ⚠️ <strong>Disclaimer:</strong> Hasil dari sistem ini hanya merupakan estimasi awal berdasarkan gejala yang Anda laporkan. 
            Bukan pengganti diagnosis dari dokter spesialis kulit.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Mulai Konsultasi Sekarang", use_container_width=False):
        st.session_state.halaman = "Data Pengguna"
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# HALAMAN 2: DATA PENGGUNA
# ══════════════════════════════════════════════════════════════════
elif halaman == "Data Pengguna":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">👤 Profil Pengguna</div>
        <h1>Data Pengguna</h1>
        <p>Isi informasi berikut sebelum memulai sesi konsultasi.</p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_info = st.columns([2, 1])

    with col_form:
        st.markdown('<div class="ds-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Formulir Pendaftaran")

        nama_input = st.text_input(
            "Nama Lengkap *",
            value=st.session_state.get("user_nama", ""),
            placeholder="Masukkan nama lengkap Anda",
        )
        col1, col2 = st.columns(2)
        with col1:
            umur_input = st.number_input(
                "Umur *",
                min_value=10,
                max_value=100,
                value=st.session_state.get("user_umur", 25),
                step=1,
            )
        with col2:
            jk_input = st.selectbox(
                "Jenis Kelamin *",
                ["Perempuan", "Laki-laki"],
                index=0 if st.session_state.get("user_jk", "Perempuan") == "Perempuan" else 1,
            )

        keluhan = st.text_area(
            "Keluhan Utama (opsional)",
            value=st.session_state.get("user_keluhan", ""),
            placeholder="Deskripsikan keluhan kulit yang Anda rasakan secara singkat...",
            height=100,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✅  Simpan & Lanjut ke Konsultasi", use_container_width=False):
            if not nama_input.strip():
                st.error("❌ Nama tidak boleh kosong!")
            else:
                st.session_state.user_nama = nama_input.strip()
                st.session_state.user_umur = umur_input
                st.session_state.user_jk = jk_input
                st.session_state.user_keluhan = keluhan

                # Reset sesi konsultasi jika ada sesi sebelumnya
                for key in ["targets", "current_target_idx", "current_symptom_idx",
                            "answers", "is_done", "stop_reason"]:
                    if key in st.session_state:
                        del st.session_state[key]

                st.success(f"✅ Data tersimpan! Selamat datang, **{nama_input}**!")
                st.session_state.halaman = "Konsultasi"
                st.rerun()

    with col_info:
        st.markdown("""
        <div class="ds-card ds-card-info">
            <h4 style="color:#1565c0; margin-top:0;">ℹ️ Mengapa Data Ini Diperlukan?</h4>
            <p style="font-size:0.88rem; color:#555; line-height:1.6;">
            Data Anda digunakan untuk:<br><br>
            • Personalisasi laporan hasil diagnosa<br>
            • Penyimpanan riwayat konsultasi<br>
            • Konteks dalam interpretasi gejala<br><br>
            <strong>Privasi terjaga</strong> — data hanya disimpan secara lokal.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("user_nama"):
            st.markdown(f"""
            <div class="ds-card ds-card-success">
                <h4 style="color:#1a6b3c; margin-top:0;">✅ Data Tersimpan</h4>
                <div style="font-size:0.88rem; color:#555;">
                    <b>Nama:</b> {st.session_state.user_nama}<br>
                    <b>Umur:</b> {st.session_state.user_umur} tahun<br>
                    <b>Jenis Kelamin:</b> {st.session_state.user_jk}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HALAMAN 3: KONSULTASI (100% logika dari pakar.py)
# ══════════════════════════════════════════════════════════════════
elif halaman == "Konsultasi":

    # Validasi pengguna
    if not st.session_state.get("user_nama"):
        st.markdown("""
        <div class="ds-card ds-card-warning">
            <h3 style="color:#b7770d; margin-top:0;">⚠️ Data Pengguna Belum Diisi</h3>
            <p>Silakan isi data pengguna terlebih dahulu sebelum memulai konsultasi.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👤  Isi Data Pengguna"):
            st.session_state.halaman = "Data Pengguna"
            st.rerun()
        st.stop()

    # ── INISIALISASI STATE DARI pakar.py ──
    if "is_done" not in st.session_state:
        st.session_state.targets = list(rules.keys())
        st.session_state.current_target_idx = 0
        st.session_state.current_symptom_idx = 0
        st.session_state.answers = {}
        st.session_state.is_done = False
        st.session_state.stop_reason = ""
        st.session_state.terbukti_count = 0 

    st.markdown("""
    <div class="hero-banner" style="padding:1.8rem 2.5rem;">
        <div class="hero-badge">🩺 Sesi Konsultasi</div>
        <h1 style="font-size:1.9rem;">Konsultasi Gejala</h1>
        <p>Jawab setiap pertanyaan sesuai gejala yang Anda rasakan.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── JIKA KONSULTASI SELESAI ──
    if st.session_state.is_done:
        st.markdown("""
        <div class="ds-card ds-card-success" style="text-align:center; padding:2rem;">
            <div style="font-size:3rem; margin-bottom:0.5rem;">🎉</div>
            <h2 style="color:#1a6b3c; margin:0;">Konsultasi Selesai!</h2>
            <p style="color:#555; margin:0.5rem 0 0;">Lihat hasil diagnosa Anda di halaman Hasil Diagnosa.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊  Lihat Hasil Diagnosa", use_container_width=True):
                st.session_state.halaman = "Hasil Diagnosa"
                st.rerun()
        with col2:
            if st.button("🔄  Ulangi Konsultasi", use_container_width=True):
                for key in ["targets", "current_target_idx", "current_symptom_idx",
                            "answers", "is_done", "stop_reason"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        st.stop()

   # ===================================================================
    # LOGIKA BARU: EVALUATE ALL, STOP ASKING (Berjalan di Belakang Layar)
    # ===================================================================
    while not st.session_state.is_done:
        current_target = st.session_state.targets[st.session_state.current_target_idx]
        gejala_target = list(rules[current_target].keys())

        # 1. Jika semua gejala di hipotesis ini sudah selesai dievaluasi
        if st.session_state.current_symptom_idx >= len(gejala_target):
            st.session_state.current_target_idx += 1
            st.session_state.current_symptom_idx = 0

            # 2. Cek apakah SEMUA hipotesis (P001-P013) sudah selesai dievaluasi
            if st.session_state.current_target_idx >= len(st.session_state.targets):
                st.session_state.is_done = True
                st.session_state.stop_reason = "Evaluasi selesai: Seluruh hipotesis telah diperiksa."
                
                # Simpan riwayat karena konsultasi benar-benar sudah mencapai akhir
                _save_data = {
                    "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "nama": st.session_state.get("user_nama", "-"),
                    "umur": st.session_state.get("user_umur", "-"),
                    "jenis_kelamin": st.session_state.get("user_jk", "-"),
                    "stop_reason": st.session_state.stop_reason,
                }
                save_riwayat(_save_data)
                
                st.rerun()
            continue

        current_symptom = gejala_target[st.session_state.current_symptom_idx]

        # 3. Lewati otomatis jika gejala INI sudah pernah dijawab sebelumnya
        if current_symptom in st.session_state.answers:
            st.session_state.current_symptom_idx += 1
        else:
            # Gejala baru ditemukan, hentikan loop untuk menampilkannya di layar
            break

    # Perlindungan agar layar tidak error saat loop baru saja menyelesaikan konsultasi
    if st.session_state.is_done:
        st.stop()

    # ── TAMPILKAN PERTANYAAN KE LAYAR ──
    current_target = st.session_state.targets[st.session_state.current_target_idx]
    gejala_target = list(rules[current_target].keys())
    current_symptom = gejala_target[st.session_state.current_symptom_idx]

    # Progress keseluruhan
    total_questions = sum(len(v) for v in rules.values())
    questions_done = sum(
        len(list(rules[t].keys())) for t in st.session_state.targets[:st.session_state.current_target_idx]
    ) + st.session_state.current_symptom_idx
    progress = questions_done / total_questions if total_questions > 0 else 0

    # Header progress
    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        st.progress(progress)
    with col_p2:
        st.markdown(f"<div style='text-align:right; font-size:0.85rem; color:#666; padding-top:4px;'><b>{int(progress*100)}%</b> selesai</div>", unsafe_allow_html=True)

    # Info hipotesis yang sedang diuji
    info_curr = info_bahan.get(current_target, {})
    st.markdown(f"""
    <div style="display:flex; gap:0.7rem; align-items:center; margin-bottom:1rem; flex-wrap:wrap;">
        <div class="hypo-tag">
            🔎 Menguji: <strong>{hipotesis[current_target]}</strong> ({current_target})
        </div>
        <div class="hypo-tag">
            📍 Hipotesis {st.session_state.current_target_idx + 1} dari {len(st.session_state.targets)}
        </div>
        <div class="hypo-tag">
            ❓ Pertanyaan {st.session_state.current_symptom_idx + 1} dari {len(gejala_target)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Kotak pertanyaan
    pertanyaan_bersih = gejala_dict[current_symptom].replace("Apakah ", "").replace("?", "").strip().capitalize()
    st.markdown(f"""
    <div class="question-box">
        <div class="question-label">🩺 Pertanyaan Gejala #{questions_done + 1}</div>
        <div class="question-text">{gejala_dict[current_symptom]}</div>
    </div>
    """, unsafe_allow_html=True)

    # Form jawaban
    with st.form(key="form_jawaban"):
        pilihan_user = st.radio(
            "Seberapa yakin Anda mengalami hal ini?",
            list(cf_user_options.keys()),
            horizontal=False,
            index=2,
        )

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            submit = st.form_submit_button("✅  Jawab & Lanjut →", use_container_width=True)
        with col_btn2:
            skip = st.form_submit_button("⏭  Lewati", use_container_width=True)

        if submit or skip:
            # 1. Simpan jawaban dari pengguna
            cf_value = cf_user_options[pilihan_user] if submit else 0.0
            st.session_state.answers[current_symptom] = cf_value
            
            # 2. Maju satu indeks
            st.session_state.current_symptom_idx += 1
            
            # (Early stopping dan hitung CF sementara di tombol ini telah DIHAPUS. 
            #  Semuanya diatur otomatis dengan lancar oleh loop while di atas)
            
            st.rerun()

    # Gejala yang sudah dijawab
    answered_ids = [k for k in st.session_state.answers if st.session_state.answers[k] > 0]
    if answered_ids:
        with st.expander(f"📝 Gejala yang sudah dikonfirmasi ({len(answered_ids)} gejala)"):
            tags_html = "".join([
                f'<span class="symptom-tag symptom-tag-active">✓ {gejala_dict[g][:50]}{"..." if len(gejala_dict[g]) > 50 else ""}</span>'
                for g in answered_ids[-8:]
            ])
            st.markdown(f'<div>{tags_html}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HALAMAN 4: HASIL DIAGNOSA
# ══════════════════════════════════════════════════════════════════
elif halaman == "Hasil Diagnosa":

    if not st.session_state.get("is_done"):
        st.markdown("""
        <div class="ds-card ds-card-warning">
            <h3 style="color:#b7770d; margin-top:0;">⏳ Konsultasi Belum Selesai</h3>
            <p>Silakan selesaikan sesi konsultasi terlebih dahulu untuk melihat hasil diagnosa.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🩺  Mulai Konsultasi"):
            st.session_state.halaman = "Konsultasi"
            st.rerun()
        st.stop()

    # ── HITUNG HASIL (LOGIKA DARI pakar.py, TIDAK DIUBAH) ──
    hasil_akhir = {}
    current_target_stop = st.session_state.targets[min(
        st.session_state.current_target_idx,
        len(st.session_state.targets) - 1
    )]

    if st.session_state.stop_reason:
        # Early stopping
        for target in st.session_state.targets:
            cf_combine = 0.0
            for idx, (id_gejala, cf_pakar) in enumerate(rules[target].items()):
                cf_user = st.session_state.answers.get(id_gejala, 0.0)
                cf_gejala = float(cf_pakar) * float(cf_user)
                if idx == 0:
                    cf_combine = cf_gejala
                else:
                    cf_combine = cf_combine + cf_gejala * (1 - cf_combine)
            if cf_combine > 0:
                hasil_akhir[target] = cf_combine * 100
        # Pastikan target yang memicu stop ada di hasil
        if current_target_stop not in hasil_akhir:
            cf_combine = 0.0
            for idx, (id_gejala, cf_pakar) in enumerate(rules[current_target_stop].items()):
                cf_user = st.session_state.answers.get(id_gejala, 0.0)
                cf_gejala = float(cf_pakar) * float(cf_user)
                if idx == 0:
                    cf_combine = cf_gejala
                else:
                    cf_combine = cf_combine + cf_gejala * (1 - cf_combine)
            hasil_akhir[current_target_stop] = cf_combine * 100
    else:
        # Normal
        for target in st.session_state.targets:
            cf_combine = 0.0
            for idx, (id_gejala, cf_pakar) in enumerate(rules[target].items()):
                cf_user = st.session_state.answers.get(id_gejala, 0.0)
                cf_gejala = float(cf_pakar) * float(cf_user)
                if idx == 0:
                    cf_combine = cf_gejala
                else:
                    cf_combine = cf_combine + cf_gejala * (1 - cf_combine)
            hasil_akhir[target] = cf_combine * 100

    hasil_urut = dict(sorted(hasil_akhir.items(), key=lambda x: x[1], reverse=True))
    top_items = [(k, v) for k, v in hasil_urut.items() if v > 0]

    if not top_items:
        st.markdown("""
        <div class="ds-card ds-card-success" style="text-align:center; padding:2.5rem;">
            <div style="font-size:3rem; margin-bottom:0.5rem;">✅</div>
            <h2 style="color:#1a6b3c;">Tidak Terindikasi Bahan Berbahaya</h2>
            <p style="color:#555;">Berdasarkan gejala yang Anda laporkan, sistem tidak menemukan indikasi efek samping bahan berbahaya yang signifikan.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    top_id, top_persen = top_items[0]
    top_info = info_bahan.get(top_id, {})

    # Ringkasan pasien
    st.markdown(f"""
    <div class="ds-card ds-card-info" style="padding:1rem 1.5rem; margin-bottom:1rem;">
        <div style="display:flex; gap:2rem; flex-wrap:wrap; font-size:0.88rem;">
            <div>📅 <b>Tanggal:</b> {datetime.now().strftime("%d %B %Y, %H:%M")}</div>
            <div>👤 <b>Nama:</b> {st.session_state.get('user_nama', '-')}</div>
            <div>🎂 <b>Umur:</b> {st.session_state.get('user_umur', '-')} tahun</div>
            <div>⚧ <b>Jenis Kelamin:</b> {st.session_state.get('user_jk', '-')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Notifikasi early stopping
    if st.session_state.stop_reason:
        st.info(st.session_state.stop_reason)

    # Hasil utama
    col_main, col_gauge = st.columns([3, 2])
    with col_main:
        level_label = (
            "Sangat Tinggi" if top_persen >= 80 else
            "Tinggi" if top_persen >= 60 else
            "Sedang" if top_persen >= 40 else "Rendah"
        )
        level_color = (
            "#e74c3c" if top_persen >= 80 else
            "#f39c12" if top_persen >= 60 else
            "#3498db" if top_persen >= 40 else "#27ae60"
        )
        st.markdown(f"""
        <div class="result-main">
            <div class="result-label">INDIKASI TERKUAT</div>
            <div style="font-size:2.5rem; margin:0.3rem 0;">{top_info.get('emoji','🔬')}</div>
            <div class="result-bahan">{hipotesis[top_id]}</div>
            <div class="result-cf">{top_persen:.1f}%</div>
            <div style="display:inline-block; background:rgba(255,255,255,0.15); border-radius:50px; padding:0.3rem 1rem; margin-top:0.7rem; font-size:0.85rem;">
                Tingkat Keyakinan: <strong>{level_label}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_gauge:
        # Bar chart CF manual dengan HTML
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**📊 Perbandingan Keyakinan Top 5**")
        for i, (kid, kpersen) in enumerate(top_items[:5]):
            kinfo = info_bahan.get(kid, {})
            bar_color = kinfo.get("warna", "#2c5364") if i == 0 else "#8fb8c8"
            bar_width = min(kpersen, 100)
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            st.markdown(f"""
            <div style="margin-bottom:0.8rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:#333; margin-bottom:0.2rem;">
                    <span>{medals[i]} <b>{hipotesis[kid]}</b></span>
                    <span style="font-weight:700; color:{bar_color};">{kpersen:.1f}%</span>
                </div>
                <div style="background:#eee; border-radius:50px; height:8px; overflow:hidden;">
                    <div style="width:{bar_width}%; height:100%; background:{bar_color}; border-radius:50px; transition:width 0.5s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detail penjelasan diagnosis
    tab1, tab2, tab3 = st.tabs(["📖 Penjelasan Diagnosis", "🔍 Gejala Terkonfirmasi", "📐 Detail CF"])

    with tab1:
        col_x, col_y = st.columns([2, 1])
        with col_x:
            st.markdown(f"""
            <div class="ds-card" style="border-top:4px solid {top_info.get('warna','#2c5364')};">
                <h3 style="color:#1a2533; margin-top:0;">{top_info.get('emoji','🔬')} {hipotesis[top_id]}</h3>
                <p style="color:#555; line-height:1.7;">{top_info.get('definisi','')}</p>
                <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-top:0.5rem;">
                    <div style="background:#f0f4f8; border-radius:8px; padding:0.5rem 1rem; font-size:0.82rem;">
                        📏 <b>Kadar Aman:</b> {top_info.get('kadar_max','-')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Dampak
            dampak_list = top_info.get("dampak", [])
            if dampak_list:
                st.markdown('<div class="ds-card ds-card-danger"><h4 style="color:#c0392b;margin-top:0;">⚠️ Dampak yang Dapat Terjadi</h4>', unsafe_allow_html=True)
                for d in dampak_list:
                    st.markdown(f"<div style='padding:0.3rem 0; color:#333; font-size:0.88rem;'>🔹 {d}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with col_y:
            # Penanganan
            penanganan = top_info.get("penanganan", "")
            if penanganan:
                st.markdown(f"""
                <div class="ds-card ds-card-success">
                    <h4 style="color:#1a6b3c; margin-top:0;">💊 Penanganan</h4>
                    <p style="font-size:0.88rem; color:#333; line-height:1.6;">{penanganan}</p>
                </div>
                """, unsafe_allow_html=True)

            pencegahan = top_info.get("pencegahan", "")
            if pencegahan:
                st.markdown(f"""
                <div class="ds-card ds-card-info">
                    <h4 style="color:#1565c0; margin-top:0;">🛡️ Pencegahan</h4>
                    <p style="font-size:0.88rem; color:#333; line-height:1.6;">{pencegahan}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div class="warn-box">
                ⚠️ <b>Penting:</b> Segera konsultasikan dengan dokter spesialis kulit untuk penanganan lebih lanjut.
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        gejala_aktif = [(k, v) for k, v in st.session_state.answers.items() if v > 0]
        if gejala_aktif:
            st.markdown(f"**{len(gejala_aktif)} gejala dikonfirmasi:**")
            col_g1, col_g2 = st.columns(2)
            for i, (g_id, g_cf) in enumerate(gejala_aktif):
                cf_label = next((k for k, v in cf_user_options.items() if v == g_cf), str(g_cf))
                col = col_g1 if i % 2 == 0 else col_g2
                with col:
                    st.markdown(f"""
                    <div style="background:white; border-radius:10px; padding:0.7rem 1rem; margin-bottom:0.5rem;
                                border-left:3px solid #2c5364; box-shadow:0 2px 8px rgba(0,0,0,0.05); font-size:0.85rem;">
                        <div style="color:#1a2533; font-weight:500;">{gejala_dict.get(g_id, g_id)}</div>
                        <div style="color:#7f8c8d; font-size:0.78rem; margin-top:0.2rem;">Keyakinan: <b>{cf_label}</b> ({g_cf*100:.0f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Tidak ada gejala yang dikonfirmasi.")

    with tab3:
        st.markdown("**Detail perhitungan Certainty Factor untuk hipotesis teratas:**")
        for target_id, target_persen in top_items[:3]:
            with st.expander(f"{info_bahan.get(target_id,{}).get('emoji','🔬')} {hipotesis[target_id]} — CF: {target_persen:.2f}%"):
                rows = []
                cf_running = 0.0
                for idx, (g_id, cf_pakar) in enumerate(rules[target_id].items()):
                    cf_u = st.session_state.answers.get(g_id, 0.0)
                    cf_combined = cf_pakar * cf_u
                    if idx == 0:
                        cf_running = cf_combined
                    else:
                        cf_running = cf_running + cf_combined * (1 - cf_running)
                    rows.append({
                        "Gejala": gejala_dict.get(g_id, g_id)[:60],
                        "CF Pakar": f"{cf_pakar:.1f}",
                        "CF User": f"{cf_u:.1f}",
                        "CF(H|E)": f"{cf_combined:.4f}",
                        "CF Kumulatif": f"{cf_running:.4f}",
                    })
                df = pd.DataFrame(rows)
                st.dataframe(df, hide_index=True, use_container_width=True)
                st.markdown(f"**CF Final = {cf_running:.4f} → {cf_running*100:.2f}%**")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄  Mulai Konsultasi Baru"):
        for key in ["targets", "current_target_idx", "current_symptom_idx",
                    "answers", "is_done", "stop_reason"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.halaman = "Konsultasi"
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# HALAMAN 5: INFO BAHAN
# ══════════════════════════════════════════════════════════════════
elif halaman == "Info Bahan":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">📚 Ensiklopedia Kosmetik</div>
        <h1>Informasi Bahan Berbahaya</h1>
        <p>Edukasi lengkap mengenai 13 bahan berbahaya dalam kosmetik, bahaya, dan cara penanganannya.</p>
    </div>
    """, unsafe_allow_html=True)

    # Filter
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search = st.text_input("🔍 Cari bahan...", placeholder="Ketik nama bahan, contoh: merkuri")
    with col_f2:
        filter_bahaya = st.selectbox("Filter", ["Semua", "Dilarang keras", "Hanya resep dokter", "Kadar terbatas"])

    st.markdown("<br>", unsafe_allow_html=True)

    for kode, info in info_bahan.items():
        nama = info["nama"]
        if search and search.lower() not in nama.lower() and search.lower() not in kode.lower():
            continue

        is_dilarang = "DILARANG" in info["kadar_max"].upper()
        is_resep = "RESEP" in info["kadar_max"].upper()
        if filter_bahaya == "Dilarang keras" and not is_dilarang:
            continue
        if filter_bahaya == "Hanya resep dokter" and not is_resep:
            continue
        if filter_bahaya == "Kadar terbatas" and (is_dilarang or is_resep):
            continue

        border_color = info.get("warna", "#2c5364")
        kadar_color = "#e74c3c" if is_dilarang else "#f39c12" if is_resep else "#27ae60"
        kadar_bg = "#fff5f5" if is_dilarang else "#fffbf0" if is_resep else "#f0faf5"

        with st.expander(f"{info['emoji']}  **{nama}** ({kode})  •  {info['kadar_max']}"):
            col_info1, col_info2 = st.columns([3, 2])
            with col_info1:
                st.markdown(f"**Definisi:** {info['definisi']}")
                st.markdown("**⚠️ Dampak:**")
                for d in info["dampak"]:
                    st.markdown(f"- {d}")
                st.markdown(f"**🛡️ Pencegahan:** {info['pencegahan']}")
            with col_info2:
                st.markdown(f"""
                <div style="background:{kadar_bg}; border:1px solid {kadar_color}; border-radius:10px; 
                            padding:0.8rem 1rem; margin-bottom:0.8rem;">
                    <div style="font-size:0.75rem; color:{kadar_color}; font-weight:700; text-transform:uppercase; letter-spacing:1px;">
                        Kadar Maksimum
                    </div>
                    <div style="font-size:1rem; font-weight:700; color:{kadar_color}; margin-top:0.2rem;">
                        {info['kadar_max']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**💊 Penanganan:** {info['penanganan']}")
                
                # Gejala terkait
                gejala_terkait = list(rules.get(kode, {}).keys())
                if gejala_terkait:
                    st.markdown("**Gejala terkait dalam rule:**")
                    tags = "".join([f'<span class="symptom-tag">{gejala_dict.get(g, g)[:35]}</span>' for g in gejala_terkait])
                    st.markdown(f'<div>{tags}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HALAMAN 6: RIWAYAT KONSULTASI
# ══════════════════════════════════════════════════════════════════
elif halaman == "Riwayat":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">📋 Riwayat</div>
        <h1>Riwayat Konsultasi</h1>
        <p>Rekap semua sesi konsultasi yang telah dilakukan.</p>
    </div>
    """, unsafe_allow_html=True)

    riwayat = load_riwayat()

    if not riwayat:
        st.markdown("""
        <div class="ds-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <h3 style="color:#7f8c8d;">Belum Ada Riwayat</h3>
            <p style="color:#aaa;">Riwayat konsultasi akan muncul setelah Anda menyelesaikan sesi konsultasi.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Filter & search
        col_s, col_f = st.columns([3, 1])
        with col_s:
            search_riwayat = st.text_input("🔍 Cari nama...", placeholder="Masukkan nama")
        with col_f:
            st.markdown(f"**Total: {len(riwayat)} sesi**")

        filtered = [r for r in riwayat if search_riwayat.lower() in r.get("nama","").lower()] if search_riwayat else riwayat
        filtered_rev = list(reversed(filtered))

        st.markdown(f"Menampilkan **{len(filtered_rev)}** dari **{len(riwayat)}** sesi", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        for r in filtered_rev:
            nama_r = r.get("nama", "-")
            tanggal_r = r.get("tanggal", "-")
            stop_r = r.get("stop_reason", "Selesai normal")
            umur_r = r.get("umur", "-")
            jk_r = r.get("jenis_kelamin", "-")

            st.markdown(f"""
            <div class="ds-card" style="padding:1rem 1.5rem; border-left:4px solid #2c5364;">
                <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;">
                    <div>
                        <span style="font-weight:700; color:#1a2533;">👤 {nama_r}</span>
                        <span style="color:#7f8c8d; font-size:0.82rem; margin-left:0.7rem;">{umur_r} tahun, {jk_r}</span>
                    </div>
                    <div style="color:#7f8c8d; font-size:0.82rem;">📅 {tanggal_r}</div>
                </div>
                <div style="color:#555; font-size:0.85rem; margin-top:0.5rem;">{stop_r if stop_r else '—'}</div>
            </div>
            """, unsafe_allow_html=True)

        # Download riwayat
        st.markdown("<br>", unsafe_allow_html=True)
        df_riwayat = pd.DataFrame(riwayat)
        csv_data = df_riwayat.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="⬇️  Download Riwayat (CSV)",
            data=csv_data,
            file_name=f"riwayat_konsultasi_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

        if st.button("🗑️  Hapus Semua Riwayat"):
            if os.path.exists(RIWAYAT_FILE):
                os.remove(RIWAYAT_FILE)
            st.success("Riwayat berhasil dihapus.")
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# HALAMAN 7: TENTANG SISTEM
# ══════════════════════════════════════════════════════════════════
elif halaman == "Tentang Sistem":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">ℹ️ Dokumentasi</div>
        <h1>Tentang DermaScan</h1>
        <p>Penjelasan teknis metode, arsitektur sistem, dan referensi jurnal.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_a, tab_b, tab_c = st.tabs(["🔗 Metode Backward Chaining", "🧮 Certainty Factor", "📚 Referensi"])

    with tab_a:
        col_ta, col_tb = st.columns([3, 2])
        with col_ta:
            st.markdown("""
            <div class="ds-card">
                <h3 style="color:#1a2533; margin-top:0;">Backward Chaining (Penalaran Mundur)</h3>
                <p style="color:#555; line-height:1.8;">
                Backward Chaining adalah metode inferensi dalam sistem pakar yang <b>berangkat dari hipotesis (goal)</b> 
                menuju fakta-fakta pendukung. Berbeda dengan Forward Chaining yang dimulai dari fakta, 
                Backward Chaining memulai dari kesimpulan yang ingin dibuktikan.<br><br>
                Dalam DermaScan, sistem mencoba membuktikan satu per satu apakah bahan berbahaya tertentu 
                (hipotesis) cocok dengan gejala yang dilaporkan pengguna. Jika semua gejala dalam sebuah 
                rule dikonfirmasi, hipotesis dinyatakan terbukti.
                </p>
                <div class="info-box">
                    <b>Alur kerja sistem ini:</b><br>
                    1. Sistem mengambil hipotesis pertama (misal: Hidroquinone)<br>
                    2. Sistem menanyakan semua gejala terkait Hidroquinone<br>
                    3. CF dihitung berdasarkan jawaban pengguna<br>
                    4. Jika CF ≥ 80% (threshold), sistem berhenti (early stopping)<br>
                    5. Jika tidak, sistem lanjut ke hipotesis berikutnya
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_tb:
            # Diagram alur sederhana
            st.markdown("""
            <div class="ds-card" style="text-align:center;">
                <h4 style="color:#1a2533; margin-top:0;">Diagram Alur</h4>
            </div>
            """, unsafe_allow_html=True)
            steps_bc = [
                ("🎯", "Tentukan Hipotesis", "Pilih bahan berbahaya yang akan diuji (P001..P013)"),
                ("❓", "Tanya Gejala", "Tanyakan semua gejala yang terkait hipotesis tersebut"),
                ("🧮", "Hitung CF", "Hitung Certainty Factor berdasarkan jawaban user"),
                ("🔀", "Evaluasi", "CF ≥ 80%? → Hentikan (early stop). CF < 80%? → Hipotesis berikutnya"),
                ("📊", "Hasil", "Tampilkan hipotesis dengan CF tertinggi"),
            ]
            for i, (ico, ttl, desc) in enumerate(steps_bc):
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-dot">{ico}</div>
                    <div class="timeline-content">
                        <strong>{ttl}</strong><br>
                        <span style="color:#666; font-size:0.82rem;">{desc}</span>
                    </div>
                </div>
                {"" if i == len(steps_bc)-1 else '<div style="margin-left:15px; border-left:2px dashed #c8d8e4; height:0.8rem;"></div>'}
                """, unsafe_allow_html=True)

    with tab_b:
        st.markdown("""
        <div class="ds-card">
            <h3 style="color:#1a2533; margin-top:0;">Certainty Factor (CF)</h3>
            <p style="color:#555; line-height:1.8;">
            Certainty Factor adalah metode untuk merepresentasikan <b>tingkat kepastian</b> dalam sistem pakar berbasis 
            aturan ketika pengetahuan tidak pasti atau tidak lengkap.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_ca, col_cb = st.columns(2)
        with col_ca:
            st.markdown("""
            <div class="ds-card ds-card-accent">
                <h4 style="color:#1a2533; margin-top:0;">📐 Rumus CF Tunggal</h4>
                <div style="background:#f8f9fa; border-radius:8px; padding:1rem; font-family:monospace; font-size:0.9rem; color:#1a2533;">
                    CF(H|E) = CF_pakar × CF_user
                </div>
                <p style="font-size:0.85rem; color:#555; margin-top:0.8rem;">
                    CF_pakar = keyakinan pakar terhadap gejala<br>
                    CF_user = keyakinan user terhadap gejala yang dialami
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_cb:
            st.markdown("""
            <div class="ds-card ds-card-accent">
                <h4 style="color:#1a2533; margin-top:0;">📐 Rumus CF Kombinasi</h4>
                <div style="background:#f8f9fa; border-radius:8px; padding:1rem; font-family:monospace; font-size:0.9rem; color:#1a2533;">
                    CF_combined = CF_old + CF_new × (1 - CF_old)
                </div>
                <p style="font-size:0.85rem; color:#555; margin-top:0.8rem;">
                    Diterapkan secara iteratif untuk setiap gejala tambahan, menghasilkan nilai CF kumulatif.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ds-card">
            <h4 style="color:#1a2533; margin-top:0;">📊 Skala Keyakinan Pengguna</h4>
        </div>
        """, unsafe_allow_html=True)

        cf_data = [
            ("Sangat Yakin", 1.0, "#e74c3c"),
            ("Yakin", 0.8, "#e67e22"),
            ("Cukup Yakin", 0.6, "#f39c12"),
            ("Kurang Yakin", 0.4, "#3498db"),
            ("Tidak Tahu", 0.2, "#95a5a6"),
            ("Tidak", 0.0, "#bdc3c7"),
        ]
        for label, val, color in cf_data:
            bar_w = int(val * 100)
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.5rem;">
                <div style="width:130px; font-size:0.85rem; font-weight:600; color:#333;">{label}</div>
                <div style="flex:1; background:#eee; border-radius:50px; height:10px; overflow:hidden;">
                    <div style="width:{bar_w}%; height:100%; background:{color}; border-radius:50px;"></div>
                </div>
                <div style="width:50px; text-align:right; font-size:0.85rem; font-weight:700; color:{color};">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_c:
        st.markdown("""
        <div class="ds-card">
            <h3 style="color:#1a2533; margin-top:0;">📚 Referensi Jurnal</h3>
            <div style="background:#f8f9fa; border-radius:10px; padding:1.2rem; border-left:4px solid #2c5364;">
                <b>Jurnal Utama:</b><br>
                Ardiansyah, R., Aristo, M., Yudhaswana J, Y., & Sakti Pratiwi, I. (2023). 
                <em>Implementasi Algoritma Forward Chaining dan Certainty Factor pada Sistem Pakar Diagnosa 
                Efek Samping Bahan Pemutih Kosmetik pada Kulit.</em> 
                Jurnal FORISTEK, Volume 13, No.1, Hal. 60–73. 
                DOI: 10.54757/fs.v14i1.253.
            </div>
            <br>
            <p style="font-size:0.88rem; color:#555; line-height:1.8;">
            Sistem pakar ini dikembangkan berdasarkan penelitian yang melibatkan dokter spesialis kulit 
            (dr. Sari Handayani Pusa). Data primer berupa 37 gejala dan 13 jenis bahan berbahaya diperoleh 
            melalui wawancara langsung dengan pakar. Pengujian akurasi menggunakan 20 sampel data 
            menghasilkan akurasi sebesar <b>90%</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ds-card ds-card-info">
            <h4 style="color:#1565c0; margin-top:0;">🏗️ Arsitektur Sistem</h4>
            <div style="font-size:0.88rem; color:#333; line-height:1.8;">
                <b>Bahasa:</b> Python 3.x<br>
                <b>Framework:</b> Streamlit<br>
                <b>Metode Inferensi:</b> Backward Chaining<br>
                <b>Metode Kepastian:</b> Certainty Factor (CF)<br>
                <b>Basis Pengetahuan:</b> 13 hipotesis, 37 gejala, rule berbasis CF pakar<br>
                <b>Early Stopping:</b> Threshold CF ≥ 80%<br>
                <b>Penyimpanan:</b> JSON lokal (riwayat konsultasi)
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ds-footer">
    🔬 <b>DermaScan</b> — Sistem Pakar Diagnosa Efek Samping Kosmetik &nbsp;|&nbsp;
    Backward Chaining + Certainty Factor &nbsp;|&nbsp;
    Berdasarkan Jurnal FORISTEK Vol.13 No.1, 2023<br>
    ⚕️ <em>Bukan pengganti diagnosis dokter. Selalu konsultasikan ke tenaga medis profesional.</em>
</div>
""", unsafe_allow_html=True)