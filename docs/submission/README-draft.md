# Bahan README.pdf Tugas 2 — DRAFT, bukti belum lengkap

## Arsitektur

Aplikasi mobile Expo (dikerjakan Yumna) → gateway HTTPS yang akan dikonfigurasi asisten → CourtSlot FastAPI di Docker STB → SQLite pada volume persisten. AERIVA dan LocalLoop memanggil tiga API baca CourtSlot dengan key masing-masing. Layanan Rencana Kunjungan di luar STB termasuk pekerjaan berikutnya.

## Endpoint dan akses

Endpoint partner: `GET /api/public/facilities`, `GET /api/public/facilities/{facility_id}`, `GET /api/public/facilities/{facility_id}/availability?start=...&end=...`. Key berbeda diberikan kepada AERIVA dan LocalLoop melalui kanal privat; request memakai `X-API-Key`. Dokumentasi skema lokal tersedia di `/docs` dan `/openapi.json`.

Endpoint pengguna: register/login, katalog, slot, buat reservasi, reservasi saya, batal. Lihat `docs/mobile-api-draft.md`. Login menghasilkan bearer token satu jam. Contoh tanpa secret: `curl -H 'X-API-Key: <KEY_DARI_PENGELOLA>' 'https://<HOSTNAME_TERVERIFIKASI>/api/public/facilities'`.

## Bukti yang perlu diisi sebelum membuat PDF final

- [ ] URL live HTTPS yang sudah diuji dari jaringan luar dan entri API Registry.
- [ ] URL repository final.
- [ ] Screenshot navigasi aplikasi Expo, login, daftar/detail fasilitas, pilih slot, booking, reservasi saya.
- [ ] Screenshot respons API CourtSlot dari hostname live dan contoh error key salah/konflik booking.
- [ ] Arsitektur final port gateway/tunnel STB dan hasil healthcheck/persistence di STB.
- [ ] Akun demo fiktif yang benar-benar dibuat; jangan menaruh password nyata dalam PDF publik.
- [ ] Ekspor ke `README.pdf` kurang dari 10 MB dan periksa tampilannya.

Belum ada APK final, video gabungan, atau bukti deployment publik. Dokumen ini bahan pengumpulan, bukan klaim bahwa komponen tersebut telah selesai.
