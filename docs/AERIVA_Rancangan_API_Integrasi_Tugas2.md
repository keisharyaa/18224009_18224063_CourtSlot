# AERIVA — Spesifikasi API dan Integrasi

**Versi kontrak:** 1.0.0
**Tanggal:** 22 November 2026
**Pemilik spesifikasi:** Tim AERIVA, kelas K02
**Mitra:** LocalLoop dan CourtSlot, kelas K01

Dokumen ini menetapkan acuan implementasi integrasi ketiga tim. Berdasarkan arahan tim AERIVA, LocalLoop dan CourtSlot akan mengikuti kontrak ini. Status implementasi setiap endpoint tetap perlu dibuktikan melalui pengujian. Nama domain berikut adalah target rancangan yang belum diverifikasi di API Registry. Seluruh JSON dalam dokumen ini adalah contoh fiktif.

## 1. Layanan dan hubungan integrasi

| Layanan | Base URL target | Peran |
|---|---|---|
| AERIVA Core | `https://aeriva.stei.site` | Penilaian kondisi lingkungan dan rekomendasi waktu |
| LocalLoop | `https://localloop.stei.fun` | Katalog kegiatan publik |
| CourtSlot | `https://courtslot.stei.fun` | Katalog dan ketersediaan fasilitas publik |

```text
Aplikasi AERIVA → Integrator AERIVA (di luar STB)
                   ├── AERIVA Core API (STB AERIVA)
                   ├── LocalLoop API (STB LocalLoop)
                   └── CourtSlot API (STB CourtSlot)

Integrator LocalLoop dan CourtSlot → AERIVA Core API
```

API yang dibutuhkan AERIVA dipakai pada fitur aplikasi. Penggunaan API AERIVA oleh mitra juga mendukung peninjauan acara dan kunjungan. Integrator memegang API key dan menerjemahkan respons mitra menjadi bentuk yang digunakan aplikasi. API key tidak disimpan dalam aplikasi mobile.

## 2. Standar bersama

- Protokol HTTPS, respons `application/json; charset=utf-8`.
- Waktu dalam ISO 8601 dengan offset atau UTC `Z`. `start` inklusif dan `end` eksklusif. Perbandingan dilakukan sebagai waktu UTC dan tampilan memakai zona waktu pengguna.
- Koordinat WGS84 menggunakan lintang `lat` −90 sampai 90 dan bujur `lon` −180 sampai 180. Jarak dinyatakan dalam kilometer.
- Request server antarkelompok memakai header `X-API-Key`. Setiap penyedia menerbitkan kunci berbeda untuk setiap kelompok konsumen melalui kanal privat. Akun pengguna AERIVA memakai `Authorization: Bearer <JWT>` pada endpoint pengguna yang memerlukannya.
- Kunci partner disimpan sebagai variabel lingkungan pada integrator atau server. Token, database dan kunci tidak dicantumkan pada GitHub atau contoh request.
- Batas acuan **60 request per menit per API key per layanan**. Respons berlebih memakai HTTP `429` dan header `Retry-After` dalam detik. Ini ketentuan rancangan, belum bukti limit telah diterapkan.
- Timeout integrator **10 detik**, maksimal satu percobaan ulang untuk GET pada error jaringan, 502, 503 atau 504. Untuk 429, patuhi `Retry-After` tanpa menunggu lebih dari anggaran waktu permintaan pengguna. Cache hasil GET paling lama **5 menit**, dibatasi oleh waktu kedaluwarsa data dari penyedia bila lebih singkat. Data lama hanya ditampilkan dengan waktu pembaruan dan penanda data tersimpan.
- Dalam rancangan ini kredensial mitra tidak memiliki tanggal kedaluwarsa tetap. Penyedia dapat mencabut dan menggantinya. Status online, URL registry, penanggung jawab operasional dan akun uji diisi berdasarkan data yang benar-benar tersedia saat registrasi, tanpa mencantumkan rahasia dalam repository.

### 2.1 Format error

AERIVA dan CourtSlot menggunakan bentuk berikut untuk respons error rancangan.

