<template>
  <div>
    <!-- Header Banner -->
    <section class="hero-banner">
      <div class="app-container">
        <!-- Back Navigation Button -->
        <div style="margin-bottom: 0.85rem;">
          <router-link to="/" class="btn-action-secondary" style="display: inline-flex; align-items: center; gap: 0.5rem; text-decoration: none;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"/>
              <polyline points="12 19 5 12 12 5"/>
            </svg>
            <span style="font-weight: 600;">Kembali ke Daftar Perangkat Daerah</span>
          </router-link>
        </div>

        <div class="hero-content">
          <div class="hero-title-group">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem; flex-wrap: wrap;">
              <span class="code-pill" style="background: #e0e7ff; color: #3730a3; border-color: #c7d2fe; font-size: 0.85rem;">
                KODE: {{ opdInfo?.kode_skpd || '...' }}
              </span>
              <span class="badge-tag">DOKUMEN RENSTRA PERANGKAT DAERAH</span>
              <span class="badge-year">T.A. 2026 (PERIODE 2025 - 2029)</span>
            </div>
            <h2>
              <span>{{ opdInfo?.nama_skpd || 'Memuat Data SKPD...' }}</span>
            </h2>
            <p>
              Rencana Strategis (RENSTRA) &bull; Perencanaan Pembangunan Pemerintah Kota Tegal
            </p>
          </div>

          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sub-badge has-units" style="font-size: 0.88rem; padding: 0.5rem 1rem;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 14 14"/>
              </svg>
              <span>{{ cascadingData?.total_tujuan || 0 }} Tujuan &bull; {{ cascadingData?.total_sasaran || 0 }} Sasaran</span>
            </div>
            <div class="sub-badge" style="font-size: 0.88rem; padding: 0.5rem 1rem;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
              <span>{{ subList.length }} Sub SKPD</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content Area with Tabs -->
    <main class="app-container" style="margin-top: 1.5rem;">
      <div class="renstra-tabs-container">
        <!-- Tab Navigation Bar -->
        <nav class="renstra-tabs-nav">
          <!-- Tab 1: Tujuan & Sasaran -->
          <button
            :class="['renstra-tab-btn', { active: activeTab === 'tujuan_sasaran' }]"
            @click="activeTab = 'tujuan_sasaran'"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <circle cx="12" cy="12" r="6"/>
              <circle cx="12" cy="12" r="2"/>
            </svg>
            <span>Tujuan &amp; Sasaran</span>
            <span class="tab-badge">{{ cascadingData?.total_tujuan || 0 }}</span>
          </button>

          <!-- Tab 2: Program / Kegiatan / Subkegiatan (Menampilkan Sub SKPD) -->
          <button
            :class="['renstra-tab-btn', { active: activeTab === 'program_kegiatan' }]"
            @click="activeTab = 'program_kegiatan'"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="8" y1="6" x2="21" y2="6"/>
              <line x1="8" y1="12" x2="21" y2="12"/>
              <line x1="8" y1="18" x2="21" y2="18"/>
              <line x1="3" y1="6" x2="3.01" y2="6"/>
              <line x1="3" y1="12" x2="3.01" y2="12"/>
              <line x1="3" y1="18" x2="3.01" y2="18"/>
            </svg>
            <span>Program / Kegiatan / Subkegiatan (Sub SKPD)</span>
            <span class="tab-badge">{{ subList.length }}</span>
          </button>
        </nav>

        <!-- =================================================================== -->
        <!-- TAB 1: TUJUAN & SASARAN CASCADING (WITH FULL CRUD)                -->
        <!-- =================================================================== -->
        <div v-if="activeTab === 'tujuan_sasaran'" class="renstra-tab-pane">
          <!-- Toolbar Tujuan & Sasaran -->
          <div class="tab-pane-header">
            <div>
              <h3>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <circle cx="12" cy="12" r="6"/>
                  <circle cx="12" cy="12" r="2"/>
                </svg>
                <span>Matriks Cascading Tujuan &amp; Sasaran RENSTRA</span>
              </h3>
              <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 0.25rem;">
                Hirarki: <strong>Tujuan &rarr; Indikator Tujuan &rarr; Sasaran &rarr; Indikator Sasaran</strong> beserta target capaian per tahun.
              </p>
            </div>

            <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
              <!-- Filter Perubahan / Data Baru -->
              <div class="filter-pills-status">
                <button
                  type="button"
                  class="filter-pill-btn"
                  :class="{ active: changeFilter === 'all' }"
                  @click="changeFilter = 'all'"
                  title="Tampilkan semua data"
                >
                  Semua
                  <span v-if="cascadingData?.total_indikator" class="pill-count">
                    {{ cascadingData.total_indikator }}
                  </span>
                </button>
                <button
                  type="button"
                  class="filter-pill-btn"
                  :class="{ active: changeFilter === 'perubahan', perubahan: true }"
                  @click="changeFilter = 'perubahan'"
                  title="Hanya tampilkan indikator dengan penyesuaian target"
                >
                  <span class="pulse-dot perubahan"></span>
                  <span>Perubahan</span>
                  <span v-if="cascadingData?.total_indikator_perubahan" class="pill-count" style="background: rgba(245, 158, 11, 0.25); color: #92400e;">
                    {{ cascadingData.total_indikator_perubahan }}
                  </span>
                </button>
                <button
                  type="button"
                  class="filter-pill-btn"
                  :class="{ active: changeFilter === 'baru', baru: true }"
                  @click="changeFilter = 'baru'"
                  title="Hanya tampilkan data baru"
                >
                  <span class="pulse-dot baru"></span>
                  <span>Data Baru</span>
                  <span v-if="cascadingData?.total_indikator_baru" class="pill-count" style="background: rgba(16, 185, 129, 0.25); color: #065f46;">
                    {{ cascadingData.total_indikator_baru }}
                  </span>
                </button>
              </div>

              <!-- Target View Mode Switcher -->
              <div class="target-toggle-group">
                <button
                  type="button"
                  class="target-toggle-btn"
                  :class="{ active: targetViewFilter === 'all' }"
                  @click="targetViewFilter = 'all'"
                  title="Tampilkan Semua Target (Murni & Perubahan)"
                >
                  Semua Target
                </button>
                <button
                  type="button"
                  class="target-toggle-btn"
                  :class="{ active: targetViewFilter === 'murni' }"
                  @click="targetViewFilter = 'murni'"
                  title="Tampilkan Target Murni Saja"
                >
                  Murni
                </button>
                <button
                  type="button"
                  class="target-toggle-btn perubahan-toggle"
                  :class="{ active: targetViewFilter === 'perubahan' }"
                  @click="targetViewFilter = 'perubahan'"
                  title="Tampilkan Target Perubahan Saja"
                >
                  Perubahan
                </button>
              </div>

              <!-- Tombol Tambah Tujuan Baru -->
              <button class="btn-action-view" @click="openCreateTujuan" style="display: inline-flex; align-items: center; gap: 0.4rem;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                <span>+ Tambah Tujuan</span>
              </button>

              <!-- Search box for Tujuan & Sasaran -->
              <div class="search-box" style="min-width: 240px; max-width: 320px;">
                <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"/>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                <input
                  type="text"
                  class="search-input"
                  style="padding: 0.5rem 1rem 0.5rem 2.3rem; font-size: 0.84rem;"
                  v-model="searchCascading"
                  placeholder="Saring Tujuan / Sasaran / Indikator..."
                />
                <button
                  v-if="searchCascading"
                  class="clear-search-btn"
                  @click="searchCascading = ''"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Loading state -->
          <div v-if="loadingCascading" class="state-container" style="padding: 3rem 1rem;">
            <div class="spinner"></div>
            <p style="color: var(--text-muted); font-size: 0.88rem;">Memuat data cascading Tujuan &amp; Sasaran dari database...</p>
          </div>

          <!-- Empty state -->
          <div v-else-if="!cascadingData?.tujuan_list || cascadingData.tujuan_list.length === 0" class="empty-tab-placeholder">
            <div class="placeholder-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <h4>Data Tujuan &amp; Sasaran Belum Tersedia</h4>
            <p>
              Perangkat Daerah ini belum memiliki rekaman Tujuan pada tabel <code>renstra_tujuan</code>.
            </p>
            <button class="btn-action-view" @click="openCreateTujuan" style="margin-top: 0.5rem;">
              + Tambah Tujuan Pertama
            </button>
          </div>

          <!-- Cascading Data Table -->
          <div v-else class="cascading-table-wrapper">
            <table class="cascading-table">
              <thead>
                <tr>
                  <th rowspan="2" style="width: 110px; text-align: center;">AKSI</th>
                  <th rowspan="2" style="width: 120px; text-align: center;">HIRARKI</th>
                  <th rowspan="2" style="min-width: 260px;">TUJUAN / SASARAN / INDIKATOR</th>
                  <th rowspan="2" style="width: 65px; text-align: center;">IKU</th>
                  <th rowspan="2" style="width: 80px; text-align: center;">SATUAN</th>

                  <!-- Header Target Murni Group -->
                  <th v-if="showTargetMurni" colspan="7" class="th-target-group murni">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.4rem;">
                      <span class="badge-group-murni">Murni</span>
                      <span>TARGET CAPAIAN TAHUNAN</span>
                    </div>
                  </th>

                  <!-- Header Target Perubahan Group -->
                  <th v-if="showTargetPerubahan" colspan="7" class="th-target-group perubahan">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.45rem;">
                      <span class="badge-group-perubahan">Perubahan</span>
                      <span>TARGET PERUBAHAN</span>
                    </div>
                  </th>
                </tr>
                <tr>
                  <!-- Sub-header Target Murni (7 Cols) -->
                  <template v-if="showTargetMurni">
                    <th class="th-sub-target" style="width: 85px; text-align: center;">
                      <div>AWAL</div>
                      <div style="font-size: 0.62rem; font-weight: 500; opacity: 0.75;">(Baseline)</div>
                    </th>
                    <th class="th-sub-target" style="width: 75px; text-align: center;">2026</th>
                    <th class="th-sub-target" style="width: 75px; text-align: center;">2027</th>
                    <th class="th-sub-target" style="width: 75px; text-align: center;">2028</th>
                    <th class="th-sub-target" style="width: 75px; text-align: center;">2029</th>
                    <th class="th-sub-target" style="width: 75px; text-align: center;">2030</th>
                    <th class="th-sub-target th-sub-final" style="width: 85px; text-align: center;">
                      <div>AKHIR</div>
                    </th>
                  </template>

                  <!-- Sub-header Target Perubahan (7 Cols) -->
                  <template v-if="showTargetPerubahan">
                    <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2025</th>
                    <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2026</th>
                    <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2027</th>
                    <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2028</th>
                    <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2029</th>
                    <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2030</th>
                    <th class="th-sub-target th-sub-final-p" style="width: 85px; text-align: center;">
                      <div>AKHIR (P)</div>
                    </th>
                  </template>
                </tr>
              </thead>
              <tbody>
                <template v-for="(tujuan, tIdx) in filteredTujuanList" :key="tujuan.idtujuan">
                  <!-- 1. BARIS TUJUAN -->
                  <tr class="row-tujuan">
                    <!-- Aksi Tujuan -->
                    <td style="text-align: center;">
                      <div class="action-dropdown">
                        <button
                          class="btn-action-dropdown"
                          :class="{ active: activeDropdown === 'tujuan_' + tujuan.idtujuan }"
                          @click.stop="toggleDropdown('tujuan_' + tujuan.idtujuan, $event)"
                        >
                          <span>Aksi</span>
                          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <polyline points="6 9 12 15 18 9"/>
                          </svg>
                        </button>
                        <div v-if="activeDropdown === 'tujuan_' + tujuan.idtujuan" class="dropdown-menu-list">
                          <button class="dropdown-menu-item" @click="openCreateIndikatorTujuan(tujuan); closeDropdown();">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                            <span>+ Indikator Tujuan</span>
                          </button>
                          <button class="dropdown-menu-item" @click="openCreateSasaran(tujuan); closeDropdown();">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                            <span>+ Sasaran</span>
                          </button>
                          <div class="dropdown-menu-divider"></div>
                          <button class="dropdown-menu-item" @click="openEditTujuan(tujuan); closeDropdown();">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                            <span>Ubah Metadata Tujuan</span>
                          </button>
                        </div>
                      </div>
                    </td>
                    <td style="text-align: center;">
                      <span class="badge-hirarki tujuan">TUJUAN {{ tIdx + 1 }}</span>
                    </td>
                    <td :colspan="tujuanSasaranColspan" style="font-size: 0.92rem; padding: 0.85rem 1rem;">
                      <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap;">
                        <span style="font-weight: 600; color: #0f172a;">{{ tujuan.uraitujuan }}</span>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                          <span v-if="tujuan.is_baru" class="badge-status-perubahan baru">
                            <span class="pulse-dot baru"></span> DATA BARU
                          </span>
                          <span v-if="tujuan.total_perubahan > 0" class="badge-chip-summary perubahan" title="Jumlah indikator dengan penyesuaian target">
                            🔄 {{ tujuan.total_perubahan }} Perubahan
                          </span>
                          <span v-if="tujuan.total_baru > 0" class="badge-chip-summary baru" title="Jumlah indikator baru">
                            ✨ {{ tujuan.total_baru }} Baru
                          </span>
                        </div>
                      </div>
                    </td>
                  </tr>

                  <!-- 1.1 INDIKATOR TUJUAN -->
                  <tr
                    v-for="(indTujuan) in tujuan.indikator_tujuan"
                    :key="indTujuan.id"
                    class="row-indikator-tujuan"
                    :class="{ 'has-perubahan': indTujuan.is_perubahan, 'is-baru': indTujuan.is_baru }"
                  >
                    <!-- Aksi Indikator Tujuan -->
                    <td style="text-align: center;">
                      <button
                        class="btn-table-edit"
                        @click="openEditIndikatorTujuan(indTujuan)"
                        title="Ubah Metadata & Target Perubahan"
                      >
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                        <span>Ubah Target</span>
                      </button>
                    </td>
                    <td style="text-align: center;">
                      <span class="badge-hirarki indikator">IND. TUJUAN</span>
                    </td>
                    <td style="padding-left: 2rem;">
                      <div class="tree-indent" style="align-items: flex-start;">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-top: 3px; flex-shrink: 0;">
                          <polyline points="9 18 15 12 9 6"/>
                        </svg>
                        <div style="display: flex; flex-direction: column; gap: 0.2rem; flex: 1;">
                          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                            <span style="font-weight: 600; color: #1e293b;">{{ indTujuan.uraian }}</span>
                            <span v-if="indTujuan.is_baru" class="badge-status-perubahan baru" title="Data Baru pada RENSTRA Perubahan">
                              <span class="pulse-dot baru"></span> DATA BARU
                            </span>
                            <span v-else-if="indTujuan.is_perubahan" class="badge-status-perubahan perubahan" title="Terdapat penyesuaian target pada RENSTRA Perubahan">
                              <span class="pulse-dot perubahan"></span> ADA PERUBAHAN
                            </span>
                            <span v-if="indTujuan.iku === '1' || indTujuan.iku === 1" class="badge-iku-tag">IKU</span>
                            <span v-if="indTujuan.status && indTujuan.status !== '-'" class="badge-status-indikator" :class="indTujuan.status">
                              {{ indTujuan.status }}
                            </span>
                          </div>
                          <div v-if="indTujuan.definisi_operasional && indTujuan.definisi_operasional !== '-'" class="indikator-def-box">
                           {{ indTujuan.definisi_operasional }}
                          </div>
                        </div>
                      </div>
                    </td>
                    <!-- IKU Indikator Tujuan -->
                    <td style="text-align: center;">
                      <span
                        v-if="indTujuan.iku === '1' || indTujuan.iku === 1"
                        class="badge-iku-check"
                        title="Indikator Kinerja Utama (IKU)"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      </span>
                      <span v-else style="color: #cbd5e1; font-weight: 500;">-</span>
                    </td>
                    <td style="text-align: center; color: var(--text-muted);">{{ indTujuan.satuan }}</td>

                    <!-- Target Murni Values -->
                    <template v-if="showTargetMurni">
                      <td class="col-target baseline">{{ indTujuan.target_awal }}</td>
                      <td class="col-target">{{ indTujuan.target2026 }}</td>
                      <td class="col-target">{{ indTujuan.target2027 }}</td>
                      <td class="col-target">{{ indTujuan.target2028 }}</td>
                      <td class="col-target">{{ indTujuan.target2029 }}</td>
                      <td class="col-target">{{ indTujuan.target2030 }}</td>
                      <td class="col-target final">{{ indTujuan.target_akhir }}</td>
                    </template>

                    <!-- Target Perubahan Values -->
                    <template v-if="showTargetPerubahan">
                      <td
                        class="col-target col-target-p"
                        :class="{ 'col-target-diff': indTujuan.changed_targets?.includes('2025'), 'col-target-new': indTujuan.is_baru && indTujuan.p_target2025 !== '-' }"
                        :title="indTujuan.changed_targets?.includes('2025') ? `Awal: ${indTujuan.target_awal} ➔ Perubahan: ${indTujuan.p_target2025}` : ''"
                      >
                        {{ indTujuan.p_target2025 }}
                        <span v-if="indTujuan.changed_targets?.includes('2025')" class="target-diff-tag">berubah</span>
                      </td>
                      <td
                        class="col-target col-target-p"
                        :class="{ 'col-target-diff': indTujuan.changed_targets?.includes('2026'), 'col-target-new': indTujuan.is_baru && indTujuan.p_target2026 !== '-' }"
                        :title="indTujuan.changed_targets?.includes('2026') ? `Murni: ${indTujuan.target2026} ➔ Perubahan: ${indTujuan.p_target2026}` : ''"
                      >
                        {{ indTujuan.p_target2026 }}
                        <span v-if="indTujuan.changed_targets?.includes('2026')" class="target-diff-tag">berubah</span>
                      </td>
                      <td
                        class="col-target col-target-p"
                        :class="{ 'col-target-diff': indTujuan.changed_targets?.includes('2027'), 'col-target-new': indTujuan.is_baru && indTujuan.p_target2027 !== '-' }"
                        :title="indTujuan.changed_targets?.includes('2027') ? `Murni: ${indTujuan.target2027} ➔ Perubahan: ${indTujuan.p_target2027}` : ''"
                      >
                        {{ indTujuan.p_target2027 }}
                        <span v-if="indTujuan.changed_targets?.includes('2027')" class="target-diff-tag">berubah</span>
                      </td>
                      <td
                        class="col-target col-target-p"
                        :class="{ 'col-target-diff': indTujuan.changed_targets?.includes('2028'), 'col-target-new': indTujuan.is_baru && indTujuan.p_target2028 !== '-' }"
                        :title="indTujuan.changed_targets?.includes('2028') ? `Murni: ${indTujuan.target2028} ➔ Perubahan: ${indTujuan.p_target2028}` : ''"
                      >
                        {{ indTujuan.p_target2028 }}
                        <span v-if="indTujuan.changed_targets?.includes('2028')" class="target-diff-tag">berubah</span>
                      </td>
                      <td
                        class="col-target col-target-p"
                        :class="{ 'col-target-diff': indTujuan.changed_targets?.includes('2029'), 'col-target-new': indTujuan.is_baru && indTujuan.p_target2029 !== '-' }"
                        :title="indTujuan.changed_targets?.includes('2029') ? `Murni: ${indTujuan.target2029} ➔ Perubahan: ${indTujuan.p_target2029}` : ''"
                      >
                        {{ indTujuan.p_target2029 }}
                        <span v-if="indTujuan.changed_targets?.includes('2029')" class="target-diff-tag">berubah</span>
                      </td>
                      <td
                        class="col-target col-target-p"
                        :class="{ 'col-target-diff': indTujuan.changed_targets?.includes('2030'), 'col-target-new': indTujuan.is_baru && indTujuan.p_target2030 !== '-' }"
                        :title="indTujuan.changed_targets?.includes('2030') ? `Murni: ${indTujuan.target2030} ➔ Perubahan: ${indTujuan.p_target2030}` : ''"
                      >
                        {{ indTujuan.p_target2030 }}
                        <span v-if="indTujuan.changed_targets?.includes('2030')" class="target-diff-tag">berubah</span>
                      </td>
                      <td
                        class="col-target final-p"
                        :class="{ 'col-target-diff': indTujuan.changed_targets?.includes('akhir'), 'col-target-new': indTujuan.is_baru && indTujuan.p_target_akhir !== '-' }"
                        :title="indTujuan.changed_targets?.includes('akhir') ? `Murni Akhir: ${indTujuan.target_akhir} ➔ Perubahan: ${indTujuan.p_target_akhir}` : ''"
                      >
                        {{ indTujuan.p_target_akhir }}
                        <span v-if="indTujuan.changed_targets?.includes('akhir')" class="target-diff-tag">berubah</span>
                      </td>
                    </template>
                  </tr>

                  <!-- 2. SASARAN (Di bawah Tujuan) -->
                  <template v-for="(sasaran, sIdx) in tujuan.sasaran" :key="sasaran.idsasaran">
                    <!-- 2.1 BARIS SASARAN -->
                    <tr class="row-sasaran">
                      <!-- Aksi Sasaran -->
                      <td style="text-align: center;">
                        <div class="action-dropdown">
                          <button
                            class="btn-action-dropdown"
                            :class="{ active: activeDropdown === 'sasaran_' + sasaran.idsasaran }"
                            @click.stop="toggleDropdown('sasaran_' + sasaran.idsasaran, $event)"
                          >
                            <span>Aksi</span>
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                              <polyline points="6 9 12 15 18 9"/>
                            </svg>
                          </button>
                          <div v-if="activeDropdown === 'sasaran_' + sasaran.idsasaran" class="dropdown-menu-list">
                            <button class="dropdown-menu-item" @click="openCreateIndikatorSasaran(sasaran); closeDropdown();">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                              <span>+ Indikator Sasaran</span>
                            </button>
                            <div class="dropdown-menu-divider"></div>
                            <button class="dropdown-menu-item" @click="openEditSasaran(sasaran); closeDropdown();">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                              <span>Ubah Metadata Sasaran</span>
                            </button>
                          </div>
                        </div>
                      </td>
                      <td style="text-align: center;">
                        <span class="badge-hirarki sasaran">SASARAN {{ tIdx + 1 }}.{{ sIdx + 1 }}</span>
                      </td>
                      <td :colspan="tujuanSasaranColspan" style="padding-left: 1.5rem; font-size: 0.9rem;">
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap;">
                          <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                              <polyline points="9 18 15 12 9 6"/>
                            </svg>
                            <span>{{ sasaran.uraisasaran }}</span>
                          </div>
                          <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span v-if="sasaran.is_baru" class="badge-status-perubahan baru">
                              <span class="pulse-dot baru"></span> DATA BARU
                            </span>
                            <span v-if="sasaran.total_perubahan > 0" class="badge-chip-summary perubahan" title="Jumlah indikator dengan penyesuaian target">
                              🔄 {{ sasaran.total_perubahan }} Perubahan
                            </span>
                            <span v-if="sasaran.total_baru > 0" class="badge-chip-summary baru" title="Jumlah indikator baru">
                              ✨ {{ sasaran.total_baru }} Baru
                            </span>
                          </div>
                        </div>
                      </td>
                    </tr>

                    <!-- 2.2 INDIKATOR SASARAN -->
                    <tr
                      v-for="(indSasaran) in sasaran.indikator_sasaran"
                      :key="indSasaran.id"
                      class="row-indikator-sasaran"
                      :class="{ 'has-perubahan': indSasaran.is_perubahan, 'is-baru': indSasaran.is_baru }"
                    >
                      <!-- Aksi Indikator Sasaran -->
                      <td style="text-align: center;">
                        <button
                          class="btn-table-edit"
                          @click="openEditIndikatorSasaran(indSasaran)"
                          title="Ubah Metadata & Target Perubahan"
                        >
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                          <span>Ubah Target</span>
                        </button>
                      </td>
                      <td style="text-align: center;">
                        <span class="badge-hirarki indikator">IND. SASARAN</span>
                      </td>
                      <td style="padding-left: 3rem;">
                        <div class="tree-indent" style="align-items: flex-start;">
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-top: 3px; flex-shrink: 0;">
                            <polyline points="9 18 15 12 9 6"/>
                          </svg>
                          <div style="display: flex; flex-direction: column; gap: 0.2rem; flex: 1;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                              <span style="color: #334155; font-weight: 500;">{{ indSasaran.uraian }}</span>
                              <span v-if="indSasaran.is_baru" class="badge-status-perubahan baru" title="Data Baru pada RENSTRA Perubahan">
                                <span class="pulse-dot baru"></span> DATA BARU
                              </span>
                              <span v-else-if="indSasaran.is_perubahan" class="badge-status-perubahan perubahan" title="Terdapat penyesuaian target pada RENSTRA Perubahan">
                                <span class="pulse-dot perubahan"></span> ADA PERUBAHAN
                              </span>
                              <span v-if="indSasaran.iku === '1' || indSasaran.iku === 1" class="badge-iku-tag">IKU</span>
                              <span v-if="indSasaran.status && indSasaran.status !== '-'" class="badge-status-indikator" :class="indSasaran.status">
                                {{ indSasaran.status }}
                              </span>
                            </div>
                            <div v-if="indSasaran.definisi_operasional && indSasaran.definisi_operasional !== '-'" class="indikator-def-box">
                             {{ indSasaran.definisi_operasional }}
                            </div>
                          </div>
                        </div>
                      </td>
                      <!-- IKU Indikator Sasaran -->
                      <td style="text-align: center;">
                        <span
                          v-if="indSasaran.iku === '1' || indSasaran.iku === 1"
                          class="badge-iku-check"
                          title="Indikator Kinerja Utama (IKU)"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="20 6 9 17 4 12"/>
                          </svg>
                        </span>
                        <span v-else style="color: #cbd5e1; font-weight: 500;">-</span>
                      </td>
                      <td style="text-align: center; color: var(--text-muted);">{{ indSasaran.satuan }}</td>

                      <!-- Target Murni Values -->
                      <template v-if="showTargetMurni">
                        <td class="col-target baseline">{{ indSasaran.target_awal }}</td>
                        <td class="col-target">{{ indSasaran.target2026 }}</td>
                        <td class="col-target">{{ indSasaran.target2027 }}</td>
                        <td class="col-target">{{ indSasaran.target2028 }}</td>
                        <td class="col-target">{{ indSasaran.target2029 }}</td>
                        <td class="col-target">{{ indSasaran.target2030 }}</td>
                        <td class="col-target final">{{ indSasaran.target_akhir }}</td>
                      </template>

                      <!-- Target Perubahan Values -->
                      <template v-if="showTargetPerubahan">
                        <td
                          class="col-target col-target-p"
                          :class="{ 'col-target-diff': indSasaran.changed_targets?.includes('2025'), 'col-target-new': indSasaran.is_baru && indSasaran.p_target2025 !== '-' }"
                          :title="indSasaran.changed_targets?.includes('2025') ? `Awal: ${indSasaran.target_awal} ➔ Perubahan: ${indSasaran.p_target2025}` : ''"
                        >
                          {{ indSasaran.p_target2025 }}
                          <span v-if="indSasaran.changed_targets?.includes('2025')" class="target-diff-tag">berubah</span>
                        </td>
                        <td
                          class="col-target col-target-p"
                          :class="{ 'col-target-diff': indSasaran.changed_targets?.includes('2026'), 'col-target-new': indSasaran.is_baru && indSasaran.p_target2026 !== '-' }"
                          :title="indSasaran.changed_targets?.includes('2026') ? `Murni: ${indSasaran.target2026} ➔ Perubahan: ${indSasaran.p_target2026}` : ''"
                        >
                          {{ indSasaran.p_target2026 }}
                          <span v-if="indSasaran.changed_targets?.includes('2026')" class="target-diff-tag">berubah</span>
                        </td>
                        <td
                          class="col-target col-target-p"
                          :class="{ 'col-target-diff': indSasaran.changed_targets?.includes('2027'), 'col-target-new': indSasaran.is_baru && indSasaran.p_target2027 !== '-' }"
                          :title="indSasaran.changed_targets?.includes('2027') ? `Murni: ${indSasaran.target2027} ➔ Perubahan: ${indSasaran.p_target2027}` : ''"
                        >
                          {{ indSasaran.p_target2027 }}
                          <span v-if="indSasaran.changed_targets?.includes('2027')" class="target-diff-tag">berubah</span>
                        </td>
                        <td
                          class="col-target col-target-p"
                          :class="{ 'col-target-diff': indSasaran.changed_targets?.includes('2028'), 'col-target-new': indSasaran.is_baru && indSasaran.p_target2028 !== '-' }"
                          :title="indSasaran.changed_targets?.includes('2028') ? `Murni: ${indSasaran.target2028} ➔ Perubahan: ${indSasaran.p_target2028}` : ''"
                        >
                          {{ indSasaran.p_target2028 }}
                          <span v-if="indSasaran.changed_targets?.includes('2028')" class="target-diff-tag">berubah</span>
                        </td>
                        <td
                          class="col-target col-target-p"
                          :class="{ 'col-target-diff': indSasaran.changed_targets?.includes('2029'), 'col-target-new': indSasaran.is_baru && indSasaran.p_target2029 !== '-' }"
                          :title="indSasaran.changed_targets?.includes('2029') ? `Murni: ${indSasaran.target2029} ➔ Perubahan: ${indSasaran.p_target2029}` : ''"
                        >
                          {{ indSasaran.p_target2029 }}
                          <span v-if="indSasaran.changed_targets?.includes('2029')" class="target-diff-tag">berubah</span>
                        </td>
                        <td
                          class="col-target col-target-p"
                          :class="{ 'col-target-diff': indSasaran.changed_targets?.includes('2030'), 'col-target-new': indSasaran.is_baru && indSasaran.p_target2030 !== '-' }"
                          :title="indSasaran.changed_targets?.includes('2030') ? `Murni: ${indSasaran.target2030} ➔ Perubahan: ${indSasaran.p_target2030}` : ''"
                        >
                          {{ indSasaran.p_target2030 }}
                          <span v-if="indSasaran.changed_targets?.includes('2030')" class="target-diff-tag">berubah</span>
                        </td>
                        <td
                          class="col-target final-p"
                          :class="{ 'col-target-diff': indSasaran.changed_targets?.includes('akhir'), 'col-target-new': indSasaran.is_baru && indSasaran.p_target_akhir !== '-' }"
                          :title="indSasaran.changed_targets?.includes('akhir') ? `Murni Akhir: ${indSasaran.target_akhir} ➔ Perubahan: ${indSasaran.p_target_akhir}` : ''"
                        >
                          {{ indSasaran.p_target_akhir }}
                          <span v-if="indSasaran.changed_targets?.includes('akhir')" class="target-diff-tag">berubah</span>
                        </td>
                      </template>
                    </tr>
                  </template>
                </template>
              </tbody>
            </table>
          </div>
        </div>

        <!-- =================================================================== -->
        <!-- TAB 2: PROGRAM / KEGIATAN / SUBKEGIATAN (MENAMPILKAN SUB SKPD)    -->
        <!-- =================================================================== -->
        <div v-if="activeTab === 'program_kegiatan'" class="renstra-tab-pane">
          <!-- VIEW 1: Sub SKPD List (When selectedSubSkpd is null) -->
          <template v-if="!selectedSubSkpd">
            <div class="tab-pane-header">
              <div>
                <h3>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                  </svg>
                  <span>Daftar Sub SKPD / Unit Kerja Pelaksana</span>
                </h3>
                <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 0.25rem;">
                  Klik nama Sub SKPD untuk menampilkan cascading data Program, Kegiatan, dan Subkegiatan.
                </p>
              </div>

              <!-- Search Sub SKPD -->
              <div class="search-box" style="min-width: 260px; max-width: 380px;">
                <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"/>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                <input
                  type="text"
                  class="search-input"
                  style="padding: 0.5rem 1rem 0.5rem 2.3rem; font-size: 0.84rem;"
                  v-model="searchSub"
                  placeholder="Cari nama atau kode Sub SKPD..."
                />
                <button
                  v-if="searchSub"
                  class="clear-search-btn"
                  @click="searchSub = ''"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Empty state for zero sub-units -->
            <div v-if="subList.length === 0" class="empty-tab-placeholder">
              <div class="placeholder-icon" style="background: var(--amber-50); color: var(--amber-600);">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
              </div>
              <h4>Unit Tunggal (0 Sub SKPD)</h4>
              <p>
                Perangkat Daerah ini beroperasi sebagai unit kerja tunggal tanpa pemisahan Sub SKPD (tabel <code>ta_sub_pd</code>). Seluruh program dan kegiatan dilaksanakan langsung oleh SKPD induk.
              </p>
            </div>

            <!-- Sub SKPD Table -->
            <div v-else class="table-responsive">
              <table class="civic-table">
                <thead>
                  <tr>
                    <th class="col-number">NO</th>
                    <th style="width: 220px;">KODE SUB SKPD</th>
                    <th>NAMA SUB SKPD</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(sub, index) in filteredSubList" :key="sub.id_sub_skpd">
                    <td class="col-number">{{ index + 1 }}</td>
                    <td>
                      <span class="code-pill">{{ sub.kode_sub_skpd || '-' }}</span>
                    </td>
                    <td>
                      <button
                        class="sub-skpd-link-btn"
                        @click="selectSubSkpd(sub)"
                        title="Klik untuk membuka cascading Program / Kegiatan / Subkegiatan"
                      >
                        <div style="width: 8px; height: 8px; border-radius: 50%; background: #2563eb; flex-shrink: 0;"></div>
                        <span>{{ sub.nama_sub_skpd }}</span>
                      </button>
                    </td>
                    
                   
                  </tr>
                </tbody>
              </table>
            </div>
          </template>

          <!-- VIEW 2: Cascading View for Selected Sub SKPD -->
          <div v-else class="sub-cascading-container">
            <!-- Cascading Header -->
            <div class="sub-cascading-header">
              <div class="sub-header-left">
                <button class="btn-back-sub" @click="backToSubList" title="Kembali ke Daftar Sub SKPD">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="15 18 9 12 15 6"/>
                  </svg>
                  <span>Daftar Sub SKPD</span>
                </button>

                <div>
                  <div class="sub-meta-breadcrumbs">
                    <span>Sub SKPD</span>
                    <span class="crumb-sep">/</span>
                    <span class="crumb-active">{{ selectedSubSkpd.nama_sub_skpd }}</span>
                  </div>
                  <div class="sub-title-text">
                    <span>{{ selectedSubSkpd.nama_sub_skpd }}</span>
                    <span class="sub-code">{{ selectedSubSkpd.kode_sub_skpd }}</span>
                  </div>
                </div>
              </div>

              <div class="sub-header-right">
                <!-- Quick Switcher -->
                <div v-if="subList.length > 1" class="quick-sub-switcher">
                  <label class="switcher-label">Pindah Sub:</label>
                  <select
                    class="switcher-select"
                    :value="selectedSubSkpd.id_sub_skpd"
                    @change="onSubSwitcherChange($event.target.value)"
                  >
                    <option
                      v-for="sub in subList"
                      :key="sub.id_sub_skpd"
                      :value="sub.id_sub_skpd"
                    >
                      {{ sub.nama_sub_skpd }}
                    </option>
                  </select>
                </div>

                <!-- Search box for Cascading Program -->
                <div class="search-box" style="min-width: 240px; max-width: 320px;">
                  <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                  </svg>
                  <input
                    type="text"
                    class="search-input"
                    style="padding: 0.5rem 1rem 0.5rem 2.3rem; font-size: 0.84rem;"
                    v-model="searchProgramCascading"
                    placeholder="Saring Program / Kegiatan / Subkeg..."
                  />
                  <button
                    v-if="searchProgramCascading"
                    class="clear-search-btn"
                    @click="searchProgramCascading = ''"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="18" y1="6" x2="6" y2="18"/>
                      <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                </div>

                <!-- Toggle Filter Target & Pagu Tab 2 -->
                <div class="target-toggle-group">
                  <button
                    type="button"
                    class="target-toggle-btn"
                    :class="{ active: subTargetViewFilter === 'all' }"
                    @click="subTargetViewFilter = 'all'"
                    title="Tampilkan Target & Pagu Lengkap (Murni & Perubahan)"
                  >
                    Semua
                  </button>
                  <button
                    type="button"
                    class="target-toggle-btn murni-toggle"
                    :class="{ active: subTargetViewFilter === 'murni' }"
                    @click="subTargetViewFilter = 'murni'"
                    title="Tampilkan Target & Pagu Murni Saja"
                  >
                    Murni
                  </button>
                  <button
                    type="button"
                    class="target-toggle-btn perubahan-toggle"
                    :class="{ active: subTargetViewFilter === 'perubahan' }"
                    @click="subTargetViewFilter = 'perubahan'"
                    title="Tampilkan Target & Pagu Perubahan Saja"
                  >
                    Perubahan
                  </button>
                </div>

                <!-- Tambah Program Button -->
                <button
                  class="btn-action-view"
                  style="display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 0.9rem; font-size: 0.82rem; white-space: nowrap;"
                  @click="openCreateProgram"
                  title="Tambah Program RENSTRA Baru"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                  <span>+ Tambah Program</span>
                </button>
              </div>
            </div>

            <!-- Stat Chips Summary -->
            <div v-if="subCascadingData" class="sub-stat-chips-row">
              <div class="stat-chip primary">
                <span class="stat-chip-label">Program:</span>
                <span class="stat-chip-val">{{ subCascadingData.total_program || 0 }}</span>
              </div>
              <div class="stat-chip sky">
                <span class="stat-chip-label">Kegiatan:</span>
                <span class="stat-chip-val">{{ subCascadingData.total_kegiatan || 0 }}</span>
              </div>
              <div class="stat-chip emerald">
                <span class="stat-chip-label">Subkegiatan:</span>
                <span class="stat-chip-val">{{ subCascadingData.total_subkegiatan || 0 }}</span>
              </div>
              <div class="stat-chip">
                <span class="stat-chip-label">Ind. Program:</span>
                <span class="stat-chip-val">{{ subCascadingData.total_indikator_program || 0 }}</span>
              </div>
              <div class="stat-chip amber" style="margin-left: auto;">
                <span class="stat-chip-label">Total Pagu (M):</span>
                <span class="stat-chip-val">{{ formatRupiah(totalAllProgramPagu) }}</span>
              </div>
              <div class="stat-chip amber">
                <span class="stat-chip-label">Total Pagu (P):</span>
                <span class="stat-chip-val" style="color: #b45309;">{{ formatRupiah(totalAllProgramPPagu) }}</span>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loadingSubCascading" class="state-container" style="padding: 3rem 1rem;">
              <div class="spinner"></div>
              <p style="color: var(--text-muted); font-size: 0.88rem;">Memuat cascading Program, Kegiatan &amp; Subkegiatan...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="!filteredPrograms || filteredPrograms.length === 0" class="empty-tab-placeholder">
              <div class="placeholder-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
              </div>
              <h4>Data Program / Kegiatan Belum Ditemukan</h4>
              <p>
                {{ searchProgramCascading ? 'Tidak ada data yang cocok dengan kata kunci pencarian.' : 'Sub SKPD ini belum memiliki data Program / Kegiatan / Subkegiatan pada database RENSTRA.' }}
              </p>
            </div>

            <!-- Cascading Table for Program / Kegiatan / Subkegiatan -->
            <div v-else class="cascading-table-wrapper">
              <table class="cascading-table">
                <thead>
                  <tr>
                    <th rowspan="2" style="width: 105px; text-align: center;">AKSI</th>
                    <th rowspan="2" style="width: 135px; text-align: center;">HIRARKI</th>
                    <th rowspan="2" style="min-width: 280px;">KODE &amp; URAIAN</th>
                    <th rowspan="2" style="min-width: 200px; color: #1e3a8a;">KINERJA</th>
                    <th rowspan="2" style="width: 60px; text-align: center;">IKU</th>
                    <th rowspan="2" style="width: 80px; text-align: center;">SATUAN</th>

                    <!-- Header Target Murni Group -->
                    <th v-if="showSubMurni" colspan="7" class="th-target-group murni" style="text-align: center;">
                      <div style="display: flex; align-items: center; justify-content: center; gap: 0.4rem;">
                        <span class="badge-group-murni">Murni</span>
                        <span>TARGET CAPAIAN TAHUNAN</span>
                      </div>
                    </th>

                    <!-- Header Target Perubahan Group -->
                    <th v-if="showSubPerubahan" colspan="7" class="th-target-group perubahan" style="text-align: center;">
                      <div style="display: flex; align-items: center; justify-content: center; gap: 0.45rem;">
                        <span class="badge-group-perubahan">Perubahan</span>
                        <span>TARGET PERUBAHAN</span>
                      </div>
                    </th>

                    <!-- Header Pagu Murni Group -->
                    <th v-if="showSubMurni" colspan="6" class="th-target-group murni" style="text-align: center; border-left: 2px solid #334155;">
                      <div style="display: flex; align-items: center; justify-content: center; gap: 0.4rem;">
                        <span class="badge-group-murni">Murni</span>
                        <span>PAGU INDIKATIF (2026 - 2030)</span>
                      </div>
                    </th>

                    <!-- Header Pagu Perubahan Group -->
                    <th v-if="showSubPerubahan" colspan="6" class="th-target-group perubahan" style="text-align: center; border-left: 2px solid #b45309;">
                      <div style="display: flex; align-items: center; justify-content: center; gap: 0.45rem;">
                        <span class="badge-group-perubahan">Perubahan</span>
                        <span>PAGU PERUBAHAN (2026 - 2030)</span>
                      </div>
                    </th>
                  </tr>
                  <tr>
                    <!-- Sub-header Target Murni (7 Cols) -->
                    <template v-if="showSubMurni">
                      <th class="th-sub-target" style="width: 80px; text-align: center;">AWAL</th>
                      <th class="th-sub-target" style="width: 75px; text-align: center;">2026</th>
                      <th class="th-sub-target" style="width: 75px; text-align: center;">2027</th>
                      <th class="th-sub-target" style="width: 75px; text-align: center;">2028</th>
                      <th class="th-sub-target" style="width: 75px; text-align: center;">2029</th>
                      <th class="th-sub-target" style="width: 75px; text-align: center;">2030</th>
                      <th class="th-sub-target th-sub-final" style="width: 85px; text-align: center;">AKHIR</th>
                    </template>

                    <!-- Sub-header Target Perubahan (7 Cols) -->
                    <template v-if="showSubPerubahan">
                      <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2025</th>
                      <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2026</th>
                      <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2027</th>
                      <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2028</th>
                      <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2029</th>
                      <th class="th-sub-target th-p" style="width: 75px; text-align: center;">2030</th>
                      <th class="th-sub-target th-sub-final-p" style="width: 85px; text-align: center;">AKHIR (P)</th>
                    </template>

                    <!-- Sub-header Pagu Murni (6 Cols) -->
                    <template v-if="showSubMurni">
                      <th class="th-sub-target" style="width: 125px; text-align: right; border-left: 2px solid #334155;">PAGU 2026</th>
                      <th class="th-sub-target" style="width: 125px; text-align: right;">PAGU 2027</th>
                      <th class="th-sub-target" style="width: 125px; text-align: right;">PAGU 2028</th>
                      <th class="th-sub-target" style="width: 125px; text-align: right;">PAGU 2029</th>
                      <th class="th-sub-target" style="width: 125px; text-align: right;">PAGU 2030</th>
                      <th class="th-sub-target th-sub-final" style="width: 140px; text-align: right;">TOTAL PAGU</th>
                    </template>

                    <!-- Sub-header Pagu Perubahan (6 Cols) -->
                    <template v-if="showSubPerubahan">
                      <th class="th-sub-target th-p" style="width: 125px; text-align: right; border-left: 2px solid #b45309;">PAGU (P) 2026</th>
                      <th class="th-sub-target th-p" style="width: 125px; text-align: right;">PAGU (P) 2027</th>
                      <th class="th-sub-target th-p" style="width: 125px; text-align: right;">PAGU (P) 2028</th>
                      <th class="th-sub-target th-p" style="width: 125px; text-align: right;">PAGU (P) 2029</th>
                      <th class="th-sub-target th-p" style="width: 125px; text-align: right;">PAGU (P) 2030</th>
                      <th class="th-sub-target th-sub-final-p" style="width: 140px; text-align: right;">TOTAL PAGU (P)</th>
                    </template>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(prog, pIdx) in filteredPrograms" :key="'prog_' + pIdx">
                    <!-- 1. PROGRAM -->
                    <tr class="row-program">
                      <td style="text-align: center;">
                        <div class="action-dropdown">
                          <button
                            class="btn-action-dropdown"
                            :class="{ active: activeDropdown === 'prog_' + pIdx }"
                            @click.stop="toggleDropdown('prog_' + pIdx, $event)"
                            title="Menu Aksi Program"
                          >
                            <span>Aksi</span>
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                              <polyline points="6 9 12 15 18 9"/>
                            </svg>
                          </button>
                          <div v-if="activeDropdown === 'prog_' + pIdx" class="dropdown-menu-list">
                            <button class="dropdown-menu-item" @click="openCreateKegiatan(prog)">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                              <span>+ Kegiatan</span>
                            </button>
                            <div class="dropdown-menu-divider"></div>
                            <button class="dropdown-menu-item" @click="openEditProgram(prog)">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                              <span>Ubah Program</span>
                            </button>
                            <button class="dropdown-menu-item danger" @click="openDeleteProgram(prog)">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                              <span>Hapus Program</span>
                            </button>
                          </div>
                        </div>
                      </td>
                      <td style="text-align: center;">
                        <span class="badge-hirarki program">PROGRAM</span>
                      </td>
                      <td>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                          <span class="code-badge-mono">{{ prog.kodeprogram }}</span>
                          <span>{{ prog.uraiprogram }}</span>
                        </div>
                      </td>
                      <td style="color: #1e3a8a; font-weight: 500; font-size: 0.83rem;">
                        {{ prog.kinerja || '-' }}
                      </td>
                      <td :colspan="subTargetColspan" style="text-align: center; color: var(--text-muted); font-size: 0.78rem; font-style: italic;">
                        (Target pada Indikator Program)
                      </td>
                      <!-- Pagu Murni (6 Cols) -->
                      <template v-if="showSubMurni">
                        <td class="col-pagu" style="border-left: 2px solid #cbd5e1;">{{ formatRupiah(prog.pagu1) }}</td>
                        <td class="col-pagu">{{ formatRupiah(prog.pagu2) }}</td>
                        <td class="col-pagu">{{ formatRupiah(prog.pagu3) }}</td>
                        <td class="col-pagu">{{ formatRupiah(prog.pagu4) }}</td>
                        <td class="col-pagu">{{ formatRupiah(prog.pagu5) }}</td>
                        <td class="col-pagu" style="font-weight: 700; color: #1e3a8a;" :title="getProgramPaguTitle(prog)">
                          {{ formatRupiah(sumProgramPagu(prog)) }}
                        </td>
                      </template>
                      <!-- Pagu Perubahan (6 Cols) -->
                      <template v-if="showSubPerubahan">
                        <td class="col-pagu col-target-p" style="border-left: 2px solid #b45309;">{{ formatRupiah(prog.p_pagu1) }}</td>
                        <td class="col-pagu col-target-p">{{ formatRupiah(prog.p_pagu2) }}</td>
                        <td class="col-pagu col-target-p">{{ formatRupiah(prog.p_pagu3) }}</td>
                        <td class="col-pagu col-target-p">{{ formatRupiah(prog.p_pagu4) }}</td>
                        <td class="col-pagu col-target-p">{{ formatRupiah(prog.p_pagu5) }}</td>
                        <td class="col-pagu col-target-p" style="font-weight: 700; color: #b45309;" :title="getProgramPPaguTitle(prog)">
                          {{ formatRupiah(sumProgramPPagu(prog)) }}
                        </td>
                      </template>
                    </tr>

                    <!-- 2. INDIKATOR PROGRAM -->
                    <tr
                      v-for="(indProg, ipIdx) in prog.indikator_program"
                      :key="'indprog_' + ipIdx"
                      class="row-ind-program"
                      :class="{ 'has-perubahan': indProg.is_perubahan, 'is-baru': indProg.is_baru }"
                    >
                      <td style="text-align: center;">
                        <button
                          class="btn-table-edit"
                          @click="openEditIndikatorProgram(prog, indProg)"
                          title="Ubah Metadata & Target Perubahan Indikator Program"
                        >
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                          <span>Ubah Target</span>
                        </button>
                      </td>
                      <td style="text-align: center;">
                        <span class="badge-hirarki ind-program">IND. PROGRAM</span>
                      </td>
                      <td style="padding-left: 1.5rem;">
                        <div style="display: flex; align-items: flex-start; gap: 0.4rem;">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-top: 3px; flex-shrink: 0;">
                            <polyline points="9 18 15 12 9 6"/>
                          </svg>
                          <div style="display: flex; flex-direction: column; gap: 0.2rem; flex: 1;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                              <span style="font-weight: 500; color: #1e3a8a;">{{ indProg.uraian }}</span>
                              <span v-if="indProg.is_baru" class="badge-status-perubahan baru">
                                <span class="pulse-dot baru"></span> DATA BARU
                              </span>
                              <span v-else-if="indProg.is_perubahan" class="badge-status-perubahan perubahan">
                                <span class="pulse-dot perubahan"></span> ADA PERUBAHAN
                              </span>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td style="text-align: center; color: var(--text-muted); font-size: 0.8rem;">-</td>
                      <td style="text-align: center; color: var(--text-muted); font-size: 0.8rem;">-</td>
                      <td style="text-align: center;">
                        <span class="badge-satuan">{{ indProg.satuan || '-' }}</span>
                      </td>
                      <!-- Target Murni -->
                      <template v-if="showSubMurni">
                        <td class="col-target">{{ indProg.target_awal || '-' }}</td>
                        <td class="col-target">{{ indProg.target2026 || '-' }}</td>
                        <td class="col-target">{{ indProg.target2027 || '-' }}</td>
                        <td class="col-target">{{ indProg.target2028 || '-' }}</td>
                        <td class="col-target">{{ indProg.target2029 || '-' }}</td>
                        <td class="col-target">{{ indProg.target2030 || '-' }}</td>
                        <td class="col-target final">{{ indProg.target_akhir || '-' }}</td>
                      </template>
                      <!-- Target Perubahan -->
                      <template v-if="showSubPerubahan">
                        <td class="col-target col-target-p" :class="{ 'col-target-diff': indProg.changed_targets?.includes('2025') }">{{ indProg.p_target2025 || '-' }}</td>
                        <td class="col-target col-target-p" :class="{ 'col-target-diff': indProg.changed_targets?.includes('2026') }">{{ indProg.p_target2026 || '-' }}</td>
                        <td class="col-target col-target-p" :class="{ 'col-target-diff': indProg.changed_targets?.includes('2027') }">{{ indProg.p_target2027 || '-' }}</td>
                        <td class="col-target col-target-p" :class="{ 'col-target-diff': indProg.changed_targets?.includes('2028') }">{{ indProg.p_target2028 || '-' }}</td>
                        <td class="col-target col-target-p" :class="{ 'col-target-diff': indProg.changed_targets?.includes('2029') }">{{ indProg.p_target2029 || '-' }}</td>
                        <td class="col-target col-target-p" :class="{ 'col-target-diff': indProg.changed_targets?.includes('2030') }">{{ indProg.p_target2030 || '-' }}</td>
                        <td class="col-target final-p">{{ indProg.p_target_akhir || '-' }}</td>
                      </template>
                      <!-- Pagu Murni (strip) -->
                      <template v-if="showSubMurni">
                        <td class="col-pagu" style="color: var(--text-muted); font-size: 0.75rem; border-left: 2px solid #cbd5e1;">-</td>
                        <td class="col-pagu" style="color: var(--text-muted); font-size: 0.75rem;">-</td>
                        <td class="col-pagu" style="color: var(--text-muted); font-size: 0.75rem;">-</td>
                        <td class="col-pagu" style="color: var(--text-muted); font-size: 0.75rem;">-</td>
                        <td class="col-pagu" style="color: var(--text-muted); font-size: 0.75rem;">-</td>
                        <td class="col-pagu" style="color: var(--text-muted); font-size: 0.75rem;">-</td>
                      </template>
                      <!-- Pagu Perubahan (strip) -->
                      <template v-if="showSubPerubahan">
                        <td class="col-pagu col-target-p" style="color: var(--text-muted); font-size: 0.75rem; border-left: 2px solid #b45309;">-</td>
                        <td class="col-pagu col-target-p">{{ formatRupiah(0) === '-' ? '-' : '-' }}</td>
                        <td class="col-pagu col-target-p">-</td>
                        <td class="col-pagu col-target-p">-</td>
                        <td class="col-pagu col-target-p">-</td>
                        <td class="col-pagu col-target-p">-</td>
                      </template>
                    </tr>

                    <!-- 3. KEGIATAN -->
                    <template v-for="(keg, kIdx) in prog.kegiatan" :key="'keg_' + kIdx">
                      <tr class="row-kegiatan">
                        <td style="text-align: center;">
                          <div class="action-dropdown">
                            <button
                              class="btn-action-dropdown"
                              :class="{ active: activeDropdown === 'keg_' + pIdx + '_' + kIdx }"
                              @click.stop="toggleDropdown('keg_' + pIdx + '_' + kIdx, $event)"
                              title="Menu Aksi Kegiatan"
                            >
                              <span>Aksi</span>
                              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <polyline points="6 9 12 15 18 9"/>
                              </svg>
                            </button>
                            <div v-if="activeDropdown === 'keg_' + pIdx + '_' + kIdx" class="dropdown-menu-list">
                              <button class="dropdown-menu-item" @click="openCreateSubkegiatan(prog, keg)">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
                                <span>+ Subkegiatan</span>
                              </button>
                              <button class="dropdown-menu-item" @click="openCreateIndikatorKegiatan(prog, keg)">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                                <span>+ Indikator Kegiatan</span>
                              </button>
                              <div class="dropdown-menu-divider"></div>
                              <button class="dropdown-menu-item" @click="openEditKegiatan(prog, keg)">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                                <span>Ubah Kegiatan</span>
                              </button>
                              <button class="dropdown-menu-item danger" @click="openDeleteKegiatan(prog, keg)">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                                <span>Hapus Kegiatan</span>
                              </button>
                            </div>
                          </div>
                        </td>
                        <td style="text-align: center;">
                          <span class="badge-hirarki kegiatan">KEGIATAN</span>
                        </td>
                        <td style="padding-left: 1.5rem;">
                          <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span class="code-badge-mono">{{ keg.kodekegiatan }}</span>
                            <span>{{ keg.uraikegiatan }}</span>
                          </div>
                        </td>
                        <td style="color: #0369a1; font-weight: 500; font-size: 0.83rem;">
                          {{ keg.kinerja || '-' }}
                        </td>
                        <td :colspan="subTargetColspan" style="text-align: center; color: var(--text-muted); font-size: 0.78rem; font-style: italic;">
                          (Target pada Indikator Kegiatan)
                        </td>
                        <!-- Pagu Murni (6 Cols) -->
                        <template v-if="showSubMurni">
                          <td class="col-pagu" style="border-left: 2px solid #cbd5e1;">{{ formatRupiah(keg.pagu1) }}</td>
                          <td class="col-pagu">{{ formatRupiah(keg.pagu2) }}</td>
                          <td class="col-pagu">{{ formatRupiah(keg.pagu3) }}</td>
                          <td class="col-pagu">{{ formatRupiah(keg.pagu4) }}</td>
                          <td class="col-pagu">{{ formatRupiah(keg.pagu5) }}</td>
                          <td class="col-pagu" style="font-weight: 700; color: #0369a1;" :title="getItemPaguTitle(keg)">
                            {{ formatRupiah(sumItemPagu(keg)) }}
                          </td>
                        </template>
                        <!-- Pagu Perubahan (6 Cols) -->
                        <template v-if="showSubPerubahan">
                          <td class="col-pagu col-target-p" style="border-left: 2px solid #b45309;">{{ formatRupiah(keg.p_pagu1) }}</td>
                          <td class="col-pagu col-target-p">{{ formatRupiah(keg.p_pagu2) }}</td>
                          <td class="col-pagu col-target-p">{{ formatRupiah(keg.p_pagu3) }}</td>
                          <td class="col-pagu col-target-p">{{ formatRupiah(keg.p_pagu4) }}</td>
                          <td class="col-pagu col-target-p">{{ formatRupiah(keg.p_pagu5) }}</td>
                          <td class="col-pagu col-target-p" style="font-weight: 700; color: #b45309;" :title="getItemPPaguTitle(keg)">
                            {{ formatRupiah(sumItemPPagu(keg)) }}
                          </td>
                        </template>
                      </tr>

                      <!-- 4. INDIKATOR KEGIATAN -->
                      <tr
                        v-for="(indKeg, ikIdx) in keg.indikator_kegiatan"
                        :key="'indkeg_' + ikIdx"
                        class="row-ind-kegiatan"
                        :class="{ 'has-perubahan': indKeg.is_perubahan, 'is-baru': indKeg.is_baru }"
                      >
                        <!-- Aksi Ubah Target Indikator Kegiatan -->
                        <td style="text-align: center;">
                          <button
                            class="btn-table-edit"
                            @click="openEditIndikatorKegiatan(prog, keg, indKeg)"
                            title="Ubah Metadata & Target Perubahan Indikator Kegiatan"
                          >
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                            <span>Ubah Target</span>
                          </button>
                        </td>
                        <td style="text-align: center;">
                          <span class="badge-hirarki ind-kegiatan">IND. KEGIATAN</span>
                        </td>
                        <td style="padding-left: 2.25rem;">
                          <div style="display: flex; align-items: flex-start; gap: 0.4rem;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-top: 3px; flex-shrink: 0;">
                              <polyline points="9 18 15 12 9 6"/>
                            </svg>
                            <div style="display: flex; flex-direction: column; gap: 0.2rem; flex: 1;">
                              <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                                <span style="font-weight: 500; color: #115e59;">{{ indKeg.uraian }}</span>
                                <span v-if="indKeg.is_baru" class="badge-status-perubahan baru">
                                  <span class="pulse-dot baru"></span> DATA BARU
                                </span>
                                <span v-else-if="indKeg.is_perubahan" class="badge-status-perubahan perubahan">
                                  <span class="pulse-dot perubahan"></span> ADA PERUBAHAN
                                </span>
                                <span v-if="indKeg.iku === '1' || indKeg.iku === 1" class="badge-iku-tag">IKU</span>
                              </div>
                              <div v-if="indKeg.definisi_operasional && indKeg.definisi_operasional !== '-'" class="indikator-def-box">
                                {{ indKeg.definisi_operasional }}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td style="text-align: center; color: var(--text-muted); font-size: 0.8rem;">-</td>
                        <!-- IKU Indikator Kegiatan -->
                        <td style="text-align: center;">
                          <span v-if="indKeg.iku === '1' || indKeg.iku === 1" class="badge-iku-check" title="Indikator Kinerja Utama (IKU)">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                              <polyline points="20 6 9 17 4 12"/>
                            </svg>
                          </span>
                          <span v-else style="color: #cbd5e1; font-size: 0.85rem;">-</span>
                        </td>
                        <td style="text-align: center;">
                          <span class="badge-satuan">{{ indKeg.satuan || '-' }}</span>
                        </td>
                        <!-- Target Murni -->
                        <template v-if="showSubMurni">
                          <td class="col-target">{{ indKeg.target_awal || '-' }}</td>
                          <td class="col-target">{{ indKeg.target2026 || '-' }}</td>
                          <td class="col-target">{{ indKeg.target2027 || '-' }}</td>
                          <td class="col-target">{{ indKeg.target2028 || '-' }}</td>
                          <td class="col-target">{{ indKeg.target2029 || '-' }}</td>
                          <td class="col-target">{{ indKeg.target2030 || '-' }}</td>
                          <td class="col-target final">{{ indKeg.target_akhir || '-' }}</td>
                        </template>
                        <!-- Target Perubahan -->
                        <template v-if="showSubPerubahan">
                          <td class="col-target col-target-p" :class="{ 'col-target-diff': indKeg.changed_targets?.includes('2025') }">{{ indKeg.p_target2025 || '-' }}</td>
                          <td class="col-target col-target-p" :class="{ 'col-target-diff': indKeg.changed_targets?.includes('2026') }">{{ indKeg.p_target2026 || '-' }}</td>
                          <td class="col-target col-target-p" :class="{ 'col-target-diff': indKeg.changed_targets?.includes('2027') }">{{ indKeg.p_target2027 || '-' }}</td>
                          <td class="col-target col-target-p" :class="{ 'col-target-diff': indKeg.changed_targets?.includes('2028') }">{{ indKeg.p_target2028 || '-' }}</td>
                          <td class="col-target col-target-p" :class="{ 'col-target-diff': indKeg.changed_targets?.includes('2029') }">{{ indKeg.p_target2029 || '-' }}</td>
                          <td class="col-target col-target-p" :class="{ 'col-target-diff': indKeg.changed_targets?.includes('2030') }">{{ indKeg.p_target2030 || '-' }}</td>
                          <td class="col-target final-p">{{ indKeg.p_target_akhir || '-' }}</td>
                        </template>
                        <!-- Pagu Murni -->
                        <template v-if="showSubMurni">
                          <td class="col-pagu" style="border-left: 2px solid #cbd5e1;">{{ indKeg.pagu1 ? formatRupiah(indKeg.pagu1) : '-' }}</td>
                          <td class="col-pagu">{{ indKeg.pagu2 ? formatRupiah(indKeg.pagu2) : '-' }}</td>
                          <td class="col-pagu">{{ indKeg.pagu3 ? formatRupiah(indKeg.pagu3) : '-' }}</td>
                          <td class="col-pagu">{{ indKeg.pagu4 ? formatRupiah(indKeg.pagu4) : '-' }}</td>
                          <td class="col-pagu">{{ indKeg.pagu5 ? formatRupiah(indKeg.pagu5) : '-' }}</td>
                          <td class="col-pagu" style="font-weight: 600;" :title="getItemPaguTitle(indKeg)">
                            {{ sumItemPagu(indKeg) > 0 ? formatRupiah(sumItemPagu(indKeg)) : '-' }}
                          </td>
                        </template>
                        <!-- Pagu Perubahan -->
                        <template v-if="showSubPerubahan">
                          <td class="col-pagu col-target-p" style="border-left: 2px solid #b45309;">{{ indKeg.p_pagu1 ? formatRupiah(indKeg.p_pagu1) : '-' }}</td>
                          <td class="col-pagu col-target-p">{{ indKeg.p_pagu2 ? formatRupiah(indKeg.p_pagu2) : '-' }}</td>
                          <td class="col-pagu col-target-p">{{ indKeg.p_pagu3 ? formatRupiah(indKeg.p_pagu3) : '-' }}</td>
                          <td class="col-pagu col-target-p">{{ indKeg.p_pagu4 ? formatRupiah(indKeg.p_pagu4) : '-' }}</td>
                          <td class="col-pagu col-target-p">{{ indKeg.p_pagu5 ? formatRupiah(indKeg.p_pagu5) : '-' }}</td>
                          <td class="col-pagu col-target-p" style="font-weight: 600; color: #b45309;" :title="getItemPPaguTitle(indKeg)">
                            {{ sumItemPPagu(indKeg) > 0 ? formatRupiah(sumItemPPagu(indKeg)) : '-' }}
                          </td>
                        </template>
                      </tr>

                      <!-- 5. SUBKEGIATAN -->
                      <template v-for="(subkeg, skIdx) in keg.subkegiatan" :key="'subkeg_' + skIdx">
                        <tr class="row-subkegiatan">
                          <td style="text-align: center;">
                            <div class="action-dropdown">
                              <button
                                class="btn-action-dropdown"
                                :class="{ active: activeDropdown === 'subkeg_' + pIdx + '_' + kIdx + '_' + skIdx }"
                                @click.stop="toggleDropdown('subkeg_' + pIdx + '_' + kIdx + '_' + skIdx, $event)"
                                title="Menu Aksi Subkegiatan"
                              >
                                <span>Aksi</span>
                                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                  <polyline points="6 9 12 15 18 9"/>
                                </svg>
                              </button>
                              <div v-if="activeDropdown === 'subkeg_' + pIdx + '_' + kIdx + '_' + skIdx" class="dropdown-menu-list">
                                <button class="dropdown-menu-item" @click="openEditSubkegiatan(prog, keg, subkeg)">
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                                  <span>Ubah Subkegiatan</span>
                                </button>
                                <div class="dropdown-menu-divider"></div>
                                <button class="dropdown-menu-item danger" @click="openDeleteSubkegiatan(prog, keg, subkeg)">
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                                  <span>Hapus Subkegiatan</span>
                                </button>
                              </div>
                            </div>
                          </td>
                          <td style="text-align: center;">
                            <span class="badge-hirarki subkegiatan">SUBKEGIATAN</span>
                          </td>
                          <td style="padding-left: 2.75rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                              <span class="code-badge-mono">{{ subkeg.kodesubkegiatan }}</span>
                              <span>{{ subkeg.uraisubkegiatan }}</span>
                            </div>
                          </td>
                          <td style="color: #047857; font-weight: 500; font-size: 0.83rem;">
                            {{ subkeg.kinerja || '-' }}
                          </td>
                          <td :colspan="subTargetColspan" style="text-align: center; color: var(--text-muted); font-size: 0.78rem; font-style: italic;">
                            (Target pada Indikator Subkegiatan)
                          </td>
                          <!-- Pagu Murni (6 Cols) -->
                          <template v-if="showSubMurni">
                            <td class="col-pagu" style="border-left: 2px solid #cbd5e1;">{{ formatRupiah(subkeg.pagu1) }}</td>
                            <td class="col-pagu">{{ formatRupiah(subkeg.pagu2) }}</td>
                            <td class="col-pagu">{{ formatRupiah(subkeg.pagu3) }}</td>
                            <td class="col-pagu">{{ formatRupiah(subkeg.pagu4) }}</td>
                            <td class="col-pagu">{{ formatRupiah(subkeg.pagu5) }}</td>
                            <td class="col-pagu" style="font-weight: 700; color: #047857;" :title="getItemPaguTitle(subkeg)">
                              {{ formatRupiah(sumSubkegPagu(subkeg)) }}
                            </td>
                          </template>
                          <!-- Pagu Perubahan (6 Cols) -->
                          <template v-if="showSubPerubahan">
                            <td class="col-pagu col-target-p" style="border-left: 2px solid #b45309;">{{ formatRupiah(subkeg.p_pagu1) }}</td>
                            <td class="col-pagu col-target-p">{{ formatRupiah(subkeg.p_pagu2) }}</td>
                            <td class="col-pagu col-target-p">{{ formatRupiah(subkeg.p_pagu3) }}</td>
                            <td class="col-pagu col-target-p">{{ formatRupiah(subkeg.p_pagu4) }}</td>
                            <td class="col-pagu col-target-p">{{ formatRupiah(subkeg.p_pagu5) }}</td>
                            <td class="col-pagu col-target-p" style="font-weight: 700; color: #b45309;" :title="getItemPPaguTitle(subkeg)">
                              {{ formatRupiah(sumSubkegPPagu(subkeg)) }}
                            </td>
                          </template>
                        </tr>

                        <!-- 6. INDIKATOR SUBKEGIATAN -->
                        <tr
                          v-if="subkeg.indikator"
                          class="row-ind-subkegiatan"
                          :class="{ 'has-perubahan': subkeg.indikator.is_perubahan, 'is-baru': subkeg.indikator.is_baru }"
                        >
                          <td style="text-align: center;">
                            <button
                              class="btn-table-edit"
                              @click="openEditSubkegiatan(prog, keg, subkeg)"
                              title="Ubah Target & Volume Indikator Subkegiatan"
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                              </svg>
                              <span>Ubah Target</span>
                            </button>
                          </td>
                          <td style="text-align: center;">
                            <span class="badge-hirarki ind-subkegiatan">IND. SUBKEGIATAN</span>
                          </td>
                          <td style="padding-left: 3.5rem;">
                            <div style="display: flex; align-items: flex-start; gap: 0.4rem;">
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-top: 3px; flex-shrink: 0;">
                                <polyline points="9 18 15 12 9 6"/>
                              </svg>
                              <div style="display: flex; flex-direction: column; gap: 0.2rem; flex: 1;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                                  <span>{{ subkeg.indikator.uraian }}</span>
                                  <span v-if="subkeg.indikator.is_baru" class="badge-status-perubahan baru">
                                    <span class="pulse-dot baru"></span> DATA BARU
                                  </span>
                                  <span v-else-if="subkeg.indikator.is_perubahan" class="badge-status-perubahan perubahan">
                                    <span class="pulse-dot perubahan"></span> ADA PERUBAHAN
                                  </span>
                                </div>
                              </div>
                            </div>
                          </td>
                          <td style="text-align: center; color: var(--text-muted); font-size: 0.8rem;">-</td>
                          <td style="text-align: center; color: var(--text-muted); font-size: 0.8rem;">-</td>
                          <td style="text-align: center;">
                            <span class="badge-satuan">{{ subkeg.indikator.satuan || '-' }}</span>
                          </td>
                          <!-- Target Murni -->
                          <template v-if="showSubMurni">
                            <td class="col-target">{{ subkeg.indikator.volume_awal || '-' }}</td>
                            <td class="col-target" :title="`2025 (vol 0): ${subkeg.indikator.volume_0 || '-'}`">{{ subkeg.indikator.volume_1 || '-' }}</td>
                            <td class="col-target">{{ subkeg.indikator.volume_2 || '-' }}</td>
                            <td class="col-target">{{ subkeg.indikator.volume_3 || '-' }}</td>
                            <td class="col-target">{{ subkeg.indikator.volume_4 || '-' }}</td>
                            <td class="col-target">{{ subkeg.indikator.volume_5 || '-' }}</td>
                            <td class="col-target final">{{ subkeg.indikator.volume_akhir || '-' }}</td>
                          </template>
                          <!-- Target Perubahan -->
                          <template v-if="showSubPerubahan">
                            <td class="col-target col-target-p" :class="{ 'col-target-diff': subkeg.indikator.changed_targets?.includes('2025') }">{{ subkeg.indikator.p_volume_0 || '-' }}</td>
                            <td class="col-target col-target-p" :class="{ 'col-target-diff': subkeg.indikator.changed_targets?.includes('2026') }">{{ subkeg.indikator.p_volume_1 || '-' }}</td>
                            <td class="col-target col-target-p" :class="{ 'col-target-diff': subkeg.indikator.changed_targets?.includes('2027') }">{{ subkeg.indikator.p_volume_2 || '-' }}</td>
                            <td class="col-target col-target-p" :class="{ 'col-target-diff': subkeg.indikator.changed_targets?.includes('2028') }">{{ subkeg.indikator.p_volume_3 || '-' }}</td>
                            <td class="col-target col-target-p" :class="{ 'col-target-diff': subkeg.indikator.changed_targets?.includes('2029') }">{{ subkeg.indikator.p_volume_4 || '-' }}</td>
                            <td class="col-target col-target-p" :class="{ 'col-target-diff': subkeg.indikator.changed_targets?.includes('2030') }">{{ subkeg.indikator.p_volume_5 || '-' }}</td>
                            <td class="col-target final-p">{{ subkeg.indikator.p_volume_akhir || '-' }}</td>
                          </template>
                          <!-- Pagu Murni -->
                          <template v-if="showSubMurni">
                            <td class="col-pagu" style="border-left: 2px solid #cbd5e1;">{{ formatRupiah(subkeg.indikator.pagu1) }}</td>
                            <td class="col-pagu">{{ formatRupiah(subkeg.indikator.pagu2) }}</td>
                            <td class="col-pagu">{{ formatRupiah(subkeg.indikator.pagu3) }}</td>
                            <td class="col-pagu">{{ formatRupiah(subkeg.indikator.pagu4) }}</td>
                            <td class="col-pagu">{{ formatRupiah(subkeg.indikator.pagu5) }}</td>
                            <td class="col-pagu" style="font-weight: 600;" :title="getItemPaguTitle(subkeg.indikator)">
                              {{ sumItemPagu(subkeg.indikator) > 0 ? formatRupiah(sumItemPagu(subkeg.indikator)) : '-' }}
                            </td>
                          </template>
                          <!-- Pagu Perubahan -->
                          <template v-if="showSubPerubahan">
                            <td class="col-pagu col-target-p" style="border-left: 2px solid #b45309;">{{ formatRupiah(subkeg.indikator.p_pagu1) }}</td>
                            <td class="col-pagu col-target-p">{{ formatRupiah(subkeg.indikator.p_pagu2) }}</td>
                            <td class="col-pagu col-target-p">{{ formatRupiah(subkeg.indikator.p_pagu3) }}</td>
                            <td class="col-pagu col-target-p">{{ formatRupiah(subkeg.indikator.p_pagu4) }}</td>
                            <td class="col-pagu col-target-p">{{ formatRupiah(subkeg.indikator.p_pagu5) }}</td>
                            <td class="col-pagu col-target-p" style="font-weight: 600; color: #b45309;" :title="getItemPPaguTitle(subkeg.indikator)">
                              {{ sumItemPPagu(subkeg.indikator) > 0 ? formatRupiah(sumItemPPagu(subkeg.indikator)) : '-' }}
                            </td>
                          </template>
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
    </main>

    <!-- CRUD Modal Dialog -->
    <RenstraCrudModal
      :is-open="isCrudModalOpen"
      :mode="crudModalMode"
      :item-data="crudModalItem"
      :id-skpd="opdIdNumber"
      @close="isCrudModalOpen = false"
      @saved="handleCrudSaved"
      @deleted="handleCrudDeleted"
    />

    <!-- Toast Feedback Notification -->
    <div v-if="toastVisible" class="toast-feedback">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../services/api';
