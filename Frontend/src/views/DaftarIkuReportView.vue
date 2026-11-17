<template>
  <div class="report-page-container">
    <div class="app-container">
      <!-- Toolbar & Controls -->
      <div class="report-toolbar-card">
        <div class="toolbar-header-row">
          <div class="toolbar-left">
            <button type="button" class="btn-toolbar-back" @click="goBack" title="Kembali">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              <span>Kembali</span>
            </button>
            <div class="toolbar-title-wrap">
              <div class="badge-report-pill">
                <span class="badge-no">Laporan #6</span>
                <span class="badge-dot">&bull;</span>
                <span>RENSTRA 2025 - 2030</span>
              </div>
              <h2 class="report-main-title">Daftar IKU Perangkat Daerah</h2>
              <div class="report-main-desc">
                Komparasi Target Capaian Kinerja (Murni) dan Target Perubahan Indikator Kinerja Utama (IKU) Pemerintah Kota Tegal
              </div>
            </div>
          </div>

          <div class="toolbar-actions">
            <!-- Export Excel Button -->
            <button
              type="button"
              class="btn-export-excel"
              :disabled="loading || exporting || filteredIndicators.length === 0"
              @click="handleExportExcel"
              title="Unduh Laporan Format Microsoft Excel (.xlsx)"
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

        <!-- Filter Controls Bar -->
        <div class="toolbar-controls-grid">
          <!-- Filter OPD -->
          <div class="control-box">
            <label class="control-label">Perangkat Daerah:</label>
            <select
              class="control-select opd-select"
              v-model="selectedOpdId"
              :disabled="loading"
            >
              <option :value="null">-- Semua Perangkat Daerah ({{ totalOpdCount }} OPD) --</option>
              <option v-for="opd in availableOpds" :key="opd.id_skpd" :value="opd.id_skpd">
                {{ opd.nama_skpd }} ({{ opd.total_iku }} IKU)
              </option>
            </select>
          </div>

          <!-- Mode Tampilan Tahun -->
          <div class="control-box">
            <label class="control-label">Tampilan Tahun Target:</label>
            <div class="view-mode-group">
              <button
                type="button"
                class="btn-view-mode"
                :class="{ active: viewMode === 'all' }"
                @click="viewMode = 'all'"
                title="Tampilkan seluruh tahun target 2025 - 2030"
              >
                Semua Tahun (2025-2030)
              </button>
              <button
                type="button"
                class="btn-view-mode"
                :class="{ active: viewMode === 'single' }"
                @click="viewMode = 'single'"
                title="Fokus pada 1 tahun target tertentu"
              >
                Fokus 1 Tahun
              </button>
            </div>
          </div>

          <!-- Pilihan Tahun Tertentu (Jika Single) -->
          <div v-if="viewMode === 'single'" class="control-box">
            <label class="control-label">Pilih Tahun:</label>
            <select class="control-select year-select" v-model="selectedYear">
              <option value="t2025">Tahun 2025 (Baseline)</option>
              <option value="t2026">Tahun 2026 (Tahun Berjalan)</option>
              <option value="t2027">Tahun 2027</option>
              <option value="t2028">Tahun 2028</option>
              <option value="t2029">Tahun 2029</option>
              <option value="t2030">Tahun 2030</option>
              <option value="akhir">Target Akhir Renstra</option>
            </select>
          </div>

          <!-- Quick Search -->
          <div class="control-box search-box">
            <label class="control-label">Pencarian Cepat:</label>
            <div class="search-input-wrap">
              <svg class="search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input
                type="text"
                class="control-input"
                v-model="searchQuery"
                placeholder="Cari OPD, Tujuan, Sasaran, atau Indikator..."
              />
              <button
                v-if="searchQuery"
                type="button"
                class="btn-clear-search"
                @click="searchQuery = ''"
                title="Hapus pencarian"
              >
                &times;
              </button>
            </div>
          </div>
        </div>

        <!-- Summary Stats Banner -->
        <div class="stats-counter-strip">
          <div class="stat-item">
            <span class="stat-label">Total Perangkat Daerah:</span>
            <span class="stat-value">{{ filteredOpdCount }} OPD</span>
          </div>
          <div class="stat-dot">&bull;</div>
          <div class="stat-item">
            <span class="stat-label">Total Indikator IKU:</span>
            <span class="stat-value highlighted">{{ filteredIndicators.length }} Indikator</span>
          </div>
          <div class="stat-dot">&bull;</div>
          <div class="stat-item">
            <span class="stat-label">Tujuan IKU:</span>
            <span class="stat-value">{{ countByLevel('Tujuan') }}</span>
          </div>
          <div class="stat-dot">&bull;</div>
          <div class="stat-item">
            <span class="stat-label">Sasaran IKU:</span>
            <span class="stat-value">{{ countByLevel('Sasaran') }}</span>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="report-loading-card">
        <div class="spinner-civic"></div>
        <p>Memuat Daftar Indikator Kinerja Utama (IKU) Perangkat Daerah...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="report-error-card">
        <p>{{ error }}</p>
        <button type="button" class="btn-retry" @click="fetchReport">Muat Ulang</button>
      </div>

      <!-- Document Sheet Preview Container -->
      <div v-else class="document-sheet-container">
        <!-- Sheet Header Title Block -->
        <div class="sheet-title-block">
          <div class="sheet-title-badge">LAPORAN 6</div>
          <h3 class="sheet-title-heading">
            DAFTAR INDIKATOR KINERJA UTAMA (IKU) PERANGKAT DAERAH
          </h3>
          <div class="sheet-title-sub">PEMERINTAH KOTA TEGAL</div>
          <div class="sheet-title-years">
            Rencana Strategis (RENSTRA) Periode Tahun 2025 - 2030
          </div>
          <div v-if="selectedOpdName" class="badge-opd-filter-active">
            Filter: {{ selectedOpdName }}
          </div>
        </div>

        <!-- Sheet Table -->
        <div class="sheet-table-wrapper">
          <table class="civic-report-table">
            <thead>
              <!-- Header Row 1: Main Columns -->
              <tr class="header-row-primary">
                <th rowspan="2" class="th-no">NO</th>
                <th rowspan="2" class="th-opd">PERANGKAT DAERAH</th>
                <th rowspan="2" class="th-tujuan-sasaran">TUJUAN / SASARAN</th>
                <th rowspan="2" class="th-indikator">INDIKATOR KINERJA UTAMA (IKU)</th>
                <th rowspan="2" class="th-satuan">SATUAN</th>

                <!-- Target Murni Header Group -->
                <th
                  :colspan="viewMode === 'all' ? 7 : 1"
                  class="th-target-murni"
                >
                  <div class="header-group-inner">
                    <span class="badge-header-murni">Murni</span>
                    <span>TARGET MURNI</span>
                    <span v-if="viewMode === 'single'" class="header-year-tag">({{ getYearLabel(selectedYear) }})</span>
                  </div>
                </th>

                <!-- Target Perubahan Header Group -->
                <th
                  :colspan="viewMode === 'all' ? 7 : 1"
                  class="th-target-perubahan"
                >
                  <div class="header-group-inner">
                    <span class="badge-header-perub">Perubahan</span>
                    <span>TARGET PERUBAHAN</span>
                    <span v-if="viewMode === 'single'" class="header-year-tag">({{ getYearLabel(selectedYear) }})</span>
                  </div>
                </th>

                <th rowspan="2" class="th-status">STATUS</th>
              </tr>

              <!-- Header Row 2: Sub-headers for Years (Only in 'all' mode) -->
              <tr class="header-row-primary header-row-sub">
                <template v-if="viewMode === 'all'">
                  <!-- Target Murni Years -->
                  <th class="th-year">2025</th>
                  <th class="th-year">2026</th>
                  <th class="th-year">2027</th>
                  <th class="th-year">2028</th>
                  <th class="th-year">2029</th>
                  <th class="th-year">2030</th>
                  <th class="th-year th-year-final">Akhir</th>

                  <!-- Target Perubahan Years -->
                  <th class="th-year th-p">2025</th>
                  <th class="th-year th-p">2026</th>
                  <th class="th-year th-p">2027</th>
                  <th class="th-year th-p">2028</th>
                  <th class="th-year th-p">2029</th>
                  <th class="th-year th-p">2030</th>
                  <th class="th-year th-year-final th-p">Akhir</th>
                </template>
                <template v-else>
                  <th class="th-year-single">{{ getYearLabel(selectedYear) }}</th>
                  <th class="th-year-single th-p">{{ getYearLabel(selectedYear) }}</th>
                </template>
              </tr>

              <!-- Header Row 3: Column Numbers -->
              <tr class="header-row-num">
                <th>(1)</th>
                <th>(2)</th>
                <th>(3)</th>
                <th>(4)</th>
                <th>(5)</th>
                <template v-if="viewMode === 'all'">
                  <th>(6)</th>
                  <th>(7)</th>
                  <th>(8)</th>
                  <th>(9)</th>
                  <th>(10)</th>
                  <th>(11)</th>
                  <th>(12)</th>
                  <th>(13)</th>
                  <th>(14)</th>
                  <th>(15)</th>
                  <th>(16)</th>
                  <th>(17)</th>
                  <th>(18)</th>
                  <th>(19)</th>
                  <th>(20)</th>
                </template>
                <template v-else>
                  <th>(6)</th>
                  <th>(7)</th>
                  <th>(8)</th>
                </template>
              </tr>
            </thead>

            <tbody>
              <!-- Empty State -->
              <tr v-if="filteredGroupedOpds.length === 0">
                <td :colspan="viewMode === 'all' ? 20 : 8" class="td-empty">
                  Tidak ditemukan data IKU yang sesuai dengan filter atau kata kunci pencarian.
                </td>
              </tr>

              <!-- Loop Groups per OPD -->
              <template v-for="(group, gIdx) in filteredGroupedOpds" :key="'opd_' + group.id_skpd">
                <tr
                  v-for="(ind, indIdx) in group.indicators"
                  :key="'ind_' + ind.id_indikator + '_' + indIdx"
                  class="row-iku-item"
                  :class="{ 'row-zebra': (calculateGlobalIndex(gIdx, indIdx) % 2 === 0) }"
                >
                  <!-- Col 1: No -->
                  <td class="td-no-col">
                    {{ calculateGlobalIndex(gIdx, indIdx) }}
                  </td>

                  <!-- Col 2: Perangkat Daerah (Merged across all indicators of this OPD) -->
                  <td
                    v-if="indIdx === 0"
                    :rowspan="group.indicators.length"
                    class="td-opd-name"
                  >
                    <div class="opd-name-wrap">
                      <div class="opd-icon-circle">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                          <path d="M3 21h18"/>
                          <path d="M5 21V7l8-4v18"/>
                          <path d="M19 21V11l-6-4"/>
                          <path d="M9 9h1"/>
                          <path d="M9 13h1"/>
                          <path d="M9 17h1"/>
                        </svg>
                      </div>
                      <div>
                        <div class="opd-title">{{ group.nama_skpd }}</div>
                        <div class="opd-meta-sub">
                          <span class="badge-total-opd-iku">{{ group.indicators.length }} IKU</span>
                        </div>
                      </div>
                    </div>
                  </td>

                  <!-- Col 3: Tujuan / Sasaran -->
                  <td class="td-tujuan-sasaran">
                    <div class="ts-level-tag" :class="ind.level.toLowerCase()">
                      {{ ind.level }}
                    </div>
                    <div class="ts-text">{{ ind.tujuan_sasaran }}</div>
                  </td>

                  <!-- Col 4: Indikator Kinerja Utama -->
                  <td class="td-indikator">
                    <div class="ind-main-row">
                      <span class="iku-badge-pill">IKU</span>
                      <span class="ind-text">{{ ind.indikator }}</span>
                    </div>
                    <div v-if="ind.definisi_operasional" class="ind-definisi-tooltip">
                      <span class="definisi-icon">ℹ</span>
                      <span>{{ ind.definisi_operasional }}</span>
                    </div>
                  </td>

                  <!-- Col 5: Satuan -->
                  <td class="td-satuan">{{ ind.satuan || '-' }}</td>

                  <!-- Mode All: Columns 6 to 12 (Target Murni) -->
                  <template v-if="viewMode === 'all'">
                    <td class="td-target">{{ ind.target_murni?.t2025 || '-' }}</td>
                    <td class="td-target">{{ ind.target_murni?.t2026 || '-' }}</td>
                    <td class="td-target">{{ ind.target_murni?.t2027 || '-' }}</td>
                    <td class="td-target">{{ ind.target_murni?.t2028 || '-' }}</td>
                    <td class="td-target">{{ ind.target_murni?.t2029 || '-' }}</td>
                    <td class="td-target">{{ ind.target_murni?.t2030 || '-' }}</td>
                    <td class="td-target td-target-final">{{ ind.target_murni?.akhir || '-' }}</td>

                    <!-- Columns 13 to 19 (Target Perubahan) -->
                    <td class="td-target td-target-perub">{{ ind.target_perubahan?.t2025 || '-' }}</td>
                    <td class="td-target td-target-perub">{{ ind.target_perubahan?.t2026 || '-' }}</td>
                    <td class="td-target td-target-perub">{{ ind.target_perubahan?.t2027 || '-' }}</td>
                    <td class="td-target td-target-perub">{{ ind.target_perubahan?.t2028 || '-' }}</td>
                    <td class="td-target td-target-perub">{{ ind.target_perubahan?.t2029 || '-' }}</td>
                    <td class="td-target td-target-perub">{{ ind.target_perubahan?.t2030 || '-' }}</td>
                    <td class="td-target td-target-perub td-target-final">{{ ind.target_perubahan?.akhir || '-' }}</td>
                  </template>

                  <!-- Mode Single: 1 Col Murni & 1 Col Perubahan -->
                  <template v-else>
                    <td class="td-target td-target-single">
                      {{ ind.target_murni?.[selectedYear] || '-' }}
                    </td>
                    <td class="td-target td-target-perub td-target-single">
                      {{ ind.target_perubahan?.[selectedYear] || '-' }}
                    </td>
                  </template>

                  <!-- Status Column -->
                  <td class="td-status">
                    <span
                      class="badge-status-perubahan"
                      :class="getStatusClass(ind.target_perubahan?.status)"
                    >
                      {{ formatStatusLabel(ind.target_perubahan?.status) }}
                    </span>
                  </td>
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();

