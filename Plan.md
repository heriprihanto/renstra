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


Data Tujuan, Sasaran, Indikator tidak bisa dihapus atau edit kalimatnya, yang bisa diedit hanya metadata dan TARGET PERUBAHAN:
- [x] Larangan Penghapusan (Delete Protection):
  - Backend API: Endpoint DELETE `/renstra/tujuan/{id}`, `/renstra/sasaran/{id}`, `/renstra/indikator-tujuan/{id}`, dan `/renstra/indikator-sasaran/{id}` diblokir secara mutlak dan mengembalikan status HTTP 403 Forbidden.
  - Frontend UI: Semua opsi dan tombol aksi "Hapus" (Hapus Tujuan, Hapus Sasaran, Hapus Indikator) dihapus sepenuhnya dari tabel cascading.
- [x] Perlindungan Kalimat Rumusan (Sentence Immutability):
  - Backend API: Pada operasi PUT (update), field uraian kalimat (`uraitujuan`, `uraisasaran`, `uraitujuan_indikator`, `uraisasaran_indikator`) tidak ditimpa/dipertahankan dari database.
  - Frontend UI: Textarea uraian kalimat pada form edit ditandai terkunci (`readonly`, `disabled`), dilengkapi badge `🔒 Kalimat Terkunci` dan pesan penjelasan bahwa rumusan kalimat tidak dapat diubah pada RENSTRA Perubahan.
- [x] Perlindungan Target Murni (Target Murni Immutability):
  - Backend API: Target capaian murni (`target_awal`, `target1` s/d `target5`) terkunci dan tidak dapat diubah melalui endpoint update.
  - Frontend UI: Seluruh input Target Murni pada modal edit ditandai terkunci (`readonly`, `disabled`) dengan badge `🔒 Terkunci`.
- [x] Hak Edit Terbuka (Metadata & Target Perubahan):
  - Yang dapat diedit secara penuh:
    - Metadata: Satuan, Status (positif/negatif/akumulatif), IKU (Indikator Kinerja Utama checkbox), Definisi Operasional / Metadata, Nomor Urut, dan Penandaan Status Perubahan.
    - Target Perubahan: Tahun 2025, 2026, 2027, 2028, 2029, 2030, dan Target Akhir Perubahan.
  - Tombol aksi indikator pada tabel cascading diubah menjadi tombol langsung yang ringkas: `Ubah Target` (membuka form penyesuaian target perubahan & metadata).

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
