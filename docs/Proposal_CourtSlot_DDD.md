# Perancangan Layanan Inti CourtSlot untuk Reservasi Fasilitas Publik Kota Berbasis Domain-Driven Design

> Transkripsi teks dari proposal PDF. Untuk tabel yang kompleks, PDF asli tetap menjadi rujukan tata letak kolom.

Tugas Besar II3160 Teknologi Sistem Terintegrasi × II3140 Pengembangan Aplikasi Web & Mobile · Tema Smart City & Mobility  
Disusun oleh: Keisha Daffa Aryani (18224009) dan Yumna Fathonah Kautsar (18224063)  
Kelompok dan kelas: [nomor kelompok] · [K01/K02]  
Dosen Pengampu: Ir. Devi Willieam Anggara, S.T., M.Phil., Ph.D., IPP.

Sekolah Teknik Elektro dan Informatika, Institut Teknologi Bandung · 2026

## BAB I PENDAHULUAN

### 1.1 Latar Belakang

Fasilitas publik kota, seperti taman, lapangan olahraga, perpustakaan, gedung serbaguna, dan kafe publik, dibangun dengan anggaran publik agar dapat dimanfaatkan seluruh warga. Dalam praktiknya, pemesanan fasilitas tersebut masih bergantung pada loket, surat permohonan, atau percakapan WhatsApp dengan petugas. Setiap fasilitas biasanya memiliki catatan jadwal sendiri sehingga tidak ada satu sumber informasi yang dapat dilihat warga maupun pemerintah. Akibatnya muncul pemesanan ganda, fasilitas yang penuh pada jam tertentu tetapi kosong pada jam lain, dan warga yang datang tanpa kepastian ketersediaan. Pemeliharaan juga cenderung reaktif karena pemerintah tidak memiliki data pemanfaatan yang terstruktur.

Kondisi tersebut berkaitan langsung dengan tema Smart City & Mobility. Perjalanan sia-sia menuju fasilitas yang penuh, ditutup, atau terdampak hujan dan banjir menghabiskan waktu warga dan menambah pergerakan yang tidak perlu di kota. Akses yang tidak diatur juga cenderung menguntungkan warga yang paling cepat atau paling dekat dengan petugas, bukan yang paling membutuhkan. Data pemanfaatan yang tercatat membantu pemerintah menentukan jadwal pemeliharaan dan menilai fasilitas mana yang kurang atau terlalu banyak dipakai. Karena itu, reservasi fasilitas publik layak dipandang sebagai layanan kota, bukan sekadar fitur penyewaan.

Rancangan CourtSlot sebelumnya berfokus pada reservasi lapangan olahraga outdoor di satu venue berskala kecil dengan pengelola sebagai pelanggan berbayar. Laporan ini mengembangkan cakupan tersebut menjadi platform reservasi untuk seluruh fasilitas publik dalam skenario kerja sama dengan pemerintah kota. Pemerintah tetap memiliki fasilitas, menetapkan aturan dan tarif, serta menunjuk petugas, sedangkan tim CourtSlot sebagai pengembang menyediakan dan memelihara sistemnya. Perubahan cakupan ini menambah

persoalan domain, yaitu kapasitas, kebijakan akses yang adil, penutupan untuk pemeliharaan, dan pengelolaan banyak instansi. Model bisnis ikut berubah dari langganan venue kecil menjadi kontrak layanan dengan pemerintah.

Fitur Rencana Kunjungan dari rancangan awal tetap dipertahankan. Fitur ini menggabungkan jadwal reservasi dengan prakiraan cuaca dan kondisi akses di sekitar fasilitas dari layanan kelompok lain, sehingga warga dapat memutuskan sebelum berangkat apakah kunjungan perlu dipindahkan. Laporan ini menyusun deskripsi sistem, analisis model bisnis dan margin, serta pemodelan domain dengan pendekatan Domain-Driven Design.

### 1.2 Rumusan Masalah

- Bagaimana merancang sistem reservasi yang melayani berbagai jenis fasilitas
publik, baik yang dipesan per slot waktu maupun berdasarkan kapasitas, tanpa pemesanan ganda?

- Bagaimana aturan domain menjaga keadilan akses warga serta menghubungkan
reservasi dengan penutupan dan pemeliharaan fasilitas?

- Bagaimana model bisnis dan margin yang realistis bagi pengembang yang bekerja
sama dengan pemerintah kota?

- Bagaimana membagi tanggung jawab layanan dengan DDD dan
mengintegrasikannya dengan minimal dua layanan kelompok lain untuk fitur Rencana Kunjungan?

### 1.3 Tujuan

- Merancang model domain reservasi fasilitas publik yang menegakkan aturan
ketersediaan, kapasitas, dan akses adil.

- Menyusun model bisnis, struktur biaya, dan simulasi margin dengan asumsi yang
eksplisit.

