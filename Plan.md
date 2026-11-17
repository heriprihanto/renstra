RENSTRA (RENCANA STRATEGIS PERANGKAT DAERAH) KOTA TEGAL
BUAT APLIKASI UNTUK PERENCANAAN PEMBANGUNAN
UNTUK MEMBUAT RENSTRA (RENCANA STRATEGIS PERANGKAT DAERAH)
Backend :
    Python, Fastapi, SQLAchemy, SQLModel
Database :
    Postgresql
Frontend :
    Vue JS 3

Tampilan Awal adalah tabel Perangkat Daerah Kota Tegal, tabel ta_opd
Nama SKPD di klik menampilkan Sub SKPD

Nama SKPD di klik menampilkan halaman baru tabel  Sub SKPD

Klik NAMA SUB SKPD menampilkan halamn Baru RENSTRA Perangkat Daerah
Layout Tab :
Tab 1 : Tujuan & Sasaran
Tab 2 : Program / Kegiatan / Subkegiatan

KOnten kosongi dulu

Revisi :
Nama SKPD di klik menampilkan halaman baru RENSTRA
Layout Tab : Tujuan & Sasaran | Program / Kegiatan / Subkegiatan

Tab Tujuan & sasaran buat Cascading :

Tujuan                      
        Indikator Tujuan    | Satuan    | Target Awal | Target 2026 | Target 2027 | Target 2028 | Target 2029 | Target Akhir   
    Sasaran
        Indikator Sasaran   | Satuan    | Target Awal | Target 2026 | Target 2027 | Target 2028 | Target 2029 | Target Akhir   

tabel terkait : renstra_tujuan, renstra_indikator_tujuan, renstra_sasaran, renstra_indikator_sasaran

Tab Program / Kegiatan / Subkegiatan
Menampilkan Sub SKPD

perhatikan tabel renstra_indikator_tujuan,  renstra_indikator_sasaran

Field target_awal adalah Baseline
        t0  : tahun 2025
        t1  : tahun 2026
        t2  : tahun 2027
        t3  : tahun 2028
        t4  : tahun 2029
        t5  : tahun 2030 

        Target Akhir memakai tahun 2029 (t4)


Form  Ubah Indikator Tujuan dan Indikator Sasaran 
tambah status, combobox, option : positif, negatif, akumulatif
Tambah field Definisi Operasional / Metadata 

Saya akan membuat perubahan target,
pada form Ubah / Tambah Indikator Tujuan dan Indikator Sasaran 
buat field Target Perubahan 
Tahun 2025
Tahun 2026
Tahun 2027
Tahun 2028
Tahun 2029
Tahun 2030

Target Akhir setelah perubahan memakai tahun 2029 perubahan

Tambahkan Target perubahan pada tampilan tabel


Pada indikator tujuan dan indikator sasaran, tampilkan apakah IKU (Indikator Kinerja Utama) dengan centang, 
pakai field iku:
- [x] Backend Model & Schemas (iku: varchar/str '1' = IKU, '0'/null = Non-IKU)
- [x] Backend Endpoints Cascading & CRUD
- [x] Kolom IKU di tabel Cascading RENSTRA dengan centang (✓) hijau
- [x] Tag IKU pada uraian indikator
- [x] Toggle checkbox IKU pada Form Tambah/Ubah Indikator Tujuan & Sasaran

Tandai jika data ada perubahan, atau ada data baru:
- [x] Database: Menambahkan kolom `perubahan_status` (VARCHAR) pada tabel `renstra_tujuan`, `renstra_sasaran`, `renstra_indikator_tujuan`, dan `renstra_indikator_sasaran`.
- [x] Backend Model & Schemas: Mendukung field `perubahan_status`, `is_baru`, `is_perubahan`, `changed_targets`, serta rollup counter perubahan/baru pada Tujuan, Sasaran, dan Response Cascading.
- [x] Backend Endpoint (`get_opd_renstra_cascading`): Deteksi otomatis perbandingan target Murni vs Perubahan (`target1`..`target5` vs `p_target0`..`p_target5`) serta deteksi data baru.
- [x] Frontend Tabel Cascading:
  - Badge `[ADA PERUBAHAN]` (oranye) dan `[DATA BARU]` (hijau) pada indikator.
  - Highlight sel target perubahan yang nilainya berubah (`col-target-diff`, background kuning-oranye lembut, teks tebal, tooltip perbandingan, dan label 'berubah').
  - Highlight sel data baru (`col-target-new`, background hijau lembut).
  - Chip ringkasan `🔄 X Perubahan` dan `✨ X Baru` pada header Tujuan dan Sasaran.
  - Border aksen visual di sisi kiri baris indikator.