```json
{"error":{"code":"INVALID_REQUEST","message":"Parameter permintaan tidak valid."}}
```

| HTTP | Kode | Arti |
|---|---|---|
| 400 | `INVALID_REQUEST` | Parameter atau rentang waktu tidak valid |
| 401 | `INVALID_API_KEY` | API key tidak ada atau tidak valid |
| 403 | `FORBIDDEN` | Kunci valid tetapi tidak memiliki akses |
| 404 | `NOT_FOUND` | Data yang diminta tidak ditemukan atau tidak tersedia untuk publik |
| 422 | `OUT_OF_FORECAST_RANGE` | Periode yang diminta berada di luar cakupan prakiraan |
| 429 | `RATE_LIMITED` | Batas panggilan terlampaui |
| 503 | `SOURCE_UNAVAILABLE` | Layanan atau sumber data sementara tidak tersedia |

**Kompatibilitas LocalLoop:** panduan partner yang diterima menyatakan error `401`, `404`, dan `503` berbentuk datar `{"code":"...","message":"..."}` dengan kode `INVALID_API_KEY`, `EVENT_NOT_FOUND`, dan `PARTNER_AUTH_UNAVAILABLE`. Error 422 menggunakan format validasi FastAPI. Integrator AERIVA menerjemahkan respons ini ke format internal yang sama tanpa menganggap perubahan pada API LocalLoop sudah diterapkan.

## 3. Daftar endpoint

| Penyedia | Method dan endpoint | Konsumen | Fungsi |
|---|---|---|---|
| AERIVA | `GET /api/v1/health` | Monitoring | Status layanan |
| AERIVA | `GET /api/v1/environment/assessment` | AERIVA, LocalLoop, CourtSlot | Kondisi dan penilaian lingkungan per periode |
| AERIVA | `GET /api/v1/environment/recommendations` | AERIVA, LocalLoop, CourtSlot | Waktu aktivitas relatif lebih mendukung |
| AERIVA | `POST /api/v1/auth/register` | Aplikasi AERIVA | Registrasi pengguna |
| AERIVA | `POST /api/v1/auth/login` | Aplikasi AERIVA | Membuat sesi pengguna |
| LocalLoop | `GET /api/public/events` | AERIVA, CourtSlot | Daftar acara publik |
| LocalLoop | `GET /api/public/events/{event_id}` | AERIVA, CourtSlot | Detail acara publik |
| CourtSlot | `GET /api/public/facilities` | AERIVA, LocalLoop | Daftar fasilitas publik |
| CourtSlot | `GET /api/public/facilities/{facility_id}` | AERIVA, LocalLoop | Detail fasilitas publik |
| CourtSlot | `GET /api/public/facilities/{facility_id}/availability` | AERIVA, LocalLoop | Ketersediaan agregat pada rentang waktu |

Path LocalLoop sesuai `partner-catalog.md` yang diberikan. Path CourtSlot dan tambahan kontrak lainnya didefinisikan dalam rancangan ini. Base URL publik dan API key LocalLoop belum diterbitkan menurut panduan mitra. Nama domain target belum menandakan URL sudah aktif.

## 4. API AERIVA Core

### 4.1 Health

`GET https://aeriva.stei.site/api/v1/health`

```json
{"status":"ok","forecast_provider_configured":true}
```

Health dapat diakses tanpa API key dan tetap dikenai rate limit. Nilai `forecast_provider_configured` menunjukkan konfigurasi sumber, bukan jaminan data semua lokasi tersedia.

### 4.2 Assessment

`GET https://aeriva.stei.site/api/v1/environment/assessment`

| Parameter | Tipe | Ketentuan |
|---|---|---|
| `lat`, `lon` | number | Wajib. Koordinat WGS84 |
| `start`, `end` | datetime | Wajib. Rentang `[start,end)` dalam ISO 8601 berzona |

