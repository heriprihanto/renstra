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
            <div class="report-badge-pill">Laporan RENSTRA</div>
            <h2 class="report-main-title">Tabel 4.1: Program, Kegiatan, Sub Kegiatan & Pendanaan</h2>
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

          <!-- Sub SKPD Selector (jika ada unit) -->
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
              title="Unduh Tabel 4.1 dalam Format Microsoft Excel (.xlsx)"
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
        <p>Memuat Laporan Program, Kegiatan, Sub Kegiatan dan Pendanaan...</p>
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
          <div class="sheet-title-table-no">Tabel 4.1</div>
          <h3 class="sheet-title-heading">
            Rencana Program, Kegiatan, Sub Kegiatan dan Pendanaan Perangkat Daerah
          </h3>
          <h4 class="sheet-title-subheading">
            {{ reportData.opd.nama_skpd }}
            <span v-if="reportData.opd.sub_title"> - {{ reportData.opd.sub_title }}</span>
            Kota Tegal Tahun {{ reportData.tahun_awal }}-{{ reportData.tahun_akhir }}
          </h4>
          <div class="sheet-title-meta">
            <span class="badge-target-type">Mode Target: {{ tipeTarget.toUpperCase() }}</span>
          </div>
        </div>

        <!-- Quick Summary Metrics Bar -->
        <div class="summary-metrics-bar">
          <div class="metric-chip">
            <span class="metric-label">Bidang Urusan</span>
            <span class="metric-val">{{ reportData.total_bidang || 0 }}</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">Program</span>
            <span class="metric-val text-prog">{{ reportData.total_program || 0 }}</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">Kegiatan</span>
            <span class="metric-val text-keg">{{ reportData.total_kegiatan || 0 }}</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">Sub Kegiatan</span>
            <span class="metric-val text-sub">{{ reportData.total_subkegiatan || 0 }}</span>
          </div>
          <div class="metric-chip pagu-chip">
            <span class="metric-label">Total Pagu (2026-2030)</span>
            <span class="metric-val text-pagu">{{ formatRupiah(calculateGrandTotalPagu()) }}</span>
          </div>
        </div>

        <!-- Preview Table Wrapper with Horizontal Scroll -->
        <div class="sheet-table-scroll-wrap">
          <table class="table-tabel-41">
            <thead>
              <!-- Header Row 1: Merged Main Labels -->
              <tr class="header-row-1">
                <th rowspan="3" class="col-no">Kode</th>
                <th rowspan="3" class="col-nama">
                  Bidang Urusan/<br>Program/Kegiatan/ Sub Kegiatan
                </th>
                <th rowspan="3" class="col-sasaran">
                  Sasaran Program/Sasaran Kegiatan/Sasaran Sub Kegiatan
                </th>
                <th rowspan="3" class="col-indikator">
                  Indikator Outcome/Output
                </th>
                <th rowspan="3" class="col-satuan">Satuan</th>
                <th rowspan="3" class="col-baseline">Baseline<br>2024</th>
                <th colspan="10" class="col-target-pagu-group">
                  Target dan Pagu Indikatif Tahun
                </th>
                <th rowspan="3" class="col-ket">Ket</th>
              </tr>

              <!-- Header Row 2: Years 2026-2030 -->
              <tr class="header-row-2">
                <th colspan="2" class="year-hdr">2026</th>
                <th colspan="2" class="year-hdr">2027</th>
                <th colspan="2" class="year-hdr">2028</th>
                <th colspan="2" class="year-hdr">2029</th>
                <th colspan="2" class="year-hdr">2030</th>
              </tr>

              <!-- Header Row 3: Target & Pagu Subheaders -->
              <tr class="header-row-3">
                <th class="sub-hdr">Target</th>
                <th class="sub-hdr">Pagu</th>
                <th class="sub-hdr">Target</th>
                <th class="sub-hdr">Pagu</th>
                <th class="sub-hdr">Target</th>
                <th class="sub-hdr">Pagu</th>
                <th class="sub-hdr">Target</th>
                <th class="sub-hdr">Pagu</th>
                <th class="sub-hdr">Target</th>
                <th class="sub-hdr">Pagu</th>
              </tr>

              <!-- Header Row 4: Column Numbering Guide (1 to 17) -->
              <tr class="header-guide-row">
                <th v-for="c in 17" :key="c" class="guide-num">{{ c }}</th>
              </tr>
            </thead>

            <tbody>
              <!-- Empty State -->
              <tr v-if="!reportData.bidang_list || reportData.bidang_list.length === 0">
                <td colspan="17" class="empty-sheet-cell">
                  Tidak ada data Program, Kegiatan, dan Sub Kegiatan untuk Perangkat Daerah ini.
                </td>
              </tr>

              <!-- Nested Rows Iteration grouped by Sub Unit (if multiple) and Bidang -->
              <template v-for="(subGroup, sgIdx) in displayedSubGroups" :key="'sg-' + sgIdx">
                <!-- Baris Header Sub Unit (Soft Blue #BDD7EE) -->
                <tr v-if="!subGroup.isSingle" class="row-subunit-header">
                  <td class="cell-no">{{ subGroup.kode_sub_skpd }}</td>
                  <td class="cell-subunit-title" colspan="16">
                    {{ subGroup.nama_sub_skpd.toUpperCase() }}
                  </td>
                </tr>

                <template v-for="(bidang, bIdx) in subGroup.bidang_list" :key="'sg-' + sgIdx + '-bidang-' + bIdx">
                  <!-- 1. BARIS BIDANG URUSAN (Soft Blue) -->
                  <tr class="row-bidang-urusan">
                    <td class="cell-no">{{ bidang.kode_bidang || bidang.kodebidang }}</td>
                    <td class="cell-bidang-title" colspan="16">
                      {{ bidang.uraibidang || bidang.nama_bidang }}
                    </td>
                  </tr>

                  <!-- Iterasi Program dalam Bidang Urusan -->
                  <template v-for="(prog, pIdx) in bidang.programs" :key="'prog-' + pIdx">
                    <!-- 2. BARIS PROGRAM (Soft Pink) -->
                    <tr class="row-program">
                      <td class="cell-no">{{ prog.kodeprogram }}</td>
                      <td class="cell-prog-title">
                        {{ prog.uraiprogram }}
                      </td>
                      <td class="cell-sasaran">
                        {{ prog.kinerja || '-' }}
                      </td>
                      <td class="cell-indikator">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'pind-' + iIdx" class="ind-item">
                          {{ ind.uraian }}
                        </div>
                        <div v-if="!prog.indicators || prog.indicators.length === 0">-</div>
                      </td>
                      <td class="cell-center">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'psat-' + iIdx" class="ind-item">
                          {{ ind.satuan }}
                        </div>
                        <div v-if="!prog.indicators || prog.indicators.length === 0">-</div>
                      </td>
                      <td class="cell-center">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'pbase-' + iIdx" class="ind-item">
                          {{ ind.baseline }}
                        </div>
                        <div v-if="!prog.indicators || prog.indicators.length === 0">-</div>
                      </td>

                      <!-- 2026 -->
                      <td class="cell-center">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'pt26-' + iIdx" class="ind-item">
                          {{ ind.targets['2026'] }}
                        </div>
                      </td>
                      <td class="cell-pagu">{{ formatRupiah(prog.pagu['2026']) }}</td>

                      <!-- 2027 -->
                      <td class="cell-center">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'pt27-' + iIdx" class="ind-item">
                          {{ ind.targets['2027'] }}
                        </div>
                      </td>
                      <td class="cell-pagu">{{ formatRupiah(prog.pagu['2027']) }}</td>

                      <!-- 2028 -->
                      <td class="cell-center">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'pt28-' + iIdx" class="ind-item">
                          {{ ind.targets['2028'] }}
                        </div>
                      </td>
                      <td class="cell-pagu">{{ formatRupiah(prog.pagu['2028']) }}</td>

                      <!-- 2029 -->
                      <td class="cell-center">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'pt29-' + iIdx" class="ind-item">
                          {{ ind.targets['2029'] }}
                        </div>
                      </td>
                      <td class="cell-pagu">{{ formatRupiah(prog.pagu['2029']) }}</td>

                      <!-- 2030 -->
                      <td class="cell-center">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'pt30-' + iIdx" class="ind-item">
                          {{ ind.targets['2030'] }}
                        </div>
                      </td>
                      <td class="cell-pagu">{{ formatRupiah(prog.pagu['2030']) }}</td>

                      <td :class="['cell-ket', { 'cell-center': !prog.indicators || prog.indicators.every(i => !i.ket || i.ket === '-') }]">
                        <div v-for="(ind, iIdx) in prog.indicators" :key="'pket-' + iIdx" class="ind-item">
                          {{ ind.ket }}
                        </div>
                      </td>
                    </tr>

                    <!-- Iterasi Kegiatan dalam Program -->
                    <template v-for="(keg, kIdx) in prog.kegiatans" :key="'keg-' + kIdx">
                      <!-- 3. BARIS KEGIATAN (Soft Green) -->
                      <tr class="row-kegiatan">
                        <td class="cell-no">{{ keg.kodekegiatan }}</td>
                        <td class="cell-keg-title">
                          {{ keg.uraikegiatan }}
                        </td>
                        <td class="cell-sasaran">
                          {{ keg.kinerja || '-' }}
                        </td>
                        <td class="cell-indikator">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'kind-' + ikIdx" class="ind-item">
                            {{ ind.uraian }}
                          </div>
                          <div v-if="!keg.indicators || keg.indicators.length === 0">-</div>
                        </td>
                        <td class="cell-center">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'ksat-' + ikIdx" class="ind-item">
                            {{ ind.satuan }}
                          </div>
                          <div v-if="!keg.indicators || keg.indicators.length === 0">-</div>
                        </td>
                        <td class="cell-center">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'kbase-' + ikIdx" class="ind-item">
                            {{ ind.baseline }}
                          </div>
                          <div v-if="!keg.indicators || keg.indicators.length === 0">-</div>
                        </td>

                        <!-- 2026 -->
                        <td class="cell-center">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'kt26-' + ikIdx" class="ind-item">
                            {{ ind.targets['2026'] }}
                          </div>
                        </td>
                        <td class="cell-pagu">{{ formatRupiah(keg.pagu['2026']) }}</td>

                        <!-- 2027 -->
                        <td class="cell-center">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'kt27-' + ikIdx" class="ind-item">
                            {{ ind.targets['2027'] }}
                          </div>
                        </td>
                        <td class="cell-pagu">{{ formatRupiah(keg.pagu['2027']) }}</td>

                        <!-- 2028 -->
                        <td class="cell-center">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'kt28-' + ikIdx" class="ind-item">
                            {{ ind.targets['2028'] }}
                          </div>
                        </td>
                        <td class="cell-pagu">{{ formatRupiah(keg.pagu['2028']) }}</td>

                        <!-- 2029 -->
                        <td class="cell-center">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'kt29-' + ikIdx" class="ind-item">
                            {{ ind.targets['2029'] }}
                          </div>
                        </td>
                        <td class="cell-pagu">{{ formatRupiah(keg.pagu['2029']) }}</td>

                        <!-- 2030 -->
                        <td class="cell-center">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'kt30-' + ikIdx" class="ind-item">
                            {{ ind.targets['2030'] }}
                          </div>
                        </td>
                        <td class="cell-pagu">{{ formatRupiah(keg.pagu['2030']) }}</td>

                        <td :class="['cell-ket', { 'cell-center': !keg.indicators || keg.indicators.every(i => !i.ket || i.ket === '-') }]">
                          <div v-for="(ind, ikIdx) in keg.indicators" :key="'kket-' + ikIdx" class="ind-item">
                            {{ ind.ket }}
                          </div>
                        </td>
                      </tr>

                      <!-- Iterasi Sub Kegiatan dalam Kegiatan -->
                      <template v-for="(sub, sIdx) in keg.subkegiatans" :key="'sub-' + sIdx">
                        <!-- 4. BARIS SUB KEGIATAN (White) -->
                        <tr class="row-subkegiatan">
                          <td class="cell-no">{{ sub.kodesubkegiatan }}</td>
                          <td class="cell-sub-title">
                            {{ sub.uraisubkegiatan }}
                          </td>
                          <td class="cell-sasaran">
                            {{ sub.kinerja || '-' }}
                          </td>
                          <td class="cell-indikator">
                            {{ sub.indikator || '-' }}
                          </td>
                          <td class="cell-center">{{ sub.satuan || '-' }}</td>
                          <td class="cell-center">{{ sub.baseline || '-' }}</td>

                          <!-- 2026 -->
                          <td class="cell-center">{{ sub.targets['2026'] || '-' }}</td>
                          <td class="cell-pagu">{{ formatRupiah(sub.pagu['2026']) }}</td>

                          <!-- 2027 -->
                          <td class="cell-center">{{ sub.targets['2027'] || '-' }}</td>
                          <td class="cell-pagu">{{ formatRupiah(sub.pagu['2027']) }}</td>

                          <!-- 2028 -->
                          <td class="cell-center">{{ sub.targets['2028'] || '-' }}</td>
                          <td class="cell-pagu">{{ formatRupiah(sub.pagu['2028']) }}</td>

                          <!-- 2029 -->
                          <td class="cell-center">{{ sub.targets['2029'] || '-' }}</td>
                          <td class="cell-pagu">{{ formatRupiah(sub.pagu['2029']) }}</td>

                          <!-- 2030 -->
                          <td class="cell-center">{{ sub.targets['2030'] || '-' }}</td>
                          <td class="cell-pagu">{{ formatRupiah(sub.pagu['2030']) }}</td>

                          <td :class="['cell-ket', { 'cell-center': !sub.ket || sub.ket === '-' }]">{{ sub.ket || '-' }}</td>
                        </tr>
                      </template>
                    </template>
                  </template>
                </template>
              </template>
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
  name: 'ProgramKegiatanReportView',
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
  computed: {
    displayedSubGroups() {
      if (this.reportData?.has_multiple_subs && this.reportData?.sub_unit_groups?.length > 0) {
        return this.reportData.sub_unit_groups;
      }
      if (this.reportData?.bidang_list) {
        return [{
          isSingle: true,
          kode_sub_skpd: this.reportData.opd?.kode_skpd || '',
          nama_sub_skpd: this.reportData.opd?.nama_skpd || '',
          bidang_list: this.reportData.bidang_list,
        }];
      }
      return [];
    },
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
        this.$router.replace({ path: `/laporan/program-kegiatan/${this.selectedOpdId}` });
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
        const data = await api.getLaporanProgramKegiatan(this.selectedOpdId, {
          idSubSkpd: this.selectedSubSkpdId,
          tipe: this.tipeTarget,
        });
        this.reportData = data;
      } catch (err) {
        this.error = err.message || 'Gagal memuat laporan Program dan Kegiatan.';
        console.error('Error fetching program kegiatan report:', err);
      } finally {
        this.loading = false;
      }
    },
    async handleExportExcel() {
      if (!this.selectedOpdId || this.exporting) return;
      this.exporting = true;
      try {
        await api.downloadLaporanProgramKegiatanExcel(this.selectedOpdId, {
          idSubSkpd: this.selectedSubSkpdId,
          tipe: this.tipeTarget,
        });
      } catch (err) {
        alert('Gagal mengunduh file Excel: ' + (err.message || 'Error'));
      } finally {
        this.exporting = false;
      }
    },
    calculateGrandTotalPagu() {
      if (!this.reportData || !this.reportData.total_pagu) return 0;
      return Object.values(this.reportData.total_pagu).reduce((acc, v) => acc + (Number(v) || 0), 0);
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
  background: #107c41; /* Microsoft Excel Brand Green */
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

.sheet-title-table-no {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
}

.sheet-title-heading {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0.25rem 0;
}

.sheet-title-subheading {
  font-size: 1.05rem;
  font-weight: 700;
  color: #334155;
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

/* Quick Summary Metrics Bar */
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

.text-prog { color: #b45309; }
.text-keg { color: #15803d; }
.text-sub { color: #2563eb; }

.pagu-chip {
  margin-left: auto;
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.text-pagu {
  color: #0f172a;
  font-size: 1.05rem;
}

/* Table Layout matching Excel Image */
.sheet-table-scroll-wrap {
  overflow-x: auto;
  border: 1px solid #000000;
}

.table-tabel-41 {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 11px;
  color: #000000;
  background: #ffffff;
}

.table-tabel-41 th,
.table-tabel-41 td {
  border: 1px solid #000000;
  padding: 5px 6px;
  line-height: 1.25;
}

/* Header Rows Styling (B4C6E7 soft blue) */
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

.col-no { min-width: 140px; width: 140px; }
.col-nama { min-width: 260px; max-width: 320px; text-align: center; }
.col-sasaran { min-width: 180px; max-width: 240px; }
.col-indikator { min-width: 200px; max-width: 260px; }
.col-satuan { width: 60px; }
.col-baseline { width: 70px; }
.col-ket { min-width: 220px; max-width: 320px; }

.year-hdr { font-size: 11px; }
.sub-hdr { width: 75px; font-size: 10px; }

.header-guide-row th {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 4px;
}

/* Row 0: Sub Unit Header (Soft Blue #BDD7EE) */
.row-subunit-header {
  background-color: #BDD7EE !important;
  font-weight: 800;
}

.row-subunit-header td {
  background-color: #BDD7EE !important;
  color: #0f172a;
  font-weight: 800;
  border-color: #64748b;
  padding: 8px 6px;
}

.cell-subunit-title {
  font-size: 13px;
  color: #0f172a;
  letter-spacing: 0.02em;
}

/* Row 1: Bidang Urusan (Soft Blue #D9E1F2) */
.row-bidang-urusan {
  background-color: #D9E1F2;
  font-weight: 700;
}

.cell-bidang-title {
  font-size: 12px;
  color: #000000;
}

/* Row 2: Program (Soft Pink #FCE4D6) */
.row-program {
  background-color: #FCE4D6;
  font-weight: 700;
}

.cell-prog-title {
  font-size: 11px;
  color: #000000;
}

/* Row 3: Kegiatan (Soft Green #E2EFDA) */
.row-kegiatan {
  background-color: #E2EFDA;
  font-weight: 600;
}

.cell-keg-title {
  font-size: 11px;
  color: #000000;
}

/* Row 4: Sub Kegiatan (White #FFFFFF) */
.row-subkegiatan {
  background-color: #FFFFFF;
}

.cell-sub-title {
  font-size: 11px;
  color: #000000;
}

/* Cell alignment helpers */
.cell-no {
  text-align: left;
  font-weight: 700;
  vertical-align: top;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  padding-left: 8px !important;
}

.cell-sasaran,
.cell-indikator {
  vertical-align: top;
}

.cell-center {
  text-align: center;
  vertical-align: top;
}

.cell-ket {
  text-align: left;
  vertical-align: top;
  font-size: 10.5px;
  line-height: 1.35;
  word-break: break-word;
}

.cell-pagu {
  text-align: right;
  vertical-align: top;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.ind-item {
  margin-bottom: 4px;
}
.ind-item:last-child {
  margin-bottom: 0;
}

.empty-sheet-cell {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  font-size: 0.95rem;
}
</style>

