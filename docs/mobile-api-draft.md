# Draft API internal mobile — belum diimplementasikan

Base path sementara `/api/v1`. Respons waktu memakai ISO 8601 berzona `Asia/Jakarta`; `start` inklusif, `end` eksklusif. Endpoint ini terpisah dari tiga endpoint partner dalam kontrak AERIVA. Setelah review Yumna, bentuk internal dapat disesuaikan sebelum tahap 3.

| Alur | Request | Contoh respons sukses |
| --- | --- | --- |
| Daftar fasilitas | `GET /api/v1/facilities` | `{"items":[{"id":"fac-bandung-lapangan","name":"Lapangan Basket Cempaka","type":"sports_field","address":"Jl. Cempaka No. 10, Bandung","status":"open"}]}` |
| Detail | `GET /api/v1/facilities/fac-bandung-lapangan` | `{"id":"fac-bandung-lapangan","name":"Lapangan Basket Cempaka","units":[{"id":"unit-bandung-lapangan-1","name":"Lapangan basket 1","slot_minutes":60}]}` |
| Slot | `GET /api/v1/units/unit-bandung-lapangan-1/slots?date=2026-12-05` | `{"items":[{"start":"2026-12-05T07:00:00+07:00","end":"2026-12-05T08:00:00+07:00","status":"available"}]}` |
| Register | `POST /api/v1/auth/register` body `{"name":"Warga Demo","email":"warga@example.test","password":"contoh-rahasia"}` | HTTP 201 `{"id":"usr-demo","name":"Warga Demo","email":"warga@example.test"}` |
| Login | `POST /api/v1/auth/login` body `{"email":"warga@example.test","password":"contoh-rahasia"}` | `{"access_token":"<token>","token_type":"bearer","expires_in":3600}` |
| Buat reservasi | `POST /api/v1/reservations` body `{"unit_id":"unit-bandung-lapangan-1","start":"2026-12-05T07:00:00+07:00"}` | HTTP 201 `{"id":"res-demo","unit_id":"unit-bandung-lapangan-1","start":"2026-12-05T07:00:00+07:00","end":"2026-12-05T08:00:00+07:00","status":"CONFIRMED"}` |
| Reservasi saya | `GET /api/v1/reservations/me` | `{"items":[{"id":"res-demo","facility_name":"Lapangan Basket Cempaka","start":"2026-12-05T07:00:00+07:00","end":"2026-12-05T08:00:00+07:00","status":"CONFIRMED"}]}` |
| Batal | `POST /api/v1/reservations/res-demo/cancel` | `{"id":"res-demo","status":"CANCELLED_BY_USER"}` |

Semua request reservasi dan `reservations/me` menggunakan `Authorization: Bearer <access_token>`. Katalog dapat dibaca tanpa login untuk browsing; keputusan final saat tahap 3. Konflik booking direncanakan HTTP 409 dengan `{"error":{"code":"SLOT_UNAVAILABLE","message":"Slot sudah tidak tersedia."}}`. Key partner tidak pernah dipasang pada mobile. Nilai ID dan token di atas hanya contoh.