- Memetakan domain ke subdomain core, supporting, dan generic beserta bounded
context dan hubungan antarkonteks.

- Menentukan batas MVP yang dapat dikerjakan dua orang pada STB dan aplikasi
mobile.

### 1.4 Ruang Lingkup dan Asumsi

- Kerja sama dengan pemerintah kota adalah skenario perancangan dan belum
merupakan perjanjian nyata. Fasilitas, tarif, dan aturan pemakaian dimodelkan sebagai konfigurasi yang ditetapkan instansi.

- MVP memakai data uji untuk tiga jenis fasilitas (lapangan, perpustakaan, taman)
pada satu kota pilot.

- Pembayaran dan pemungutan retribusi berlangsung di luar aplikasi melalui kanal
resmi pemerintah.

- Seluruh angka bisnis bersifat hipotesis ilustratif dan belum divalidasi pasar. Ketentuan
hukum dan pengadaan yang disebut perlu diverifikasi dengan peraturan terkini serta peraturan daerah setempat.

## BAB II PEMBAHASAN

### 2.1 Deskripsi Sistem

#### 2.1.1 Gambaran Umum

CourtSlot adalah platform reservasi fasilitas publik kota yang dikembangkan sebagai layanan bagi pemerintah kota. Dalam skenario kerja sama, setiap fasilitas publik, mulai dari taman, lapangan olahraga, perpustakaan, gedung serbaguna, hingga kafe publik di bawah pengelolaan pemerintah, didaftarkan ke satu katalog dan satu kalender pemanfaatan.

Warga memakai aplikasi mobile untuk menemukan fasilitas, memeriksa ketersediaan, dan memesan waktu atau tempat. Petugas dan operator memakai aplikasi yang sama dengan tampilan sesuai peran. Pemerintah tetap menjadi pemilik fasilitas dan penetap aturan serta tarif, sedangkan CourtSlot menegakkan aturan tersebut secara konsisten.

Dibanding rancangan awal, domain yang dikelola menjadi lebih luas. Sistem tidak lagi hanya mencegah dua pesanan pada slot yang sama, tetapi juga menjaga keadilan akses melalui jendela pemesanan, kuota warga, dan sanksi tidak hadir. Sistem menangani fasilitas berbasis kapasitas, misalnya kursi baca perpustakaan, di samping fasilitas berbasis slot eksklusif seperti lapangan dan ruang rapat. Reservasi juga dikaitkan dengan pemeliharaan, sehingga penutupan fasilitas oleh instansi otomatis memengaruhi reservasi yang terdampak. Setiap perubahan tercatat dalam jejak audit agar pemerintah dapat mempertanggungjawabkan pemanfaatan fasilitas. Seluruh kemampuan ini berjalan di satu microservice inti sesuai batasan penggunaan STB.

#### 2.1.2 Pemangku Kepentingan

Sistem melibatkan lima aktor internal dan beberapa sistem eksternal. Warga adalah pengguna utama dan tidak dikenai biaya memakai aplikasi. Petugas fasilitas mengelola kalender dan mencatat pesanan yang datang langsung atau melalui WhatsApp agar semuanya tetap berada dalam satu jadwal. Admin dinas menetapkan kebijakan pemesanan dan penutupan untuk fasilitas di bawah instansinya, misalnya dinas yang membidangi olahraga, perpustakaan, atau pertamanan. Operator mitra, seperti pengelola kafe publik, hanya mengelola unit yang dipercayakan kepadanya, sedangkan analis kota membaca laporan pemanfaatan tanpa dapat mengubah data.

#### 2.1.3 Jenis Fasilitas dan Model Pemesanan

| Jenis fasilitas | Contoh unit pesan | Model pemesanan | Aturan khas |
| --- | --- | --- | --- |
| Lapangan olahraga | Lapangan basket, lapangan tenis | EXCLUSIVE_SLOT, slot 60 menit | Peringatan cuaca, kuota mingguan |
| Ruang di gedung publik | Ruang rapat, aula, ruang diskusi perpustakaan | EXCLUSIVE_SLOT, boleh beberapa slot berurutan | Batas durasi, izin untuk acara besar |
| Ruang baca | Area kursi baca | CAPACITY_BASED, kuota kursi per sesi | Kapasitas tidak boleh terlampaui |
| Taman | Pavilion, area piknik, amfiteater | EXCLUSIVE_SLOT per sesi atau CAPACITY_BASED | Izin bila peserta melebihi batas |
| Kafe publik | Meja atau area makan | CAPACITY_BASED | Dikelola operator mitra |

Perbedaan perilaku antarfasilitas ditangani melalui atribut model pemesanan pada setiap unit pesan, bukan melalui kelas fasilitas yang terpisah. Dengan cara ini, jenis fasilitas baru dapat ditambahkan lewat konfigurasi katalog dan kebijakan tanpa mengubah inti reservasi.

