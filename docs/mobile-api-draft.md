# API internal mobile CourtSlot — kontrak Tahap 3

Base URL adalah konfigurasi aplikasi, misalnya `http://10.0.2.2:8000` pada emulator Android yang menjangkau backend lokal. Hostname HTTPS produksi belum aktif. Semua waktu ISO 8601 dengan offset; slot ditampilkan dalam `Asia/Jakarta`. Jangan memasang `X-API-Key` partner pada mobile. Endpoint katalog dan slot dapat dibaca tanpa login; operasi reservasi memakai `Authorization: Bearer <access_token>`.

| Layar/alur | Request | Respons sukses |
| --- | --- | --- |
| Registrasi | `POST /api/v1/auth/register` `{"name":"Warga Demo","email":"warga@example.test","password":"password-demo-123"}` | HTTP 201 `{"id":"usr-<uuid>","name":"Warga Demo","email":"warga@example.test"}` |
| Login | `POST /api/v1/auth/login` `{"email":"warga@example.test","password":"password-demo-123"}` | `{"access_token":"<token>","token_type":"bearer","expires_in":3600}` |
| Daftar fasilitas | `GET /api/v1/facilities` | `{"items":[{"id":"fac-bandung-lapangan","name":"Lapangan Basket Cempaka","type":"sports_field","address":"Jl. Cempaka No. 10, Bandung","location":{"lat":-6.9175,"lon":107.6191},"status":"open","detail_url":null,"updated_at":"<waktu-berzona>"},...]}` |
| Detail fasilitas | `GET /api/v1/facilities/fac-bandung-lapangan` | Objek fasilitas seperti daftar, ditambah `"units":[{"id":"unit-bandung-lapangan-1","name":"Lapangan basket 1","slot_minutes":60}]` |
| Slot unit | `GET /api/v1/units/unit-bandung-lapangan-1/slots?date=2026-12-05` | `{"items":[{"start":"2026-12-05T07:00:00+07:00","end":"2026-12-05T08:00:00+07:00","status":"available"},...]}` |
| Pesan | `POST /api/v1/reservations` `{"unit_id":"unit-bandung-lapangan-1","start":"2026-12-05T07:00:00+07:00"}` | HTTP 201 `{"id":"res-<uuid>","unit_id":"unit-bandung-lapangan-1","start":"2026-12-05T07:00:00+07:00","end":"2026-12-05T08:00:00+07:00","status":"CONFIRMED"}` |
| Reservasi saya | `GET /api/v1/reservations/me` | `{"items":[{"id":"res-<uuid>","unit_id":"unit-bandung-lapangan-1","facility_name":"Lapangan Basket Cempaka","start":"2026-12-05T07:00:00+07:00","end":"2026-12-05T08:00:00+07:00","status":"CONFIRMED"},...]}` |
| Batal | `POST /api/v1/reservations/{reservation_id}/cancel` | `{"id":"res-<uuid>","status":"CANCELLED_BY_USER"}` |

Urutan layar: login/register → daftar fasilitas → detail dan unit → pilih tanggal dan slot → konfirmasi booking → reservasi saya → batalkan bila perlu. Saat booking berhasil, minta ulang slot; respons slot sebelumnya hanya snapshot. Slot berstatus `full` atau `closed` tidak dapat dipesan. Daftar kosong tetap `{"items":[]}`.

Error domain berbentuk `{"error":{"code":"SLOT_UNAVAILABLE","message":"Slot sudah tidak tersedia."}}`. HTTP 400 `INVALID_REQUEST` menandakan waktu/input salah; 401 `INVALID_CREDENTIALS` atau `UNAUTHORIZED` meminta login ulang bila token invalid; 404 `NOT_FOUND` juga dipakai untuk reservasi milik orang lain; 409 `EMAIL_IN_USE`, `SLOT_UNAVAILABLE`, atau `CANNOT_CANCEL` perlu pesan dan refresh; validasi field FastAPI memakai 422 dengan `detail`; 503 `SOURCE_UNAVAILABLE` berarti konfigurasi autentikasi belum siap.

Data demo seed: `fac-bandung-lapangan`/`unit-bandung-lapangan-1` buka 07:00–21:00, `fac-bandung-perpustakaan`/`unit-bandung-ruang-baca-1` buka 08:00–17:00, dan `fac-bandung-taman`/`unit-bandung-pavilion-1` buka 07:00–18:00. Semua slot 60 menit setiap hari; pilih tanggal mendatang. Tidak ada akun/password demo yang di-seed. Buat akun fiktif melalui register.

Perubahan shape/path setelah checkpoint ini harus dicatat di dokumen ini dan dikomunikasikan kepada Yumna sebelum integrasi mobile.
