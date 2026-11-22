# CourtSlot — Instruksi Implementasi Tugas 2

Dokumen ini adalah brief kerja untuk Codex di VS Code. Kerjakan bertahap di repository CourtSlot, bukan di ZIP AERIVA. Referensi: proposal CourtSlot, `AERIVA_Rancangan_API_Integrasi_Tugas2.md`, dan brief tugas besar. Jika ada perbedaan, pertahankan kontrak publik yang sudah disepakati dan catat konflik sebelum mengubahnya.

## Target selesai

- Core API CourtSlot berjalan dalam Docker di STB, dapat diakses lewat HTTPS publik dan terdaftar di API Registry.
- Tiga endpoint publik CourtSlot sesuai kontrak AERIVA, lengkap dengan data demo yang konsisten dan dokumentasi OpenAPI.
- Alur utama warga: login, melihat fasilitas dan ketersediaan, membuat reservasi, melihat dan membatalkan reservasi. Booking bentrok ditolak secara atomik.
- Kerangka React Native/Expo memiliki navigasi, layar, login, form, loading/error/empty state, dan memanggil API CourtSlot sendiri.
- Repo memuat source code, konfigurasi tanpa rahasia, instruksi menjalankan, dan `README.pdf` untuk pengumpulan.

## Batas kontrak yang harus dijaga

Implementasikan persis `GET /api/public/facilities`, `GET /api/public/facilities/{facility_id}`, dan `GET /api/public/facilities/{facility_id}/availability`. Ikuti query, pagination `items`/`next_cursor`, bentuk `location`, `updated_at`, enum `open|closed` dan `available|full|closed`, serta format error `{"error":{"code":"...","message":"..."}}` pada dokumen AERIVA. `start` inklusif, `end` eksklusif, ISO 8601 dengan zona waktu. Respons publik tidak memuat identitas warga atau rincian reservasi. Jangan mengubah path atau shape demi menyesuaikan contoh `clients.py` AERIVA; file itu belum mencakup detail fasilitas. Tambahan endpoint internal boleh dirancang sendiri.

Catatan keputusan: dokumen AERIVA menuliskan `X-API-Key` untuk panggilan antarkelompok, sedangkan istilah `public` dapat berarti data publik, bukan akses tanpa key. Dokumentasikan dan uji aturan akses endpoint tersebut bersama mitra. Buat key berbeda per mitra, simpan rahasia hanya dalam environment, dan berikan lewat kanal privat.

## Tahapan kerja dan syarat lulus

1. **Audit repo dan kontrak.** Periksa status git, struktur, README, proposal, dan dokumen AERIVA. Buat tabel endpoint/field/query/error sebagai checklist. Jangan menyalin backend AERIVA menjadi backend CourtSlot. Jika repo belum tersambung GitHub, siapkan pekerjaan lokal dulu dan laporkan remote yang diperlukan.
2. **Backend dasar.** FastAPI dengan `/api/health`, `/docs`, konfigurasi environment, SQLite bervolume persisten, migrasi/inisialisasi, dan seed satu kota pilot (lapangan, perpustakaan, taman). Pastikan restart tidak menghapus data.
3. **API mitra.** Buat tiga endpoint kontrak dengan validasi filter, `limit` 1–100, cursor, ID tak ditemukan, rentang waktu, status dan kapasitas berdasarkan data tersimpan. Tambahkan API key per mitra dan rate limit sesuai kontrak (60/menit/key; 429 dan `Retry-After`). Uji respons terhadap contoh dokumen.
4. **Core reservasi.** Buat model Facility, BookableUnit, Reservation, jadwal/penutupan minimal. Implementasikan login/register (password hash dan token), availability, buat, lihat milik sendiri, batal. MVP mulai dengan unit `EXCLUSIVE_SLOT`; jalankan dua booking bersamaan dan pastikan tepat satu berhasil. Jangan mengklaim model `CAPACITY_BASED`, kuota, no-show, reschedule, atau penutupan otomatis selesai bila belum diimplementasikan.
5. **Mobile checkpoint.** Expo dengan navigasi dan layar login, daftar fasilitas, detail+slot, form booking, dan reservasi saya. Hubungkan ke HTTPS/API sendiri; tampilkan loading, error, dan empty state. Simpan API key mitra di server, tidak di aplikasi.
6. **Deployment.** Dockerfile backend dan Compose untuk core, gateway Nginx, tunnel Cloudflare; beri batas `mem_limit`, `cpus`, restart policy, volume data, dan `.env.example`. Uji lokal, lalu di STB. Daftarkan hostname K01 yang benar di Registry; `courtslot.stei.fun` masih target sampai terverifikasi. Uji dari jaringan luar melalui HTTPS, termasuk `/docs` dan endpoint mitra.
7. **Dokumentasi/pengumpulan.** Repo berisi README cara run, arsitektur, endpoint, akses/key, contoh curl tanpa secret, akun demo, dan hasil uji. Siapkan satu PDF (<10 MB) dengan arsitektur, daftar endpoint, cara memperoleh akses, contoh request, screenshot navigasi/layar/login/API sendiri, URL live dan repo. Isi Registry dan tiga kolom form: URL live, repo, PDF.

