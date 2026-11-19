<template>
  <div v-if="isOpen" class="audit-modal-backdrop" @click.self="closeModal">
    <div class="audit-modal-dialog">
      <!-- Modal Header -->
      <div class="audit-modal-header">
        <div class="header-left">
          <div class="ai-header-badge">
            <span class="ai-sparkle">✨</span>
            <span class="ai-badge-text">AI DOCUMENT AUDITOR</span>
          </div>
          <h3 class="modal-title">
            Audit Kesesuaian Dokumen {{ auditTargetTahap }}
          </h3>
          <div class="modal-subtitle">
            <span class="opd-name">{{ opdData?.nama_skpd || '-' }}</span>
            <span class="dot-separator">&bull;</span>
            <span class="doc-filename" :title="targetDoc?.nama_file">
              {{ targetDoc?.nama_file || '-' }}
            </span>
          </div>
        </div>

        <div class="header-right">
          <!-- Tombol Analisa Ulang AI -->
          <button
            v-if="auditResult && !loading"
            type="button"
            class="btn-reanalyze-audit"
            @click="reanalyzeAudit"
            title="Jalankan analisa ulang AI jika data database aplikasi atau berkas dokumen PDF telah diperbarui"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M23 4v6h-6"/>
              <path d="M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            <span>Analisa Ulang</span>
          </button>

          <a
            v-if="docFileUrl"
            :href="docFileUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-open-pdf"
            title="Buka Berkas PDF Asli di Tab Baru"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            <span>Buka PDF</span>
          </a>
          <button type="button" class="btn-close-modal" @click="closeModal" title="Tutup">
            &times;
          </button>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="audit-modal-body">
        <!-- Loading State -->
        <div v-if="loading" class="audit-loading-card">
          <div class="ai-scanning-glow">
            <div class="scanner-ring"></div>
            <span class="scanner-icon">✨</span>
          </div>
          <h4 class="loading-title">AI Sedang Menganalisis Dokumen {{ auditTargetTahap }}...</h4>
          <p class="loading-subtitle">
            Mengekstrak tabel matriks perencanaan dari PDF dan mencocokkan nilai pagu, indikator, serta nomenklatur dengan database resmi.
          </p>

          <div class="progress-steps-list">
            <div class="step-item" :class="{ done: currentStep > 1, active: currentStep === 1 }">
              <span class="step-bullet">{{ currentStep > 1 ? '✓' : '1' }}</span>
              <span class="step-label">Mengunduh Dokumen {{ auditTargetTahap }} dari Server</span>
            </div>
            <div class="step-item" :class="{ done: currentStep > 2, active: currentStep === 2 }">
              <span class="step-bullet">{{ currentStep > 2 ? '✓' : '2' }}</span>
              <span class="step-label">Mengekstrak Tabel Matriks Renstra (Bab IV / Pendanaan)</span>
            </div>
            <div class="step-item" :class="{ done: currentStep > 3, active: currentStep === 3 }">
              <span class="step-bullet">{{ currentStep > 3 ? '✓' : '3' }}</span>
              <span class="step-label">Menghubungkan Data Resmi Pagu &amp; Indikator Database</span>
            </div>
            <div class="step-item" :class="{ done: currentStep > 4, active: currentStep === 4 }">
              <span class="step-bullet">{{ currentStep > 4 ? '✓' : '4' }}</span>
              <span class="step-label">Menjalankan Rekonsiliasi &amp; Validasi dengan AI Engine</span>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="errorMessage" class="audit-error-card">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h4 class="error-title">Gagal Menjalankan Analisa AI</h4>
          <p class="error-desc">{{ errorMessage }}</p>
          <button type="button" class="btn-retry-audit" @click="startAudit">
            Coba Analisa Ulang
          </button>
        </div>

        <!-- Audit Result Content -->
        <div v-else-if="auditResult" class="audit-result-wrap">
          <!-- Status Database & Analisa Ulang Bar -->
          <div class="audit-db-status-bar">
            <div class="db-status-left">
              <span class="db-icon">💾</span>
              <span class="db-text">
                <template v-if="auditResult.is_cached">
                  Hasil audit tersimpan di database &bull; Terakhir dianalisa: <strong>{{ auditResult.audited_at || 'Sebelumnya' }}</strong>
                </template>
                <template v-else>
                  Analisa AI terbaru berhasil dijalankan dan disimpan ke database!
                </template>
              </span>
            </div>
            <button
              type="button"
              class="btn-reanalyze-link"
              @click="reanalyzeAudit"
              title="Jalankan analisa ulang AI jika ada pembaruan dokumen PDF atau data aplikasi"
            >
              🔄 Analisa Ulang
            </button>
          </div>

          <!-- Top Scorecard Banner -->
          <div class="audit-score-banner" :class="getScoreCardClass(auditResult.skor_kesesuaian)">
            <div class="score-left">
              <div class="score-circle">
                <span class="score-number">{{ auditResult.skor_kesesuaian }}</span>
                <span class="score-pct">%</span>
              </div>
              <div class="score-meta">
                <div class="status-badge" :class="getStatusBadgeClass(auditResult.status)">
                  <span class="status-dot"></span>
                  <span>{{ auditResult.status }}</span>
                </div>
                <div class="score-desc">
                  Skor Kesesuaian Dokumen {{ auditResult.tahap }} vs Database
                </div>
              </div>
            </div>

            <div class="score-metrics-grid">
              <div class="score-metric-box">
                <span class="metric-num text-purple">{{ (auditResult.total_tujuan_db || 0) + ' / ' + (auditResult.total_sasaran_db || 0) }}</span>
                <span class="metric-lbl">Tujuan / Sasaran</span>
              </div>
              <div class="score-metric-box">
                <span class="metric-num text-amber font-bold">⭐ {{ auditResult.total_iku_db || 0 }}</span>
                <span class="metric-lbl">Indikator IKU</span>
              </div>
              <div class="score-metric-box">
                <span class="metric-num text-blue">{{ auditResult.total_program_cocok || 0 }} / {{ auditResult.total_program_db || 0 }}</span>
                <span class="metric-lbl">Program Sesuai</span>
              </div>
              <div class="score-metric-box">
                <span class="metric-num text-teal">{{ auditResult.total_kegiatan_cocok || 0 }} / {{ auditResult.total_kegiatan_db || 0 }}</span>
                <span class="metric-lbl">Kegiatan Sesuai</span>
              </div>
              <div class="score-metric-box">
                <span class="metric-num text-green">{{ auditResult.total_subkegiatan_cocok || 0 }} / {{ auditResult.total_subkegiatan_db || 0 }}</span>
                <span class="metric-lbl">Subkegiatan Sesuai</span>
              </div>
              <div class="score-metric-box">
                <span class="metric-num">{{ auditResult.analyzed_pages }} / {{ auditResult.total_pages }}</span>
                <span class="metric-lbl">Halaman Matriks</span>
              </div>
            </div>
          </div>

          <!-- Executive Summary Callout -->
          <div class="executive-summary-card">
            <div class="summary-header">
              <span class="summary-icon">📝</span>
              <span class="summary-title">Ringkasan Eksekutif Analisis AI</span>
              <span class="source-tag">Engine: {{ auditResult.source?.toUpperCase() || 'AI' }}</span>
            </div>
            <p class="summary-text">{{ auditResult.ringkasan_analisis }}</p>
          </div>

          <!-- Tabs Navigation -->
          <div class="audit-tabs-bar">
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'tujuan_sasaran' }"
              @click="activeTab = 'tujuan_sasaran'"
            >
              <span>🎯 1. Tujuan &amp; Sasaran</span>
              <span class="tab-count-pill">{{ auditResult.audit_tujuan_sasaran?.length || 0 }}</span>
            </button>
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'program' }"
              @click="activeTab = 'program'"
            >
              <span>📂 2. Program</span>
              <span class="tab-count-pill">{{ auditResult.audit_nomenklatur?.length || auditResult.total_program_db || 0 }}</span>
            </button>
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'kegiatan' }"
              @click="activeTab = 'kegiatan'"
            >
              <span>📁 3. Kegiatan</span>
              <span class="tab-count-pill">{{ auditResult.audit_kegiatan?.length || auditResult.total_kegiatan_db || 0 }}</span>
            </button>
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'subkegiatan' }"
              @click="activeTab = 'subkegiatan'"
            >
              <span>📄 4. Subkegiatan</span>
              <span class="tab-count-pill">{{ auditResult.audit_subkegiatan?.length || auditResult.total_subkegiatan_db || 0 }}</span>
            </button>
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'pagu' }"
              @click="activeTab = 'pagu'"
            >
              <span>💰 5. Pagu &amp; Target</span>
              <span class="tab-count-pill">{{ auditResult.audit_pagu?.length || 0 }}</span>
            </button>
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'rekomendasi' }"
              @click="activeTab = 'rekomendasi'"
            >
              <span>📋 6. Rekomendasi</span>
              <span class="tab-count-pill">{{ auditResult.rekomendasi?.length || 0 }}</span>
            </button>
          </div>

          <!-- Tab 1: Tujuan, Sasaran & IKU -->
          <div v-if="activeTab === 'tujuan_sasaran'" class="tab-pane-content">
            <div class="tab-pane-desc d-flex justify-between align-center">
              <div>
                Memverifikasi keselarasan <strong>Tujuan</strong>, <strong>Sasaran</strong>, <strong>Indikator Kinerja</strong>, dan <strong>IKU (Indikator Kinerja Utama)</strong> antara Bab III / Penetapan IKU dokumen PDF dengan database aplikasi.
              </div>
              <div class="ts-filter-pills">
                <button
                  type="button"
                  class="ts-filter-pill"
                  :class="{ active: tsFilter === 'all' }"
                  @click="tsFilter = 'all'"
                >
                  Semua ({{ auditResult.audit_tujuan_sasaran?.length || 0 }})
                </button>
                <button
                  type="button"
                  class="ts-filter-pill pill-iku"
                  :class="{ active: tsFilter === 'iku' }"
                  @click="tsFilter = 'iku'"
                >
                  ⭐ Khusus IKU ({{ countIku }})
                </button>
                <button
                  type="button"
                  class="ts-filter-pill"
                  :class="{ active: tsFilter === 'Tujuan' }"
                  @click="tsFilter = 'Tujuan'"
                >
                  Tujuan
                </button>
                <button
                  type="button"
                  class="ts-filter-pill"
                  :class="{ active: tsFilter === 'Sasaran' }"
                  @click="tsFilter = 'Sasaran'"
                >
                  Sasaran
                </button>
              </div>
            </div>

            <div class="table-responsive">
              <table class="audit-data-table">
                <thead>
                  <tr>
                    <th style="width: 45px; text-align: center;">NO</th>
                    <th style="width: 130px; text-align: center;">LEVEL &amp; STATUS</th>
                    <th style="width: 250px;">TUJUAN / SASARAN DAERAH</th>
                    <th style="width: 240px;">INDIKATOR KINERJA</th>
                    <th style="width: 70px; text-align: center;">SATUAN</th>
                    <th style="width: 210px;">TARGET DATABASE</th>
                    <th style="width: 190px;">TARGET DOKUMEN PDF</th>
                    <th style="text-align: center; width: 100px;">STATUS</th>
                    <th style="min-width: 200px;">CATATAN AUDIT</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(item, idx) in filteredTujuanSasaran"
                    :key="idx"
                    :class="{ 'row-diff': !item.is_match, 'row-iku': item.is_iku }"
                  >
                    <td class="text-center font-bold">{{ idx + 1 }}</td>
                    <td class="text-center">
                      <div class="level-badges-stack">
                        <span
                          class="badge-level"
                          :class="item.level?.toLowerCase() === 'tujuan' ? 'badge-tujuan' : 'badge-sasaran'"
                        >
                          {{ item.level?.toUpperCase() }}
                        </span>
                        <span v-if="item.is_iku" class="badge-iku-gold" title="Ditetapkan sebagai Indikator Kinerja Utama (IKU)">
                          ⭐ IKU
                        </span>
                      </div>
                    </td>
                    <td class="font-medium text-slate-800">
                      {{ item.uraitujuan_sasaran || '-' }}
                    </td>
                    <td>
                      <div class="font-bold text-slate-900">{{ item.indikator }}</div>
                    </td>
                    <td class="text-center text-mono text-xs">
                      {{ item.satuan || '-' }}
                    </td>
                    <td class="text-xs">
                      <div v-if="item.target_murni_db" class="target-val-line">
                        <span class="target-lbl">Murni:</span>
                        <span class="target-txt">{{ item.target_murni_db }}</span>
                      </div>
                      <div v-if="item.target_perubahan_db" class="target-val-line text-blue">
                        <span class="target-lbl">Perubahan:</span>
                        <span class="target-txt font-bold">{{ item.target_perubahan_db }}</span>
                      </div>
                    </td>
                    <td class="text-xs">
                      <div v-if="item.target_pdf" class="target-pdf-box">
                        {{ item.target_pdf }}
                      </div>
                      <span v-else class="text-slate-400 italic">Tidak tertera</span>
                    </td>
                    <td class="text-center">
                      <span class="badge-audit" :class="item.is_match ? 'badge-match' : 'badge-mismatch'">
                        {{ item.is_match ? 'Sesuai' : 'Periksa' }}
                      </span>
                    </td>
                    <td class="text-keterangan text-xs">
                      {{ item.keterangan || '-' }}
                    </td>
                  </tr>
                  <tr v-if="!filteredTujuanSasaran?.length">
                    <td colspan="9" class="text-center py-6 text-slate-400">
                      Tidak ada data Tujuan/Sasaran yang sesuai dengan filter yang dipilih.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab 2: Program & Indikator Program -->
          <div v-if="activeTab === 'program'" class="tab-pane-content">
            <div class="tab-pane-desc">
              Memverifikasi kesesuaian rumusan <strong>Program</strong>, <strong>Indikator Kinerja Program</strong>, dan <strong>Nomenklatur Standar</strong> terhadap dokumen PDF.
            </div>

            <!-- Nomenklatur & Status Program -->
            <div class="table-responsive">
              <table class="audit-data-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">NO</th>
                    <th style="width: 120px;">KODE PROGRAM</th>
                    <th>NOMENKLATUR PROGRAM (DATABASE)</th>
                    <th>TERDETEKSI PADA BERKAS PDF</th>
                    <th style="text-align: center; width: 110px;">STATUS</th>
                    <th style="width: 250px;">CATATAN AUDIT</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(nom, idx) in auditResult.audit_nomenklatur"
                    :key="idx"
                    :class="{ 'row-diff': !nom.is_match }"
                  >
                    <td class="text-center font-bold">{{ idx + 1 }}</td>
                    <td class="text-mono font-bold">{{ nom.kode }}</td>
                    <td class="font-bold text-slate-800">{{ nom.nama_db }}</td>
                    <td :class="nom.is_match ? 'text-slate-700' : 'text-slate-400 italic'">
                      {{ nom.nama_pdf || '-' }}
                    </td>
                    <td class="text-center">
                      <span class="badge-audit" :class="nom.is_match ? 'badge-match' : 'badge-mismatch'">
                        {{ nom.is_match ? 'Sesuai' : 'Periksa' }}
                      </span>
                    </td>
                    <td class="text-keterangan">{{ nom.keterangan || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Indikator Program -->
            <div v-if="auditResult.audit_indikator?.length" class="mt-6">
              <h5 class="text-sm font-bold text-slate-700 mb-2">Indikator Kinerja Program:</h5>
              <div class="table-responsive">
                <table class="audit-data-table">
                  <thead>
                    <tr>
                      <th style="width: 50px;">NO</th>
                      <th style="width: 120px;">KODE PROGRAM</th>
                      <th>INDIKATOR KINERJA PROGRAM</th>
                      <th style="text-align: center; width: 85px;">SATUAN</th>
                      <th style="text-align: center; width: 130px;">TARGET DATABASE</th>
                      <th style="text-align: center; width: 130px;">TARGET PDF</th>
                      <th style="text-align: center; width: 100px;">STATUS</th>
                      <th>CATATAN</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(ind, idx) in auditResult.audit_indikator"
                      :key="'ind-'+idx"
                      :class="{ 'row-diff': !ind.is_match }"
                    >
                      <td class="text-center">{{ idx + 1 }}</td>
                      <td class="text-mono">{{ ind.kodeprogram || '-' }}</td>
                      <td class="font-medium">{{ ind.indikator }}</td>
                      <td class="text-center">{{ ind.satuan || '-' }}</td>
                      <td class="text-center text-mono font-bold text-blue">{{ ind.target_db || '-' }}</td>
                      <td class="text-center text-mono font-bold">{{ ind.target_pdf || '-' }}</td>
                      <td class="text-center">
                        <span class="badge-audit" :class="ind.is_match ? 'badge-match' : 'badge-mismatch'">
                          {{ ind.is_match ? 'Cocok' : 'Perlu Cek' }}
                        </span>
                      </td>
                      <td class="text-keterangan">{{ ind.keterangan || '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Tab 3: Kegiatan & Indikator Kegiatan -->
          <div v-if="activeTab === 'kegiatan'" class="tab-pane-content">
            <div class="tab-pane-desc d-flex justify-between align-center">
              <div>
                Memverifikasi rumusan <strong>Kegiatan</strong>, <strong>Indikator Kegiatan</strong>, dan <strong>Pagu/Target</strong> (Total {{ auditResult.total_kegiatan_cocok || 0 }} dari {{ auditResult.total_kegiatan_db || auditResult.audit_kegiatan?.length || 0 }} Kegiatan sesuai).
              </div>
              <div class="search-input-wrap">
                <input
                  v-model="searchKegiatan"
                  type="text"
                  placeholder="Cari kode/nama kegiatan..."
                  class="audit-search-input"
                />
              </div>
            </div>

            <div v-if="!auditResult.audit_kegiatan?.length" class="empty-tab-text">
              Tidak ada data rincian kegiatan untuk OPD ini.
            </div>
            <div v-else class="table-responsive">
              <table class="audit-data-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">NO</th>
                    <th style="width: 140px;">KODE KEGIATAN</th>
                    <th>NAMA KEGIATAN</th>
                    <th>INDIKATOR KINERJA</th>
                    <th style="text-align: center; width: 80px;">SATUAN</th>
                    <th style="text-align: center; width: 110px;">TARGET</th>
                    <th style="text-align: right; width: 140px;">PAGU ANGGARAN</th>
                    <th style="text-align: center; width: 100px;">STATUS</th>
                    <th style="width: 220px;">CATATAN AUDIT</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(k, idx) in filteredKegiatan"
                    :key="idx"
                    :class="{ 'row-diff': !k.is_match }"
                  >
                    <td class="text-center">{{ idx + 1 }}</td>
                    <td class="text-mono font-bold">{{ k.kodekegiatan }}</td>
                    <td class="font-medium text-slate-800">{{ k.uraikegiatan }}</td>
                    <td>{{ k.indikator || '-' }}</td>
                    <td class="text-center text-xs">{{ k.satuan || '-' }}</td>
                    <td class="text-center text-mono font-bold">{{ k.target_db || '-' }}</td>
                    <td class="text-right text-mono font-bold text-blue">{{ formatCurrency(k.pagu_db) }}</td>
                    <td class="text-center">
                      <span class="badge-audit" :class="k.is_match ? 'badge-match' : 'badge-mismatch'">
                        {{ k.is_match ? 'Sesuai' : 'Periksa' }}
                      </span>
                    </td>
                    <td class="text-keterangan">{{ k.keterangan || '-' }}</td>
                  </tr>
                  <tr v-if="!filteredKegiatan.length">
                    <td colspan="9" class="text-center py-6 text-slate-400">
                      Tidak ada kegiatan yang cocok dengan pencarian "{{ searchKegiatan }}".
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab 4: Subkegiatan & Indikator Subkegiatan -->
          <div v-if="activeTab === 'subkegiatan'" class="tab-pane-content">
            <div class="tab-pane-desc d-flex justify-between align-center">
              <div>
                Memverifikasi rumusan <strong>Subkegiatan</strong>, <strong>Indikator Kinerja Subkegiatan</strong>, <strong>Volume/Target</strong>, dan <strong>Pagu</strong> (Total {{ auditResult.total_subkegiatan_cocok || 0 }} dari {{ auditResult.total_subkegiatan_db || auditResult.audit_subkegiatan?.length || 0 }} Subkegiatan sesuai).
              </div>
              <div class="search-input-wrap">
                <input
                  v-model="searchSubkegiatan"
                  type="text"
                  placeholder="Cari kode/nama subkegiatan..."
                  class="audit-search-input"
                />
              </div>
            </div>

            <div v-if="!auditResult.audit_subkegiatan?.length" class="empty-tab-text">
              Tidak ada data rincian subkegiatan untuk OPD ini.
            </div>
            <div v-else class="table-responsive">
              <table class="audit-data-table">
                <thead>
                  <tr>
                    <th style="width: 45px;">NO</th>
                    <th style="width: 160px;">KODE SUBKEGIATAN</th>
                    <th>NAMA SUBKEGIATAN</th>
                    <th>INDIKATOR SUBKEGIATAN</th>
                    <th style="text-align: center; width: 75px;">SATUAN</th>
                    <th style="text-align: center; width: 100px;">TARGET / VOL</th>
                    <th style="text-align: right; width: 140px;">PAGU ANGGARAN</th>
                    <th style="text-align: center; width: 95px;">STATUS</th>
                    <th style="width: 220px;">CATATAN AUDIT</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(sk, idx) in filteredSubkegiatan"
                    :key="idx"
                    :class="{ 'row-diff': !sk.is_match }"
                  >
                    <td class="text-center">{{ idx + 1 }}</td>
                    <td class="text-mono font-bold text-xs">{{ sk.kodesubkegiatan }}</td>
                    <td class="font-medium text-slate-800 text-xs">{{ sk.uraisubkegiatan }}</td>
                    <td class="text-xs">{{ sk.indikator || '-' }}</td>
                    <td class="text-center text-xs">{{ sk.satuan || '-' }}</td>
                    <td class="text-center text-mono font-bold text-xs">{{ sk.target_db || '-' }}</td>
                    <td class="text-right text-mono font-bold text-blue text-xs">{{ formatCurrency(sk.pagu_db) }}</td>
                    <td class="text-center">
                      <span class="badge-audit" :class="sk.is_match ? 'badge-match' : 'badge-mismatch'">
                        {{ sk.is_match ? 'Sesuai' : 'Periksa' }}
                      </span>
                    </td>
                    <td class="text-keterangan text-xs">{{ sk.keterangan || '-' }}</td>
                  </tr>
                  <tr v-if="!filteredSubkegiatan.length">
                    <td colspan="9" class="text-center py-6 text-slate-400">
                      Tidak ada subkegiatan yang cocok dengan pencarian "{{ searchSubkegiatan }}".
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab 5: Pagu Anggaran & Target -->
          <div v-if="activeTab === 'pagu'" class="tab-pane-content">
            <div class="tab-pane-desc">
              Membandingkan nilai <strong>Pagu Anggaran</strong> dan <strong>Plafon Pembiayaan</strong> antara dokumen perencanaan PDF dengan data resmi di database aplikasi.
            </div>
            <div class="table-responsive">
              <table class="audit-data-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">NO</th>
                    <th style="width: 120px;">KODE</th>
                    <th>NAMA PROGRAM</th>
                    <th style="text-align: right; width: 160px;">PAGU MURNI (DB)</th>
                    <th style="text-align: right; width: 160px;">PAGU PERUBAHAN (DB)</th>
                    <th style="text-align: right; width: 160px;">PAGU DOKUMEN PDF</th>
                    <th style="text-align: center; width: 110px;">STATUS</th>
                    <th style="width: 220px;">KETERANGAN</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(item, idx) in auditResult.audit_pagu"
                    :key="idx"
                    :class="{ 'row-diff': !item.is_match }"
                  >
                    <td class="text-center">{{ idx + 1 }}</td>
                    <td class="text-mono font-bold">{{ item.kodeprogram }}</td>
                    <td class="font-medium">{{ item.uraiprogram }}</td>
                    <td class="text-right text-mono text-slate-700">
                      {{ formatCurrency(item.pagu_murni_db || item.pagu_db) }}
                    </td>
                    <td class="text-right text-mono font-bold text-blue">
                      {{ formatCurrency(item.pagu_perubahan_db || item.pagu_db) }}
                    </td>
                    <td class="text-right text-mono font-bold text-emerald-700">
                      {{ formatCurrency(item.pagu_pdf) }}
                    </td>
                    <td class="text-center">
                      <span class="badge-audit" :class="item.is_match ? 'badge-match' : 'badge-mismatch'">
                        {{ item.is_match ? 'Cocok' : 'Selisih' }}
                      </span>
                    </td>
                    <td class="text-keterangan">{{ item.keterangan || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab 6: Rekomendasi -->
          <div v-if="activeTab === 'rekomendasi'" class="tab-pane-content">
            <div class="rekomendasi-card">
              <div class="rekomendasi-header">
                <span class="rekomendasi-badge">POIN KOREKSI &amp; TINDAK LANJUT</span>
                <span class="rekomendasi-sub">Disusun otomatis untuk Verifikator Bapperida &amp; Tim Penyusun Renstra OPD</span>
              </div>
              <ul class="rekomendasi-list">
                <li
                  v-for="(rek, rIdx) in auditResult.rekomendasi"
                  :key="rIdx"
                  class="rekomendasi-item"
                >
                  <span class="rek-bullet">{{ rIdx + 1 }}</span>
                  <span class="rek-text">{{ rek }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="audit-modal-footer">
        <div class="footer-left">
          <button
            v-if="auditResult"
            type="button"
            class="btn-copy-summary"
            @click="copyAuditSummary"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            <span>{{ copied ? 'Berhasil Disalin!' : 'Salin Ringkasan Audit' }}</span>
          </button>
        </div>
        <div class="footer-right">
          <button type="button" class="btn-footer-close" @click="closeModal">
            Tutup
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import api from '../services/api';

export default {
  name: 'DokumenAiAuditModal',
  emits: ['audit-saved'],
  setup(props, { emit }) {
    const isOpen = ref(false);
    const loading = ref(false);
    const currentStep = ref(1);
    const errorMessage = ref('');
    const copied = ref(false);

    const opdData = ref(null);
    const targetDoc = ref(null);
    const auditResult = ref(null);
    const activeTab = ref('tujuan_sasaran'); // tujuan_sasaran, program, kegiatan, subkegiatan, pagu, rekomendasi
    const tsFilter = ref('all'); // all, iku, Tujuan, Sasaran
    const searchKegiatan = ref('');
    const searchSubkegiatan = ref('');

    const countIku = computed(() => {
      return (auditResult.value?.audit_tujuan_sasaran || []).filter(i => i.is_iku).length;
    });

    const filteredTujuanSasaran = computed(() => {
      const list = auditResult.value?.audit_tujuan_sasaran || [];
      if (tsFilter.value === 'iku') {
        return list.filter(i => i.is_iku);
      }
      if (tsFilter.value === 'Tujuan') {
        return list.filter(i => i.level?.toLowerCase() === 'tujuan');
      }
      if (tsFilter.value === 'Sasaran') {
        return list.filter(i => i.level?.toLowerCase() === 'sasaran');
      }
      return list;
    });

    const filteredKegiatan = computed(() => {
      const list = auditResult.value?.audit_kegiatan || [];
      const q = searchKegiatan.value.trim().toLowerCase();
      if (!q) return list;
      return list.filter(k => 
        (k.kodekegiatan || '').toLowerCase().includes(q) ||
        (k.uraikegiatan || '').toLowerCase().includes(q) ||
        (k.indikator || '').toLowerCase().includes(q)
      );
    });

    const filteredSubkegiatan = computed(() => {
      const list = auditResult.value?.audit_subkegiatan || [];
      const q = searchSubkegiatan.value.trim().toLowerCase();
      if (!q) return list;
      return list.filter(sk => 
        (sk.kodesubkegiatan || '').toLowerCase().includes(q) ||
        (sk.uraisubkegiatan || '').toLowerCase().includes(q) ||
        (sk.indikator || '').toLowerCase().includes(q)
      );
    });

    const auditTargetTahap = computed(() => {
      if (targetDoc.value) {
        return targetDoc.value.tahap || (targetDoc.value.id_ref_dokumen === 66 ? 'Penetapan' : 'Rancangan Akhir');
      }
      return 'Penetapan / Rancangan Akhir';
    });

    const docFileUrl = computed(() => {
      if (auditResult.value?.file_url) return auditResult.value.file_url;
      if (targetDoc.value?.file_url) return targetDoc.value.file_url;
      if (targetDoc.value?.link_gd) {
        const link = targetDoc.value.link_gd.lstrip ? targetDoc.value.link_gd.lstrip('/') : targetDoc.value.link_gd.replace(/^\//, '');
        return `https://monevrkpd.tegalkota.go.id/dokren/${link}`;
      }
      return null;
    });

    const openModal = async (opd, doc = null) => {
      opdData.value = opd;
      targetDoc.value = doc;
      auditResult.value = null;
      errorMessage.value = '';
      activeTab.value = 'tujuan_sasaran';
      tsFilter.value = 'all';
      isOpen.value = true;

      await startAudit(false);
    };

    const closeModal = () => {
      isOpen.value = false;
      loading.value = false;
    };

    const reanalyzeAudit = async () => {
      await startAudit(true);
    };

    const startAudit = async (forceReanalyze = false) => {
      if (!opdData.value) return;
      loading.value = true;
      errorMessage.value = '';
      currentStep.value = 1;

      // Simulated step progression for visual feedback
      const stepTimer1 = setTimeout(() => { currentStep.value = 2; }, 1200);
      const stepTimer2 = setTimeout(() => { currentStep.value = 3; }, 2600);
      const stepTimer3 = setTimeout(() => { currentStep.value = 4; }, 4200);

      try {
        const docId = targetDoc.value ? targetDoc.value.id : null;
        const res = await api.auditDokumenPerencanaan(opdData.value.id_skpd, docId, forceReanalyze);
        auditResult.value = res;
        emit('audit-saved', res);
      } catch (err) {
        console.error('Audit AI error:', err);
        errorMessage.value = err.message || 'Gagal menjalankan audit kesesuaian dokumen.';
      } finally {
        clearTimeout(stepTimer1);
        clearTimeout(stepTimer2);
        clearTimeout(stepTimer3);
        loading.value = false;
      }
    };

    const formatCurrency = (val) => {
      if (val === null || val === undefined) return '-';
      const num = Number(val);
      if (isNaN(num)) return '-';
      return new Intl.NumberFormat('id-ID', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(num);
    };

    const getScoreCardClass = (score) => {
      if (score >= 90) return 'score-green';
      if (score >= 75) return 'score-amber';
      return 'score-red';
    };

    const getStatusBadgeClass = (status) => {
      const s = (status || '').toLowerCase();
      if (s.includes('sesuai') || s.includes('cocok')) return 'status-badge-green';
      if (s.includes('selisih')) return 'status-badge-amber';
      return 'status-badge-red';
    };

    const copyAuditSummary = () => {
      if (!auditResult.value) return;
      const textToCopy = `=== HASIL AUDIT DOKUMEN ${auditResult.value.tahap.toUpperCase()} (AI) ===
Perangkat Daerah : ${auditResult.value.nama_skpd} (${auditResult.value.kode_skpd})
Nama Berkas PDF  : ${auditResult.value.nama_file}
Skor Kesesuaian  : ${auditResult.value.skor_kesesuaian}% (${auditResult.value.status})
Tujuan / Sasaran : ${auditResult.value.total_tujuan_db || 0} Tujuan / ${auditResult.value.total_sasaran_db || 0} Sasaran
Indikator IKU    : ${auditResult.value.total_iku_db || 0} IKU
Total Program    : ${auditResult.value.total_program_db} (Cocok: ${auditResult.value.total_program_cocok}, Selisih: ${auditResult.value.total_program_selisih})

Ringkasan:
${auditResult.value.ringkasan_analisis}

Rekomendasi Bapperida:
${(auditResult.value.rekomendasi || []).map((r, i) => `${i + 1}. ${r}`).join('\n')}
`;
      navigator.clipboard.writeText(textToCopy).then(() => {
        copied.value = true;
        setTimeout(() => { copied.value = false; }, 2500);
      });
    };

    return {
      isOpen,
      loading,
      currentStep,
      errorMessage,
      copied,
      opdData,
      targetDoc,
      auditResult,
      activeTab,
      tsFilter,
      countIku,
      filteredTujuanSasaran,
      searchKegiatan,
      searchSubkegiatan,
      filteredKegiatan,
      filteredSubkegiatan,
      auditTargetTahap,
      docFileUrl,
      openModal,
      closeModal,
      startAudit,
      reanalyzeAudit,
      formatCurrency,
      getScoreCardClass,
      getStatusBadgeClass,
      copyAuditSummary,
    };
  },
};
</script>

<style scoped>
.audit-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1.5rem;
}

.audit-modal-dialog {
  background: #ffffff;
  border-radius: 14px;
  width: 100%;
  max-width: 1100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

/* Header */
.audit-modal-header {
  padding: 1.25rem 1.75rem;
  background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
}

.ai-header-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  margin-bottom: 0.35rem;
}

.modal-title {
  margin: 0 0 0.3rem 0;
  font-size: 1.35rem;
  font-weight: 800;
  color: #ffffff;
}

.modal-subtitle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: #cbd5e1;
}

.doc-filename {
  font-family: monospace;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  color: #93c5fd;
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-reanalyze-audit {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #f59e0b;
  color: #1e293b;
  border: none;
  padding: 0.45rem 0.85rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn-reanalyze-audit:hover {
  background: #d97706;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.btn-open-pdf {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  padding: 0.45rem 0.85rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-open-pdf:hover {
  background: rgba(255, 255, 255, 0.3);
}

.btn-close-modal {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 1.6rem;
  cursor: pointer;
  line-height: 1;
  padding: 0.2rem 0.5rem;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.btn-close-modal:hover {
  opacity: 1;
}

/* Body */
.audit-modal-body {
  padding: 1.5rem 1.75rem;
  overflow-y: auto;
  flex: 1;
  background: #f8fafc;
}

/* Loading State */
.audit-loading-card {
  padding: 3.5rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ai-scanning-glow {
  position: relative;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.scanner-ring {
  position: absolute;
  inset: 0;
  border: 3px solid rgba(37, 99, 235, 0.2);
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.scanner-icon {
  font-size: 2rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.loading-subtitle {
  margin: 0 0 2rem 0;
  font-size: 0.86rem;
  color: #64748b;
  max-width: 580px;
  line-height: 1.45;
}

.progress-steps-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
  max-width: 480px;
  text-align: left;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.9rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.84rem;
  color: #64748b;
  transition: all 0.2s;
}

.step-bullet {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.74rem;
  background: #f1f5f9;
  color: #94a3b8;
  flex-shrink: 0;
}

.step-item.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 600;
}

.step-item.active .step-bullet {
  background: #2563eb;
  color: #ffffff;
}

.step-item.done {
  border-color: #bbf7d0;
  background: #f0fdf4;
  color: #15803d;
  font-weight: 600;
}

.step-item.done .step-bullet {
  background: #16a34a;
  color: #ffffff;
}

/* Error State */
.audit-error-card {
  padding: 3rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  color: #dc2626;
}

.error-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
}

.error-desc {
  margin: 0 0 1rem 0;
  font-size: 0.86rem;
  color: #64748b;
  max-width: 500px;
}

.btn-retry-audit {
  padding: 0.6rem 1.25rem;
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

/* Result Views */
.audit-result-wrap {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Database Status Bar */
.audit-db-status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.65rem 1.1rem;
  font-size: 0.82rem;
  color: #334155;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.db-status-left {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.db-icon {
  font-size: 1.05rem;
}

.db-text {
  line-height: 1.4;
}

.db-text strong {
  color: #0f172a;
}

.btn-reanalyze-link {
  background: #ffffff;
  border: 1px solid #94a3b8;
  color: #1e293b;
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.15s;
  flex-shrink: 0;
}

.btn-reanalyze-link:hover {
  background: #f8fafc;
  border-color: #3b82f6;
  color: #2563eb;
  box-shadow: 0 1px 3px rgba(59, 130, 246, 0.2);
}

/* Scorecard Banner */
.audit-score-banner {
  background: #ffffff;
  border-radius: 12px;
  padding: 1.25rem 1.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.score-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.score-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  flex-shrink: 0;
}

.score-green .score-circle {
  background: #ecfdf5;
  color: #059669;
  border: 3px solid #10b981;
}

.score-amber .score-circle {
  background: #fffbeb;
  color: #d97706;
  border: 3px solid #f59e0b;
}

.score-red .score-circle {
  background: #fef2f2;
  color: #dc2626;
  border: 3px solid #ef4444;
}

.score-number {
  font-size: 1.75rem;
  line-height: 1;
}

.score-pct {
  font-size: 0.95rem;
  margin-left: 1px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.35rem;
}

.status-badge-green {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}

.status-badge-amber {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
}

.status-badge-red {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.score-desc {
  font-size: 0.82rem;
  font-weight: 600;
  color: #64748b;
}

.score-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.score-metric-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f8fafc;
  padding: 0.6rem 0.9rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.metric-num {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.metric-lbl {
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  margin-top: 0.15rem;
}

/* Executive Summary Card */
.executive-summary-card {
  background: #ffffff;
  border-radius: 10px;
  padding: 1.1rem 1.4rem;
  border: 1px solid #e2e8f0;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.summary-title {
  font-size: 0.88rem;
  font-weight: 800;
  color: #1e3a8a;
}

.source-tag {
  margin-left: auto;
  font-size: 0.68rem;
  background: #f1f5f9;
  color: #64748b;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-family: monospace;
}

.summary-text {
  margin: 0;
  font-size: 0.86rem;
  color: #334155;
  line-height: 1.5;
}

/* Tabs Bar */
.audit-tabs-bar {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 2px;
}

.audit-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: 0.84rem;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
}

.audit-tab-btn:hover {
  color: #1e3a8a;
}

.audit-tab-btn.active {
  color: #1d4ed8;
  border-bottom-color: #1d4ed8;
}

.tab-count-pill {
  font-size: 0.7rem;
  background: #f1f5f9;
  color: #475569;
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
  font-weight: 700;
}

.audit-tab-btn.active .tab-count-pill {
  background: #eff6ff;
  color: #1d4ed8;
}

/* Tab Pane */
.tab-pane-content {
  background: #ffffff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  padding: 1.25rem;
}

.tab-pane-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 1rem;
}

/* Audit Table */
.audit-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.audit-data-table th {
  background: #f8fafc;
  color: #475569;
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
  border-bottom: 2px solid #e2e8f0;
  padding: 0.6rem 0.75rem;
  text-align: left;
}

.audit-data-table td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
}

.row-diff {
  background: #fef2f2;
}

.text-mono {
  font-family: monospace;
}

.font-bold { font-weight: 700; }
.font-medium { font-weight: 600; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.text-blue { color: #1d4ed8; }
.text-green { color: #16a34a; }
.text-teal { color: #0d9488; }
.text-purple { color: #7c3aed; }
.text-amber { color: #d97706; }
.text-red { color: #dc2626; }
.text-slate { color: #64748b; }

.search-input-wrap {
  min-width: 280px;
}

.audit-search-input {
  width: 100%;
  padding: 0.38rem 0.75rem;
  font-size: 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
  background: #f8fafc;
  transition: all 0.2s;
}

.audit-search-input:focus {
  background: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.badge-audit {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.18rem 0.5rem;
  border-radius: 9999px;
}

.badge-match {
  background: #dcfce7;
  color: #15803d;
}

.badge-mismatch {
  background: #fee2e2;
  color: #b91c1c;
}

.text-keterangan {
  font-size: 0.76rem;
  color: #64748b;
}

/* Rekomendasi Card */
.rekomendasi-card {
  padding: 0.5rem 0;
}

.rekomendasi-header {
  margin-bottom: 1rem;
}

.rekomendasi-badge {
  font-size: 0.74rem;
  font-weight: 800;
  color: #1e3a8a;
  letter-spacing: 0.04em;
  display: block;
}

.rekomendasi-sub {
  font-size: 0.78rem;
  color: #64748b;
}

.rekomendasi-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.rekomendasi-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 3px solid #2563eb;
  padding: 0.85rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #1e293b;
  line-height: 1.45;
}

.rek-bullet {
  width: 22px;
  height: 22px;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 800;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  flex-shrink: 0;
  margin-top: 1px;
}

/* Footer */
.audit-modal-footer {
  padding: 1rem 1.75rem;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-copy-summary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
  padding: 0.5rem 0.9rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-copy-summary:hover {
  background: #e2e8f0;
}

.btn-footer-close {
  padding: 0.55rem 1.4rem;
  background: #1e3a8a;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-footer-close:hover {
  background: #1e40af;
}

.empty-tab-text {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-style: italic;
  font-size: 0.86rem;
}

/* Tujuan, Sasaran & IKU Tab Styles */
.text-purple {
  color: #7c3aed !important;
}

.text-amber {
  color: #b45309 !important;
}

.d-flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.align-center {
  align-items: center;
}

.ts-filter-pills {
  display: flex;
  gap: 0.35rem;
  flex-shrink: 0;
  margin-left: 1rem;
}

.ts-filter-pill {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 9999px;
  padding: 0.25rem 0.65rem;
  font-size: 0.74rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.ts-filter-pill:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.ts-filter-pill.active {
  background: #1e3a8a;
  color: #ffffff;
  border-color: #1e3a8a;
}

.ts-filter-pill.pill-iku.active {
  background: #d97706;
  color: #ffffff;
  border-color: #d97706;
}

.level-badges-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.badge-level {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.03em;
}

.badge-tujuan {
  background: #ede9fe;
  color: #6d28d9;
  border: 1px solid #ddd6fe;
}

.badge-sasaran {
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
}

.badge-iku-gold {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.1rem 0.45rem;
  box-shadow: 0 1px 2px rgba(245, 158, 11, 0.15);
}

.row-iku {
  background-color: #fffbeb !important;
}

.row-iku:hover {
  background-color: #fef3c7 !important;
}

.target-val-line {
  display: flex;
  gap: 0.35rem;
  align-items: baseline;
  line-height: 1.35;
  margin-bottom: 0.15rem;
}

.target-lbl {
  color: #64748b;
  font-size: 0.68rem;
  font-weight: 600;
  flex-shrink: 0;
}

.target-txt {
  font-family: monospace;
  font-size: 0.73rem;
  color: #1e293b;
}

.target-pdf-box {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 0.25rem 0.45rem;
  font-family: monospace;
  font-size: 0.72rem;
  color: #0f172a;
  line-height: 1.3;
}
</style>

