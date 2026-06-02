import streamlit as st

# ==========================================
# 1. BASIS PENGETAHUAN (KNOWLEDGE BASE)
# ==========================================

# Tabel Hipotesis
hipotesis = {
    "P001": "Hidroquinone",
    "P002": "Asam retinoat",
    "P003": "Merkury",
    "P004": "Resorcinol",
    "P005": "Klorin",
    "P006": "Arbutin",
    "P007": "Kojic acid",
    "P008": "Tretinoin",
    "P009": "Benzoyl peroxide",
    "P010": "Arsenic",
    "P011": "AHA (alpha hydroxy acid)",
    "P012": "Sodium laureth sulfate",
    "P013": "Steroid"
}

# Tabel Gejala
gejala_dict = {
    "G001": "Apakah kulit Anda terasa gatal?",
    "G002": "Apakah kulit Anda terasa seperti terbakar?",
    "G003": "Apakah kulit Anda terasa kering?",
    "G004": "Apakah kulit Anda terasa seperti tersengat?",
    "G005": "Apakah kulit Anda tampak bersisik?",
    "G006": "Apakah kulit Anda terasa gatal dan mulai terkelupas?",
    "G007": "Apakah muncul bintik-bintik hitam pada kulit?",
    "G008": "Apakah kulit Anda memerah dan sampai melepuh?",
    "G009": "Apakah kulit tampak berubah warna menjadi kebiruan atau kemerahan?",
    "G010": "Apakah Anda mengalami nafas terasa sesak (efek sistemik)?",
    "G011": "Apakah kulit Anda berubah warna menjadi biru (Okronosis parah)?",
    "G012": "Apakah muncul ruam kemerahan pada kulit?",
    "G013": "Apakah Anda mengalami breakout (jerawat parah/mendadak)?",
    "G014": "Apakah muncul bercak-bercak pada kulit?",
    "G015": "Apakah area kulit Anda mengalami pembengkakan?",
    "G016": "Apakah timbul rasa nyeri pada kulit wajah/tubuh?",
    "G017": "Apakah kulit Anda bengkak, disertai memar, dan terasa kering?",
    "G018": "Apakah ada sensasi menyengat di area kulit wajah?",
    "G019": "Apakah luka pada jerawat Anda terasa semakin parah/bertambah?",
    "G020": "Apakah kosmetik meninggalkan bekas belang (terang/gelap) di area pemakaian?",
    "G021": "Apakah kulit terasa gatal sekaligus bengkak?",
    "G022": "Apakah kulit terasa seperti melepuh atau terbakar parah?",
    "G023": "Apakah kulit sangat kering hingga mengelupas?",
    "G024": "Apakah tiba-tiba tumbuh kutil pada area kulit?",
    "G025": "Apakah terjadi perubahan pigmentasi (warna kulit tidak rata)?",
    "G026": "Apakah muncul lesi (luka/jaringan abnormal) pada kulit?",
    "G027": "Apakah kulit Anda menjadi sangat sensitif saat terkena paparan sinar matahari?",
    "G028": "Apakah kulit terasa gatal disertai sensasi panas/terbakar?",
    "G029": "Apakah kulit Anda terkelupas?",
    "G030": "Apakah kulit terasa panas?",
    "G031": "Apakah kulit wajah Anda terasa jauh lebih sensitif dari biasanya?",
    "G032": "Apakah muncul benjolan kecil-kecil berwarna putih atau merah (beruntusan) pada kulit anda ?",
    "G033": "Apakah kulit Anda mudah memar tanpa sebab yang jelas?",
    "G034": "Apakah muncul bercak merah atau urat/garis pembuluh darah di bawah kulit?",
    "G035": "Apakah kulit Anda terasa menipis dan sangat rapuh?",
    "G036": "Apakah kulit Anda justru semakin menggelap (kusam/gosong)?",
    "G037": "Apakah tumbuh rambut/bulu halus yang tidak wajar di wajah Anda?"
}