- [x] Frontend Filter Toolbar: Tombol filter cepat `Semua`, `Perubahan`, dan `Data Baru` beserta badge jumlah data.
- [x] Frontend Modal Form: Pilihan penandaan status perubahan (Otomatis/Perubahan/Baru/Tetap) dan live banner deteksi tahun target yang berubah.


Revisi: Bisa Tambah, Edit, dan Hapus SEMUA Data (Full CRUD):
- [x] Pencabutan Pembatasan Hapus (Delete Unlocked):
  - Backend API: Membuka kembali endpoint DELETE untuk semua entitas:
    - `DELETE /renstra/tujuan/{id}` (dengan cascade delete child indikator tujuan, sasaran, & indikator sasaran).
    - `DELETE /renstra/sasaran/{id}` (dengan cascade delete child indikator sasaran).
    - `DELETE /renstra/indikator-tujuan/{id}`.
    - `DELETE /renstra/indikator-sasaran/{id}`.
    - `DELETE /renstra/program/{id}` (dengan cascade delete child kegiatan, subkegiatan, & indikator).
    - `DELETE /renstra/indikator-program/{id}` (endpoint baru).
    - `DELETE /renstra/kegiatan/{id}` (dengan cascade delete child subkegiatan & indikator kegiatan).
    - `DELETE /renstra/indikator-kegiatan/{id}`.
    - `DELETE /renstra/subkegiatan/{id}`.
  - Frontend UI: Menambahkan tombol aksi dropdown 'Hapus' lengkap dengan dialog konfirmasi hapus aman untuk semua entitas di Tab 1 & Tab 2.
- [x] Hak Edit Penuh Kalimat Rumusan (Sentence Edit Unlocked):
  - Backend API: Pada operasi PUT (update), semua field uraian kalimat (`uraitujuan`, `uraisasaran`, `uraitujuan_indikator`, `uraisasaran_indikator`, `uraiprogram`, `uraiindikator` program & kegiatan, `uraikegiatan`, `uraisubkegiatan`) dapat diubah dan disimpan ke database.
  - Frontend UI: Membuka kunci textarea uraian kalimat (menghapus status `readonly`, `disabled`, badge `🔒 Kalimat Terkunci`, dan pesan helper terkunci) sehingga pengguna dapat mengedit kalimat dengan leluasa.
- [x] Hak Edit Penuh Target Murni & Target Perubahan:
  - Backend API: Target capaian murni (`target_awal`, `target1` s/d `target5`, `target_akhir`) serta target perubahan dan pagu dapat diedit secara penuh melalui endpoint update.
  - Frontend UI: Membuka kunci semua input Target Murni pada modal form (menghapus status `readonly` dan `disabled`).
- [x] Penambahan Entitas Baru (Create Full Support):
  - Backend API: Menambahkan endpoint `POST /renstra/indikator-program` untuk melengkapi entri baru Indikator Program.
  - Frontend UI: Menambahkan opsi `+ Indikator Program` pada dropdown aksi Program dan mendukung form tambah indikator program.

Pindah Kolom Aksi ke Kolom Pertama:
- [x] Header Tabel: Memindahkan kolom `AKSI` dari posisi paling kanan ke kolom urutan pertama (`th rowspan="2"` di awal `<thead>`).
- [x] Baris Data:
  - Baris Tujuan (`row-tujuan`): Kolom dropdown tombol Aksi dipindahkan ke kolom pertama.
  - Baris Indikator Tujuan (`row-indikator-tujuan`): Tombol `Ubah Target` dipindahkan ke kolom pertama.
  - Baris Sasaran (`row-sasaran`): Kolom dropdown tombol Aksi dipindahkan ke kolom pertama.
  - Baris Indikator Sasaran (`row-indikator-sasaran`): Tombol `Ubah Target` dipindahkan ke kolom pertama.
- [x] Styling & UX Dropdown: Mengatur posisi menu dropdown (`.dropdown-menu-list`) agar anchor di sebelah kiri (`left: 0;`), sehingga saat tombol Aksi di kolom pertama diklik, menu dropdown terbuka ke arah kanan di atas isi tabel dan tidak terpotong tepi layar.


