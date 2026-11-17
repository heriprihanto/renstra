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
                <span class="badge-no">Laporan #7</span>
                <span class="badge-dot">&bull;</span>
                <span>RENSTRA 2026 - 2030</span>
              </div>
              <h2 class="report-main-title">Pagu RPJMD vs Renstra</h2>
              <div class="report-main-desc">
                Komparasi Pagu Program RPJMD vs Renstra (Pagu Murni &amp; Pagu Perubahan) serta Penandaan Selisih Anggaran
              </div>
            </div>
          </div>

          <div class="toolbar-actions">
            <!-- Export Excel Button -->
            <button
              type="button"
              class="btn-export-excel"
              :disabled="loading || exporting || totalDisplayPrograms === 0"
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
              @change="fetchData"
            >
              <option :value="null">-- Semua Perangkat Daerah (Kota Tegal) --</option>
              <option v-for="opd in opdList" :key="opd.id_skpd" :value="opd.id_skpd">
                {{ opd.kode_skpd }} - {{ opd.nama_skpd }}
              </option>
            </select>
          </div>

          <!-- Filter Status Selisih -->
          <div class="control-box">
            <label class="control-label">Status Kesesuaian:</label>
            <select
              class="control-select status-select"
              v-model="statusFilter"
              :disabled="loading"
            >
              <option value="all">Semua Program ({{ reportSummary.total_programs || 0 }})</option>
              <option value="diff">Hanya Selisih / Tidak Sama ({{ reportSummary.total_discrepancies || 0 }})</option>
              <option value="match">Hanya Sesuai RPJMD ({{ reportSummary.total_matched || 0 }})</option>
            </select>
          </div>

          <!-- Filter Tahun Tampilan -->
          <div class="control-box">
            <label class="control-label">Tampilan Tahun:</label>
            <select
              class="control-select year-select"
              v-model="selectedYearView"
            >
              <option value="all">Semua Tahun (2026 - 2030)</option>
              <option value="2026">Tahun 2026</option>
              <option value="2027">Tahun 2027</option>
              <option value="2028">Tahun 2028</option>
              <option value="2029">Tahun 2029</option>
              <option value="2030">Tahun 2030</option>
            </select>
          </div>

          <!-- Live Search -->
          <div class="control-box search-box">
            <label class="control-label">Cari Program / Sub Unit:</label>
            <div class="search-input-wrap">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input
                type="text"
                class="control-input"
                v-model="searchQuery"
                placeholder="Ketik nama / kode program..."
              />
              <button
                v-if="searchQuery"
                type="button"
                class="btn-clear-search"
                @click="searchQuery = ''"
              >
                &times;
              </button>
            </div>
          </div>
        </div>

        <!-- Legend & Notice -->
        <div class="legend-card">
          <div class="legend-item">
            <span class="legend-color legend-murni"></span>
            <span class="legend-text"><strong>Pagu Murni</strong> (pagu1 - pagu5)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color legend-perubahan"></span>
            <span class="legend-text"><strong>Pagu Perubahan</strong> (p_pagu1 - p_pagu5)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color legend-rpjmd"></span>
            <span class="legend-text"><strong>Pagu RPJMD</strong> (t1 - t5)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color legend-diff"></span>
            <span class="legend-text"><strong>Ditandai Merah / Kuning:</strong> Pagu Perubahan &ne; RPJMD</span>
          </div>
          <div class="legend-item">
            <span class="legend-color legend-match"></span>
            <span class="legend-text"><strong>Hijau:</strong> Sesuai RPJMD</span>
          </div>
        </div>
      </div>

      <!-- Summary KPI Metric Cards -->
      <div class="metric-cards-grid" v-if="!loading && opdGroups.length > 0">
        <div class="kpi-card card-total">
          <div class="kpi-icon-wrap bg-blue-subtle">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 11l3 3L22 4"/>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
          </div>
          <div class="kpi-content">
            <span class="kpi-label">Total Program</span>
            <span class="kpi-value text-blue-dark">{{ reportSummary.total_programs || 0 }}</span>
            <span class="kpi-sub">Program dianalisis</span>
          </div>
        </div>

        <div class="kpi-card card-diff">
          <div class="kpi-icon-wrap bg-red-subtle">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="kpi-content">
            <span class="kpi-label">Pagu Selisih (Tidak Sama)</span>
            <span class="kpi-value text-red">{{ reportSummary.total_discrepancies || 0 }}</span>
            <span class="kpi-sub text-red">Perlu penyesuaian / verifikasi</span>
          </div>
        </div>

        <div class="kpi-card card-match">
          <div class="kpi-icon-wrap bg-green-subtle">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="kpi-content">
            <span class="kpi-label">Sesuai RPJMD</span>
            <span class="kpi-value text-green">{{ reportSummary.total_matched || 0 }}</span>
            <span class="kpi-sub text-green">Pagu Perubahan = Pagu RPJMD</span>
          </div>
        </div>

        <div class="kpi-card card-budget">
          <div class="kpi-icon-wrap bg-purple-subtle">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="1" x2="12" y2="23"/>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
          </div>
          <div class="kpi-content">
            <span class="kpi-label">Total Pagu Perubahan (2026-2030)</span>
            <span class="kpi-value text-purple">{{ formatCurrencyShort(reportSummary.grand_total_perubahan) }}</span>
            <span class="kpi-sub">RPJMD: {{ formatCurrencyShort(reportSummary.grand_total_rpjmd) }}</span>
          </div>
        </div>
      </div>

      <!-- Main Content / Table Area -->
      <div class="report-table-card">
        <!-- Loading State -->
        <div v-if="loading" class="state-loading">
          <div class="spinner"></div>
          <p class="state-text">Memuat data komparasi Pagu RPJMD vs Renstra...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="errorMessage" class="state-error">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <p class="error-msg">{{ errorMessage }}</p>
          <button type="button" class="btn-retry" @click="fetchData">Coba Lagi</button>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredOpdGroups.length === 0" class="state-empty">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <circle cx="11" cy="13" r="3"/>
          </svg>
          <p class="empty-title">Tidak ada data program ditemukan</p>
          <p class="empty-desc">Silakan sesuaikan filter OPD, status, atau kata kunci pencarian Anda.</p>
        </div>

        <!-- Table Display -->
        <div v-else class="table-responsive-container">
          <table class="report-table">
            <thead>
              <!-- Top Header Row -->
              <tr class="tr-top-header">
                <th rowspan="2" class="th-no">NO</th>
                <th rowspan="2" class="th-prog">KODE &amp; NAMA PROGRAM</th>
                <th rowspan="2" class="th-subunit">SUB UNIT</th>
                
                <!-- Year columns (All or Selected) -->
                <template v-if="selectedYearView === 'all'">
                  <th colspan="4" class="th-year-group" v-for="y in ['2026', '2027', '2028', '2029', '2030']" :key="y">
                    TAHUN {{ y }}
                  </th>
                  <th colspan="4" class="th-total-group">TOTAL (2026 - 2030)</th>
                </template>
                <template v-else>
                  <th colspan="4" class="th-year-group th-active-single">
                    TAHUN {{ selectedYearView }}
                  </th>
                  <th colspan="4" class="th-total-group">TOTAL (2026 - 2030)</th>
                </template>

                <th rowspan="2" class="th-status">STATUS</th>
              </tr>

              <!-- Sub Header Row -->
              <tr class="tr-sub-header">
                <!-- Years -->
                <template v-if="selectedYearView === 'all'">
                  <template v-for="y in ['2026', '2027', '2028', '2029', '2030']" :key="'sub-' + y">
                    <th class="th-val">Murni</th>
                    <th class="th-val th-perub">Perubahan</th>
                    <th class="th-val th-rpjmd">RPJMD</th>
                    <th class="th-val th-selisih">Selisih</th>
                  </template>
                </template>
                <template v-else>
                  <th class="th-val">Murni</th>
                  <th class="th-val th-perub">Perubahan</th>
                  <th class="th-val th-rpjmd">RPJMD</th>
                  <th class="th-val th-selisih">Selisih</th>
                </template>

                <!-- Total -->
                <th class="th-val th-tot">Murni</th>
                <th class="th-val th-tot th-perub">Perubahan</th>
                <th class="th-val th-tot th-rpjmd">RPJMD</th>
                <th class="th-val th-tot th-selisih">Selisih</th>
              </tr>
            </thead>

            <tbody>
              <template v-for="(opd, opdIdx) in filteredOpdGroups" :key="opd.id_skpd">
                <!-- OPD Group Header Row -->
                <tr class="tr-opd-group">
                  <td :colspan="columnCount" class="td-opd-title">
                    <div class="opd-title-flex">
                      <span class="opd-badge-code">{{ opd.kode_skpd }}</span>
                      <span class="opd-name">{{ opd.nama_skpd }}</span>
                      <div class="opd-stats-pills">
                        <span class="badge-pill-count">{{ opd.programs.length }} Program</span>
                        <span v-if="opd.discrepancy_count > 0" class="badge-pill-diff">
                          {{ opd.discrepancy_count }} Selisih
                        </span>
                        <span v-else class="badge-pill-ok">
                          Semua Sesuai
                        </span>
                      </div>
                    </div>
                  </td>
                </tr>

                <!-- Program Rows under this OPD -->
                <tr
                  v-for="(prog, progIdx) in opd.programs"
                  :key="prog.kodeprogram + '-' + (prog.kode_sub_skpd || '')"
                  :class="['tr-program-row', { 'tr-has-diff': prog.has_discrepancy }]"
                >
                  <!-- No -->
                  <td class="td-no">{{ getGlobalRowIndex(opdIdx, progIdx) }}</td>

                  <!-- Kode & Nama Program -->
                  <td class="td-program">
                    <div class="prog-info-wrap">
                      <span class="prog-code">{{ prog.kodeprogram }}</span>
                      <span class="prog-name">{{ prog.uraiprogram }}</span>
                    </div>
                  </td>

                  <!-- Sub Unit -->
                  <td class="td-subunit">
                    <span
                      class="subunit-tag"
                      :class="{ 'subunit-distinct': prog.nama_sub_skpd && prog.nama_sub_skpd !== prog.nama_skpd }"
                    >
                      {{ prog.nama_sub_skpd || prog.nama_skpd }}
                    </span>
                  </td>

                  <!-- Year Breakdown Columns -->
                  <template v-if="selectedYearView === 'all'">
                    <template v-for="y in ['2026', '2027', '2028', '2029', '2030']" :key="y">
                      <!-- Murni -->
                      <td class="td-currency td-murni">
                        {{ formatCurrency(prog.years[y]?.murni) }}
                      </td>

                      <!-- Perubahan (Tandai jika beda dengan RPJMD) -->
                      <td
                        class="td-currency td-perubahan"
                        :class="{ 'cell-diff-alert': prog.years[y]?.is_diff }"
                      >
                        <div class="val-with-mark">
                          <span>{{ formatCurrency(prog.years[y]?.perubahan) }}</span>
                          <span
                            v-if="prog.years[y]?.is_diff"
                            class="pill-diff-indicator"
                            title="Pagu Perubahan tidak sama dengan RPJMD"
                          >
                            &ne; RPJMD
                          </span>
                        </div>
                      </td>

                      <!-- RPJMD -->
                      <td class="td-currency td-rpjmd">
                        {{ formatCurrency(prog.years[y]?.rpjmd) }}
                      </td>

                      <!-- Selisih -->
                      <td
                        class="td-currency td-selisih"
                        :class="{ 'text-diff-negative': prog.years[y]?.selisih < 0, 'text-diff-positive': prog.years[y]?.selisih > 0 }"
                      >
                        {{ formatCurrency(prog.years[y]?.selisih) }}
                      </td>
                    </template>
                  </template>

                  <!-- Single Year Selected -->
                  <template v-else>
                    <!-- Murni -->
                    <td class="td-currency td-murni">
                      {{ formatCurrency(prog.years[selectedYearView]?.murni) }}
                    </td>

                    <!-- Perubahan -->
                    <td
                      class="td-currency td-perubahan"
                      :class="{ 'cell-diff-alert': prog.years[selectedYearView]?.is_diff }"
                    >
                      <div class="val-with-mark">
                        <span>{{ formatCurrency(prog.years[selectedYearView]?.perubahan) }}</span>
                        <span
                          v-if="prog.years[selectedYearView]?.is_diff"
                          class="pill-diff-indicator"
                          title="Pagu Perubahan tidak sama dengan RPJMD"
                        >
                          &ne; RPJMD
                        </span>
                      </div>
                    </td>

                    <!-- RPJMD -->
                    <td class="td-currency td-rpjmd">
                      {{ formatCurrency(prog.years[selectedYearView]?.rpjmd) }}
                    </td>

                    <!-- Selisih -->
                    <td
                      class="td-currency td-selisih"
                      :class="{ 'text-diff-negative': prog.years[selectedYearView]?.selisih < 0, 'text-diff-positive': prog.years[selectedYearView]?.selisih > 0 }"
                    >
                      {{ formatCurrency(prog.years[selectedYearView]?.selisih) }}
                    </td>
                  </template>

                  <!-- Total 2026-2030 -->
                  <td class="td-currency td-total-murni">
                    {{ formatCurrency(prog.total_murni) }}
                  </td>
                  <td
                    class="td-currency td-total-perubahan"
                    :class="{ 'cell-diff-alert': prog.has_discrepancy }"
                  >
                    {{ formatCurrency(prog.total_perubahan) }}
                  </td>
                  <td class="td-currency td-total-rpjmd">
                    {{ formatCurrency(prog.total_rpjmd) }}
                  </td>
                  <td
                    class="td-currency td-total-selisih"
                    :class="{ 'text-diff-negative': prog.total_selisih < 0, 'text-diff-positive': prog.total_selisih > 0 }"
                  >
                    {{ formatCurrency(prog.total_selisih) }}
                  </td>

                  <!-- Status Column -->
                  <td class="td-status">
                    <span v-if="prog.has_discrepancy" class="badge-status badge-diff">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                      </svg>
                      <span>Selisih ({{ prog.discrepancy_years.join(', ') }})</span>
                    </span>
                    <span v-else class="badge-status badge-match">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      <span>Sesuai RPJMD</span>
                    </span>
                  </td>
                </tr>
              </template>
            </tbody>

            <!-- Table Footer Grand Total -->
            <tfoot>
              <tr class="tr-grand-total">
                <td colspan="3" class="td-total-label">TOTAL KESELURUHAN (KOTA TEGAL)</td>
                
                <template v-if="selectedYearView === 'all'">
                  <template v-for="y in ['2026', '2027', '2028', '2029', '2030']" :key="'foot-' + y">
                    <td class="td-currency td-foot-val">{{ formatCurrency(footTotals[y]?.murni) }}</td>
                    <td class="td-currency td-foot-val">{{ formatCurrency(footTotals[y]?.perubahan) }}</td>
                    <td class="td-currency td-foot-val">{{ formatCurrency(footTotals[y]?.rpjmd) }}</td>
                    <td class="td-currency td-foot-val">{{ formatCurrency(footTotals[y]?.selisih) }}</td>
                  </template>
                </template>
                <template v-else>
                  <td class="td-currency td-foot-val">{{ formatCurrency(footTotals[selectedYearView]?.murni) }}</td>
                  <td class="td-currency td-foot-val">{{ formatCurrency(footTotals[selectedYearView]?.perubahan) }}</td>
                  <td class="td-currency td-foot-val">{{ formatCurrency(footTotals[selectedYearView]?.rpjmd) }}</td>
                  <td class="td-currency td-foot-val">{{ formatCurrency(footTotals[selectedYearView]?.selisih) }}</td>
                </template>

                <td class="td-currency td-foot-val">{{ formatCurrency(reportSummary.grand_total_murni) }}</td>
                <td class="td-currency td-foot-val">{{ formatCurrency(reportSummary.grand_total_perubahan) }}</td>
                <td class="td-currency td-foot-val">{{ formatCurrency(reportSummary.grand_total_rpjmd) }}</td>
                <td class="td-currency td-foot-val">{{ formatCurrency(reportSummary.grand_total_selisih) }}</td>

                <td class="td-foot-status"></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