```http
GET /api/v1/environment/assessment?lat=-6.9175&lon=107.6191&start=2026-12-05T07%3A00%3A00%2B07%3A00&end=2026-12-05T10%3A00%3A00%2B07%3A00
X-API-Key: <API_KEY_AERIVA>
```

```json
{
  "location":{"lat":-6.9175,"lon":107.6191},
  "timezone":"Asia/Jakarta",
  "generated_at":"2026-12-04T18:00:00+07:00",
  "data_status":"partial",
  "periods":[{
    "start":"2026-12-05T07:00:00+07:00",
    "end":"2026-12-05T10:00:00+07:00",
    "assessment_status":"insufficient_data",
    "caution_level":null,
    "indicators":[
      {"type":"temperature","value":24,"unit":"°C","status":"available","source":"contoh","updated_at":"2026-12-04T17:00:00+07:00"},
      {"type":"precipitation_probability","value":40,"unit":"%","status":"available","source":"contoh","updated_at":"2026-12-04T17:00:00+07:00"},
      {"type":"uv_index","value":null,"unit":"index","status":"unavailable","source":null,"updated_at":null}
    ]
  }]
}
```

`data_status` bernilai `available`, `partial`, atau `unavailable`. `assessment_status` bernilai `available` atau `insufficient_data`. `caution_level` dapat berisi `good`, `moderate`, `caution`, atau `high_caution` hanya setelah aturan dan sumber memenuhi syarat validasi. Indikator hilang selalu ditandai `unavailable`, dengan nilai `null`. Hujan dinyatakan dengan `precipitation_probability` dalam persen. Apabila data hanya tersedia sebagai jumlah hujan, gunakan indikator terpisah `precipitation_amount` dengan satuan `mm`, bukan mengganti makna persen.

### 4.3 Recommendations

`GET https://aeriva.stei.site/api/v1/environment/recommendations` menggunakan parameter `lat`, `lon`, `start`, dan `end` dengan aturan yang sama.

```json
{
  "location":{"lat":-6.9175,"lon":107.6191},
  "window":{"start":"2026-12-05T07:00:00+07:00","end":"2026-12-05T10:00:00+07:00"},
  "status":"insufficient_data",
  "recommended_period":null,
  "reasons":[],
  "message":"Data belum cukup untuk menentukan waktu yang disarankan.",
  "generated_at":"2026-12-04T18:00:00+07:00"
}
```

Jika data memadai, `status` menjadi `available`, `recommended_period` berisi `start`, `end`, dan `caution_level`, serta `reasons` berupa daftar alasan teks. Ambang penilaian, syarat minimum data dan aturan tie harus bersumber serta diuji sebelum hasil tersedia. Rekomendasi menunjukkan perbandingan lingkungan dan tidak otomatis mengubah reservasi atau status acara.

### 4.4 Registrasi dan login aplikasi

`POST /api/v1/auth/register` menerima `name`, `email`, dan `password`. Keberhasilan mengembalikan HTTP 201 dengan `id`, `name`, dan `email`. `POST /api/v1/auth/login` menerima `email` dan `password`; keberhasilan mengembalikan `access_token`, `token_type` bernilai `bearer`, dan `expires_in` dalam detik. Password disimpan menggunakan hash yang sesuai. Data contoh dan akun uji dikelola oleh pemilik layanan.

## 5. API LocalLoop

### 5.1 Katalog acara

`GET https://localloop.stei.fun/api/public/events`

| Parameter opsional | Ketentuan |
|---|---|
| `q` | Maks. 100 karakter, pencarian sebagian judul atau deskripsi |
| `category` | Maks. 64 karakter, kecocokan penuh tanpa membedakan kapital |
| `event_format` | `in_person` atau `online` |
| `location` | Maks. 100 karakter, pencarian sebagian lokasi teks |
| `starts_from` | Datetime berzona, waktu mulai acara lebih besar atau sama dengan nilai ini |
| `starts_before` | Datetime berzona, waktu mulai acara lebih kecil dari nilai ini |

Filter digabungkan dengan AND. Daftar diurutkan berdasarkan ID menaik dan versi MVP belum memiliki pagination. `in_person` mencakup acara di dalam atau luar ruangan.