Buat Data Program / Kegiatan / Subkegiatan (Sub SKPD)
- Klik NAMA SUB SKPD (UNIT KERJA / PELAKSANA), menampilkan data cascading :
Program
  - Indikator Program
  Kegiatan
  - Indikator Kegiatan
    Subkegiatan
    - Indikator Subkegiatan

- [x] Database:
  - Verifikasi tabel `renstra_program`, `renstra_indikator_program`, `renstra_kegiatan`, `renstra_output_kegiatan`, dan `renstra_subkegiatan`.
  - Migrasi DDL & 879 data rekaman tabel `renstra_output_kegiatan` ke database `db_renstra`.
- [x] Backend:
  - Model SQLModel: `RenstraProgram`, `RenstraIndikatorProgram`, `RenstraKegiatan`, `RenstraOutputKegiatan`, `RenstraSubkegiatan`.
  - Schemas Pydantic: `IndikatorSubkegiatanItem`, `SubkegiatanCascadingItem`, `IndikatorKegiatanItem`, `KegiatanCascadingItem`, `IndikatorProgramItem`, `ProgramCascadingItem`, `SubSkpdCascadingResponse`.
  - Endpoint API: `GET /api/opd/sub/{id_sub_skpd}/cascading` menghasilkan hirarki 6 level terintegrasi dari Program sampai Indikator Subkegiatan beserta Pagu Anggaran per tahun dan totalnya.
- [x] Frontend:
  - Service API: Menambahkan fungsi `getSubSkpdCascading(idSubSkpd)`.
  - Desain & CSS: Desain badge level hirarki (`PROGRAM`, `IND. PROGRAM`, `KEGIATAN`, `IND. KEGIATAN`, `SUBKEGIATAN`, `IND. SUBKEGIATAN`), styling baris hirarki berjenjang (`row-program`, `row-ind-program`, `row-kegiatan`, `row-ind-kegiatan`, `row-subkegiatan`, `row-ind-subkegiatan`), container breadcrumbs, quick switcher, dan stat chips.
  - Tab 2 Sub SKPD View:
    - Nama Sub SKPD dapat diklik secara interaktif (`sub-skpd-link-btn`) dan dilengkapi tombol aksi `Lihat Cascading`.
    - Tampilan detail Cascading 6-level dengan tombol kembali ke daftar Sub SKPD (`btn-back-sub`), quick switcher dropdown antar Sub SKPD, live search box, dan chip ringkasan (Program, Kegiatan, Subkegiatan, Indikator Program, Total Pagu).
    - Tabel cascading menampilkan kolom: HIRARKI, KODE & URAIAN (dengan indentasi berjenjang), SATUAN, TARGET CAPAIAN TAHUNAN (Awal, 2026, 2027, 2028, 2029, 2030, Akhir), dan PAGU ANGGARAN (Rupiah dengan breakdown tahunan pada tooltip).



Tambah Indikator Kegiatan (jika di database belum ada tabel, buat baru):
- [x] Database:
  - Membuat tabel baru `renstra_indikator_kegiatan` di database `db_renstra` dengan struktur lengkap (kolom kode/uraian kegiatan & program, satuan, status, IKU, target capaian murni awal s/d akhir, target perubahan 2025 s/d akhir, pagu1..5, definisi operasional, perubahan_status, urut, no).
  - Migrasi awal 879 data rekaman dari `renstra_output_kegiatan` ke dalam `renstra_indikator_kegiatan` sehingga data eksisting langsung tersedia.
- [x] Backend:
  - Model SQLModel `RenstraIndikatorKegiatan` di `Backend/app/models/renstra.py`.
  - Schema Pydantic `IndikatorKegiatanItem`, `IndikatorKegiatanCreate`, dan `IndikatorKegiatanUpdate` di `Backend/app/schemas/renstra.py` dan `renstra_crud.py`.
  - Endpoint Cascading di `Backend/app/api/endpoints/opd.py`: Mengambil indikator kegiatan dari `renstra_indikator_kegiatan`, mendeteksi evaluasi perubahan target & data baru, serta menyajikan nilai target tahunan dan pagu.
  - Endpoint CRUD di `Backend/app/api/endpoints/renstra_crud.py`:
    - `POST /api/renstra/indikator-kegiatan`: Menambahkan indikator kegiatan baru ke database.
    - `PUT /api/renstra/indikator-kegiatan/{id}`: Mengubah metadata dan target perubahan indikator kegiatan.
    - `DELETE /api/renstra/indikator-kegiatan/{id}`: Proteksi penghapusan (403 Forbidden).