Integrasi CourtSlot yang *mengonsumsi* AERIVA dan LocalLoop, layanan Rencana Kunjungan, APK final, serta video gabungan adalah tahap berikutnya. Namun API CourtSlot harus siap dipakai kedua mitra pada akhir M14.

## Cara bekerja bersama Codex

Gunakan Codex extension di VS Code pada clone repository yang sama dengan GitHub. Chat ini cocok untuk mengulas kontrak dan keputusan; Codex di VS Code cocok untuk mengedit file, menjalankan tes, dan mencoba Docker di komputer lokal. Satu repo dan satu branch kerja per perubahan; commit setelah setiap tahap lulus, lalu push agar teman bisa review. Jangan jalankan dua agent yang menulis file yang sama bersamaan. Sebelum menerima hasil, baca diff dan jalankan perintah tes yang dilaporkan Codex. Deployment STB dilakukan setelah konfigurasi lokal lolos dan akses STB tersedia.

### Prompt awal untuk Codex di VS Code

> Baca `CourtSlot_Tugas2_Codex_Instructions.md`, proposal CourtSlot, kontrak `AERIVA_Rancangan_API_Integrasi_Tugas2.md`, dan seluruh file repo yang relevan. Mulai dari tahap 1–2 saja. Audit status repo tanpa menimpa perubahan yang ada; lalu implementasikan backend FastAPI dasar, SQLite persisten, seed data demo, `/api/health`, dan dokumentasi cara menjalankan lokal. Jangan mengubah tiga endpoint/shape kontrak AERIVA atau mengerjakan fitur Tugas 3. Jalankan tes yang relevan. Di akhir, laporkan file yang berubah, cara menjalankan, hasil tes, serta keputusan/pertanyaan yang benar-benar menghambat tahap berikutnya.

### Prompt lanjutan setelah tahap 1–2 lulus

> Lanjutkan tahap 3 pada `CourtSlot_Tugas2_Codex_Instructions.md`. Implementasikan tiga endpoint CourtSlot persis sesuai dokumen kontrak AERIVA, termasuk filter, pagination, rentang waktu, bentuk respons/error, API key per mitra, dan rate limit. Tambahkan tes kontrak yang membandingkan contoh request/response dan kasus gagal. Jalankan tes, laporkan hasil dan diff; jangan mengubah kontrak tanpa mengangkat mismatch secara eksplisit.

Setelah itu berikan tahap 4, 5, 6, dan 7 satu per satu dengan format serupa. Minta Codex berhenti pada akhir setiap tahap agar kalian bisa review sebelum melanjutkan.
