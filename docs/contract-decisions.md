# Keputusan kontrak CourtSlot

Dokumen `AERIVA_Rancangan_API_Integrasi_Tugas2.md` versi 1.0.0 menjadi acuan tiga endpoint partner. Tahap 1 belum mengimplementasikan endpoint tersebut.

- Data demo: Bandung, `Asia/Jakarta`, fiktif.
- Unit demo: `EXCLUSIVE_SLOT`, durasi 60 menit, kapasitas satu. Ruang baca perpustakaan pada seed juga eksklusif; `CAPACITY_BASED` belum tersedia.
- ID demo dibuat stabil agar seed dapat diulang dan klien demo dapat mengacu padanya.
- Seed hanya menyisipkan data yang belum ada; tidak mengubah data fasilitas yang sudah disunting setelah seed pertama.
- Skema database versi 1 memakai `PRAGMA user_version`; migrasi untuk versi berikutnya harus eksplisit dan tidak boleh menghapus database persisten.

Keputusan query, cursor, error, dan status untuk endpoint partner dicatat saat tahap 2, sebelum endpoint dibuka.