- [x] Frontend:
  - Service API: Menambahkan fungsi `createIndikatorKegiatan`, `updateIndikatorKegiatan`, dan `deleteIndikatorKegiatan`.
  - Modal Form (`RenstraCrudModal.vue`): Mendukung mode `'create_ind_kegiatan'` dan `'edit_ind_kegiatan'` lengkap dengan input Target Murni & Target Perubahan, IKU, Satuan, Status, dan Definisi Operasional.
  - Tabel Cascading Tab 2 (`OpdRenstraView.vue`):
    - Kolom AKSI pada baris Kegiatan: Tombol `+ Indikator` untuk membuka form Tambah Indikator Kegiatan Baru.
    - Kolom AKSI pada baris Indikator Kegiatan: Tombol `Ubah Target` untuk mengubah metadata & target perubahan.
    - Kolom IKU dengan centang hijau jika IKU aktif, badge status perubahan (DATA BARU / ADA PERUBAHAN), kolom satuan, target tahunan (Awal, 2026 s/d 2030, Akhir), dan pagu anggaran.


- perhatikan tabel renstra_program,renstra_kegiatan ada perubahan field
- Tambah / Edit / Hapus (CRUD) pada Data Program / Kegiatan / Subkegiatan 
- Tambah kolom kinerja 
- Indikator pada tabel renstra_indikator_subkegiatan  adalah field uraisubkegiatan_indikator, target adalah field volume_0, volume_1, dst

Data Program / Kegiatan / Subkegiatan

- Tambahkan kolom perubahan target indikator Program / Kegiatan / Subkegiatan
- Tambahkan kolom perubahan pagu 


tambah kolom pagu  tahun 2026 - 2030 field pagu1 - pagu5

Aplikasi ini akan dideploy di https://monevrkpd.tegalkota.go.id/renstra
Apache reverse proxy


Dalam perumusan indikator kinerja, baik itu indikator tujuan, sasaran, program, kegiatan, dan subkegiatan harus memperhatikan Indikator kinerja SMART. Indikator kinerja SMART adalah ukuran atau kriteria yang digunakan untuk menentukan target atau tujuan kerja yang jelas, terstruktur, dan mudah dievaluasi.

Kepanjangan dan Arti SMART

• Specific (Spesifik): Tujuan harus jelas, rinci, dan tidak menimbulkan makna ganda (menjawab apa, siapa, di mana, dan mengapa).
• Measurable (Terukur): Target harus memiliki ukuran atau angka yang pasti agar progresnya bisa dipantau.
• Achievable / Attainable (Dapat Dicapai): Target bersifat realistis, dapat digapai berdasarkan kapasitas dan sumber daya yang ada.
• Relevant (Relevan): Tujuan harus sesuai dengan visi, misi, atau prioritas utama organisasi maupun individu.
• Time-Bound (Terikat Waktu): Memiliki batas waktu atau tenggat yang jelas kapan target tersebut harus mulai dan selesai dikerjakan.

tambahkan fitur AI Assistan untuk membantu / rekomendasi  dalam perumusan indikator kinerja,
berikan rekomendasi indikator kinerja yang SMART  berdasarkan inputan  uraian tujuan, sasaran, program, kegiatan, dan subkegiatan. pada Indikator Kegiatan, perhatikan data dibawah kegiatan yaitu subkegiatan dan indikator subkegiatan 
gunakan openai, api key di file .env


Buatkan Menu Laporan :
1. Tujuan dan Sasaran 
2. Cascading Kinerja 
3. Rencana Program, Kegiatan, Sub Kegiatan dan Pendanaan Perangkat Daerah
4. Indikator Kinerja Utama

Laporan hanya bisa export excel
sekarang buat laporan Tujuan dan sasaran dulu, layout seperti contoh gambar

Buat laporan 
Indikator Kinerja Utama
Nama Perangkat Daerah
No  | Tujuan /Sasaran | Indikator | Satuan  |  Target Tahun                               | 
                                            | 2025  | 2026  | 2027  | 2028 | 2029 | 2030 |


Pada entri Kegiatan, referensi dari database tabel ref_subkegiatan berdasasrkan kode_program diatasnya
Pada entri Sub Kegiatan, referensi dari database tabel ref_subkegiatan berdasasrkan kode_kegiatan diatasnya

