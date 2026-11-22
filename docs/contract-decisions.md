# Keputusan kontrak CourtSlot

Dokumen `AERIVA_Rancangan_API_Integrasi_Tugas2.md` versi 1.0.0 menjadi acuan tiga endpoint partner. Tahap 1 belum mengimplementasikan endpoint tersebut.

- Data demo: Bandung, `Asia/Jakarta`, fiktif.
- Unit demo: `EXCLUSIVE_SLOT`, durasi 60 menit, kapasitas satu. Ruang baca perpustakaan pada seed juga eksklusif; `CAPACITY_BASED` belum tersedia.
- ID demo dibuat stabil agar seed dapat diulang dan klien demo dapat mengacu padanya.
- Seed hanya menyisipkan data yang belum ada; tidak mengubah data fasilitas yang sudah disunting setelah seed pertama.
- Skema database versi 1 memakai `PRAGMA user_version`; migrasi untuk versi berikutnya harus eksplisit dan tidak boleh menghapus database persisten.

## Tahap 2: API partner

- `docs/api_catalog.json` adalah daftar kesepakatan antarkelompok: CourtSlot mencantumkan daftar fasilitas dan availability. Dokumen MD AERIVA v1.0.0 juga meminta detail fasilitas. Detail ditambahkan sebagai endpoint ketiga tanpa mengubah dua path JSON. Nama placeholder `{id}` pada JSON dan `{facility_id}` pada MD merujuk segmen URL yang sama.
- `draft_not_verified` dan `proposed` menyatakan status URL/implementasi, bukan izin mengganti path. `https://courtslot.stei.fun` adalah target operasional dan tidak di-hardcode di backend.
- Semua tiga endpoint mengharuskan `X-API-Key`; dua key berbeda dibaca dari environment. Jika konfigurasi kosong atau sama, API partner mengembalikan 503. Health dan docs tetap terbuka. Rate limit 60 permintaan per menit per key berlaku pada satu proses API; deployment multi-worker memerlukan penyimpan limit bersama.
- Filter `city` dan `type` adalah kecocokan penuh tanpa membedakan kapital. Koordinat harus dikirim berpasangan; `radius_km` positif hanya boleh bersama keduanya. Tanpa radius, koordinat memilih fasilitas yang memiliki lokasi. Jarak radius dihitung dengan Haversine. Hasil diurutkan menurut ID naik.
- Cursor adalah base64url dari ID terakhir pada halaman. Filter sebaiknya dipertahankan konsumen pada halaman berikutnya. Cursor invalid menghasilkan 400. `limit` default 20 dan valid 1–100.
- `detail_url` bernilai null sampai URL aplikasi tersedia. Fasilitas `closed` tetap terlihat pada katalog/detail. `updated_at` berasal dari baris fasilitas yang tersimpan. Availability menggunakan waktu pembaruan fasilitas yang sama; pada tahap 3 perubahan reservasi perlu memperbarui timestamp yang relevan.
- Availability membangkitkan slot penuh 60 menit dari jam operasional unit dalam timezone unit. Hanya slot yang sepenuhnya masuk `[start,end)` dikirim. Rentang maksimum 31 hari untuk membatasi respons. Perbandingan memakai UTC, respons slot memakai offset lokal unit. Tidak ada batas tanggal masa lalu pada API baca.
- Unit eksklusif terbuka menghasilkan `available`/1, slot dengan reservasi aktif menghasilkan `full`/0, fasilitas berstatus `closed` menghasilkan `closed`/0. Bentuk error partner selalu `{"error":{"code":"...","message":"..."}}`; input invalid memakai HTTP 400, termasuk validasi yang biasanya dikembalikan FastAPI sebagai 422.

## Tahap 3: reservasi warga

- Skema SQLite versi 2 menambah `users` dan `reservations` melalui migrasi dari versi 1. Index unik parsial `(unit_id,start_utc)` untuk status `CONFIRMED` menjadi pengaman akhir konflik; `BEGIN IMMEDIATE` membuat pemeriksaan dan insert serial dalam SQLite. Baris fasilitas dan unit yang ada tidak dihapus.
- Password memakai PBKDF2-HMAC-SHA256 dengan salt acak dan 600.000 iterasi. Token bearer bertanda tangan HS256 berlaku satu jam; `COURTSLOT_TOKEN_SECRET` wajib minimal 32 karakter dan hanya di environment. Tidak ada akun demo yang di-seed.
- Booking hanya pada slot 60 menit dari jam buka unit, waktu mulai di masa depan, dengan offset eksplisit. Jam operasional seed berlaku setiap hari; hari libur, jendela H-14, kuota, dan sanksi belum diterapkan. Pembatalan pemilik sebelum mulai membebaskan slot; pembatalan ulang/selepas mulai ditolak.
- API baca partner mempertahankan shape dan path. `updated_at` fasilitas diperbarui setiap booking/pembatalan. Rincian user dan reservasi tidak masuk ke respons partner.
- API internal `/api/v1` dibekukan dalam `docs/mobile-api-draft.md` untuk Yumna. Perubahan kontrak berikutnya harus diberitahukan sebelum mobile diintegrasikan.