# Rule Base & Nilai CF Pakar
rules = {
    "P001": {"G002": 0.9, "G003": 0.6, "G004": 0.4, "G012": 0.8},
    "P002": {"G003": 0.6, "G004": 0.4, "G005": 0.8, "G006": 0.6},
    "P003": {"G004": 0.4, "G006": 0.6, "G007": 0.4, "G008": 0.6, "G010": 0.8},
    "P004": {"G009": 0.9, "G011": 0.4, "G012": 0.8, "G013": 0.6},
    "P005": {"G003": 0.6, "G009": 0.9, "G012": 0.8},
    "P006": {"G012": 0.8, "G013": 0.6, "G014": 0.9},
    "P007": {"G002": 0.9, "G012": 0.8, "G015": 0.8, "G016": 0.6},
    "P008": {"G017": 0.9, "G018": 0.4, "G019": 0.5, "G020": 0.6, "G023": 0.6},
    "P009": {"G002": 0.9, "G012": 0.8, "G021": 0.8, "G022": 0.5, "G023": 0.6},
    "P010": {"G012": 0.8, "G024": 0.8, "G025": 0.6, "G026": 0.5, "G027": 0.6, "G028": 0.4, "G036": 0.4},
    "P011": {"G027": 0.6, "G028": 0.4, "G029": 0.9, "G030": 0.6},
    "P012": {"G001": 0.6, "G003": 0.6, "G012": 0.8, "G029": 0.9, "G030": 0.6},
    "P013": {"G031": 0.8, "G032": 0.6, "G033": 0.5, "G034": 0.6, "G035": 0.4, "G037": 0.6}
}

cf_user_options = {
    "Sangat Yakin": 1.0,
    "Yakin": 0.8,
    "Cukup Yakin": 0.6,
    "Kurang Yakin": 0.4,
    "Tidak Tahu": 0.2,
    "Tidak": 0.0
}

# BATAS KEYAKINAN (EARLY STOPPING)
# Jika persentase sudah mencapai batas ini, sistem langsung berhenti bertanya.
THRESHOLD = 0.80 # Artinya 80%

# ==========================================
# 2. INISIALISASI STATE 
# ==========================================

if 'is_done' not in st.session_state:
    st.session_state.targets = list(rules.keys()) 
    st.session_state.current_target_idx = 0
    st.session_state.current_symptom_idx = 0
    st.session_state.answers = {} 
    st.session_state.is_done = False
    st.session_state.stop_reason = "" # Menyimpan alasan kenapa sistem berhenti

# ==========================================
# 3. ANTARMUKA & LOGIKA BACKWARD CHAINING
# ==========================================
st.set_page_config(page_title="Sistem Pakar Efek Kosmetik", page_icon="🧴")
st.title("Sistem Pakar Diagnosa Efek Samping Kosmetik")
st.markdown("Jawab pertanyaan berikut untuk mengetahui bahan kosmetik berbahaya yang merusak kulit Anda.")