Unit pesan adalah bagian fasilitas yang dapat dipesan, misalnya satu lapangan, satu ruang diskusi, atau satu area kursi baca. Setiap unit memiliki jadwal operasional, kebijakan pemesanan, dan model pemesanan sendiri. Kebijakan tersebut ditetapkan oleh instansi pemilik fasilitas.

#### 2.1.4 Alur Utama

Alur utama dimulai ketika warga memilih fasilitas, unit, dan tanggal kunjungan. Sistem menampilkan slot atau sisa kapasitas berdasarkan jam operasional, jendela pemesanan, penutupan, dan kuota warga yang bersangkutan. Warga mengirim permintaan, lalu Core API memeriksa seluruh aturan dalam satu transaksi sebelum menyimpan reservasi berstatus terkonfirmasi. Jika slot sudah diambil lewat aplikasi atau dicatat petugas, sistem mengembalikan konflik dan memperbarui pilihan. Sebelum waktu mulai, warga dapat memindahkan atau membatalkan reservasi sesuai kebijakan. Pada hari kunjungan, warga melakukan check-in melalui kode QR di lokasi, dan ketidakhadiran tanpa pembatalan tercatat sebagai tidak hadir.

Petugas memakai kalender yang sama untuk melihat reservasi, mencatat pesanan walk-in atau WhatsApp, dan melakukan check-in manual. Admin dinas dapat menjadwalkan penutupan untuk pemeliharaan, kegiatan pemerintah, atau alasan keselamatan. Reservasi

yang terdampak penutupan resmi dibatalkan otomatis dengan alasan tercatat, dan pemesannya mendapat prioritas penjadwalan ulang selama 24 jam. Perlakuan ini berbeda dari cuaca dan kondisi akses, yang hanya menjadi peringatan dan tidak mengubah reservasi secara otomatis. Dengan demikian keputusan yang bersifat otoritatif berada pada instansi, sedangkan keputusan kunjungan berada pada warga. Seluruh perubahan status menghasilkan notifikasi dan catatan audit.

#### 2.1.5 Integrasi dan Implementasi

Rencana Kunjungan menggabungkan jadwal CourtSlot dengan dua layanan kelompok lain.

AERIVA menyediakan prakiraan lingkungan sesuai kontraknya, dan kelompok kedua, yang masih kandidat dan mengikuti API Registry, menyediakan laporan kondisi akses seperti banjir atau penutupan jalan di sekitar fasilitas. Open-Meteo dipakai sebagai API publik untuk prakiraan hujan per jam saat warga memilih slot. Setiap sumber memiliki status ketersediaan sendiri sehingga kegagalan satu mitra tidak menghalangi pemesanan.

Layanan integrasi berjalan di luar STB sesuai ketentuan tugas, sedangkan API baca CourtSlot untuk kelompok lain hanya memuat data fasilitas dan ketersediaan agregat tanpa identitas warga. Pada tema Smart City & Mobility, fitur ini mengurangi kunjungan yang berakhir sia- sia.

Core API diusulkan memakai FastAPI dan SQLite dalam Docker di STB dengan volume persisten, Nginx sebagai gateway, dan Cloudflare Tunnel untuk akses publik. Aplikasi mobile memakai React Native dan Expo dengan tampilan sesuai peran. Untuk dua orang, MVP membatasi model slot eksklusif secara penuh dan model kapasitas pada satu jenis unit, yaitu kursi baca perpustakaan. Penutupan resmi, kuota warga, dan check-in masuk sebagai fitur domain, sedangkan persetujuan kegiatan skala besar dan pembayaran berada di luar demo. Stack dan performanya tetap perlu diuji pada STB yang dipakai tim.

### 2.2 Model Bisnis dan Analisis Margin

#### 2.2.1 Pembayar dan Proposisi Nilai

Pembayar utama CourtSlot adalah pemerintah kota melalui dinas yang membawahi fasilitas publik, sedangkan warga memakai aplikasi tanpa biaya. Model bisnis berubah dari B2B venue kecil menjadi B2G (business-to-government). Nilai bagi pemerintah mencakup satu kalender pemanfaatan lintas fasilitas, akses yang adil dan dapat diaudit, berkurangnya pencatatan manual, serta data pemanfaatan untuk menjadwalkan pemeliharaan. Produk pembanding pada rancangan awal (BookLapang, Gelora SmartVenue, AYO) menyasar pengelola venue olahraga, sehingga kebutuhan lintas jenis fasilitas publik dengan kebijakan akses dan pelaporan untuk pemerintah belum terpetakan dan perlu riset pasar tersendiri.

#### 2.2.2 Skema Pendapatan