import RenstraCrudModal from '../components/RenstraCrudModal.vue';

const route = useRoute();

const opdInfo = ref(null);
const cascadingData = ref(null);
const subList = ref([]);
const loadingCascading = ref(false);

const activeTab = ref('tujuan_sasaran'); // 'tujuan_sasaran' | 'program_kegiatan'
const searchCascading = ref('');
const searchSub = ref('');

// Sub SKPD Cascading Program / Kegiatan / Subkegiatan State
const selectedSubSkpd = ref(null);
const subCascadingData = ref(null);
const loadingSubCascading = ref(false);
const searchProgramCascading = ref('');

// Filter Status Perubahan / Data Baru
const changeFilter = ref('all'); // 'all' | 'perubahan' | 'baru'

// Target View Filter (All, Murni, Perubahan)
const targetViewFilter = ref('all');
const showTargetMurni = computed(() => targetViewFilter.value === 'all' || targetViewFilter.value === 'murni');
const showTargetPerubahan = computed(() => targetViewFilter.value === 'all' || targetViewFilter.value === 'perubahan');
const totalTargetColumns = computed(() => {
  let count = 0;
  if (showTargetMurni.value) count += 7;
  if (showTargetPerubahan.value) count += 7;
  return count;
});
const tujuanSasaranColspan = computed(() => 3 + totalTargetColumns.value);