```json
{"items":[{"id":7,"title":"Community Sports Day","capacity":40,"waitlist_enabled":true,"status":"published","category":"Sports","description":"Outdoor activities with local communities","event_format":"in_person","starts_at":"2026-12-05T02:00:00Z","ends_at":"2026-12-05T05:00:00Z","location":"Bandung, West Java","registration_opens_at":"2026-11-25T00:00:00Z","registration_closes_at":"2026-12-04T16:00:00Z"}]}
```

ID, judul, kapasitas total, status waitlist, dan status publikasi selalu ada. Field lainnya opsional dan dapat tidak dikirim. Daftar kosong adalah `{"items":[]}`. `capacity` bukan jumlah kursi tersisa. Katalog tidak memuat identitas peserta, data pendaftaran individual, atau informasi kehadiran.

### 5.2 Detail acara

`GET https://localloop.stei.fun/api/public/events/{event_id}` menerima ID bilangan bulat positif dan mengembalikan satu objek acara dengan field seperti item daftar, tanpa pembungkus `items`. Acara yang tidak ada, masih draft, atau dibatalkan menghasilkan `404 EVENT_NOT_FOUND`.

### 5.3 Lokasi untuk penilaian lingkungan

Katalog LocalLoop saat ini mengirim `location` berupa teks, tanpa koordinat dan tanpa ID fasilitas CourtSlot. Integrator AERIVA akan menerima lokasi teks tersebut dan meminta pengguna memilih lokasi/koordinat yang sesuai sebelum memanggil assessment. Jika lokasi atau waktu yang dibutuhkan tidak tersedia, tampilkan data acara dan status lingkungan belum tersedia. Jangan memperlakukan `in_person` sebagai kepastian acara outdoor. Integrator tidak menebak koordinat.

## 6. API CourtSlot

Endpoint di bagian ini merupakan kontrak target yang didefinisikan oleh AERIVA. Implementasi, URL publik, key dan kesiapan layanan CourtSlot belum diverifikasi.

### 6.1 Daftar fasilitas

`GET https://courtslot.stei.fun/api/public/facilities`

| Parameter opsional | Ketentuan |
|---|---|
| `lat`, `lon` | Keduanya dikirim bersama jika mencari berdasarkan koordinat |
| `radius_km` | Angka positif, digunakan bersama `lat` dan `lon` |
| `city` | Wilayah kota dalam teks |
| `type` | Jenis fasilitas seperti `park`, `sports_field`, atau `library` |
| `limit` | Bilangan bulat 1–100, default 20 |
| `cursor` | Penanda halaman berikutnya dari respons sebelumnya |

```json
{"items":[{"id":"fac-demo-01","name":"Taman contoh","type":"park","address":"Alamat contoh","location":{"lat":-6.9175,"lon":107.6191},"status":"open","detail_url":null,"updated_at":"2026-12-04T18:00:00+07:00"}],"next_cursor":null}
```

`next_cursor: null` menunjukkan tidak ada halaman berikut. Status fasilitas pada kontrak ini adalah `open` atau `closed`. Jika koordinat tidak tersedia, `location` bernilai `null` dan fitur penilaian lingkungan meminta pengguna memilih lokasi.

### 6.2 Detail fasilitas

`GET https://courtslot.stei.fun/api/public/facilities/{facility_id}` mengembalikan satu objek fasilitas dengan struktur yang sama seperti item daftar, tanpa pembungkus `items`.

### 6.3 Ketersediaan agregat

`GET https://courtslot.stei.fun/api/public/facilities/{facility_id}/availability?start=...&end=...`

`start` dan `end` wajib memakai ISO 8601 berzona dan membentuk rentang `[start,end)`.

```json
{"facility_id":"fac-demo-01","slots":[{"unit_id":"unit-demo-01","start":"2026-12-05T07:00:00+07:00","end":"2026-12-05T08:00:00+07:00","status":"available","remaining_capacity":10}],"updated_at":"2026-12-04T18:00:00+07:00"}
```