const loading = ref(false);
const exporting = ref(false);
const error = ref(null);
const reportData = ref(null);

const selectedOpdId = ref(null);
const viewMode = ref('all'); // 'all' or 'single'
const selectedYear = ref('t2026'); // t2025, t2026, t2027, t2028, t2029, t2030, akhir
const searchQuery = ref('');

function goBack() {
  router.push('/');
}

async function fetchReport() {
  loading.value = true;
  error.value = null;
  try {
    const data = await api.getLaporanDaftarIku();
    reportData.value = data;
  } catch (err) {
    console.error('Gagal memuat laporan Daftar IKU:', err);
    error.value = err.message || 'Gagal memuat data laporan Daftar IKU';
  } finally {
    loading.value = false;
  }
}

const availableOpds = computed(() => {
  return reportData.value?.opd_groups || [];
});

const totalOpdCount = computed(() => {
  return availableOpds.value.length;
});

const selectedOpdName = computed(() => {
  if (!selectedOpdId.value) return null;
  const match = availableOpds.value.find(o => o.id_skpd === selectedOpdId.value);
  return match?.nama_skpd || null;
});

// Filter indicators based on selected OPD and search query
const filteredGroupedOpds = computed(() => {
  if (!reportData.value?.opd_groups) return [];

  const q = searchQuery.value.trim().toLowerCase();
  const opdFilter = selectedOpdId.value;

  const result = [];

  for (const group of reportData.value.opd_groups) {
    if (opdFilter && group.id_skpd !== opdFilter) {
      continue;
    }

    const filteredIndicators = group.indicators.filter(ind => {
      if (!q) return true;
      const opdMatch = group.nama_skpd.toLowerCase().includes(q);
      const tsMatch = (ind.tujuan_sasaran || '').toLowerCase().includes(q);
      const indMatch = (ind.indikator || '').toLowerCase().includes(q);
      const satMatch = (ind.satuan || '').toLowerCase().includes(q);
      return opdMatch || tsMatch || indMatch || satMatch;
    });

    if (filteredIndicators.length > 0) {
      result.push({
        ...group,
        indicators: filteredIndicators,
      });
    }
  }

  return result;
});

