<template>
  <div class="report-page-container">
    <div class="app-container">
      <!-- Toolbar & Controls -->
      <div class="report-toolbar-card">
        <div class="toolbar-left">
          <button type="button" class="btn-toolbar-back" @click="goBack" title="Kembali">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span>Kembali</span>
          </button>
          <div class="toolbar-title-wrap">
            <div class="report-badge-pill">Laporan Evaluasi Renstra</div>
            <h2 class="report-main-title">Evaluasi Hasil Renstra Perangkat Daerah</h2>
          </div>
        </div>

        <div class="toolbar-controls">
          <!-- OPD Selector -->
          <div class="control-group">
            <label class="control-label">Perangkat Daerah:</label>
            <select
              class="control-select opd-select"
              v-model="selectedOpdId"
              @change="onOpdChange"
              :disabled="loading"
            >
              <option v-for="opd in opdList" :key="opd.id_skpd" :value="opd.id_skpd">
                {{ opd.nama_skpd }}
              </option>
            </select>
          </div>

          <!-- Sub SKPD Selector -->
          <div v-if="subUnitList.length > 0" class="control-group">
            <label class="control-label">Unit Kerja:</label>
            <select
              class="control-select"
              v-model="selectedSubSkpdId"
              @change="fetchReport"
              :disabled="loading"
            >
              <option :value="null">-- Semua Unit Kerja --</option>
              <option v-for="sub in subUnitList" :key="sub.id_sub_skpd" :value="sub.id_sub_skpd">
                {{ sub.nama_sub_skpd }}
              </option>
            </select>
          </div>

          <!-- Tipe Target Filter -->
          <div class="control-group">
            <label class="control-label">Tipe Target:</label>
            <div class="target-toggle-group">
              <button
                type="button"
                class="btn-toggle-type"
                :class="{ active: tipeTarget === 'murni' }"
                @click="setTipeTarget('murni')"
              >
                Murni
              </button>
              <button
                type="button"
                class="btn-toggle-type"
                :class="{ active: tipeTarget === 'perubahan' }"
                @click="setTipeTarget('perubahan')"
              >
                Perubahan
              </button>
            </div>
          </div>

          <!-- Export Excel Button -->
          <div class="control-group" style="justify-content: flex-end;">
            <button
              type="button"
              class="btn-export-excel"
              :disabled="loading || exporting || !reportData"
              @click="handleExportExcel"
              title="Unduh Formulir Evaluasi Renstra dalam Format Microsoft Excel (.xlsx)"
            >
              <svg v-if="!exporting" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="8" y1="13" x2="16" y2="13"/>
                <line x1="8" y1="17" x2="16" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              <svg v-else class="spin-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
              <span>{{ exporting ? 'Mengunduh...' : 'Export Excel (.xlsx)' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="report-loading-card">
        <div class="spinner-civic"></div>
        <p>Memuat Laporan Evaluasi Hasil Renstra...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="report-error-card">
        <p>{{ error }}</p>
        <button type="button" class="btn-retry" @click="fetchReport">Muat Ulang</button>
      </div>

      <!-- Document Sheet Preview Container -->
      <div v-else-if="reportData" class="document-sheet-container">
        <!-- Sheet Header Title Block -->
        <div class="sheet-title-block">
          <h3 class="sheet-title-heading">
            EVALUASI HASIL RENCANA STRATEGIS PERANGKAT DAERAH (RENSTRA)
          </h3>
          <h4 class="sheet-title-subheading">
            {{ reportData.opd.nama_skpd }}
            <span v-if="reportData.opd.sub_title"> - {{ reportData.opd.sub_title }}</span>
          </h4>
          <h5 class="sheet-title-city">KOTA TEGAL</h5>
          <div class="sheet-title-meta">
            <span class="badge-target-type">Mode Target: {{ tipeTarget.toUpperCase() }}</span>
          </div>
        </div>

        <!-- Quick Summary Metrics Bar -->
        <div class="summary-metrics-bar">
          <div class="metric-chip">
            <span class="metric-label">Sasaran</span>
            <span class="metric-val text-sas">{{ reportData.summary?.total_sasaran || 0 }}</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">Program</span>
            <span class="metric-val text-prog">{{ reportData.summary?.total_program || 0 }}</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">Kegiatan</span>
            <span class="metric-val text-keg">{{ reportData.summary?.total_kegiatan || 0 }}</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">Sub Kegiatan</span>
            <span class="metric-val text-sub">{{ reportData.summary?.total_subkegiatan || 0 }}</span>
          </div>
          <div class="metric-chip eval-chip">
            <span class="metric-label">Rata-rata Capaian</span>
            <span class="metric-val text-rate">
              {{ reportData.summary?.rata_rata_capaian !== null && reportData.summary?.rata_rata_capaian !== undefined ? reportData.summary?.rata_rata_capaian + '%' : '-' }}
            </span>
          </div>
          <div class="metric-chip predikat-chip">
            <span class="metric-label">Predikat Kinerja</span>
            <span class="badge-predikat" :class="getPredikatClass(reportData.summary?.predikat_kinerja)">
              {{ reportData.summary?.predikat_kinerja || '-' }}
            </span>
          </div>
        </div>

        <!-- Table Wrapper with Horizontal Scroll (38 Columns) -->
        <div class="sheet-table-scroll-wrap">
          <table class="table-evaluasi">
            <thead>
              <!-- Header Row 1: Merged Main Labels -->
              <tr class="header-row-1">
                <th rowspan="3" class="col-kode">No</th>
                <th rowspan="3" class="col-sasaran">Sasaran</th>
                <th rowspan="3" class="col-progkeg">Program/Kegiatan/<br>Sub Kegiatan</th>
                <th rowspan="3" class="col-indikator">Indikator Kinerja</th>
                <th rowspan="2" class="col-awal">Data Capaian Pada Awal Tahun</th>
                <th colspan="2" class="col-akhir">Target Capaian pada Akhir Tahun</th>
                <th colspan="10" class="col-target-th">Target Renstra Perangkat Daerah kabupaten/kota Tahun ke-</th>
                <th colspan="10" class="col-real-th">Realisasi Capaian Tahun ke-</th>
                <th colspan="10" class="col-rasio-th">Rasio Capaian pada Tahun ke-</th>
                <th rowspan="3" class="col-unit">Unit Penang- gung Jawab</th>
              </tr>

              <!-- Header Row 2: Perencanaan & Sub Labels -->
              <tr class="header-row-2">
                <th colspan="2" class="col-akhir-sub">Perencanaan</th>
                <th colspan="2" class="year-hdr">1</th>
                <th colspan="2" class="year-hdr">2</th>
                <th colspan="2" class="year-hdr">3</th>
                <th colspan="2" class="year-hdr">4</th>
                <th colspan="2" class="year-hdr">5</th>
                <th colspan="2" class="year-hdr">1</th>
                <th colspan="2" class="year-hdr">2</th>
                <th colspan="2" class="year-hdr">3</th>
                <th colspan="2" class="year-hdr">4</th>
                <th colspan="2" class="year-hdr">5</th>
                <th colspan="2" class="year-hdr">1</th>
                <th colspan="2" class="year-hdr">2</th>
                <th colspan="2" class="year-hdr">3</th>
                <th colspan="2" class="year-hdr">4</th>
                <th colspan="2" class="year-hdr">5</th>
              </tr>

              <!-- Header Row 3: K & Rp Subheaders -->
              <tr class="header-row-3">
                <th class="sub-hdr">Perencanaan</th>
                <th class="sub-krp">K</th>
                <th class="sub-krp">Rp</th>
                <!-- Target 1..5 -->
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <!-- Realisasi 1..5 -->
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <!-- Rasio 1..5 -->
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
                <th class="sub-krp">K</th><th class="sub-krp">Rp</th>
              </tr>

              <!-- Header Row 4: Column Numbering Guide (-1 s/d -22) -->
              <tr class="header-guide-row">
                <th class="guide-num">(1)</th>
                <th class="guide-num">(2)</th>
                <th class="guide-num">(3)</th>
                <th class="guide-num">(4)</th>
                <th class="guide-num">(5)</th>
                <th colspan="2" class="guide-num">(6)</th>
                <th colspan="2" class="guide-num">(7)</th>
                <th colspan="2" class="guide-num">(8)</th>
                <th colspan="2" class="guide-num">(9)</th>
                <th colspan="2" class="guide-num">(10)</th>
                <th colspan="2" class="guide-num">(11)</th>
                <th colspan="2" class="guide-num">(12)</th>
                <th colspan="2" class="guide-num">(13)</th>
                <th colspan="2" class="guide-num">(14)</th>
                <th colspan="2" class="guide-num">(15)</th>
                <th colspan="2" class="guide-num">(16)</th>
                <th colspan="2" class="guide-num">(17)</th>
                <th colspan="2" class="guide-num">(18)</th>
                <th colspan="2" class="guide-num">(19)</th>
                <th colspan="2" class="guide-num">(20)</th>
                <th colspan="2" class="guide-num">(21)</th>
                <th class="guide-num">(22)</th>
              </tr>
            </thead>

            <tbody>
              <!-- Empty State -->
              <tr v-if="!reportData.rows || reportData.rows.length === 0">
                <td colspan="38" class="empty-sheet-cell">
                  Tidak ada data evaluasi Renstra untuk Perangkat Daerah ini.
                </td>
              </tr>

              <!-- Iteration over Evaluation Rows -->
              <tr
                v-for="(row, rIdx) in reportData.rows"
                :key="'eval-r-' + rIdx"
                :class="getRowClass(row.level)"
              >
                <!-- 1. No / Kode -->
                <td class="cell-kode">{{ row.no }}</td>
                <!-- 2. Sasaran -->
                <td class="cell-sasaran">{{ row.sasaran }}</td>
                <!-- 3. Program/Kegiatan -->
                <td class="cell-progkeg">{{ row.program_kegiatan }}</td>
                <!-- 4. Indikator Kinerja -->
                <td class="cell-indikator">{{ row.indikator }}</td>
                <!-- 5. Awal Tahun -->
                <td class="cell-center">{{ row.awal }}</td>
                <!-- 6 & 7. Akhir Tahun (K & Rp) -->
                <td class="cell-center">{{ row.akhir_k }}</td>
                <td class="cell-pagu">{{ formatRupiah(row.akhir_rp) }}</td>

                <!-- 8-17. Target Tahun 1-5 (K & Rp) -->
                <template v-for="y in ['1', '2', '3', '4', '5']" :key="'tgt-' + y">
                  <td class="cell-center">{{ row.tahun_targets?.[y]?.k || '-' }}</td>
                  <td class="cell-pagu">{{ formatRupiah(row.tahun_targets?.[y]?.rp) }}</td>
                </template>

                <!-- 18-27. Realisasi Tahun 1-5 (K & Rp) -->
                <template v-for="y in ['1', '2', '3', '4', '5']" :key="'real-' + y">
                  <td class="cell-center">{{ row.tahun_realisasi?.[y]?.k || '-' }}</td>
                  <td class="cell-pagu">{{ formatRupiah(row.tahun_realisasi?.[y]?.rp) }}</td>
                </template>

                <!-- 28-37. Rasio Tahun 1-5 (K & Rp) -->
                <template v-for="y in ['1', '2', '3', '4', '5']" :key="'rasio-' + y">
                  <td class="cell-center" :class="getRasioHighlight(row.tahun_rasio?.[y]?.k)">
                    {{ formatRasio(row.tahun_rasio?.[y]?.k) }}
                  </td>
                  <td class="cell-center" :class="getRasioHighlight(row.tahun_rasio?.[y]?.rp)">
                    {{ formatRasio(row.tahun_rasio?.[y]?.rp) }}
                  </td>
                </template>

                <!-- 38. Unit Penanggung Jawab -->
                <td class="cell-unit">{{ row.unit_pj || '-' }}</td>
              </tr>

              <!-- Footer Section (matching user CSV) -->
              <tr class="row-footer-header">
                <td colspan="4" class="footer-label-bold">Rata-rata capaian kinerja (%)</td>
                <td colspan="34" class="footer-val">
                  {{ reportData.summary?.rata_rata_capaian !== null && reportData.summary?.rata_rata_capaian !== undefined ? reportData.summary?.rata_rata_capaian + '%' : '-' }}
                </td>
              </tr>
              <tr class="row-footer-header">
                <td colspan="4" class="footer-label-bold">Predikat kinerja</td>
                <td colspan="34" class="footer-val font-semibold">
                  {{ reportData.summary?.predikat_kinerja || '-' }}
                </td>
              </tr>
              <tr class="row-footer-header">
                <td colspan="4" class="footer-label-bold">Faktor pendorong pencapaian kinerja:</td>
                <td colspan="34" class="footer-val">{{ reportData.summary?.faktor_pendorong || '-' }}</td>
              </tr>
              <tr class="row-footer-header">
                <td colspan="4" class="footer-label-bold">Faktor penghambat:</td>
                <td colspan="34" class="footer-val">{{ reportData.summary?.faktor_penghambat || '-' }}</td>
              </tr>
              <tr class="row-footer-header">
                <td colspan="4" class="footer-label-bold">Usulan tindak lanjut pada Renja Perangkat Daerah kabupaten/kota berikutnya:</td>
                <td colspan="34" class="footer-val">{{ reportData.summary?.usulan_renja || '-' }}</td>
              </tr>
              <tr class="row-footer-header">
                <td colspan="4" class="footer-label-bold">Usulan tindak lanjut pada Renstra Perangkat Daerah kabupaten/kota berikutnya:</td>
                <td colspan="34" class="footer-val">{{ reportData.summary?.usulan_renstra || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'EvaluasiRenstraReportView',
  data() {
    return {
      opdList: [],
      subUnitList: [],
      selectedOpdId: null,
      selectedSubSkpdId: null,
      tipeTarget: 'murni',
      reportData: null,
      loading: false,
      exporting: false,
      error: null,
    };
  },
  async created() {
    await this.fetchOpdList();
    const routeId = this.$route.params.id;
    if (routeId) {
      this.selectedOpdId = parseInt(routeId, 10);
    } else if (this.opdList.length > 0) {
      this.selectedOpdId = this.opdList[0].id_skpd;
    }

    if (this.selectedOpdId) {
      await this.loadSubUnits();
      await this.fetchReport();
    }
  },
  methods: {
    goBack() {
      if (this.selectedOpdId) {
        this.$router.push(`/opd/${this.selectedOpdId}`);
      } else {
        this.$router.push('/');
      }
    },
    async fetchOpdList() {
      try {
        this.opdList = await api.getLaporanOpdList();
      } catch (err) {
        console.error('Error fetching OPD list for report:', err);
      }
    },
    async loadSubUnits() {
      this.subUnitList = [];
      this.selectedSubSkpdId = null;
      if (!this.selectedOpdId) return;
      try {
        const subs = await api.getSubPd(this.selectedOpdId);
        if (Array.isArray(subs) && subs.length > 1) {
          this.subUnitList = subs;
        }
      } catch (err) {
        console.warn('Could not fetch sub units:', err);
      }
    },
    async onOpdChange() {
      if (this.selectedOpdId) {
        this.$router.replace({ path: `/laporan/evaluasi-renstra/${this.selectedOpdId}` });
        await this.loadSubUnits();
        await this.fetchReport();
      }
    },
    setTipeTarget(tipe) {
      if (this.tipeTarget === tipe) return;
      this.tipeTarget = tipe;
      this.fetchReport();
    },
    async fetchReport() {
      if (!this.selectedOpdId) return;
      this.loading = true;
      this.error = null;
      try {
        const data = await api.getLaporanEvaluasiRenstra(this.selectedOpdId, {
          idSubSkpd: this.selectedSubSkpdId,
          tipe: this.tipeTarget,
        });
        this.reportData = data;
      } catch (err) {
        this.error = err.message || 'Gagal memuat laporan Evaluasi Hasil Renstra.';
        console.error('Error fetching evaluasi renstra report:', err);
      } finally {
        this.loading = false;
      }
    },
    async handleExportExcel() {
      if (!this.selectedOpdId || this.exporting) return;
      this.exporting = true;
      try {
        await api.downloadLaporanEvaluasiRenstraExcel(this.selectedOpdId, {
          idSubSkpd: this.selectedSubSkpdId,
          tipe: this.tipeTarget,
        });
      } catch (err) {
        alert('Gagal mengunduh file Excel: ' + (err.message || 'Error'));
      } finally {
        this.exporting = false;
      }
    },
    getRowClass(level) {
      if (level === 'sub_unit') return 'row-sub-unit';
      if (level === 'sasaran') return 'row-sasaran';
      if (level === 'program') return 'row-program';
      if (level === 'kegiatan') return 'row-kegiatan';
      if (level === 'subkegiatan') return 'row-subkegiatan';
      return '';
    },
    getPredikatClass(predikat) {
      if (!predikat) return '';
      if (predikat === 'Sangat Tinggi') return 'pred-st';
      if (predikat === 'Tinggi') return 'pred-t';
      if (predikat === 'Sedang') return 'pred-s';
      if (predikat === 'Rendah') return 'pred-r';
      if (predikat === 'Sangat Rendah') return 'pred-sr';
      return '';
    },
    getRasioHighlight(val) {
      if (val === null || val === undefined || val === '-') return '';
      const num = Number(val);
      if (isNaN(num)) return '';
      if (num >= 90) return 'text-success-bold';
      if (num < 50) return 'text-danger-bold';
      return '';
    },
    formatRasio(val) {
      if (val === null || val === undefined || val === '' || val === '-') return '-';
      const num = Number(val);
      if (isNaN(num)) return '-';
      return num.toFixed(2) + '%';
    },
    formatRupiah(val) {
      if (val === null || val === undefined || val === '' || val === 0) return '-';
      const num = Number(val);
      if (isNaN(num) || num === 0) return '-';
      return num.toLocaleString('id-ID');
    },
  },
};
</script>

<style scoped>
.report-page-container {
  padding: 1.5rem 0 3rem 0;
  min-height: calc(100vh - 70px);
  background: #f8fafc;
}

.report-toolbar-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 992px) {
  .report-toolbar-card {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-toolbar-back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-toolbar-back:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #0f172a;
}

.toolbar-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.report-badge-pill {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  color: #1d4ed8;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  width: fit-content;
}

.report-main-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.toolbar-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-label {
  font-size: 0.825rem;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}

.control-select {
  padding: 0.45rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  font-size: 0.85rem;
  color: #1e293b;
  outline: none;
  transition: border-color 0.15s;
}

.control-select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.opd-select {
  max-width: 280px;
}

.target-toggle-group {
  display: inline-flex;
  border-radius: 8px;
  background: #e2e8f0;
  padding: 2px;
}

.btn-toggle-type {
  padding: 0.35rem 0.75rem;
  border: none;
  background: transparent;
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-toggle-type.active {
  background: #ffffff;
  color: #1e293b;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn-export-excel {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.1rem;
  border-radius: 8px;
  background: #107c41;
  color: #ffffff;
  border: none;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(16, 124, 65, 0.2);
  transition: all 0.2s;
}

.btn-export-excel:hover:not(:disabled) {
  background: #0d6535;
  box-shadow: 0 4px 8px rgba(16, 124, 65, 0.3);
}

.btn-export-excel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.report-loading-card,
.report-error-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 3rem 2rem;
  text-align: center;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner-civic {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.btn-retry {
  padding: 0.5rem 1.25rem;
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

/* Document Sheet */
.document-sheet-container {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 2rem 1.5rem;
  overflow: hidden;
}

.sheet-title-block {
  text-align: center;
  margin-bottom: 1.5rem;
}

.sheet-title-heading {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0.25rem 0;
}

.sheet-title-subheading {
  font-size: 1.1rem;
  font-weight: 700;
  color: #334155;
  margin: 0.2rem 0;
}

.sheet-title-city {
  font-size: 1rem;
  font-weight: 700;
  color: #475569;
  margin: 0;
}

.sheet-title-meta {
  margin-top: 0.5rem;
}

.badge-target-type {
  font-size: 0.75rem;
  font-weight: 700;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  color: #475569;
}

/* Summary Metrics Bar */
.summary-metrics-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.metric-chip {
  display: flex;
  flex-direction: column;
  padding: 0.25rem 0.75rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.metric-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
}

.metric-val {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0f172a;
}

.text-sas { color: #854d0e; }
.text-prog { color: #b45309; }
.text-keg { color: #15803d; }
.text-sub { color: #2563eb; }

.eval-chip {
  margin-left: auto;
  background: #eff6ff;
  border-color: #bfdbfe;
}
.text-rate {
  color: #1d4ed8;
}

.badge-predikat {
  font-size: 0.85rem;
  font-weight: 700;
  padding: 0.15rem 0.6rem;
  border-radius: 6px;
  width: fit-content;
  margin-top: 2px;
}
.pred-st { background: #dcfce7; color: #15803d; }
.pred-t { background: #e0f2fe; color: #0369a1; }
.pred-s { background: #fef9c3; color: #854d0e; }
.pred-r { background: #fee2e2; color: #b91c1c; }
.pred-sr { background: #f3e8ff; color: #7e22ce; }

/* Table 38 Columns */
.sheet-table-scroll-wrap {
  overflow-x: auto;
  border: 1px solid #000000;
}

.table-evaluasi {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 11px;
  color: #000000;
  background: #ffffff;
  white-space: normal;
}

.table-evaluasi th,
.table-evaluasi td {
  border: 1px solid #000000;
  padding: 5px 6px;
  line-height: 1.25;
}

/* Header Styling */
.header-row-1 th,
.header-row-2 th,
.header-row-3 th,
.header-guide-row th {
  background-color: #B4C6E7;
  color: #000000;
  font-weight: 700;
  text-align: center;
  vertical-align: middle;
}

.col-kode { min-width: 130px; width: 130px; }
.col-sasaran { min-width: 220px; max-width: 280px; }
.col-progkeg { min-width: 240px; max-width: 300px; }
.col-indikator { min-width: 220px; max-width: 280px; }
.col-awal { width: 90px; }
.col-akhir { width: 180px; }
.col-target-th, .col-real-th, .col-rasio-th { min-width: 800px; }
.col-unit { min-width: 180px; max-width: 240px; }

.year-hdr { font-size: 10.5px; width: 85px; }
.sub-krp { width: 45px; font-size: 10px; }

.header-guide-row th {
  background-color: #D9E1F2;
  font-size: 9.5px;
  font-weight: 600;
  padding: 2px 4px;
}

/* Row Coloring */
.row-sub-unit {
  background-color: #BDD7EE !important;
  font-weight: 800;
}
.row-sub-unit td {
  background-color: #BDD7EE !important;
  color: #0f172a;
  font-weight: 800;
  border-color: #64748b;
  padding: 8px 6px;
}
.row-sub-unit .cell-progkeg {
  font-size: 12px;
  letter-spacing: 0.02em;
}

.row-sasaran {
  background-color: #FFF2CC;
  font-weight: 700;
}
.row-program {
  background-color: #FCE4D6;
  font-weight: 700;
}
.row-kegiatan {
  background-color: #E2EFDA;
  font-weight: 600;
}
.row-subkegiatan {
  background-color: #FFFFFF;
}

/* Alignment Helpers */
.cell-kode {
  text-align: left;
  font-weight: 700;
  vertical-align: top;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.cell-sasaran,
.cell-progkeg,
.cell-indikator,
.cell-unit {
  vertical-align: top;
}
.cell-center {
  text-align: center;
  vertical-align: top;
}
.cell-pagu {
  text-align: right;
  vertical-align: top;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.text-success-bold {
  color: #15803d;
  font-weight: 700;
}
.text-danger-bold {
  color: #b91c1c;
  font-weight: 700;
}

/* Footer summary rows */
.row-footer-header td {
  background-color: #f8fafc;
  font-size: 11px;
}
.footer-label-bold {
  font-weight: 700;
  color: #0f172a;
}
.footer-val {
  color: #334155;
}

.empty-sheet-cell {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  font-size: 0.95rem;
}
</style>