Komponen Skema Hipotesis harga Biaya platform kota Langganan bulanan per kota: dashboard, pelaporan, dukungan, SLA Rp10.000.000 per bulan Biaya per fasilitas aktif Langganan bulanan per fasilitas Rp250.000 per bulan Onboarding Sekali per fasilitas: input data, pelatihan petugas, kode QR Rp2.000.000 Tidak dikenakan Komisi atas retribusi atau tarif, serta biaya kepada warga Rp0 CourtSlot sengaja tidak mengambil komisi dari tarif atau retribusi karena dana tersebut adalah pendapatan daerah yang mengalir ke kas daerah melalui kanal resmi. Pendapatan pengembang bersumber dari layanan sistem, bukan dari transaksi warga. Pendapatan tambahan seperti modul pelaporan khusus atau integrasi dengan sistem aset daerah tidak dimasukkan ke simulasi.

#### 2.2.3 Struktur Biaya

Komponen Nilai Keterangan Biaya variabel per fasilitas aktif Rp60.000 per bulan Notifikasi, penyimpanan, bagian dukungan Biaya tetap, skenario pilot Rp18.000.000 per bulan Hosting dan pemantauan Rp3 juta; dukungan satu orang Rp7 juta; pemeliharaan perangkat lunak Rp6 juta; audit keamanan diamortisasi Rp2 juta Biaya tetap, skenario tiga kota Rp30.000.000 per bulan Dukungan dan pemeliharaan bertambah Biaya onboarding Rp1.200.000 per fasilitas Pengisian data, pelatihan petugas, kode QR

#### 2.2.4 Simulasi Margin

Per bulan Pilot: 1 kota, 60 fasilitas Ekspansi: 3 kota, 180 fasilitas Biaya platform kota Rp10.000.000 Rp30.000.000

Per bulan Pilot: 1 kota, 60 fasilitas Ekspansi: 3 kota, 180 fasilitas Biaya per fasilitas Rp15.000.000 Rp45.000.000 Pendapatan langganan Rp25.000.000 Rp75.000.000 Biaya variabel Rp3.600.000 Rp10.800.000 Margin kontribusi Rp21.400.000 (85,6%) Rp64.200.000 (85,6%) Biaya tetap Rp18.000.000 Rp30.000.000 Laba operasi Rp3.400.000 (13,6%) Rp34.200.000 (45,6%) Pada skenario pilot, titik impas tercapai pada 43 fasilitas aktif dalam satu kota. Onboarding 60 fasilitas menghasilkan pendapatan sekali Rp120 juta dengan biaya Rp72 juta, sehingga selisihnya Rp48 juta. Margin pilot tipis dan hanya menjadi sehat ketika biaya tetap dibagi ke beberapa kota. Hasil ini sensitif terhadap harga: bila biaya per fasilitas turun menjadi Rp150.000, pilot rugi Rp2,6 juta per bulan dan titik impas naik menjadi 89 fasilitas. Simulasi belum memasukkan pengembangan awal, biaya mengikuti tender atau pengadaan, gaji pendiri, pajak, dan risiko pembayaran terlambat.

#### 2.2.5 Nilai Ekonomi bagi Pemerintah Kota

Biaya langganan pilot bagi kota adalah Rp25 juta per bulan atau Rp300 juta per tahun.

Sebagai ilustrasi, penghematan waktu administrasi 60 fasilitas selama 8 jam per bulan dengan nilai Rp35.000 per jam setara Rp16,8 juta per bulan. Tambahan 400 pemesanan berbayar per bulan dari slot yang sebelumnya kosong atau tidak tercatat, dengan tarif rata- rata Rp25.000, menambah retribusi Rp10 juta per bulan. Total manfaat finansial Rp26,8 juta hanya sedikit di atas biaya Rp25 juta. Artinya posisi produk yang kuat bukan penghematan uang semata, melainkan kualitas layanan publik, transparansi, dan pemeliharaan berbasis data, yang tidak dimonetisasi dalam simulasi ini.

#### 2.2.6 Risiko dan Validasi

Risiko Dampak Mitigasi Siklus anggaran dan pengadaan pemerintah Penjualan lambat, pembayaran tertunda Mulai dari satu dinas dengan pilot kecil; cek ambang pengadaan langsung yang berlaku Petugas tidak konsisten mencatat pesanan Kalender tidak dipercaya Pelatihan, mode input walk-in cepat, laporan kepatuhan pencatatan

Risiko Dampak Mitigasi Tarif dan retribusi diatur peraturan daerah Sistem salah menampilkan tarif Tarif sebagai konfigurasi instansi; pembayaran lewat kanal resmi Data pribadi warga Pelanggaran UU Pelindungan Data Pribadi Minimisasi data, data uji pada demo, peran akses ketat SQLite pada skala kota; lisensi data cuaca komersial Kinerja dan biaya Migrasi ke PostgreSQL saat skala naik; cek lisensi Open-Meteo untuk penggunaan komersial Validasi dilakukan lewat pilot empat sampai delapan minggu pada 3 sampai 5 fasilitas satu dinas. Indikator yang diukur adalah persentase pesanan walk-in dan WhatsApp yang masuk kalender, tingkat tidak hadir sebelum dan sesudah sistem, tingkat pemanfaatan jam sepi, dan waktu administrasi petugas. Kesediaan dinas melanjutkan dengan kontrak berbayar menjadi indikator terkuat bahwa harga hipotesis dapat diterima.

