<template>
  <div class="report-page-container">
    <div class="app-container">
      <!-- Toolbar & Controls -->
      <div class="report-toolbar-card">
        <div class="toolbar-left">
          <button type="button" class="btn-toolbar-back" @click="goBack" title="Kembali ke Beranda">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span>Kembali</span>
          </button>
          <div class="toolbar-title-wrap">
            <div class="report-badge-pill">Laporan RENSTRA</div>
            <h2 class="report-main-title">Tabel 3.1: Tujuan dan Sasaran</h2>
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
              title="Unduh Laporan dalam Format Microsoft Excel (.xlsx)"
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
        <p>Memuat Laporan Tujuan dan Sasaran...</p>
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
          <div class="sheet-title-table-no">Tabel 3.1</div>
          <h3 class="sheet-title-heading">
            Tujuan dan Sasaran {{ reportData.opd?.nama_skpd }} Kota Tegal
          </h3>
          <div class="sheet-title-years">Tahun 2025-2029</div>
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
                <th rowspan="2" class="th-no">No.</th>
                <th rowspan="2" class="th-tujuan">Tujuan</th>
                <th rowspan="2" class="th-sasaran">Sasaran</th>
                <th rowspan="2" class="th-indikator">Indikator</th>
                <th rowspan="2" class="th-satuan">Satuan</th>
                <th class="th-kondisi">Kondisi<br />Awal</th>
                <th colspan="6" class="th-target-group">Target</th>
                <th rowspan="2" class="th-ket">Ket</th>
              </tr>
              <!-- Header Row 2 -->
              <tr class="header-row-primary header-row-sub">
                <th class="th-year">2024</th>
                <th class="th-year">2025</th>
                <th class="th-year">2026</th>
                <th class="th-year">2027</th>
                <th class="th-year">2028</th>
                <th class="th-year">2029</th>
                <th class="th-year">2030</th>
              </tr>
              <!-- Header Row 3: Column Numbering (1 to 13) -->
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
                <th>11</th>
                <th>12</th>
                <th>13</th>
              </tr>
            </thead>
            <tbody>
              <!-- Empty Table Fallback -->
              <tr v-if="!reportData.tujuan_list || reportData.tujuan_list.length === 0">
                <td colspan="13" class="td-empty">
                  Belum ada data Tujuan dan Sasaran yang terinput untuk Perangkat Daerah ini.
                </td>
              </tr>

              <!-- Loop Tujuan -->
              <template v-for="(t, tIdx) in reportData.tujuan_list" :key="'tujuan_' + tIdx">
                <!-- Case 1: Has Indikator Tujuan -->
                <template v-if="t.indikator_tujuan_list && t.indikator_tujuan_list.length > 0">
                  <tr
                    v-for="(it, itIdx) in t.indikator_tujuan_list"
                    :key="'t_ind_' + tIdx + '_' + itIdx"
                    class="row-indikator-tujuan"
                  >
                    <!-- Col 1 (No): rendered only on first row of this Tujuan, with rowspan -->
                    <td
                      v-if="itIdx === 0"
                      :rowspan="calculateTujuanRowspan(t)"
                      class="td-no-col"
                    >
                      {{ t.no || (tIdx + 1) }}
                    </td>
                    <!-- Col 2 (Tujuan): rendered only on first row of this Tujuan, with rowspan -->
                    <td
                      v-if="itIdx === 0"
                      :rowspan="calculateTujuanRowspan(t)"
                      class="td-tujuan"
                    >
                      {{ t.uraitujuan }}
                    </td>
                    <!-- Col 3 (Sasaran): Empty for Indikator Tujuan row -->
                    <td class="td-sasaran-blank"></td>
                    <!-- Col 4 (Indikator Tujuan): Multi-line header + name -->
                    <td class="td-indikator">
                      <div class="ind-badge-label">{{ it.no_label }}</div>
                      <div class="ind-name">{{ it.uraian }}</div>
                    </td>
                    <!-- Col 5: Satuan -->
                    <td class="td-satuan">{{ it.satuan || '-' }}</td>
                    <!-- Cols 6-12: Targets -->
                    <td class="td-target">{{ it.target_awal || '-' }}</td>
                    <td class="td-target">{{ it.target0 || '-' }}</td>
                    <td class="td-target">{{ it.target1 || '-' }}</td>
                    <td class="td-target">{{ it.target2 || '-' }}</td>
                    <td class="td-target">{{ it.target3 || '-' }}</td>
                    <td class="td-target">{{ it.target4 || '-' }}</td>
                    <td class="td-target">{{ it.target5 || '-' }}</td>
                    <!-- Col 13: Ket (Metadata) -->
                    <td class="td-ket">{{ it.ket || '-' }}</td>
                  </tr>
                </template>

                <!-- Case 2: No Indikator Tujuan, but has Sasarans or nothing -->
                <template v-else-if="!t.sasaran_list || t.sasaran_list.length === 0">
                  <tr class="row-tujuan-alone">
                    <td class="td-no-col">{{ t.no || (tIdx + 1) }}</td>
                    <td class="td-tujuan">{{ t.uraitujuan }}</td>
                    <td class="td-sasaran-blank">-</td>
                    <td class="td-indikator">-</td>
                    <td class="td-satuan">-</td>
                    <td class="td-target">-</td>
                    <td class="td-target">-</td>
                    <td class="td-target">-</td>
                    <td class="td-target">-</td>
                    <td class="td-target">-</td>
                    <td class="td-target">-</td>
                    <td class="td-target">-</td>
                    <td class="td-ket">-</td>
                  </tr>
                </template>

                <!-- Loop Sasarans under this Tujuan -->
                <template v-for="(s, sIdx) in t.sasaran_list" :key="'sas_' + tIdx + '_' + sIdx">
                  <!-- Sasaran with Indicators -->
                  <template v-if="s.indikator_list && s.indikator_list.length > 0">
                    <tr
                      v-for="(isas, isIdx) in s.indikator_list"
                      :key="'sas_ind_' + tIdx + '_' + sIdx + '_' + isIdx"
                      class="row-sasaran"
                    >
                      <!-- Col 1 (No): Only if Tujuan has NO indikator and this is the very first Sasaran/indicator -->
                      <td
                        v-if="(!t.indikator_tujuan_list || t.indikator_tujuan_list.length === 0) && sIdx === 0 && isIdx === 0"
                        :rowspan="calculateTujuanRowspan(t)"
                        class="td-no-col"
                      >
                        {{ t.no || (tIdx + 1) }}
                      </td>
                      <!-- Col 2 (Tujuan): Only if Tujuan has NO indikator and this is the very first Sasaran/indicator -->
                      <td
                        v-if="(!t.indikator_tujuan_list || t.indikator_tujuan_list.length === 0) && sIdx === 0 && isIdx === 0"
                        :rowspan="calculateTujuanRowspan(t)"
                        class="td-tujuan"
                      >
                        {{ t.uraitujuan }}
                      </td>
                      <!-- Col 3 (Sasaran): Span across all indicators of this Sasaran -->
                      <td
                        v-if="isIdx === 0"
                        :rowspan="s.indikator_list.length"
                        class="td-sasaran"
                      >
                        <div class="sas-badge-label">{{ s.no_label }}</div>
                        <div class="sas-name">{{ s.uraisasaran }}</div>
                      </td>
                      <!-- Col 4: Indikator Sasaran -->
                      <td class="td-indikator">
                        {{ isas.uraian }}
                      </td>
                      <!-- Col 5: Satuan -->
                      <td class="td-satuan">{{ isas.satuan || '-' }}</td>
                      <!-- Cols 6-12: Targets -->
                      <td class="td-target">{{ isas.target_awal || '-' }}</td>
                      <td class="td-target">{{ isas.target0 || '-' }}</td>
                      <td class="td-target">{{ isas.target1 || '-' }}</td>
                      <td class="td-target">{{ isas.target2 || '-' }}</td>
                      <td class="td-target">{{ isas.target3 || '-' }}</td>
                      <td class="td-target">{{ isas.target4 || '-' }}</td>
                      <td class="td-target">{{ isas.target5 || '-' }}</td>
                      <!-- Col 13: Ket (Metadata) -->
                      <td class="td-ket">{{ isas.ket || '-' }}</td>
                    </tr>
                  </template>

                  <!-- Sasaran without Indicators -->
                  <template v-else>
                    <tr class="row-sasaran">
                      <!-- Col 1 (No) if first row of Tujuan -->
                      <td
                        v-if="(!t.indikator_tujuan_list || t.indikator_tujuan_list.length === 0) && sIdx === 0"
                        :rowspan="calculateTujuanRowspan(t)"
                        class="td-no-col"
                      >
                        {{ t.no || (tIdx + 1) }}
                      </td>
                      <!-- Col 2 (Tujuan) if first row of Tujuan -->
                      <td
                        v-if="(!t.indikator_tujuan_list || t.indikator_tujuan_list.length === 0) && sIdx === 0"
                        :rowspan="calculateTujuanRowspan(t)"
                        class="td-tujuan"
                      >
                        {{ t.uraitujuan }}
                      </td>
                      <!-- Col 3 (Sasaran) -->
                      <td class="td-sasaran">
                        <div class="sas-badge-label">{{ s.no_label }}</div>
                        <div class="sas-name">{{ s.uraisasaran }}</div>
                      </td>
                      <!-- Cols 4-13 blank -->
                      <td class="td-indikator">-</td>
                      <td class="td-satuan">-</td>
                      <td class="td-target">-</td>
                      <td class="td-target">-</td>
                      <td class="td-target">-</td>
                      <td class="td-target">-</td>
                      <td class="td-target">-</td>
                      <td class="td-target">-</td>
                      <td class="td-target">-</td>
                      <td class="td-ket">-</td>
                    </tr>
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

