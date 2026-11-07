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
            <h2 class="report-main-title">Indikator Kinerja Utama (IKU)</h2>
          </div>
        </div>

        <div class="toolbar-controls">
          <!-- OPD Selector -->
          <div class="control-group">
            <label class="control-label">Perangkat Daerah (OPD):</label>
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
              title="Unduh Laporan IKU dalam Format Microsoft Excel (.xlsx)"
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
        <p>Memuat Laporan Indikator Kinerja Utama (IKU)...</p>
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
          <div class="sheet-title-table-no">Indikator Kinerja Utama</div>
          <h3 class="sheet-title-heading">
            {{ reportData.opd?.nama_skpd }} Kota Tegal
          </h3>
          <div class="sheet-title-years">Tahun 2025-2030</div>
          <div v-if="tipeTarget === 'perubahan'" class="badge-tipe-preview">
            Versi Target Perubahan
          </div>
        </div>

        <!-- Sheet Table -->
        <div class="sheet-table-wrapper">
          <table class="civic-report-table">
            <thead>
              <!-- Header Row 1 -->
              <tr class="header-row-primary">
                <th rowspan="2" class="th-no">No</th>
                <th rowspan="2" class="th-tujuan-sasaran">Tujuan / Sasaran</th>
                <th rowspan="2" class="th-indikator">Indikator</th>
                <th rowspan="2" class="th-satuan">Satuan</th>
                <th colspan="6" class="th-target-group">Target Tahun</th>
              </tr>
              <!-- Header Row 2 -->
              <tr class="header-row-primary header-row-sub">
                <th class="th-year">2025</th>
                <th class="th-year">2026</th>
                <th class="th-year">2027</th>
                <th class="th-year">2028</th>
                <th class="th-year">2029</th>
                <th class="th-year">2030</th>
              </tr>
              <!-- Header Row 3: Column Numbering (1 to 10) -->
              <tr class="header-row-num">
                <th>1</th>
                <th>2</th>
                <th>3</th>
                <th>4</th>
                <th>5</th>
                <th>6</th>
                <th>7</th>
                <th>8</th>
                <th>9</th>
                <th>10</th>
              </tr>
            </thead>
            <tbody>
              <!-- Empty Table Fallback -->
              <tr v-if="!reportData.groups || reportData.groups.length === 0">
                <td colspan="10" class="td-empty">
                  Belum ada indikator yang ditandai sebagai Indikator Kinerja Utama (IKU) untuk Perangkat Daerah ini.
                </td>
              </tr>

              <!-- Loop Groups & Indicators -->
              <template v-for="(g, gIdx) in reportData.groups" :key="'group_' + gIdx">
                <tr
                  v-for="(ind, indIdx) in g.indikator_list"
                  :key="'ind_' + gIdx + '_' + indIdx"
                  class="row-iku-item"
                >
                  <!-- Col 1: No -->
                  <td class="td-no-col">
                    {{ calculateGlobalIndex(gIdx, indIdx) }}
                  </td>

                  <!-- Col 2: Tujuan / Sasaran (Rowspan across its indicators if multiple) -->
                  <td
                    v-if="indIdx === 0"
                    :rowspan="g.indikator_list.length"
                    class="td-tujuan-sasaran"
                  >
                    <div class="level-indicator-tag" :class="g.level.toLowerCase()">
                      {{ g.level }}
                    </div>
                    <div class="tujuan-sasaran-text">{{ g.tujuan_sasaran }}</div>
                  </td>

                  <!-- Col 3: Indikator -->
                  <td class="td-indikator">
                    <span class="iku-badge-pill">IKU</span>
                    {{ ind.uraian }}
                  </td>

                  <!-- Col 4: Satuan -->
                  <td class="td-satuan">{{ ind.satuan || '-' }}</td>

                  <!-- Cols 5-10: Targets 2025-2030 -->
                  <td class="td-target">{{ ind.target0 || '-' }}</td>
                  <td class="td-target">{{ ind.target1 || '-' }}</td>
                  <td class="td-target">{{ ind.target2 || '-' }}</td>
                  <td class="td-target">{{ ind.target3 || '-' }}</td>
                  <td class="td-target">{{ ind.target4 || '-' }}</td>
                  <td class="td-target">{{ ind.target5 || '-' }}</td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const router = useRouter();

const opdList = ref([]);
const selectedOpdId = ref(null);
const tipeTarget = ref('murni');
const loading = ref(false);
const exporting = ref(false);
const error = ref(null);
const reportData = ref(null);

function calculateGlobalIndex(targetGroupIdx, indIdx) {
  if (!reportData.value?.groups) return 1;
  let count = 0;
  for (let i = 0; i < targetGroupIdx; i++) {
    count += reportData.value.groups[i].indikator_list?.length || 0;
  }
  return count + indIdx + 1;
}

async function loadOpdList() {
  try {
    const list = await api.getLaporanOpdList();
    opdList.value = list || [];
    const paramId = route.params.id ? parseInt(route.params.id) : null;
    if (paramId && opdList.value.some(o => o.id_skpd === paramId)) {
      selectedOpdId.value = paramId;
    } else if (opdList.value.some(o => o.id_skpd === 464)) {
      selectedOpdId.value = 464; // Default sample OPD (Dinas Tenaga Kerja)
    } else if (opdList.value.length > 0) {
      selectedOpdId.value = opdList.value[0].id_skpd;
    }
  } catch (err) {
    console.error('Gagal memuat daftar OPD:', err);
  }
}