### 2.3 Identifikasi Core Domain dan Dekomposisi Subdomain

#### 2.3.1 Core Domain dan Alasan Pemilihannya

Domain CourtSlot adalah Manajemen Reservasi Fasilitas Publik Kota (Public Facility Reservation Management). Core subdomain-nya adalah Reservasi dan Akses Adil Fasilitas Publik karena di sinilah pembeda produk berada. Fasilitas publik tidak dapat diperlakukan seperti venue komersial yang hanya mengejar keterisian, sehingga sistem harus menegakkan kesetaraan akses, kapasitas, dan prioritas kegiatan resmi. Kombinasi aturan tersebut tidak tersedia pada perangkat generik sehingga dibangun sendiri oleh tim. Nilai bagi pemerintah, yang menjadi dasar pembayaran langganan, bergantung pada kualitas aturan ini.

#### 2.3.2 Pembagian Subdomain: Core, Supporting, dan Generic

Core subdomain terdiri atas tiga bagian. Ketersediaan dan Kapasitas menentukan slot atau sisa kapasitas yang dapat dipesan dari jadwal, penutupan, dan reservasi aktif. Siklus Reservasi mengatur pemesanan, pencatatan pesanan dari luar aplikasi, pemindahan, pembatalan, check-in, dan ketidakhadiran. Kebijakan Akses Adil mengevaluasi jendela pemesanan, kuota warga, prioritas kegiatan resmi, dan sanksi. Ketiganya memeriksa data yang sama dan harus diputuskan dalam satu transaksi.

Subdomain pendukung terdiri atas Katalog Fasilitas Publik, Pemeliharaan dan Penutupan Fasilitas, Perencanaan Kunjungan, Tarif dan Pembebasan Biaya, serta Analitik dan Pelaporan Pemanfaatan. Katalog menyimpan data instansi, fasilitas, unit pesan, jadwal, dan kebijakan.

Pemeliharaan sangat dekat dengan tujuan pemerintah, tetapi aturannya cukup sederhana, yaitu periode, cakupan unit, dan alasan, sehingga tetap berstatus supporting. Perencanaan Kunjungan kini juga memuat peringatan cuaca per slot yang sebelumnya menjadi subdomain terpisah. Tarif hanya menampilkan ketentuan instansi tanpa memungut dana.

Subdomain generik terdiri atas Identitas dan Akses, Notifikasi, Jejak Audit, serta Peta dan Geocoding berbasis OpenStreetMap. Identitas dan Akses kini mengenal peran Warga, Petugas, Operator Mitra, Admin Dinas, dan Analis Kota dengan lingkup instansi. Jejak Audit penting bagi pemerintah, tetapi mekanismenya umum dan tidak menjadi pembeda. AERIVA dan kelompok mitra tetap memiliki model domain dan sumber data masing-masing.

Domain: Manajemen Reservasi Fasilitas Publik Kota ├─ CORE │ └─ Reservasi dan Akses Adil Fasilitas Publik │ ├─ Ketersediaan dan Kapasitas │ ├─ Siklus Reservasi (pesan, pindah, batal, check-in, tidak hadir) │ └─ Kebijakan Akses Adil (jendela, kuota, prioritas, sanksi) ├─ SUPPORTING │ ├─ Katalog Fasilitas Publik │ ├─ Pemeliharaan dan Penutupan Fasilitas │ ├─ Perencanaan Kunjungan (cuaca dan kondisi akses) │ ├─ Tarif dan Pembebasan Biaya │ └─ Analitik dan Pelaporan Pemanfaatan └─ GENERIC ├─ Identitas dan Akses ├─ Notifikasi ├─ Jejak Audit └─ Peta dan Geocoding (OSM)

### 2.4 Identifikasi Bounded Context

Pembagian bounded context memisahkan model, data, dan aturan setiap bagian sistem agar istilah yang sama tidak bercampur artinya. Contoh paling jelas adalah istilah “slot” dan “fasilitas”: Katalog memandangnya sebagai data master, sedangkan Reservasi memandangnya sebagai sesuatu yang dapat ditahan. Konteks-konteks internal dapat diimplementasikan sebagai modul dalam satu microservice CourtSlot Core API, sedangkan Rencana Kunjungan berjalan pada layanan integrasi di luar STB. Komunikasi antarmodul memakai antarmuka yang jelas dan domain event, bukan akses langsung ke tabel konteks lain.

