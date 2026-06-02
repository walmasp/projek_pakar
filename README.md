# DermaScan — Sistem Pakar Efek Samping Kosmetik

## Struktur Folder

```
project/
├── app.py              ← Aplikasi Streamlit utama (FILE INI)
├── pakar.py            ← Logika backward chaining (FILE ANDA, JANGAN DIUBAH)
├── requirements.txt    ← Dependensi Python
└── riwayat_konsultasi.json  ← Dibuat otomatis saat konsultasi pertama
```

## Langkah Instalasi & Menjalankan

1. Pastikan Python 3.9+ terinstal di komputer Anda.

2. Letakkan `app.py`, `pakar.py`, dan `requirements.txt` dalam satu folder yang sama.

3. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```

5. Browser akan terbuka otomatis di `http://localhost:8501`

## Fitur Halaman

| Halaman          | Deskripsi |
|-----------------|-----------|
| 🏠 Beranda      | Informasi sistem, statistik, cara penggunaan |
| 👤 Data Pengguna | Form nama, umur, jenis kelamin — wajib diisi |
| 🩺 Konsultasi   | Sesi tanya-jawab gejala (100% logika dari pakar.py) |
| 📊 Hasil        | Diagnosa dengan visualisasi CF, detail gejala, penjelasan |
| 📚 Info Bahan   | Ensiklopedia 13 bahan berbahaya lengkap |
| 📋 Riwayat      | Riwayat konsultasi dengan fitur download CSV |
| ℹ️ Tentang      | Penjelasan metode, rumus CF, referensi jurnal |

## Catatan Teknis

- **Semua logika inferensi** (backward chaining, CF, early stopping, threshold 80%)
  berasal **100% dari `pakar.py`** tanpa modifikasi apapun.
- `app.py` hanya mengimpor `hipotesis`, `gejala_dict`, `rules`, `cf_user_options`, dan `THRESHOLD`
  dari `pakar.py`.
- Riwayat konsultasi disimpan ke file `riwayat_konsultasi.json` secara lokal.