Anda adalah pejabat pembuat komitmen pada pekerjaan pengembangan aplikasi SImlaba, rapikan dokumen KAK ini, lengkapi narasi yang belum lengkap,  sistematika sebagai berikut : A. RENCANA PENGEMBANGAN
B. METODE KERJA
C. LINGKUP KEGIATAN
D. KELUARAN KEGIATAN
E. KEBUTUHAN PERSONIL DAN PERALATAN
F. SUMBER PENDANAAN
G. PELAPORAN
M. JANGKA WAKTU PELAKSANAAN PEKERJAAN
N. P E N U T U P

output adalah file ms word docx


Pada Halaman Daftar Perangkat Daerah, tambahkan kolom Dokumen Perencanaan
tabel dokumen_perencanaan where id_ref_dokumen 64,65,66 


- [x] Backend: Model `DokumenPerencanaan` (`Backend/app/models/dokumen.py`) mapping ke tabel `dokumen_perencanaan`.
- [x] Backend: Schema `DokumenItem` dan penambahan list `dokumen` pada `OpdListItem` (`Backend/app/schemas/opd.py`).
- [x] Backend: Endpoint `GET /api/opd` memuat dokumen dengan `id_ref_dokumen IN (64, 65, 66)` dikelompokkan per OPD (relasi via `id_sub_pd` -> `ta_sub_pd.id_skpd` / `ta_opd.id_skpd`).
- [x] Backend: Endpoint streaming `GET /api/opd/dokumen/{doc_id}/download` untuk streaming/unduh berkas langsung dari server penyimpanan.
- [x] Link Dokumen disesuaikan langsung mengarah ke `https://monevrkpd.tegalkota.go.id/dokren/{link_gd}`.
- [x] Frontend: Kolom baru **DOKUMEN PERENCANAAN** pada tabel Daftar Perangkat Daerah (`Frontend/src/components/OpdTable.vue`).
- [x] Frontend: Badge interaktif per tahap:
  - **Penetapan** (id_ref_dokumen = 66, warna Emerald)
  - **Rankir** (id_ref_dokumen = 65, warna Biru/Indigo)
  - **Rancangan** (id_ref_dokumen = 64, warna Amber)
- [x] Frontend: Filter tombol baru "Ada Dokumen" pada toolbar pencarian.
- [x] Verifikasi build frontend & live test API.

Revisi kolom DOKUMEN PERENCANAAN
link nya ke https://monevrkpd.tegalkota.go.id/dokren/{link_gd}

Fitur Form Ubah Indikator (Copy Target Murni ke Target Perubahan)
- [x] Frontend: Tambah tombol `Salin dari Target Murni` pada section **Target Perubahan** di form indikator (`RenstraCrudModal.vue`).
- [x] Frontend: Tambah tombol `Salin ke Target Perubahan` pada section **Target Capaian Kinerja (Murni)** untuk kemudahan akses langsung.
- [x] Frontend: Otomatis memetakan nilai `target_awal` -> `p_target2025`, `target2026..target2030` -> `p_target2026..p_target2030`, dan `target_akhir` -> `p_target_akhir`.
- [x] Frontend: Menyetel status penandaan menjadi `Tetap (Tidak Ada Perubahan)` (`perubahan_status = 'tetap'`).
- [x] Frontend: Ditambahkan juga pada form Subkegiatan untuk tombol `Salin Volume Murni` ke Target Volume Perubahan.
- [x] Frontend: Terdapat indikator visual animasi sukses (*Target Murni Berhasil Disalin!*).
- [x] Verifikasi build frontend berhasil tanpa error.


Tambahkan Authentifikasi dengan FIrebase :
- [x] Inisialisasi Firebase SDK (`firebase/app`, `firebase/auth`, `firebase/analytics`) dengan konfigurasi `renstra-f461b` ([firebase.js](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/services/firebase.js)).
- [x] Modul reactive state autentikasi ([auth.js](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/services/auth.js)):
  - Google Sign-In via Popup (`signInWithPopup`).
  - Email & Password Login / Register (`signInWithEmailAndPassword`, `createUserWithEmailAndPassword`).
  - Sign Out (`signOut`).
  - Penerjemahan kode error Firebase ke pesan ramah bahasa Indonesia.
- [x] Komponen Modal Autentikasi Modern ([AuthModal.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/components/AuthModal.vue)):
  - Tab Masuk & Daftar Akun Baru.
  - Tombol masuk cepat dengan Akun Google (Google Branding resmi).
  - Form email & kata sandi dengan toggle intip password.
  - Tampilan profil pengguna (Avatar, Nama, Email, UID, Provider, Tombol Logout).