Konteks Jenis Tanggung jawab Penempatan Reservasi dan Akses Core Ketersediaan, kapasitas, siklus reservasi, kebijakan akses adil Core API (STB) Katalog Fasilitas Publik Supporting Instansi, fasilitas, unit pesan, jadwal, kebijakan, tarif Core API (STB) Pemeliharaan dan Penutupan Supporting Penutupan resmi dan alasannya Core API (STB) Rencana Kunjungan Supporting Gabungan jadwal, cuaca, dan kondisi akses beserta status sumber Layanan integrasi (luar STB) Pelaporan dan Audit Supporting dan Generic Ringkasan pemanfaatan dan catatan audit dari domain event Core API (STB) Identitas dan Akses Generic Akun, peran, lingkup instansi Core API (STB) Notifikasi Generic Penyampaian status ke pengguna Core API (STB) Konteks Reservasi dan Akses adalah satu-satunya konteks yang berwenang menentukan apakah suatu unit dapat dipesan, mengubah, atau membatalkan reservasi. Konteks ini memakai data unit, jadwal, dan kebijakan dari Katalog tanpa memiliki data master tersebut, serta mendengarkan penutupan dari konteks Pemeliharaan. Evaluasi kebijakan akses berada di dalam konteks yang sama karena kuota dan sanksi bergantung pada riwayat reservasi dan harus diperiksa atomik bersama pembuatan reservasi. Informasi cuaca dan kondisi akses tidak pernah mengubah reservasi secara otomatis.

Konteks pendukung memiliki batas yang tegas. Katalog Fasilitas Publik memiliki data master dan kebijakan yang ditetapkan instansi, sedangkan keputusan ketersediaan tetap milik Reservasi. Pemeliharaan dan Penutupan menerbitkan penutupan resmi, dan Reservasi bereaksi dengan membatalkan reservasi terdampak serta membuka prioritas penjadwalan ulang. Rencana Kunjungan hanya membaca data reservasi dan fasilitas, tidak berwenang membuat atau mengubah reservasi, dan menandai status tiap sumber sehingga kegagalan satu mitra tidak memengaruhi reservasi. Pelaporan dan Audit hanya menerima event dan tidak dapat memengaruhi keputusan reservasi.

Konteks generik menyediakan kemampuan umum. Identitas dan Akses memberikan identitas dan peran tervalidasi melalui token yang dipakai konteks lain untuk memeriksa kepemilikan dan kewenangan tanpa mengakses data autentikasi. Notifikasi menyampaikan

status resmi dari Reservasi dan tidak berwenang mengubah status. Hubungan dengan pihak luar dijaga lapisan penerjemah: respons AERIVA, kelompok kedua, dan Open-Meteo diubah menjadi model Rencana Kunjungan sehingga perubahan kontrak mitra tidak merambat ke konteks inti.

Hubungan (hulu → hilir) Pola Isi Katalog → Reservasi Customer-Supplier Data unit, jadwal, kebijakan sebagai published language Pemeliharaan → Reservasi Customer-Supplier Event penutupan yang memicu pembatalan dan prioritas jadwal ulang Identitas → semua konteks Open Host Service Token berisi identitas, peran, dan lingkup instansi Reservasi → Notifikasi, Pelaporan dan Audit Publish-Subscribe Domain event reservasi Reservasi dan Katalog → Rencana Kunjungan Open Host Service API baca dengan API key, tanpa identitas warga AERIVA, kelompok kedua, Open-Meteo → Rencana Kunjungan Anti-Corruption Layer Penerjemahan respons mitra ke model internal Kelompok lain → API baca CourtSlot Open Host Service Kontrak OpenAPI untuk fasilitas dan ketersediaan agregat

### 2.5 Aturan Domain

#### 2.5.1 Aturan Bisnis dan Invarian

Aturan berikut menjadi inti rancangan dan dapat langsung diterjemahkan menjadi pemeriksaan di Core API serta kasus uji. Parameter bernilai default, misalnya batas 14 hari atau kuota dua reservasi, dapat diubah per unit oleh admin dinas melalui kebijakan pemesanan.

ID Aturan Konteks Cara penegakan R01 Unit EXCLUSIVE_SLOT tidak boleh memiliki lebih dari satu item reservasi aktif pada slot yang sama Reservasi Unique partial index pada slot_id untuk item aktif