Status slot adalah `available`, `full`, atau `closed`. `remaining_capacity` berupa bilangan bulat nonnegatif atau `null` jika tidak disediakan. Hasilnya adalah informasi agregat pada waktu pembaruan dan bukan konfirmasi reservasi. API ini tidak mengembalikan identitas warga atau detail reservasi per pengguna. Fasilitas umum CourtSlot tidak otomatis merupakan fasilitas kesehatan.

## 7. Pemakaian pada fitur dan kondisi gagal

1. Pengguna membuka daftar kegiatan dari LocalLoop. Integrator menampilkan acara publik beserta lokasi teks dan jadwal jika tersedia. Pengguna memilih koordinat lokasi yang sesuai dan AERIVA menampilkan assessment untuk periode acara.
2. Pengguna membuka fasilitas dari CourtSlot dan melihat detail serta ketersediaan agregat. AERIVA menampilkan assessment untuk koordinat fasilitas dan slot yang dipilih, selama data memadai.
3. LocalLoop dan CourtSlot memanggil assessment AERIVA untuk lokasi dan waktu masing-masing. Recommendation dapat dipakai untuk menampilkan alternatif waktu, sesuai cakupan prakiraan.
4. Bila satu sumber gagal, fitur dari sumber lain tetap dapat dipakai. Informasi yang gagal diberi status tersedia sebagian atau tidak tersedia. Cache yang ditampilkan diberi waktu pembaruan. Data yang belum ada tidak dianggap baik dan tidak menghasilkan rekomendasi palsu.

## 8. Konfigurasi dan dokumentasi

| Variabel | Nilai target atau fungsi |
|---|---|
| `AERIVA_BASE_URL` | `https://aeriva.stei.site` |
| `LOCALLOOP_BASE_URL` | `https://localloop.stei.fun` |
| `COURTSLOT_BASE_URL` | `https://courtslot.stei.fun` |
| `AERIVA_API_KEY` | Kunci khusus konsumen untuk memanggil AERIVA |
| `LOCALLOOP_API_KEY` | Kunci khusus AERIVA dari LocalLoop |
| `COURTSLOT_API_KEY` | Kunci khusus AERIVA dari CourtSlot |

URL target digunakan dalam rancangan dan harus sesuai nama yang terdaftar pada API Registry. Jika hostname aktual berbeda, ganti variabel konfigurasi di integrator tanpa mengubah format data aplikasi. Dokumentasi runtime direncanakan tersedia melalui `{BASE_URL}/docs` dan OpenAPI melalui `{BASE_URL}/openapi.json` pada masing-masing layanan setelah tersedia. AERIVA menyediakan `README.pdf` berisi arsitektur, endpoint, cara memperoleh akses dan contoh request untuk pengumpulan Tugas 2.

## 9. Status implementasi pada 22 November 2026

- Dokumen ini menetapkan kontrak target. Domain, API key, route mitra yang diusulkan, rate limit, cache, dan fitur integrasi perlu diimplementasikan serta diuji pada layanan masing-masing.
- Panduan LocalLoop menyatakan endpoint katalog dan detail telah diimplementasikan. Base URL publik dan key belum diterbitkan dalam panduan tersebut.
- API lokal AERIVA saat ini memiliki route health, assessment dan recommendations, dengan respons data belum tersedia. Registrasi, login, autentikasi mitra, provider prakiraan dan aturan penilaian belum dibuat.
- Contoh respons dan format error dalam dokumen ini merupakan target implementasi. Respons kerangka AERIVA saat ini belum sepenuhnya mengikuti seluruh field tersebut.
- Nanda mengerjakan layanan inti, Docker, pembatasan resource, gateway dan tunnel STB. Integrasi di luar STB, penggunaan dua API pada fitur, dokumentasi registry dan pengujian end-to-end masih harus diselesaikan.
- URL microservice dan entri Registry tercantum untuk akhir M14. Semua tautan final dikumpulkan di Edunex paling lambat 13 Desember 2026 pukul 23.59 WIB.