- [x] Integrasi Navbar ([HeaderNavbar.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/components/HeaderNavbar.vue)):
  - Tombol `Masuk` di navbar saat belum login.
  - Badge profil mini (Avatar + Nama + Status Online) saat terautentikasi.
- [x] Build frontend dan verifikasi inisialisasi Firebase berjalan 100% sukses.

Authenfikasi di awal sebelum membuka data 
- [x] Halaman Login dedicated ([LoginView.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/views/LoginView.vue)):
  - Antarmuka eksekutif khas Pemerintah Kota Tegal (Banner Area Terbatas & Keamanan Perencanaan).
  - Opsi masuk dengan Akun Google (sekali klik) atau Email & Kata Sandi.
  - Tab pendaftaran akun baru.
- [x] Global Router Auth Navigation Guard ([router/index.js](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/router/index.js)):
  - Menggunakan `waitForAuthInit()` untuk menunggu pemulihan token sesi Firebase.
  - Jika pengguna belum terautentikasi, otomatis dialihkan (*redirect*) ke `/login?redirect=...`.
  - Jika pengguna sudah terautentikasi dan mengakses `/login`, otomatis diarahkan ke halaman utama `/`.
- [x] Proteksi Menu Navbar ([HeaderNavbar.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/components/HeaderNavbar.vue)):
  - Menu navigasi "Data RENSTRA" dan dropdown "Laporan" disembunyikan sampai pengguna berhasil masuk.
  - Logout otomatis mengarahkan kembali ke `/login`.
- [x] Verifikasi build frontend berhasil tanpa error.


Revisi Halaman Login,hanya login dengan google saja, hapus form login 
- [x] Halaman Login ([LoginView.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/views/LoginView.vue)):
  - Menghapus seluruh input form email, kata sandi, dan tab pendaftaran.
  - Menampilkan satu tombol utama berukuran besar **"Masuk dengan Akun Google"** dengan ikon resmi Google SVG dan indikator loading.
  - Tetap mempertahankan identitas resmi Pemerintah Kota Tegal (lambang perisai, banner area terbatas, dan jaminan keamanan resmi Firebase).
- [x] Modal Autentikasi ([AuthModal.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/components/AuthModal.vue)):
  - Disesuaikan sehingga saat belum login, modal hanya menampilkan tombol **"Masuk dengan Akun Google"** tanpa form email/password.
- [x] Pengujian build frontend Vite berhasil 100% tanpa error.
- [x] Halaman Login ([LoginView.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/views/LoginView.vue)):
  - Menghapus seluruh input form email, kata sandi, dan tab pendaftaran.
  - Menampilkan satu tombol utama berukuran besar **"Masuk dengan Akun Google"** dengan ikon resmi Google SVG dan indikator loading.
  - Tetap mempertahankan identitas resmi Pemerintah Kota Tegal (lambang perisai, banner area terbatas, dan jaminan keamanan resmi Firebase).
- [x] Modal Autentikasi ([AuthModal.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/components/AuthModal.vue)):
  - Disesuaikan sehingga saat belum login, modal hanya menampilkan tombol **"Masuk dengan Akun Google"** tanpa form email/password.
- [x] Pengujian build frontend Vite berhasil 100% tanpa error.

Buat Laporan :
  6. Daftar IKU Perangkat Daerah
  Perangkat Daerah | Tujuan / Sasaran |  INDIKATOR | Target Murni | Target Perubahan

- [x] Backend Service: Menambahkan fungsi `get_daftar_iku_report_data` dan `generate_daftar_iku_excel` pada `Backend/app/services/laporan_service.py`:
  - Query union seluruh Indikator Tujuan dan Indikator Sasaran bertanda `iku = '1'` (Total 92 IKU dari 29 Perangkat Daerah se-Kota Tegal).
  - Format Target Murni (2025 s.d. 2030 & Target Akhir) dan Target Perubahan (2025 s.d. 2030 & Target Akhir).
  - Generator Excel openpyxl dengan format styling dinas (Title block, merge header, zebra rows, border sel, auto-width kolom).
