# CourtSlot

CourtSlot adalah rancangan platform reservasi fasilitas publik kota. Warga dapat melihat ketersediaan dan mengajukan reservasi; petugas mencatat pemesanan dari kanal lain dalam kalender yang sama; instansi mengatur fasilitas, kebijakan, dan penutupan resmi. Proyek ini dibuat untuk tugas besar II3160 Teknologi Sistem Terintegrasi dan II3140 Pengembangan Aplikasi Web & Mobile oleh Keisha Daffa Aryani dan Yumna Fathonah Kautsar.

> Status: backend Tugas 2 tahap 3 dan paket Docker lokal tersedia. Mobile dikerjakan Yumna; deployment STB dan HTTPS publik belum diuji. Kerja sama pemerintah kota tetap skenario perancangan.

## Menjalankan backend di Windows

Gunakan Python 3.12 atau lebih baru dari direktori root repository:

```powershell
cd D:\CourtSlot-git
py -3.12 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
$env:COURTSLOT_DB_PATH = 'D:\CourtSlot-git\backend\data\courtslot.sqlite3'
$env:COURTSLOT_AERIVA_API_KEY = '<key-uji-aeriva>'
$env:COURTSLOT_LOCALLOOP_API_KEY = '<key-uji-localloop-berbeda>'
$env:COURTSLOT_TOKEN_SECRET = '<nilai-acak-minimal-32-karakter>'
cd D:\CourtSlot-git\backend
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Jalankan tes dari `D:\CourtSlot-git\backend` dengan `.\.venv\Scripts\python.exe -m pytest -q`.

Buka `http://127.0.0.1:8000/api/health` dan `http://127.0.0.1:8000/docs`. Database berada di path `COURTSLOT_DB_PATH`; bila variabel tidak diisi, default `backend/data/courtslot.sqlite3` saat dijalankan dari folder `backend`. Seed aman dijalankan ulang dan tidak menimpa baris yang sudah ada.

Alternatif Docker lokal dari root: `docker compose up --build -d`, lalu `docker compose exec api python -m app.seed`. Compose memasang volume `courtslot_data` pada `/data`. Docker daemon harus berjalan. Konfigurasi STB belum termasuk tahap ini.

Tiga endpoint partner mengikuti [kontrak AERIVA](docs/AERIVA_Rancangan_API_Integrasi_Tugas2.md) serta dua path di [catalog antarkelompok](docs/api_catalog.json). Catatan perbedaan dan keputusan ada di [contract-decisions](docs/contract-decisions.md). Tetapkan `COURTSLOT_AERIVA_API_KEY` dan `COURTSLOT_LOCALLOOP_API_KEY` dengan nilai berbeda melalui environment atau `.env` lokal sebelum memakai endpoint partner. Keduanya wajib dikirim sebagai `X-API-Key`; jangan masukkan key asli ke repo atau aplikasi mobile. Cara partner memperoleh key: hubungi pengelola CourtSlot melalui kanal privat, lalu key dibuat dan disampaikan khusus per mitra.

API internal untuk mobile, contoh request/response, bearer token, error, dan data uji didokumentasikan di [mobile-api-draft.md](docs/mobile-api-draft.md). Backend memakai satu service FastAPI dengan SQLite v2 pada volume Docker; transaksi `BEGIN IMMEDIATE` dan index unik parsial menjaga booking eksklusif. Alur yang bekerja: register → login → katalog/detail → slot → booking → reservasi saya → batal. `CAPACITY_BASED`, kuota, check-in, no-show, reschedule, dan workflow petugas/admin masih rancangan proposal.

Compose lokal membatasi API pada 0,75 CPU dan 256 MB memori, memasang volume persisten, serta mengikat port host loopback yang dapat diubah dengan `COURTSLOT_BIND_PORT`. Persiapan STB dan rollback ada di [deployment-stb.md](docs/deployment-stb.md); bahan PDF pengumpulan yang masih menunggu bukti ada di [README-draft.md](docs/submission/README-draft.md). Port 80, aaPanel, dan tunnel belum disentuh.

Contoh dari PowerShell, setelah key disetel pada environment lokal:

```powershell
$headers = @{ 'X-API-Key' = $env:COURTSLOT_AERIVA_API_KEY }
Invoke-RestMethod -Headers $headers 'http://127.0.0.1:8000/api/public/facilities?city=Bandung&limit=1'
Invoke-RestMethod -Headers $headers 'http://127.0.0.1:8000/api/public/facilities/fac-bandung-lapangan'
Invoke-RestMethod -Headers $headers 'http://127.0.0.1:8000/api/public/facilities/fac-bandung-lapangan/availability?start=2026-12-05T07%3A00%3A00%2B07%3A00&end=2026-12-05T08%3A00%3A00%2B07%3A00'
```

## Tujuan dan batas produk

- **Pengguna:** warga, petugas fasilitas, admin dinas; peran operator mitra dan analis kota disiapkan dalam model, tetapi tidak harus memiliki seluruh tampilan pada demo awal.
- **Nilai inti:** satu sumber ketersediaan fasilitas, tanpa pemesanan ganda atau kapasitas berlebih, dengan kebijakan akses warga yang dapat ditelusuri.
- **Unit pesan:** bagian fasilitas yang dapat dipesan, misalnya satu lapangan atau area kursi baca. Satu fasilitas dapat memiliki beberapa unit.
- **Dua model pemesanan:** `EXCLUSIVE_SLOT` untuk satu pemesan per slot dan `CAPACITY_BASED` untuk beberapa pemesan sampai kapasitas terpenuhi.
- **Batas pilot:** satu kota dengan data uji untuk lapangan, perpustakaan, dan taman. Implementasi penuh dimulai dari slot eksklusif, lalu satu unit berbasis kapasitas (kursi baca).
- **Di luar MVP:** pembayaran/retribusi, persetujuan acara besar, seluruh fasilitas dalam kota, dan integrasi resmi pemerintah.

Dalam skenario bisnis, pemerintah kota adalah pembayar layanan platform dan warga tidak dikenai biaya aplikasi. Tarif fasilitas hanya ditampilkan sesuai kebijakan instansi; pembayaran dilakukan di kanal resmi di luar CourtSlot. Angka biaya dan margin dalam dokumen tugas adalah hipotesis untuk analisis, bukan harga produk yang sudah divalidasi.

## Model domain (DDD)

| Kategori | Subdomain / bounded context | Tanggung jawab |
| --- | --- | --- |
| Core | Reservasi dan Akses | Menghitung ketersediaan, menegakkan kapasitas dan kuota, serta mengubah status reservasi secara atomik. |
| Supporting | Katalog Fasilitas | Memiliki data instansi, fasilitas, unit pesan, jam operasional, kebijakan, dan tarif. |
| Supporting | Pemeliharaan dan Penutupan | Menerbitkan penutupan resmi yang memblokir slot dan memengaruhi reservasi terkait. |
| Supporting | Rencana Kunjungan | Menggabungkan informasi slot, prakiraan cuaca, dan kondisi akses dari mitra untuk membantu keputusan warga; ditempatkan di luar STB. |
| Supporting | Pelaporan | Mengolah riwayat pemanfaatan tanpa mengambil alih keputusan reservasi. |
| Generic | Identitas, notifikasi, audit | Mengelola peran, menyampaikan perubahan status, dan menyimpan jejak perubahan. |

**Batas kewenangan:** hanya konteks Reservasi dan Akses yang boleh memutuskan apakah pemesanan sah. Katalog memiliki definisi unit dan kebijakan; Penutupan mengumumkan keputusan instansi; Rencana Kunjungan hanya membaca dan memberi peringatan. Prakiraan cuaca atau laporan akses tidak membatalkan reservasi otomatis. Bounded context adalah batas model, bukan keharusan membuat satu microservice per konteks: modul-modul internal dapat berada dalam satu Core API di STB.

Istilah utama: `Facility` (lokasi publik), `BookableUnit` (bagian yang dipesan), `TimeSlot` (rentang waktu pada unit), `Reservation` (hak pakai pemesan), `FacilityClosure` (penutupan resmi), dan `BookerStanding` (kuota serta catatan ketidakhadiran).

### Aturan yang harus dijaga