function calculateTujuanRowspan(t) {
  let count = 0;
  if (t.indikator_tujuan_list && t.indikator_tujuan_list.length > 0) {
    count += t.indikator_tujuan_list.length;
  }
  if (t.sasaran_list && t.sasaran_list.length > 0) {
    for (const s of t.sasaran_list) {
      if (s.indikator_list && s.indikator_list.length > 0) {
        count += s.indikator_list.length;
      } else {
        count += 1;
      }
    }
  }
  return count > 0 ? count : 1;
}

async function loadOpdList() {
  try {
    const list = await api.getLaporanOpdList();
    opdList.value = list || [];
    // If route has param id, use it; otherwise pick first OPD or default 464 (Dinas Tenaga Kerja)
    const paramId = route.params.id ? parseInt(route.params.id) : null;
    if (paramId && opdList.value.some(o => o.id_skpd === paramId)) {
      selectedOpdId.value = paramId;
    } else if (opdList.value.some(o => o.id_skpd === 464)) {
      selectedOpdId.value = 464; // Default to sample OPD (Dinas Tenaga Kerja)
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
    const data = await api.getLaporanTujuanSasaran(selectedOpdId.value, tipeTarget.value);
    reportData.value = data;
  } catch (err) {
    console.error('Gagal memuat laporan:', err);
    error.value = err.message || 'Gagal memuat laporan tujuan dan sasaran';
  } finally {
    loading.value = false;
  }
}

function onOpdChange() {
  if (selectedOpdId.value) {
    router.replace(`/laporan/tujuan-sasaran/${selectedOpdId.value}`);
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
    await api.downloadLaporanTujuanSasaranExcel(selectedOpdId.value, tipeTarget.value);
  } catch (err) {
    alert('Gagal mengunduh file Excel: ' + err.message);
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

/* Document Sheet Container (Paper preview like in the image) */
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
  font-size: 1.05rem;
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

/* Header Styles (matching the blue palette in user image) */
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
.th-no { width: 45px; }
.th-tujuan { width: 230px; }
.th-sasaran { width: 220px; }
.th-indikator { width: 250px; }
.th-satuan { width: 85px; }
.th-kondisi { width: 85px; }
.th-year { width: 75px; text-align: center; }
.th-ket { width: 220px; }

/* Column A No */
.td-no-col {
  background-color: #4a709c;
  color: #ffffff;
  font-weight: 700;
  text-align: center;
  vertical-align: middle;
  font-size: 0.95rem;
}

.td-tujuan {
  vertical-align: middle;
  line-height: 1.45;
  font-weight: 500;
}

.td-sasaran {
  vertical-align: middle;
  line-height: 1.45;
  background-color: #f8fafc;
}

.sas-badge-label {
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.2rem;
}

.sas-name {
  color: #334155;
}

.td-sasaran-blank {
  background-color: #f8fafc;
}

.td-indikator {
  line-height: 1.4;
  vertical-align: middle;
}

.ind-badge-label {
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.2rem;
}

.ind-name {
  color: #334155;
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

.td-ket {
  text-align: left;
  line-height: 1.4;
  font-size: 0.82rem;
  color: #334155;
  vertical-align: middle;
  min-width: 160px;
  max-width: 280px;
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