async function fetchReport() {
  if (!selectedOpdId.value) return;
  loading.value = true;
  error.value = null;
  try {
    const data = await api.getLaporanIku(selectedOpdId.value, tipeTarget.value);
    reportData.value = data;
  } catch (err) {
    console.error('Gagal memuat laporan IKU:', err);
    error.value = err.message || 'Gagal memuat laporan IKU';
  } finally {
    loading.value = false;
  }
}

function onOpdChange() {
  if (selectedOpdId.value) {
    router.replace(`/laporan/iku/${selectedOpdId.value}`);
    fetchReport();
  }
}

function setTipeTarget(tipe) {
  if (tipeTarget.value !== tipe) {
    tipeTarget.value = tipe;
    fetchReport();
  }
}

async function handleExportExcel() {
  if (!selectedOpdId.value) return;
  exporting.value = true;
  try {
    await api.downloadLaporanIkuExcel(selectedOpdId.value, tipeTarget.value);
  } catch (err) {
    alert('Gagal mengunduh file Excel IKU: ' + err.message);
  } finally {
    exporting.value = false;
  }
}

function goBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push('/');
  }
}

onMounted(async () => {
  await loadOpdList();
  if (selectedOpdId.value) {
    await fetchReport();
  }
});

watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      const parsed = parseInt(newId);
      if (parsed !== selectedOpdId.value) {
        selectedOpdId.value = parsed;
        fetchReport();
      }
    }
  }
);
</script>

<style scoped>
.report-page-container {
  padding: 1.5rem 0 3rem 0;
  background-color: var(--bg-app);
  min-height: calc(100vh - 120px);
}

/* Toolbar & Filter Bar */
.report-toolbar-card {
  background: #ffffff;
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
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
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-toolbar-back:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.toolbar-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.report-badge-pill {
  display: inline-block;
  align-self: flex-start;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #1d4ed8;
  background: #dbeafe;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.report-main-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #0f172a;
}

.toolbar-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.control-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
}

.control-select {
  padding: 0.55rem 0.85rem;
  font-size: 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  color: #1e293b;
  cursor: pointer;
  outline: none;
  font-weight: 500;
}

.control-select.opd-select {
  min-width: 280px;
  max-width: 380px;
}

.target-toggle-group {
  display: inline-flex;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  overflow: hidden;
}

.btn-toggle-type {
  padding: 0.55rem 0.9rem;
  font-size: 0.82rem;
  font-weight: 600;
  border: none;
  background: #f8fafc;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-toggle-type.active {
  background: #2563eb;
  color: #ffffff;
}

.btn-export-excel {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #16a34a;
  color: #ffffff;
  border: 1px solid #15803d;
  padding: 0.55rem 1.15rem;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(22, 163, 74, 0.2);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-export-excel:hover:not(:disabled) {
  background: #15803d;
  box-shadow: 0 4px 8px rgba(22, 163, 74, 0.3);
  transform: translateY(-1px);
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

/* Document Sheet Container */
.document-sheet-container {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
  padding: 2.5rem 2rem;
  overflow: hidden;
}

.sheet-title-block {
  text-align: center;
  margin-bottom: 1.75rem;
}

.sheet-title-table-no {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.sheet-title-heading {
  margin: 0 0 0.25rem 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
}

.sheet-title-years {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.badge-tipe-preview {
  display: inline-block;
  margin-top: 0.4rem;
  font-size: 0.75rem;
  font-weight: 700;
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
}

/* Sheet Table */
.sheet-table-wrapper {
  overflow-x: auto;
  border: 1px solid #94a3b8;
}

.civic-report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  color: #0f172a;
  background: #ffffff;
}

.civic-report-table th,
.civic-report-table td {
  border: 1px solid #94a3b8;
  padding: 0.55rem 0.65rem;
  vertical-align: middle;
}

/* Header Styles */
.header-row-primary th {
  background-color: #3b6998;
  color: #ffffff;
  font-weight: 700;
  text-align: center;
  font-size: 0.85rem;
}

.header-row-sub th {
  background-color: #3b6998;
  font-size: 0.82rem;
}

.header-row-num th {
  background-color: #5885af;
  color: #ffffff;
  font-weight: 700;
  text-align: center;
  font-size: 0.78rem;
  padding: 0.25rem 0.4rem;
}

/* Cell Widths & Alignments */
.th-no { width: 50px; }
.th-tujuan-sasaran { width: 280px; }
.th-indikator { width: 300px; }
.th-satuan { width: 100px; }
.th-target-group { text-align: center; }
.th-year { width: 80px; text-align: center; }

/* Data Columns */
.td-no-col {
  background-color: #4a709c;
  color: #ffffff;
  font-weight: 700;
  text-align: center;
  vertical-align: middle;
  font-size: 0.95rem;
}

.td-tujuan-sasaran {
  vertical-align: middle;
  line-height: 1.45;
  font-weight: 500;
}

.level-indicator-tag {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  margin-bottom: 0.25rem;
}

.level-indicator-tag.tujuan {
  background: #dbeafe;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.level-indicator-tag.sasaran {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
}

.tujuan-sasaran-text {
  color: #1e293b;
}

.td-indikator {
  line-height: 1.4;
  vertical-align: middle;
}

.iku-badge-pill {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 800;
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #bbf7d0;
  padding: 0.08rem 0.35rem;
  border-radius: 4px;
  margin-right: 0.35rem;
}

.td-satuan {
  text-align: center;
  font-weight: 500;
  white-space: nowrap;
}

.td-target {
  text-align: center;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  font-weight: 500;
}

.td-empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #64748b;
  font-style: italic;
}

/* Loading & Error States */
.report-loading-card,
.report-error-card {
  background: #ffffff;
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  color: #475569;
}

.spinner-civic {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem auto;
}

.btn-retry {
  margin-top: 1rem;
  background: #2563eb;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}
</style>