- [x] Backend Endpoints: Menambahkan route `GET /api/laporan/daftar-iku` dan `GET /api/laporan/daftar-iku/export-excel` pada `Backend/app/api/endpoints/laporan.py`.
- [x] Frontend API: Menambahkan fungsi `getLaporanDaftarIku`, `getLaporanDaftarIkuExcelUrl`, dan `downloadLaporanDaftarIkuExcel` pada `Frontend/src/services/api.js`.
- [x] Frontend View ([DaftarIkuReportView.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/views/DaftarIkuReportView.vue)):
  - Halaman laporan interaktif dengan struktur kolom resmi:
    `No | Perangkat Daerah | Tujuan / Sasaran | INDIKATOR (IKU) | Satuan | Target Murni | Target Perubahan | Status`
  - Grouping dan merge Perangkat Daerah rapi untuk seluruh indikator di bawah OPD terkait.
  - Mode Tampilan Fleksibel:
    - Mode **Semua Tahun (2025 - 2030)**: Menampilkan sub-kolom tahun 2025 s.d. 2030 & Akhir untuk Target Murni dan Target Perubahan.
    - Mode **Fokus 1 Tahun (misal: Tahun Berjalan 2026)**: Tampilan ringkas 1 kolom Target Murni dan 1 kolom Target Perubahan untuk tahun terpilih.
  - Fitur Filter Perangkat Daerah (Semua OPD atau pilih OPD tertentu).
  - Fitur Pencarian Cepat (*Live Search*) lintas OPD, Tujuan/Sasaran, atau nama Indikator.
  - Kartu statistik jumlah OPD, total IKU (92 Indikator), rincian IKU Tujuan & IKU Sasaran.
  - Tombol **Export Excel (.xlsx)** dengan indikator proses unduh.
- [x] Frontend Router & Navigasi:
  - Mendaftarkan rute `/laporan/daftar-iku` pada [router/index.js](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/router/index.js).
  - Menambahkan menu **6. Daftar IKU Perangkat Daerah** pada dropdown laporan [HeaderNavbar.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/components/HeaderNavbar.vue).
- [x] Verifikasi build frontend berhasil tanpa error (`built in 987ms`).


Revisi Laporan Daftar IKU Perangkat Daerah
Perangkat Daerah diurut by kode perangkat daerah
- [x] Backend Service ([laporan_service.py](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Backend/app/services/laporan_service.py)):
  - Memperbarui query SQL untuk mengurutkan `ORDER BY kode_skpd, level DESC, no_urut, urut, tujuan_sasaran, indikator`.
  - Mengurutkan `opd_groups` menggunakan `key=lambda x: x["kode_skpd"]` sehingga urutan Perangkat Daerah konsisten mengikuti hierarki kode Permendagri/SIPD (mulai dari 1.01 Dinas Pendidikan, 1.02 Dinas Kesehatan, dst.).
  - Memperbarui generator Excel untuk menyertakan `[kode_opd]` pada kolom Perangkat Daerah.
- [x] Frontend View ([DaftarIkuReportView.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/views/DaftarIkuReportView.vue)):
  - Memperbarui dropdown pilihan OPD menampilkan `kode_skpd` (`1.01.2.22.0.00.01.0000 - Dinas Pendidikan dan Kebudayaan`).
  - Menampilkan badge `kode_skpd` di bawah nama Perangkat Daerah pada tabel laporan.
  - Memastikan `availableOpds` dan `filteredGroupedOpds` diurutkan secara ascending berdasarkan `kode_skpd`.
- [x] Verifikasi API endpoint dan build frontend Vite berhasil tanpa error.

Form Subkegiatan: Field Pagu Murni dan Perubahan
- [x] Frontend Component Modal ([RenstraCrudModal.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/components/RenstraCrudModal.vue)):
  - Menambahkan section form **Alokasi Pagu Anggaran Subkegiatan**:
    - **Pagu Indikatif (Murni)**: Input tahun 2026 (`pagu1`), 2027 (`pagu2`), 2028 (`pagu3`), 2029 (`pagu4`), 2030 (`pagu5`), lengkap dengan pratinjau teks format Rupiah (`Rp ...`) dan perhitungan otomatis Total Pagu Murni.
    - **Pagu Anggaran Perubahan**: Input tahun 2026 (`p_pagu1`), 2027 (`p_pagu2`), 2028 (`p_pagu3`), 2029 (`p_pagu4`), 2030 (`p_pagu5`), lengkap dengan pratinjau teks format Rupiah (`Rp ...`) dan perhitungan otomatis Total Pagu Perubahan.
  - Tombol **Salin Pagu Murni ke Perubahan** sekali klik untuk menyalin nilai `pagu1..pagu5` ke `p_pagu1..p_pagu5` jika tidak ada perubahan anggaran.
  - Mengintegrasikan pengiriman payload `pagu1..pagu5` dan `p_pagu1..p_pagu5` pada `api.createSubkegiatan` dan `api.updateSubkegiatan`.