export default {
  name: 'RpjmdVsRenstraReportView',
  setup() {
    const router = useRouter();

    const loading = ref(false);
    const exporting = ref(false);
    const errorMessage = ref('');

    const opdList = ref([]);
    const selectedOpdId = ref(null);
    const statusFilter = ref('all'); // all, diff, match
    const selectedYearView = ref('all'); // all, 2026, 2027, 2028, 2029, 2030
    const searchQuery = ref('');

    const reportSummary = ref({
      total_programs: 0,
      total_discrepancies: 0,
      total_matched: 0,
      grand_total_murni: 0,
      grand_total_perubahan: 0,
      grand_total_rpjmd: 0,
      grand_total_selisih: 0,
    });
    const opdGroups = ref([]);

    // Column count calculation for colspan
    const columnCount = computed(() => {
      // 3 fixed (no, prog, subunit) + years cols + total cols (4) + status (1)
      const yearCols = selectedYearView.value === 'all' ? 20 : 4;
      return 3 + yearCols + 4 + 1;
    });

    // Load OPD list
    const loadOpdList = async () => {
      try {
        const list = await api.getOpdList();
        opdList.value = list || [];
      } catch (err) {
        console.error('Failed to load OPD list:', err);
      }
    };

    // Fetch report data
    const fetchData = async () => {
      loading.value = true;
      errorMessage.value = '';
      try {
        const res = await api.getLaporanRpjmdVsRenstra({
          idSkpd: selectedOpdId.value,
          discrepancyOnly: false,
        });
        reportSummary.value = res.summary || {};
        opdGroups.value = res.opd_groups || [];
      } catch (err) {
        console.error('Error fetching Pagu RPJMD vs Renstra report:', err);
        errorMessage.value = err.message || 'Gagal memuat data laporan';
      } finally {
        loading.value = false;
      }
    };

    // Filtered OPD Groups based on status filter & search query
    const filteredOpdGroups = computed(() => {
      const q = searchQuery.value.trim().toLowerCase();
      const status = statusFilter.value;

      const result = [];
      for (const opd of opdGroups.value) {
        const filteredProgs = opd.programs.filter((prog) => {
          // Status filter
          if (status === 'diff' && !prog.has_discrepancy) return false;
          if (status === 'match' && prog.has_discrepancy) return false;

          // Search query
          if (q) {
            const matchProg =
              (prog.kodeprogram && prog.kodeprogram.toLowerCase().includes(q)) ||
              (prog.uraiprogram && prog.uraiprogram.toLowerCase().includes(q)) ||
              (prog.nama_sub_skpd && prog.nama_sub_skpd.toLowerCase().includes(q)) ||
              (opd.nama_skpd && opd.nama_skpd.toLowerCase().includes(q));
            if (!matchProg) return false;
          }

          return true;
        });

        if (filteredProgs.length > 0) {
          result.push({
            ...opd,
            programs: filteredProgs,
          });
        }
      }
      return result;
    });

    const totalDisplayPrograms = computed(() => {
      return filteredOpdGroups.value.reduce((acc, grp) => acc + grp.programs.length, 0);
    });

    // Dynamic sum for footer
    const footTotals = computed(() => {
      const totals = {
        '2026': { murni: 0, perubahan: 0, rpjmd: 0, selisih: 0 },
        '2027': { murni: 0, perubahan: 0, rpjmd: 0, selisih: 0 },
        '2028': { murni: 0, perubahan: 0, rpjmd: 0, selisih: 0 },
        '2029': { murni: 0, perubahan: 0, rpjmd: 0, selisih: 0 },
        '2030': { murni: 0, perubahan: 0, rpjmd: 0, selisih: 0 },
      };

      for (const opd of filteredOpdGroups.value) {
        for (const prog of opd.programs) {
          for (const y of ['2026', '2027', '2028', '2029', '2030']) {
            const yd = prog.years[y] || {};
            totals[y].murni += yd.murni || 0;
            totals[y].perubahan += yd.perubahan || 0;
            totals[y].rpjmd += yd.rpjmd || 0;
            totals[y].selisih += yd.selisih || 0;
          }
        }
      }
      return totals;
    });

    // Helper: calculate global row index
    const getGlobalRowIndex = (targetOpdIdx, progIdx) => {
      let count = 0;
      for (let i = 0; i < targetOpdIdx; i++) {
        count += filteredOpdGroups.value[i].programs.length;
      }
      return count + progIdx + 1;
    };

    // Currency Formatter
    const formatCurrency = (val) => {
      if (val === null || val === undefined) return '-';
      const num = Number(val);
      if (isNaN(num)) return '-';
      return new Intl.NumberFormat('id-ID', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(num);
    };

    const formatCurrencyShort = (val) => {
      if (!val) return 'Rp 0';
      const num = Number(val);
      if (Math.abs(num) >= 1e12) {
        return `Rp ${(num / 1e12).toFixed(2)} T`;
      }
      if (Math.abs(num) >= 1e9) {
        return `Rp ${(num / 1e9).toFixed(2)} M`;
      }
      if (Math.abs(num) >= 1e6) {
        return `Rp ${(num / 1e6).toFixed(2)} Jt`;
      }
      return `Rp ${formatCurrency(num)}`;
    };

    // Export Excel
    const handleExportExcel = async () => {
      exporting.value = true;
      try {
        await api.downloadLaporanRpjmdVsRenstraExcel({
          idSkpd: selectedOpdId.value,
          discrepancyOnly: statusFilter.value === 'diff',
        });
      } catch (err) {
        console.error('Export error:', err);
        alert(`Gagal mengunduh Excel: ${err.message || 'Terjadi kesalahan sistem'}`);
      } finally {
        exporting.value = false;
      }
    };

    const goBack = () => {
      router.back();
    };

    onMounted(() => {
      loadOpdList();
      fetchData();
    });

    return {
      loading,
      exporting,
      errorMessage,
      opdList,
      selectedOpdId,
      statusFilter,
      selectedYearView,
      searchQuery,
      reportSummary,
      opdGroups,
      filteredOpdGroups,
      totalDisplayPrograms,
      columnCount,
      footTotals,
      getGlobalRowIndex,
      formatCurrency,
      formatCurrencyShort,
      handleExportExcel,
      fetchData,
      goBack,
    };
  },
};
</script>

<style scoped>
.report-page-container {
  min-height: calc(100vh - 70px);
  background: #f8fafc;
  padding: 1.5rem 0 3rem 0;
}

.app-container {
  max-width: 1560px;
  margin: 0 auto;
  padding: 0 1.25rem;
}

/* Toolbar & Header */
.report-toolbar-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
  margin-bottom: 1.25rem;
  border: 1px solid #e2e8f0;
}