ID Aturan Konteks Cara penegakan R02 Total peserta aktif pada satu sesi tidak boleh melebihi kapasitas unit CAPACITY_BASED Reservasi Pengurangan sisa kapasitas atomik dalam transaksi, bersyarat sisa mencukupi R03 Pemesanan beberapa slot harus berurutan pada unit yang sama dan tidak melebihi durasi maksimum; semua slot berhasil ditahan atau tidak sama sekali Reservasi Satu transaksi R04 Slot hanya ditawarkan dalam jam operasional, di luar hari libur dan penutupan Katalog, Pemeliharaan Pembangkitan slot dari jadwal dan penutupan R05 Jendela pemesanan: paling cepat H-14 dan paling lambat 120 menit sebelum mulai (default) Reservasi Policy service saat membuat dan memindahkan R06 Warga terverifikasi maksimal 2 reservasi aktif mendatang per kategori fasilitas per pekan (default); pesanan atas namanya yang dicatat petugas ikut dihitung Reservasi Policy service R07 Tidak check-in dalam masa tenggang 15 menit menjadi NO_SHOW dan menambah satu strike; tiga strike dalam 30 hari menangguhkan hak pesan 14 hari; petugas dapat membatalkan strike Reservasi Agregat BookerStanding R08 Pembatalan oleh pemesan bebas sanksi hingga 2 jam sebelum mulai; pembatalan lebih lambat dihitung seperti tidak hadir; pembatalan setelah mulai tidak diperbolehkan Reservasi Status dan waktu R09 Pemindahan jadwal hanya sebelum waktu mulai, pada unit yang sama, maksimal 2 kali per reservasi; slot tujuan harus memenuhi seluruh aturan, dan bila gagal reservasi lama tetap utuh Reservasi Satu transaksi dengan pengembalian konflik

ID Aturan Konteks Cara penegakan R10 Penutupan resmi memblokir slot; reservasi terdampak menjadi CANCELLED_BY_CLOSURE dengan alasan tercatat dan pemesannya mendapat prioritas jadwal ulang 24 jam; penutupan non-darurat dijadwalkan minimal 72 jam sebelumnya Pemeliharaan, Reservasi Event ClosureAnnounced R11 Cuaca dan kondisi akses bersifat peringatan dan tidak mengubah reservasi; kegagalan mitra tidak memengaruhi pemesanan Rencana Kunjungan Status per sumber R12 Warga hanya mengelola reservasinya sendiri; petugas dan admin hanya pada fasilitas dalam lingkup instansinya; operator mitra hanya pada unit miliknya Identitas Peran dan lingkup pada token R13 Reservasi yang telah lewat tidak dapat diubah, kecuali koreksi kehadiran oleh petugas dengan alasan tercatat Reservasi Status dan peran R14 Setiap perubahan status, penutupan, dan koreksi tercatat (siapa, kapan, alasan) dan tidak dapat diubah atau dihapus Pelaporan dan Audit Log append-only R15 API untuk kelompok lain hanya memuat data fasilitas dan ketersediaan agregat tanpa identitas; demo memakai data uji Katalog, Reservasi Kontrak API R16 Sistem menampilkan tarif yang ditetapkan instansi, tidak menghitung komisi, dan tidak menerima dana Katalog Di luar alur pembayaran R17 Opsional per kebijakan: kegiatan skala besar berstatus PENDING_APPROVAL yang menahan slot paling lama 24 jam; MVP memakai konfirmasi langsung Reservasi Kebijakan unit Seperti pada rancangan awal, keunikan reservasi tidak dapat dijamin oleh objek Reservation sendiri karena objek tersebut tidak mengetahui transaksi lain yang berjalan bersamaan.

Karena itu R01 dan R02 ditegakkan di tingkat basis data, sedangkan aturan lain diperiksa di dalam transaksi yang sama.

#### 2.5.2 Siklus Hidup Reservasi

Status Arti Transisi berikutnya CONFIRMED Reservasi sah, slot atau kapasitas ditahan CHECKED_IN, NO_SHOW, CANCELLED_BY_USER, CANCELLED_BY_STAFF, CANCELLED_BY_CLOSURE; pemindahan jadwal tetap berstatus CONFIRMED CHECKED_IN Pemesan hadir pada masa check-in COMPLETED COMPLETED Reservasi selesai Akhir NO_SHOW Tidak hadir melewati masa tenggang Akhir, dapat dikoreksi petugas (R13) CANCELLED_BY_USER Dibatalkan pemesan sebelum batas Akhir CANCELLED_BY_STAFF Dibatalkan petugas atau admin dengan alasan Akhir CANCELLED_BY_CLOSURE Dibatalkan karena penutupan resmi Akhir, disertai hak prioritas jadwal ulang

#### 2.5.3 Aggregate, Entity, Value Object, dan Domain Event

Konteks Aggregate root Entity Value object Domain event Reservasi dan Akses Reservation ReservationItem TimeWindow, PartySize, ReservationSourc e (APP, STAFF), ReservationStatus ReservationConf irmed, ReservationResc heduled, ReservationCan celled, CheckedIn, ReservationNoS how Reservasi dan Akses BookerStanding StrikeRecord SuspensionPeriod BookerSuspende d