- [x] Frontend View ([OpdRenstraView.vue](file:///home/herry/1_Project/2026/RENSTRA_PERUBAHAN/Frontend/src/views/OpdRenstraView.vue)):
  - Memastikan modal Ubah Subkegiatan menerima data `pagu1..pagu5` dan `p_pagu1..p_pagu5` baik dari object subkegiatan maupun indikator subkegiatan.
- [x] Verifikasi test API endpoint PUT `/api/renstra/subkegiatan/{id}` dan build frontend Vite berhasil tanpa error (`built in 840ms`).




Buat Laporan :
7. Pagu RPJMD vs Renstra dengan query :
SELECT
    o.id_skpd,
    o.kode_skpd,
    o.nama_skpd,
    s.kodeprogram,
    p.uraiprogram,

    s.pagu1, s.pagu2, s.pagu3, s.pagu4, s.pagu5,
    s.p_pagu1, s.p_pagu2, s.p_pagu3, s.p_pagu4, s.p_pagu5,

    rj.t1, rj.t2, rj.t3, rj.t4, rj.t5

FROM (
    SELECT
        kodeskpd,
        kodeprogram,
        SUM(pagu1) AS pagu1,
        SUM(pagu2) AS pagu2,
        SUM(pagu3) AS pagu3,
        SUM(pagu4) AS pagu4,
        SUM(pagu5) AS pagu5,
        SUM(p_pagu1) AS p_pagu1,
        SUM(p_pagu2) AS p_pagu2,
        SUM(p_pagu3) AS p_pagu3,
        SUM(p_pagu4) AS p_pagu4,
        SUM(p_pagu5) AS p_pagu5
    FROM public.renstra_subkegiatan
    GROUP BY kodeskpd, kodeprogram
) s

JOIN public.renstra_program p
    ON p.kodeskpd = s.kodeskpd
   AND p.kodeprogram = s.kodeprogram

JOIN public.ta_sub_pd spd
    ON spd.kode_sub_skpd = s.kodeskpd

JOIN public.ta_opd o
    ON o.id_skpd = spd.id_skpd

JOIN public.rpjmd_program rj
    ON rj.id_pd = o.id_skpd
   AND rj.kodeprogram = s.kodeprogram
   ORDER BY o.kode_skpd, p.kodeprogram;

   pagu1 - pagu5 = pagu  murni
   p_pagu1 - p_pagu5 = pagu perubahan
   t1 - t5 = pagu rpjmd

   jika pagu perubahan tidak sama dengan RPJMD tandai 


### Status Laporan 7: Pagu RPJMD vs Renstra
- [x] Query SQL dieksekusi dan diverifikasi pada database (283 baris program, 138 program terdeteksi ada selisih antara Pagu Perubahan dan RPJMD).
- [x] Backend service `get_rpjmd_vs_renstra_report_data` dan `generate_rpjmd_vs_renstra_excel` di `Backend/app/services/laporan_service.py`.
- [x] Endpoint API:
  - `GET /api/laporan/rpjmd-vs-renstra`: Mengembalikan ringkasan KPI (total program, program selisih, program sesuai, grand total pagu murni, perubahan, RPJMD, selisih) dan daftar program per OPD.
  - `GET /api/laporan/rpjmd-vs-renstra/export-excel`: Menghasilkan file Excel terformat rapi dengan penandaan warna (kuning/merah) pada pagu yang tidak sama dengan RPJMD, rumus SUM otomatis, dan format Rupiah.
- [x] Integrasi API di `Frontend/src/services/api.js`.
- [x] Antarmuka Frontend `Frontend/src/views/RpjmdVsRenstraReportView.vue`:
  - Kartu KPI ringkasan: Total Program, Selisih (Tidak Sama), Sesuai RPJMD, dan Total Pagu.
  - Filter interaktif: Filter OPD, Filter Status Kesesuaian (Semua / Hanya Selisih / Hanya Sesuai), Tampilan Tahun (Semua Tahun 2026-2030 atau per tahun), dan live search.
  - Penandaan selisih: Baris dan sel yang tidak sama dengan RPJMD ditandai dengan badge peringatan merah/kuning dan indikator selisih.
  - Fitur Export Excel (.xlsx).
- [x] Route `/laporan/rpjmd-vs-renstra` di `Frontend/src/router/index.js` dan menu dropdown "7. Pagu RPJMD vs Renstra" pada `Frontend/src/components/HeaderNavbar.vue`.
- [x] Kompilasi frontend build `npm run build` sukses 100%.