// Target & Pagu View Filter for Sub SKPD Cascading (All, Murni, Perubahan)
const subTargetViewFilter = ref('all');
const showSubMurni = computed(() => subTargetViewFilter.value === 'all' || subTargetViewFilter.value === 'murni');
const showSubPerubahan = computed(() => subTargetViewFilter.value === 'all' || subTargetViewFilter.value === 'perubahan');
const subTargetColspan = computed(() => 2 + (showSubMurni.value ? 7 : 0) + (showSubPerubahan.value ? 7 : 0));

// Dropdown State
const activeDropdown = ref(null);

function toggleDropdown(id, event) {
  if (event) event.stopPropagation();
  if (activeDropdown.value === id) {
    activeDropdown.value = null;
  } else {
    activeDropdown.value = id;
  }
}

function closeDropdown() {
  activeDropdown.value = null;
}

// CRUD Modal States
const isCrudModalOpen = ref(false);
const crudModalMode = ref('create_tujuan');
const crudModalItem = ref(null);

// Toast States
const toastVisible = ref(false);
const toastMessage = ref('');

const opdIdNumber = computed(() => {
  return Number(route.params.id) || null;
});

async function loadOpdRenstra() {
  const idSkpd = route.params.id;
  if (!idSkpd) return;

  loadingCascading.value = true;
  try {
    const [cascadingRes, opdDetailRes] = await Promise.all([
      api.getOpdRenstraCascading(idSkpd),
      api.getOpdDetail(idSkpd)
    ]);
    cascadingData.value = cascadingRes;
    opdInfo.value = opdDetailRes;
    subList.value = opdDetailRes.sub_pd_list || [];
  } catch (err) {
    console.error('Gagal mengambil data RENSTRA:', err);
  } finally {
    loadingCascading.value = false;
  }
}