Konteks Aggregate root Entity Value object Domain event Katalog Fasilitas Publik Facility BookableUnit BookingModel, BookingPolicy, OperatingSchedul e, GeoLocation FacilityRegistere d, PolicyChanged Pemeliharaan dan Penutupan FacilityClosure ClosureScope ClosureReason, ClosurePeriod ClosureAnnounc ed, ClosureCancelle d Identitas dan Akses Account RoleAssignment AgencyScope AccountRegister ed Rencana Kunjungan VisitPlan (read model) Tidak ada SourceStatus, ForecastSlice, AccessReport Tidak ada TimeSlot dikelola sebagai entity yang dihasilkan dari jadwal Katalog dan direferensikan oleh ReservationItem melalui ID. Dengan demikian aggregate Reservation tetap kecil, sedangkan konsistensi antara reservasi dan slot dijaga oleh batasan basis data dan transaksi.

#### 2.5.4 Bahasa Bersama (Ubiquitous Language)

Istilah Nama di kode Makna Fasilitas Facility Lokasi publik milik instansi, misalnya taman atau perpustakaan Unit pesan BookableUnit Bagian fasilitas yang dapat dipesan Slot TimeSlot Rentang waktu 60 menit pada unit Reservasi Reservation Hak pakai atas slot atau kapasitas oleh seorang pemesan Pemesan Booker Warga atau pihak yang dicatat petugas Penutupan resmi FacilityClosure Penutupan otoritatif oleh instansi Kuota warga BookingQuota Batas reservasi aktif per warga Strike NoShowStrike Catatan ketidakhadiran atau pembatalan terlambat

## BAB III PENUTUP

### 3.1 Kesimpulan

Pengembangan CourtSlot dari reservasi lapangan olahraga menjadi reservasi fasilitas publik kota memperluas domain tanpa mengubah prinsip dasarnya, yaitu satu sumber kebenaran untuk ketersediaan. Core domain bergeser menjadi Reservasi dan Akses Adil, yang menggabungkan slot eksklusif, kapasitas, siklus reservasi, dan kebijakan akses dalam satu konteks yang konsisten. Penutupan resmi untuk pemeliharaan membedakan keputusan otoritatif instansi dari peringatan cuaca dan akses yang tetap menjadi pertimbangan warga.

Pembagian ke tujuh bounded context memungkinkan satu microservice di STB dan satu layanan integrasi di luar STB mengerjakan peran yang berbeda.

Dari sisi bisnis, model B2G dengan langganan platform kota dan biaya per fasilitas memberi margin kontribusi sekitar 85,6% pada asumsi yang dipakai. Margin operasi pilot hanya 13,6% dengan titik impas 43 fasilitas, sehingga bisnis ini baru sehat ketika biaya tetap dibagi ke beberapa kota. Manfaat finansial bagi pemerintah relatif sebanding dengan biayanya, sehingga nilai jual utama adalah kualitas layanan publik, transparansi, dan data pemeliharaan. Seluruh angka tersebut masih hipotesis dan perlu divalidasi melalui pilot.

### 3.2 Ringkasan Perubahan dari Rancangan Awal

Aspek Rancangan awal Pengembangan Cakupan Lapangan olahraga outdoor, satu venue Seluruh fasilitas publik kota: lapangan, taman, perpustakaan, gedung, kafe publik Pembayar Pengelola venue (B2B) Pemerintah kota (B2G); warga gratis Model pemesanan Slot eksklusif Slot eksklusif, kapasitas, dan multi-slot berurutan Core subdomain Facility Slot Reservation Reservasi dan Akses Adil Fasilitas Publik Aturan baru Satu reservasi aktif per slot, cuaca sebagai peringatan Jendela pemesanan, kuota warga, sanksi tidak hadir, penutupan resmi, jejak audit Peran Pemain dan pengelola venue Warga, Petugas, Operator Mitra, Admin Dinas, Analis Kota Status reservasi CONFIRMED dan CANCELLED Ditambah CHECKED_IN, COMPLETED, NO_SHOW, dan pembatalan karena penutupan

Aspek Rancangan awal Pengembangan Peringatan cuaca Subdomain terpisah Digabung ke Perencanaan Kunjungan

### 3.3 Hal yang Perlu Dikonfirmasi

- Uji STB dengan layanan minimal: arsitektur perangkat, ketersediaan image, akses
HTTPS ke endpoint kesehatan, penggunaan memori, dan ketahanan data SQLite setelah kontainer dibuat ulang.

- Kontrak API AERIVA: lokasi, periode prakiraan, dan indikator hujan yang dapat
dipetakan ke slot. Identitas kelompok kedua mengikuti API Registry, dengan batas Minggu 14 untuk Base URL dan dokumentasi.

- Aturan nyata pemerintah kota setempat: kebijakan pemesanan, tarif, ambang
pengadaan, dan kewajiban perlindungan data pribadi.

- Pilot satu dinas dengan beberapa fasilitas untuk menguji harga, tingkat pencatatan
walk-in, dan penurunan tingkat tidak hadir.