.toolbar-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
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
  padding: 0.5rem 0.85rem;
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.btn-toolbar-back:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.badge-report-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  margin-bottom: 0.35rem;
}

.report-main-title {
  margin: 0 0 0.25rem 0;
  font-size: 1.45rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.01em;
}

.report-main-desc {
  font-size: 0.86rem;
  color: #64748b;
  line-height: 1.4;
}

.btn-export-excel {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #059669;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 0.65rem 1.25rem;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(5, 150, 105, 0.2);
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-export-excel:hover:not(:disabled) {
  background: #047857;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(5, 150, 105, 0.25);
}

.btn-export-excel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Filter Controls Grid */
.toolbar-controls-grid {
  display: grid;
  grid-template-columns: 2.2fr 1.3fr 1.1fr 1.4fr;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1rem;
}

@media (max-width: 1024px) {
  .toolbar-controls-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .toolbar-controls-grid {
    grid-template-columns: 1fr;
  }
}

.control-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.control-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.control-select,
.control-input {
  width: 100%;
  padding: 0.55rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #1e293b;
  background: #ffffff;
  transition: border-color 0.15s;
}

.control-select:focus,
.control-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-wrap svg {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  pointer-events: none;
}

.search-input-wrap .control-input {
  padding-left: 2.2rem;
  padding-right: 2rem;
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

/* Legend Card */
.legend-card {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.6rem 1rem;
  font-size: 0.78rem;
  color: #475569;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  border: 1px solid #cbd5e1;
}

.legend-murni { background: #f8fafc; }
.legend-perubahan { background: #eff6ff; border-color: #93c5fd; }
.legend-rpjmd { background: #f0fdf4; border-color: #86efac; }
.legend-diff { background: #fef3c7; border-color: #f59e0b; }
.legend-match { background: #dcfce7; border-color: #22c55e; }

/* KPI Metric Cards */
.metric-cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.25rem;
}

@media (max-width: 900px) {
  .metric-cards-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.kpi-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem 1.2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.kpi-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bg-blue-subtle { background: #eff6ff; color: #1d4ed8; }
.bg-red-subtle { background: #fef2f2; color: #dc2626; }
.bg-green-subtle { background: #f0fdf4; color: #16a34a; }
.bg-purple-subtle { background: #faf5ff; color: #9333ea; }

.kpi-content {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 0.74rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.kpi-value {
  font-size: 1.45rem;
  font-weight: 800;
  line-height: 1.2;
}

.text-blue-dark { color: #1e3a8a; }
.text-red { color: #dc2626; }
.text-green { color: #16a34a; }
.text-purple { color: #7e22ce; }

.kpi-sub {
  font-size: 0.72rem;
  color: #94a3b8;
  margin-top: 0.15rem;
}

/* Report Table */
.report-table-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.table-responsive-container {
  overflow-x: auto;
  max-height: calc(100vh - 280px);
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.report-table th,
.report-table td {
  border: 1px solid #e2e8f0;
  padding: 0.45rem 0.6rem;
}

/* Header Styles */
.tr-top-header th {
  background: #1e3a8a;
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 700;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 10;
}

.tr-sub-header th {
  background: #2563eb;
  color: #ffffff;
  font-size: 0.74rem;
  font-weight: 700;
  text-align: center;
  position: sticky;
  top: 36px;
  z-index: 10;
}

.th-year-group {
  letter-spacing: 0.02em;
}

.th-total-group {
  background: #0f172a !important;
}

.th-active-single {
  background: #1d4ed8 !important;
  font-size: 0.88rem !important;
}

.th-no { width: 44px; }
.th-prog { min-width: 280px; text-align: left !important; }
.th-subunit { min-width: 160px; }
.th-val { min-width: 105px; }
.th-status { min-width: 150px; }

/* OPD Group Header Row */
.tr-opd-group td {
  background: #f1f5f9;
  padding: 0.6rem 0.85rem;
}

.opd-title-flex {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.opd-badge-code {
  background: #1e3a8a;
  color: #ffffff;
  font-weight: 800;
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.opd-name {
  font-weight: 800;
  font-size: 0.88rem;
  color: #0f172a;
}

.opd-stats-pills {
  margin-left: auto;
  display: flex;
  gap: 0.4rem;
}

.badge-pill-count {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
}

.badge-pill-diff {
  background: #fee2e2;
  color: #b91c1c;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  border: 1px solid #fecaca;
}

.badge-pill-ok {
  background: #dcfce7;
  color: #15803d;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  border: 1px solid #bbf7d0;
}

/* Program Row */
.tr-program-row:hover {
  background: #f8fafc;
}

.tr-has-diff {
  background: rgba(254, 243, 199, 0.12);
}

.td-no {
  text-align: center;
  font-weight: 600;
  color: #64748b;
}

.prog-info-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.prog-code {
  font-family: monospace;
  font-weight: 700;
  font-size: 0.76rem;
  color: #1e40af;
}

.prog-name {
  font-weight: 600;
  color: #0f172a;
  line-height: 1.35;
}

.td-subunit {
  font-size: 0.76rem;
}

.subunit-tag {
  color: #475569;
  font-weight: 500;
}

.subunit-distinct {
  color: #0369a1;
  font-weight: 700;
  background: #f0f9ff;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  display: inline-block;
  border: 1px solid #bae6fd;
}

/* Currency Cells */
.td-currency {
  text-align: right;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
  font-size: 0.8rem;
  white-space: nowrap;
}

.td-murni {
  color: #475569;
}

.td-perubahan {
  font-weight: 600;
  color: #0f172a;
}

.td-rpjmd {
  color: #047857;
}

.td-selisih {
  font-weight: 700;
}

.text-diff-negative {
  color: #dc2626;
}

.text-diff-positive {
  color: #059669;
}

/* Alert Cell for Discrepancy */
.cell-diff-alert {
  background: #fef3c7 !important;
  color: #b45309 !important;
  font-weight: 700 !important;
  border-left: 2px solid #f59e0b !important;
}

.val-with-mark {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.1rem;
}

.pill-diff-indicator {
  font-size: 0.62rem;
  font-weight: 800;
  color: #b91c1c;
  background: #fee2e2;
  padding: 0.05rem 0.3rem;
  border-radius: 3px;
  border: 1px solid #fecaca;
}

/* Total Columns */
.td-total-murni,
.td-total-perubahan,
.td-total-rpjmd,
.td-total-selisih {
  font-weight: 700;
  background: rgba(15, 23, 42, 0.02);
}

/* Status Column */
.td-status {
  text-align: center;
}

.badge-status {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  white-space: nowrap;
}

.badge-diff {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.badge-match {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

/* Grand Total Footer */
.tr-grand-total td {
  background: #0f172a;
  color: #ffffff;
  font-weight: 800;
  position: sticky;
  bottom: 0;
  z-index: 5;
}

.td-total-label {
  text-align: center;
  font-size: 0.84rem;
  letter-spacing: 0.02em;
}

.td-foot-val {
  font-size: 0.8rem;
  color: #ffffff;
}

/* Loading & Empty States */
.state-loading,
.state-error,
.state-empty {
  padding: 4rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3.5px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.state-text {
  font-size: 0.9rem;
  color: #64748b;
}

.error-msg {
  color: #dc2626;
  font-weight: 600;
}

.btn-retry {
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.empty-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #334155;
  margin: 0;
}

.empty-desc {
  font-size: 0.84rem;
  color: #64748b;
  margin: 0;
}
</style>