// ===================================================
// CRUD Handlers
// ===================================================

function showToast(msg) {
  toastMessage.value = msg;
  toastVisible.value = true;
  setTimeout(() => {
    toastVisible.value = false;
  }, 3500);
}

function handleCrudSaved() {
  showToast('Data berhasil disimpan ke database!');
  loadOpdRenstra();
  if (selectedSubSkpd.value) {
    selectSubSkpd(selectedSubSkpd.value);
  }
}

function handleCrudDeleted() {
  showToast('Data berhasil dihapus dari database!');
  loadOpdRenstra();
  if (selectedSubSkpd.value) {
    selectSubSkpd(selectedSubSkpd.value);
  }
}

// Tujuan Actions
function openCreateTujuan() {
  crudModalMode.value = 'create_tujuan';
  crudModalItem.value = {
    suggested_no: (cascadingData.value?.total_tujuan || 0) + 1,
  };
  isCrudModalOpen.value = true;
}

function openEditTujuan(tujuan) {
  crudModalMode.value = 'edit_tujuan';
  crudModalItem.value = {
    id: tujuan.idtujuan,
    uraian: tujuan.uraitujuan,
    no_urut: tujuan.no_urut,
    perubahan_status: tujuan.perubahan_status || 'otomatis',
  };
  isCrudModalOpen.value = true;
}