# Jika Diagnosa Selesai (Entah karena semua habis, atau karena Early Stopping)
# Jika Diagnosa Selesai 
if st.session_state.is_done:
    st.header("Hasil Diagnosa Akhir")
    
    if st.session_state.stop_reason:
        st.success(st.session_state.stop_reason)
        # JIKA EARLY STOPPING: Hanya tampilkan target yang memicu penghentian
        target_berhenti = st.session_state.targets[st.session_state.current_target_idx]
        
        # Hitung CF akhir khusus untuk target ini saja
        cf_combine = 0.0
        for idx, (id_gejala, cf_pakar) in enumerate(rules[target_berhenti].items()):
            cf_user = st.session_state.answers.get(id_gejala, 0.0)
            cf_gejala = float(cf_pakar) * float(cf_user)
            if idx == 0:
                cf_combine = cf_gejala
            else:
                cf_combine = cf_combine + cf_gejala * (1 - cf_combine)
                
        persentase_akhir = cf_combine * 100
        
        st.error(f"Indikasi terkuat adalah kerusakan kulit akibat bahan **{hipotesis[target_berhenti]}** ({persentase_akhir:.2f}%).")
        st.info("Catatan: Bahan lain tidak dievaluasi karena ambang batas keyakinan (Threshold) sudah terpenuhi pada bahan ini.")

    else:
        # JIKA NORMAL (Semua ditanyakan sampai habis karena tidak ada yg tembus threshold)
        hasil_akhir = {}
        for target in st.session_state.targets:
            cf_combine = 0.0
            gejala_terkait = rules[target]
            
            for idx, (id_gejala, cf_pakar) in enumerate(gejala_terkait.items()):
                cf_user = st.session_state.answers.get(id_gejala, 0.0)
                cf_gejala = float(cf_pakar) * float(cf_user)
                if idx == 0:
                    cf_combine = cf_gejala
                else:
                    cf_combine = cf_combine + cf_gejala * (1 - cf_combine)
                    
            hasil_akhir[target] = cf_combine * 100

        hasil_urut = dict(sorted(hasil_akhir.items(), key=lambda item: item[1], reverse=True))
        
        st.subheader("Berdasarkan Analisa Certainty Factor:")
        top_3 = list(hasil_urut.items())[:3]
        for bahan_id, persentase in top_3:
            if persentase > 0:
                st.write(f"🔹 **{hipotesis[bahan_id]}**: {persentase:.2f}%")
            
        tertinggi_id = list(hasil_urut.keys())[0]
        tertinggi_persen = hasil_urut[tertinggi_id]
        
        if tertinggi_persen > 0:
            st.error(f"Indikasi terkuat adalah kerusakan kulit akibat bahan **{hipotesis[tertinggi_id]}** ({tertinggi_persen:.2f}%).")
        else:
            st.info("Berdasarkan jawaban Anda, tidak terindikasi adanya efek samping dari bahan berbahaya di atas.")
    
    if st.button("Ulangi Diagnosa"):
        st.session_state.clear()
        st.rerun()

# Jika belum selesai, lanjutkan pertanyaan
else:
    current_target = st.session_state.targets[st.session_state.current_target_idx]
    gejala_target = list(rules[current_target].keys())
    current_symptom = gejala_target[st.session_state.current_symptom_idx]
    
    st.progress((st.session_state.current_target_idx) / len(st.session_state.targets))
    st.caption(f"Menguji Hipotesis: {hipotesis[current_target]} ({st.session_state.current_target_idx + 1}/{len(st.session_state.targets)})")
    
    with st.container():
        st.subheader("Pertanyaan:")
        st.info(f"**{gejala_dict[current_symptom]}**")
        
        with st.form(key="form_jawaban"):
            pilihan_user = st.radio("Seberapa yakin Anda mengalami hal ini?", list(cf_user_options.keys()))
            submit_button = st.form_submit_button(label="Jawab & Lanjut")
            
            if submit_button:
                # 1. Simpan jawaban user
                st.session_state.answers[current_symptom] = cf_user_options[pilihan_user]
                
                # 2. Pindah ke gejala selanjutnya
                st.session_state.current_symptom_idx += 1
                
                # 3. Cek apakah gejala untuk target INI sudah habis dijawab semua
                if st.session_state.current_symptom_idx >= len(gejala_target):
                    
                    # LOGIKA BARU: Hitung CF sementaranya di sini
                    cf_combine_sementara = 0.0
                    for idx, (id_gejala, cf_pakar) in enumerate(rules[current_target].items()):
                        cf_u = st.session_state.answers.get(id_gejala, 0.0)
                        cfg = float(cf_pakar) * float(cf_u)
                        if idx == 0:
                            cf_combine_sementara = cfg
                        else:
                            cf_combine_sementara = cf_combine_sementara + cfg * (1 - cf_combine_sementara)
                    
                    # LOGIKA BARU: Cek Early Stopping
                    if cf_combine_sementara >= THRESHOLD:
                        # Jika nilainya >= 80%, hentikan pencarian!
                        st.session_state.is_done = True
                        st.session_state.stop_reason = f"✨ Diagnosa dihentikan lebih awal karena indikasi untuk **{hipotesis[current_target]}** sudah sangat kuat ({cf_combine_sementara*100:.2f}%)."
                    else:
                        # Jika di bawah 80%, ganti Target Hipotesis
                        st.session_state.current_target_idx += 1
                        st.session_state.current_symptom_idx = 0 
                
                # 4. Jika semua hipotesis sudah diuji dan tidak ada yang tembus threshold
                if st.session_state.current_target_idx >= len(st.session_state.targets):
                    st.session_state.is_done = True
                
                st.rerun()