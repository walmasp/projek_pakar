Nama Kelompok : Kelompok 6
Anggota :

Cendikia Permata Dewanti (123230011)

Celsi Fransisca Sitompul (123230015)

Alma Wulan Saptaningrum (123230101)

Judul Aplikasi : DermaScan: Sistem Pakar Deteksi Efek Samping Bahan Kosmetik Berbahaya
Menggunakan Metode Backward Chaining dan Certainty Factor
Metode : Backward Chaining dan Certainty Factor
Bahasa Pemrograman : Python
Framework : Streamlit
Database : JSON
Username Login : Alma
Password Login : 123230101
Cara Menjalankan Program :

Pastikan Python sudah terinstall pada komputer atau laptop.

Buka terminal atau command prompt, lalu arahkan ke dalam folder direktori proyek.

Install seluruh library yang dibutuhkan dengan menjalankan perintah pip install -r requirements.txt.

Jalankan aplikasi dengan menggunakan perintah streamlit run app.py.

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