function openDeleteTujuan(tujuan) {
  crudModalMode.value = 'delete';
  crudModalItem.value = {
    type: 'tujuan',
    id: tujuan.idtujuan,
    uraian: tujuan.uraitujuan,
  };
  isCrudModalOpen.value = true;
}

// Indikator Tujuan Actions
function openCreateIndikatorTujuan(tujuan) {
  crudModalMode.value = 'create_ind_tujuan';
  crudModalItem.value = {
    idtujuan: tujuan.idtujuan,
    suggested_no: (tujuan.indikator_tujuan?.length || 0) + 1,
  };
  isCrudModalOpen.value = true;
}

function openEditIndikatorTujuan(ind) {
  crudModalMode.value = 'edit_ind_tujuan';
  crudModalItem.value = {
    id: ind.id,
    uraian: ind.uraian,
    satuan: ind.satuan,
    status: ind.status,
    iku: ind.iku || '0',
    perubahan_status: ind.perubahan_status || 'otomatis',
    definisi_operasional: ind.definisi_operasional,
    target_awal: ind.target_awal,
    target2026: ind.target2026,
    target2027: ind.target2027,
    target2028: ind.target2028,
    target2029: ind.target2029,
    target2030: ind.target2030,
    target_akhir: ind.target_akhir,
    p_target2025: ind.p_target2025,
    p_target2026: ind.p_target2026,
    p_target2027: ind.p_target2027,
    p_target2028: ind.p_target2028,
    p_target2029: ind.p_target2029,
    p_target2030: ind.p_target2030,
    p_target_akhir: ind.p_target_akhir,
  };
  isCrudModalOpen.value = true;
}