1. Satu slot `EXCLUSIVE_SLOT` tidak boleh mempunyai lebih dari satu reservasi aktif; jumlah peserta aktif pada sesi `CAPACITY_BASED` tidak boleh melampaui kapasitas.
2. Reservasi hanya dibuat dalam jam operasional, jendela pemesanan, dan kuota pengguna yang ditetapkan kebijakan unit. Pesanan yang dicatat petugas tetap memakai pemeriksaan yang sama.
3. Pemindahan jadwal memeriksa slot tujuan dalam transaksi yang sama; jika gagal, reservasi lama tetap berlaku.
4. Penutupan resmi memblokir slot dan membatalkan reservasi terdampak dengan alasan yang tercatat. Peringatan cuaca dan kondisi akses tidak mengubah status reservasi.
5. Perubahan status dan koreksi kehadiran dicatat bersama aktor, waktu, dan alasan. API baca untuk kelompok lain tidak membocorkan identitas pemesan.

Parameter awal rancangan, seperti jendela H-14, kuota dua reservasi per kategori per pekan, dan tenggang check-in 15 menit, adalah *default* yang dapat dikonfigurasi per unit. Jangan mengunci angka tersebut dalam logika aplikasi.

## Arsitektur yang direncanakan

```mermaid
flowchart LR
    Mobile["Aplikasi mobile\nReact Native / Expo"] --> Gateway["HTTPS gateway"]
    Gateway --> Core["CourtSlot Core API\nFastAPI di STB"]
    Core --> DB["SQLite\nvolume persisten"]
    Mobile --> Visit["Rencana Kunjungan\ndi luar STB"]
    Visit --> Core
    Visit --> Partners["AERIVA + mitra kedua\n+ prakiraan publik"]
```

- **Core API:** satu service FastAPI dalam Docker di STB. Modul internal mengikuti bounded context; transaksi database menjaga konflik slot dan kapasitas saat ada permintaan bersamaan.
- **Data:** SQLite dengan volume persisten untuk pilot. Kelayakan image Docker, memori STB, dan ketahanan data setelah kontainer dibuat ulang perlu diuji sebelum memilih konfigurasi final. Jika skala atau pola tulis meningkat, evaluasi PostgreSQL.
- **Akses:** gateway Nginx dan Cloudflare Tunnel adalah usulan untuk HTTPS publik; konfigurasi, domain, dan kontrol akses belum ditetapkan di baseline ini. Jangan menaruh kredensial, token tunnel, atau data warga asli di repo.
- **Mobile:** React Native dan Expo dengan tampilan berdasarkan peran. Aplikasi memanggil Core API untuk katalog dan reservasi.
- **Integrasi:** Rencana Kunjungan berada di luar STB; memakai API baca CourtSlot, kontrak AERIVA, kandidat mitra kedua dari API Registry, dan prakiraan publik. Adapter menerjemahkan data mitra; kegagalan salah satu sumber menampilkan status tidak tersedia dan tidak menghalangi pemesanan.

Untuk Tugas 2, tiga path dan bentuk respons endpoint partner sudah ditetapkan dalam kontrak AERIVA. Endpoint internal untuk aplikasi mobile dirancang terpisah. Pemilik data reservasi tetap CourtSlot.

## Urutan kerja

1. Sepakati skenario demo, data uji, peran yang benar-benar diimplementasikan, serta prioritas aturan domain dari rancangan tugas.
2. Tetapkan kontrak API dan model data untuk fasilitas, unit, slot, reservasi, dan penutupan. Putuskan perilaku ketika dua permintaan masuk bersamaan.
3. Bangun Core API dan uji aturan konflik slot, kapasitas, kuota, pemindahan, serta penutupan. Pastikan data tetap ada sesudah kontainer dibuat ulang.
4. Bangun alur mobile warga dan tampilan petugas/admin yang diperlukan untuk demo.
5. Integrasikan Rencana Kunjungan setelah kontrak AERIVA dan kelompok kedua tersedia; tampilkan kegagalan sumber secara eksplisit.
6. Uji end-to-end melalui HTTPS di STB: warga memesan, permintaan bentrok ditolak, petugas check-in, admin menutup unit, dan reservasi terdampak berubah sesuai aturan.

Desain: [Figma Y2K](https://www.figma.com/design/0BHK9h77LUCvGAzNkvDngJ/Y2K?node-id=0-1). Acuan domain dan model bisnis: *Perancangan Layanan Inti CourtSlot untuk Reservasi Fasilitas Publik Kota Berbasis Domain-Driven Design* (dokumen tugas kelompok). Detail visual Figma perlu dicocokkan kembali sebelum implementasi layar.