const filteredIndicators = computed(() => {
  return filteredGroupedOpds.value.flatMap(g => g.indicators);
});

const filteredOpdCount = computed(() => {
  return filteredGroupedOpds.value.length;
});

function countByLevel(level) {
  return filteredIndicators.value.filter(ind => ind.level === level).length;
}

function calculateGlobalIndex(targetGroupIdx, indIdx) {
  let count = 0;
  for (let i = 0; i < targetGroupIdx; i++) {
    count += filteredGroupedOpds.value[i].indicators.length;
  }
  return count + indIdx + 1;
}

function getYearLabel(yearKey) {
  const map = {
    t2025: '2025',
    t2026: '2026',
    t2027: '2027',
    t2028: '2028',
    t2029: '2029',
    t2030: '2030',
    akhir: 'Akhir',
  };
  return map[yearKey] || yearKey;
}

function getStatusClass(status) {
  if (!status || status === 'tetap') return 'status-tetap';
  if (status === 'bertambah') return 'status-bertambah';
  if (status === 'berkurang') return 'status-berkurang';
  return 'status-ubah';
}

function formatStatusLabel(status) {
  if (!status || status === 'tetap') return 'Tetap';
  if (status === 'bertambah') return 'Bertambah';
  if (status === 'berkurang') return 'Berkurang';
  return status;
}