function openDeleteIndikatorTujuan(ind) {
  crudModalMode.value = 'delete';
  crudModalItem.value = {
    type: 'ind_tujuan',
    id: ind.id,
    uraian: ind.uraian,
  };
  isCrudModalOpen.value = true;
}

// Sasaran Actions
function openCreateSasaran(tujuan) {
  crudModalMode.value = 'create_sasaran';
  crudModalItem.value = {
    idtujuan: tujuan.idtujuan,
    suggested_no: (tujuan.sasaran?.length || 0) + 1,
  };
  isCrudModalOpen.value = true;
}

function openEditSasaran(sasaran) {
  crudModalMode.value = 'edit_sasaran';
  crudModalItem.value = {
    id: sasaran.idsasaran,
    uraian: sasaran.uraisasaran,
    no_urut: sasaran.no_urut,
    perubahan_status: sasaran.perubahan_status || 'otomatis',
  };
  isCrudModalOpen.value = true;
}

function openDeleteSasaran(sasaran) {
  crudModalMode.value = 'delete';
  crudModalItem.value = {
    type: 'sasaran',
    id: sasaran.idsasaran,
    uraian: sasaran.uraisasaran,
  };
  isCrudModalOpen.value = true;
}

// Indikator Sasaran Actions
function openCreateIndikatorSasaran(sasaran) {
  crudModalMode.value = 'create_ind_sasaran';
  crudModalItem.value = {
    idsasaran: sasaran.idsasaran,
    suggested_no: (sasaran.indikator_sasaran?.length || 0) + 1,
  };
  isCrudModalOpen.value = true;
}

function openEditIndikatorSasaran(ind) {
  crudModalMode.value = 'edit_ind_sasaran';
  crudModalItem.value = {
    id: ind.id,
    uraian: ind.uraian,
    satuan: ind.satuan,
    status: ind.status,
    iku: ind.iku || '0',
    perubahan_status: ind.perubahan_status || 'otomatis',
    definisi_operasional: ind.definisi_operasional,
    target_awal: ind.target_awal,
    target2026: ind.target2026,
    target2027: ind.target2027,
    target2028: ind.target2028,
    target2029: ind.target2029,
    target2030: ind.target2030,
    target_akhir: ind.target_akhir,
    p_target2025: ind.p_target2025,
    p_target2026: ind.p_target2026,
    p_target2027: ind.p_target2027,
    p_target2028: ind.p_target2028,
    p_target2029: ind.p_target2029,
    p_target2030: ind.p_target2030,
    p_target_akhir: ind.p_target_akhir,
  };
  isCrudModalOpen.value = true;
}

function openDeleteIndikatorSasaran(ind) {
  crudModalMode.value = 'delete';
  crudModalItem.value = {
    type: 'ind_sasaran',
    id: ind.id,
    uraian: ind.uraian,
  };
  isCrudModalOpen.value = true;
}

// Indikator Kegiatan Actions
function openCreateIndikatorKegiatan(prog, keg) {
  crudModalMode.value = 'create_ind_kegiatan';
  crudModalItem.value = {
    kodeskpd: selectedSubSkpd.value?.kode_sub_skpd,
    kodekegiatan: keg.kodekegiatan,
    kodeprogram: prog.kodeprogram,
    uraikegiatan: keg.uraikegiatan,
    suggested_no: (keg.indikator_kegiatan?.length || 0) + 1,
  };
  isCrudModalOpen.value = true;
}

function openEditIndikatorKegiatan(prog, keg, indKeg) {
  crudModalMode.value = 'edit_ind_kegiatan';
  crudModalItem.value = {
    id: indKeg.id,
    uraian: indKeg.uraian,
    satuan: indKeg.satuan,
    status: indKeg.status,
    iku: indKeg.iku || '0',
    perubahan_status: indKeg.perubahan_status || 'otomatis',
    definisi_operasional: indKeg.definisi_operasional,
    target_awal: indKeg.target_awal,
    target2026: indKeg.target2026,
    target2027: indKeg.target2027,
    target2028: indKeg.target2028,
    target2029: indKeg.target2029,
    target2030: indKeg.target2030,
    target_akhir: indKeg.target_akhir,
    p_target2025: indKeg.p_target2025,
    p_target2026: indKeg.p_target2026,
    p_target2027: indKeg.p_target2027,
    p_target2028: indKeg.p_target2028,
    p_target2029: indKeg.p_target2029,
    p_target2030: indKeg.p_target2030,
    p_target_akhir: indKeg.p_target_akhir,
    pagu1: indKeg.pagu1,
    pagu2: indKeg.pagu2,
    pagu3: indKeg.pagu3,
    pagu4: indKeg.pagu4,
    pagu5: indKeg.pagu5,
    p_pagu1: indKeg.p_pagu1,
    p_pagu2: indKeg.p_pagu2,
    p_pagu3: indKeg.p_pagu3,
    p_pagu4: indKeg.p_pagu4,
    p_pagu5: indKeg.p_pagu5,
  };
  isCrudModalOpen.value = true;
}

function openEditIndikatorProgram(prog, indProg) {
  crudModalMode.value = 'edit_ind_program';
  crudModalItem.value = {
    id: indProg.id,
    kodeprogram: prog.kodeprogram,
    uraian: indProg.uraian,
    satuan: indProg.satuan,
    status: indProg.status,
    perubahan_status: indProg.perubahan_status || 'otomatis',
    target_awal: indProg.target_awal,
    target2026: indProg.target2026,
    target2027: indProg.target2027,
    target2028: indProg.target2028,
    target2029: indProg.target2029,
    target2030: indProg.target2030,
    target_akhir: indProg.target_akhir,
    p_target2025: indProg.p_target2025,
    p_target2026: indProg.p_target2026,
    p_target2027: indProg.p_target2027,
    p_target2028: indProg.p_target2028,
    p_target2029: indProg.p_target2029,
    p_target2030: indProg.p_target2030,
    p_target_akhir: indProg.p_target_akhir,
  };
  isCrudModalOpen.value = true;
}

// Program Actions
function openCreateProgram() {
  crudModalMode.value = 'create_program';
  crudModalItem.value = {
    kodeskpd: selectedSubSkpd.value?.kode_sub_skpd,
  };
  isCrudModalOpen.value = true;
}