async function handleExportExcel() {
  exporting.value = true;
  try {
    const yearParam = viewMode.value === 'single' ? selectedYear.value : null;
    await api.downloadLaporanDaftarIkuExcel(selectedOpdId.value, yearParam);
  } catch (err) {
    console.error('Gagal export excel:', err);
    alert('Gagal mengunduh file Excel: ' + err.message);
  } finally {
    exporting.value = false;
  }
}

onMounted(() => {
  fetchReport();
});
</script>

<style scoped>
.report-page-container {
  padding: 1.5rem 1rem 3rem 1rem;
  min-height: calc(100vh - 72px);
  background: #f8fafc;
}

.app-container {
  max-width: 1720px;
  margin: 0 auto;
}

/* Toolbar Card */
.report-toolbar-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  padding: 1.4rem 1.6rem;
  margin-bottom: 1.5rem;
}

.toolbar-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.btn-toolbar-back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
  padding: 0.55rem 0.9rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-toolbar-back:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.badge-report-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  margin-bottom: 0.35rem;
}

.badge-no {
  color: #2563eb;
}

.badge-dot {
  opacity: 0.5;
}

.report-main-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.01em;
}

.report-main-desc {
  font-size: 0.82rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.btn-export-excel {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  background: #047857;
  color: #ffffff;
  border: none;
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(4, 120, 87, 0.2);
  transition: all 0.15s;
}

.btn-export-excel:hover:not(:disabled) {
  background: #065f46;
  box-shadow: 0 4px 6px rgba(4, 120, 87, 0.3);
  transform: translateY(-1px);
}

.btn-export-excel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Controls Grid */
.toolbar-controls-grid {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
  flex-wrap: wrap;
}

.control-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.control-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.control-select {
  padding: 0.55rem 0.85rem;
  font-size: 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  color: #1e293b;
  min-width: 220px;
  transition: border-color 0.15s;
}

.control-select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.opd-select {
  min-width: 340px;
}

.year-select {
  min-width: 170px;
}

/* View Mode Switcher */
.view-mode-group {
  display: flex;
  background: #f1f5f9;
  padding: 0.2rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.btn-view-mode {
  background: transparent;
  border: none;
  padding: 0.45rem 0.8rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-view-mode.active {
  background: #ffffff;
  color: #1e40af;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Search Box */
.search-box {
  flex: 1;
  min-width: 260px;
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
}

.control-input {
  width: 100%;
  padding: 0.55rem 2rem 0.55rem 2.2rem;
  font-size: 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #1e293b;
  transition: border-color 0.15s;
}

.control-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.btn-clear-search {
  position: absolute;
  right: 0.6rem;
  background: transparent;
  border: none;
  font-size: 1.1rem;
  color: #94a3b8;
  cursor: pointer;
}

/* Stats Counter Strip */
.stats-counter-strip {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem 0.9rem;
  margin-top: 1rem;
  font-size: 0.78rem;
  color: #475569;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.stat-label {
  color: #64748b;
}

.stat-value {
  font-weight: 700;
  color: #1e293b;
}

.stat-value.highlighted {
  color: #2563eb;
}

.stat-dot {
  color: #cbd5e1;
}

/* Loading & Error Cards */
.report-loading-card,
.report-error-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 3rem;
  text-align: center;
  color: #64748b;
}

.spinner-civic {
  width: 36px;
  height: 36px;
  border: 3.5px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem auto;
}

.spin-icon {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Sheet Container */
.document-sheet-container {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.sheet-title-block {
  padding: 1.8rem 1.5rem 1.4rem 1.5rem;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  border-bottom: 2px solid #e2e8f0;
  text-align: center;
}

.sheet-title-badge {
  display: inline-block;
  background: #1e3a8a;
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  padding: 0.18rem 0.6rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.sheet-title-heading {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.01em;
}

.sheet-title-sub {
  font-size: 0.95rem;
  font-weight: 700;
  color: #334155;
  margin-top: 0.2rem;
}

.sheet-title-years {
  font-size: 0.82rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.badge-opd-filter-active {
  display: inline-block;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.75rem;
  border-radius: 9999px;
  margin-top: 0.6rem;
}

/* Sheet Table */
.sheet-table-wrapper {
  overflow-x: auto;
  max-width: 100%;
}

.civic-report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
  border-spacing: 0;
}

/* Header Rows */
.header-row-primary th {
  background: #1e3a8a;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.78rem;
  text-align: center;
  padding: 0.65rem 0.55rem;
  border: 1px solid #3b82f6;
  white-space: nowrap;
}

.header-row-sub th {
  font-size: 0.74rem;
  padding: 0.45rem 0.4rem;
}

.th-target-murni {
  background: #1e40af !important;
  border-bottom: 1px solid #60a5fa !important;
}

.th-target-perubahan {
  background: #047857 !important;
  border-color: #34d399 !important;
}

.header-group-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

.badge-header-murni {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.68rem;
}

.badge-header-perub {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.68rem;
}

.header-year-tag {
  font-weight: 400;
  opacity: 0.9;
}

.th-p {
  background: #065f46 !important;
  border-color: #059669 !important;
}

.header-row-num th {
  background: #334155;
  color: #e2e8f0;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.3rem;
  border: 1px solid #475569;
}

/* Data Cells */
.civic-report-table td {
  border: 1px solid #cbd5e1;
  padding: 0.6rem 0.7rem;
  vertical-align: middle;
  line-height: 1.4;
  color: #1e293b;
}

.row-zebra td {
  background-color: #f8fafc;
}

.td-no-col {
  text-align: center;
  font-weight: 700;
  color: #475569;
  background: #f1f5f9;
  width: 44px;
}

/* OPD Name Column */
.td-opd-name {
  background: #ffffff !important;
  vertical-align: top !important;
  min-width: 220px;
  max-width: 260px;
  border-right: 2px solid #cbd5e1 !important;
}

.opd-name-wrap {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.2rem 0;
}

.opd-icon-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #eff6ff;
  color: #1d4ed8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 0.15rem;
}

.opd-title {
  font-weight: 700;
  font-size: 0.85rem;
  color: #0f172a;
}

.opd-meta-sub {
  margin-top: 0.3rem;
}

.badge-total-opd-iku {
  display: inline-block;
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
}

/* Tujuan / Sasaran Column */
.td-tujuan-sasaran {
  min-width: 240px;
  max-width: 300px;
}

.ts-level-tag {
  display: inline-block;
  font-size: 0.66rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.12rem 0.45rem;
  border-radius: 4px;
  margin-bottom: 0.25rem;
  letter-spacing: 0.04em;
}

.ts-level-tag.tujuan {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.ts-level-tag.sasaran {
  background: #fdf4ff;
  color: #86198f;
  border: 1px solid #f0abfc;
}

.ts-text {
  font-size: 0.82rem;
  color: #334155;
  font-weight: 500;
}

/* Indikator Column */
.td-indikator {
  min-width: 260px;
  max-width: 340px;
}

.ind-main-row {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
}

.iku-badge-pill {
  background: #1e3a8a;
  color: #ffffff;
  font-size: 0.64rem;
  font-weight: 800;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  flex-shrink: 0;
  margin-top: 0.15rem;
}

.ind-text {
  font-weight: 600;
  color: #0f172a;
  font-size: 0.84rem;
}

.ind-definisi-tooltip {
  margin-top: 0.35rem;
  font-size: 0.72rem;
  color: #64748b;
  display: flex;
  align-items: flex-start;
  gap: 0.3rem;
  line-height: 1.35;
  background: #f8fafc;
  padding: 0.3rem 0.45rem;
  border-radius: 4px;
  border-left: 2px solid #94a3b8;
}

.definisi-icon {
  font-size: 0.75rem;
  color: #3b82f6;
  font-weight: bold;
}

/* Satuan Column */
.td-satuan {
  text-align: center;
  font-weight: 600;
  color: #475569;
  font-size: 0.78rem;
  width: 75px;
}

/* Target Columns */
.td-target {
  text-align: center;
  font-weight: 500;
  font-size: 0.82rem;
  color: #1e293b;
  width: 70px;
}

.td-target-final {
  font-weight: 700;
  background: rgba(30, 64, 175, 0.04);
}

.td-target-perub {
  background: rgba(4, 120, 87, 0.03);
}

.td-target-single {
  font-size: 0.92rem;
  font-weight: 700;
  width: 110px;
}

/* Status Column */
.td-status {
  text-align: center;
  width: 95px;
}

.badge-status-perubahan {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.18rem 0.5rem;
  border-radius: 9999px;
  white-space: nowrap;
}

.status-tetap {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.status-bertambah {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.status-berkurang {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.status-ubah {
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
}

.td-empty {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  font-style: italic;
  font-size: 0.9rem;
}
</style>