function openEditProgram(prog) {
  closeDropdown();
  crudModalMode.value = 'edit_program';
  crudModalItem.value = {
    id: prog.id,
    kodeprogram: prog.kodeprogram,
    uraiprogram: prog.uraiprogram,
    kinerja: prog.kinerja,
  };
  isCrudModalOpen.value = true;
}

function openDeleteProgram(prog) {
  closeDropdown();
  crudModalMode.value = 'delete';
  crudModalItem.value = {
    type: 'program',
    id: prog.id,
    uraian: `${prog.kodeprogram} ${prog.uraiprogram}`,
  };
  isCrudModalOpen.value = true;
}

// Kegiatan Actions
function openCreateKegiatan(prog) {
  closeDropdown();
  crudModalMode.value = 'create_kegiatan';
  crudModalItem.value = {
    kodeskpd: selectedSubSkpd.value?.kode_sub_skpd,
    kodeprogram: prog.kodeprogram,
  };
  isCrudModalOpen.value = true;
}

function openEditKegiatan(prog, keg) {
  closeDropdown();
  crudModalMode.value = 'edit_kegiatan';
  crudModalItem.value = {
    id: keg.id,
    kodeprogram: prog.kodeprogram,
    kodekegiatan: keg.kodekegiatan,
    uraikegiatan: keg.uraikegiatan,
    kinerja: keg.kinerja,
  };
  isCrudModalOpen.value = true;
}

function openDeleteKegiatan(prog, keg) {
  closeDropdown();
  crudModalMode.value = 'delete';
  crudModalItem.value = {
    type: 'kegiatan',
    id: keg.id,
    uraian: `${keg.kodekegiatan} ${keg.uraikegiatan}`,
  };
  isCrudModalOpen.value = true;
}

// Subkegiatan Actions
function openCreateSubkegiatan(prog, keg) {
  closeDropdown();
  crudModalMode.value = 'create_subkegiatan';
  crudModalItem.value = {
    kodeskpd: selectedSubSkpd.value?.kode_sub_skpd,
    kodeprogram: prog.kodeprogram,
    kodekegiatan: keg.kodekegiatan,
  };
  isCrudModalOpen.value = true;
}

function openEditSubkegiatan(prog, keg, subkeg) {
  closeDropdown();
  crudModalMode.value = 'edit_subkegiatan';
  crudModalItem.value = {
    id: subkeg.id,
    kodeprogram: prog.kodeprogram,
    kodekegiatan: keg.kodekegiatan,
    kodesubkegiatan: subkeg.kodesubkegiatan,
    uraisubkegiatan: subkeg.uraisubkegiatan,
    kinerja: subkeg.kinerja,
    indikator: subkeg.indikator,
    volume_awal: subkeg.indikator?.volume_awal || '-',
    volume_0: subkeg.indikator?.volume_0 || '-',
    volume_1: subkeg.indikator?.volume_1 || '-',
    volume_2: subkeg.indikator?.volume_2 || '-',
    volume_3: subkeg.indikator?.volume_3 || '-',
    volume_4: subkeg.indikator?.volume_4 || '-',
    volume_5: subkeg.indikator?.volume_5 || '-',
    p_volume_0: subkeg.indikator?.p_volume_0 || '-',
    p_volume_1: subkeg.indikator?.p_volume_1 || '-',
    p_volume_2: subkeg.indikator?.p_volume_2 || '-',
    p_volume_3: subkeg.indikator?.p_volume_3 || '-',
    p_volume_4: subkeg.indikator?.p_volume_4 || '-',
    p_volume_5: subkeg.indikator?.p_volume_5 || '-',
    p_volume_akhir: subkeg.indikator?.p_volume_akhir || '-',
    pagu1: subkeg.pagu1,
    pagu2: subkeg.pagu2,
    pagu3: subkeg.pagu3,
    pagu4: subkeg.pagu4,
    pagu5: subkeg.pagu5,
    p_pagu1: subkeg.p_pagu1 !== undefined ? subkeg.p_pagu1 : subkeg.pagu1,
    p_pagu2: subkeg.p_pagu2 !== undefined ? subkeg.p_pagu2 : subkeg.pagu2,
    p_pagu3: subkeg.p_pagu3 !== undefined ? subkeg.p_pagu3 : subkeg.pagu3,
    p_pagu4: subkeg.p_pagu4 !== undefined ? subkeg.p_pagu4 : subkeg.pagu4,
    p_pagu5: subkeg.p_pagu5 !== undefined ? subkeg.p_pagu5 : subkeg.pagu5,
  };
  isCrudModalOpen.value = true;
}

function openDeleteSubkegiatan(prog, keg, subkeg) {
  closeDropdown();
  crudModalMode.value = 'delete';
  crudModalItem.value = {
    type: 'subkegiatan',
    id: subkeg.id,
    uraian: `${subkeg.kodesubkegiatan} ${subkeg.uraisubkegiatan}`,
  };
  isCrudModalOpen.value = true;
}

// ===================================================
// Filters
// ===================================================

const filteredTujuanList = computed(() => {
  if (!cascadingData.value?.tujuan_list) return [];
  const q = searchCascading.value.trim().toLowerCase();
  const cFilter = changeFilter.value;

  return cascadingData.value.tujuan_list.filter(t => {
    // Check change filter
    if (cFilter === 'perubahan') {
      const hasPerubahan = (t.total_perubahan > 0) || (t.perubahan_status === 'perubahan');
      if (!hasPerubahan) return false;
    } else if (cFilter === 'baru') {
      const hasBaru = (t.total_baru > 0) || t.is_baru || (t.perubahan_status === 'baru');
      if (!hasBaru) return false;
    }

    if (!q) return true;

    const matchTujuan = t.uraitujuan && t.uraitujuan.toLowerCase().includes(q);
    const matchIndTujuan = t.indikator_tujuan && t.indikator_tujuan.some(it => it.uraian.toLowerCase().includes(q));
    const matchSasaran = t.sasaran && t.sasaran.some(s => {
      const matchS = s.uraisasaran && s.uraisasaran.toLowerCase().includes(q);
      const matchIS = s.indikator_sasaran && s.indikator_sasaran.some(is => is.uraian.toLowerCase().includes(q));
      return matchS || matchIS;
    });
    return matchTujuan || matchIndTujuan || matchSasaran;
  });
});

const filteredSubList = computed(() => {
  if (!searchSub.value.trim()) return subList.value;
  const q = searchSub.value.trim().toLowerCase();
  return subList.value.filter(s => {
    const namaMatch = s.nama_sub_skpd && s.nama_sub_skpd.toLowerCase().includes(q);
    const kodeMatch = s.kode_sub_skpd && s.kode_sub_skpd.toLowerCase().includes(q);
    return namaMatch || kodeMatch;
  });
});

// ===================================================
// Sub SKPD Cascading Helpers & Handlers
// ===================================================

async function selectSubSkpd(sub) {
  selectedSubSkpd.value = sub;
  searchProgramCascading.value = '';
  loadingSubCascading.value = true;
  try {
    const data = await api.getSubSkpdCascading(sub.id_sub_skpd);
    subCascadingData.value = data;
  } catch (err) {
    console.error('Gagal mengambil data cascading Sub SKPD:', err);
    showToast('Gagal memuat cascading Sub SKPD: ' + (err.message || 'Error'));
  } finally {
    loadingSubCascading.value = false;
  }
}

function backToSubList() {
  selectedSubSkpd.value = null;
  subCascadingData.value = null;
  searchProgramCascading.value = '';
}

function onSubSwitcherChange(idSubSkpd) {
  const target = subList.value.find(s => String(s.id_sub_skpd) === String(idSubSkpd));
  if (target) {
    selectSubSkpd(target);
  }
}

function formatRupiah(val) {
  if (val === null || val === undefined || isNaN(val) || val === 0) return 'Rp 0';
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(val);
}

function sumProgramPagu(prog) {
  if (!prog) return 0;
  return (Number(prog.pagu1) || 0) +
         (Number(prog.pagu2) || 0) +
         (Number(prog.pagu3) || 0) +
         (Number(prog.pagu4) || 0) +
         (Number(prog.pagu5) || 0);
}

function sumItemPagu(item) {
  if (!item) return 0;
  return (Number(item.pagu1) || 0) +
         (Number(item.pagu2) || 0) +
         (Number(item.pagu3) || 0) +
         (Number(item.pagu4) || 0) +
         (Number(item.pagu5) || 0);
}

function sumSubkegPagu(subkeg) {
  if (!subkeg) return 0;
  if (subkeg.indikator) return sumItemPagu(subkeg.indikator);
  return sumItemPagu(subkeg);
}

function getProgramPaguTitle(p) {
  return `2026: ${formatRupiah(p.pagu1)} | 2027: ${formatRupiah(p.pagu2)} | 2028: ${formatRupiah(p.pagu3)} | 2029: ${formatRupiah(p.pagu4)} | 2030: ${formatRupiah(p.pagu5)}`;
}

function getItemPaguTitle(item) {
  return `2026: ${formatRupiah(item.pagu1)} | 2027: ${formatRupiah(item.pagu2)} | 2028: ${formatRupiah(item.pagu3)} | 2029: ${formatRupiah(item.pagu4)} | 2030: ${formatRupiah(item.pagu5)}`;
}

const totalAllProgramPagu = computed(() => {
  if (!subCascadingData.value?.program_list) return 0;
  return subCascadingData.value.program_list.reduce((acc, p) => acc + sumProgramPagu(p), 0);
});

function sumProgramPPagu(prog) {
  if (!prog) return 0;
  return (Number(prog.p_pagu1) || 0) +
         (Number(prog.p_pagu2) || 0) +
         (Number(prog.p_pagu3) || 0) +
         (Number(prog.p_pagu4) || 0) +
         (Number(prog.p_pagu5) || 0);
}

function sumItemPPagu(item) {
  if (!item) return 0;
  return (Number(item.p_pagu1) || 0) +
         (Number(item.p_pagu2) || 0) +
         (Number(item.p_pagu3) || 0) +
         (Number(item.p_pagu4) || 0) +
         (Number(item.p_pagu5) || 0);
}

function sumSubkegPPagu(subkeg) {
  if (!subkeg) return 0;
  if (subkeg.indikator) return sumItemPPagu(subkeg.indikator);
  return sumItemPPagu(subkeg);
}

function getProgramPPaguTitle(p) {
  return `2026: ${formatRupiah(p.p_pagu1)} | 2027: ${formatRupiah(p.p_pagu2)} | 2028: ${formatRupiah(p.p_pagu3)} | 2029: ${formatRupiah(p.p_pagu4)} | 2030: ${formatRupiah(p.p_pagu5)}`;
}

function getItemPPaguTitle(item) {
  return `2026: ${formatRupiah(item.p_pagu1)} | 2027: ${formatRupiah(item.p_pagu2)} | 2028: ${formatRupiah(item.p_pagu3)} | 2029: ${formatRupiah(item.p_pagu4)} | 2030: ${formatRupiah(item.p_pagu5)}`;
}

const totalAllProgramPPagu = computed(() => {
  if (!subCascadingData.value?.program_list) return 0;
  return subCascadingData.value.program_list.reduce((acc, p) => acc + sumProgramPPagu(p), 0);
});

const filteredPrograms = computed(() => {
  if (!subCascadingData.value?.program_list) return [];
  const q = searchProgramCascading.value.trim().toLowerCase();
  if (!q) return subCascadingData.value.program_list;

  return subCascadingData.value.program_list.filter(prog => {
    if (prog.uraiprogram?.toLowerCase().includes(q) || prog.kodeprogram?.toLowerCase().includes(q)) return true;
    if (prog.indikator_program?.some(ip => ip.uraian?.toLowerCase().includes(q))) return true;
    if (prog.kegiatan?.some(keg => {
      if (keg.uraikegiatan?.toLowerCase().includes(q) || keg.kodekegiatan?.toLowerCase().includes(q)) return true;
      if (keg.indikator_kegiatan?.some(ik => ik.uraian?.toLowerCase().includes(q))) return true;
      if (keg.subkegiatan?.some(sk => {
        if (sk.uraisubkegiatan?.toLowerCase().includes(q) || sk.kodesubkegiatan?.toLowerCase().includes(q)) return true;
        if (sk.indikator?.uraian?.toLowerCase().includes(q)) return true;
        return false;
      })) return true;
      return false;
    })) return true;
    return false;
  });
});

onMounted(() => {
  loadOpdRenstra();
  window.addEventListener('click', closeDropdown);
});

onUnmounted(() => {
  window.removeEventListener('click', closeDropdown);
});
</script>
