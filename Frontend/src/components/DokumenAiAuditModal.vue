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
                <span class="metric-num">{{ auditResult.total_program_db }}</span>
                <span class="metric-lbl">Total Program</span>
              </div>
              <div class="score-metric-box">
                <span class="metric-num text-green">{{ auditResult.total_program_cocok }}</span>
                <span class="metric-lbl">Pagu Cocok</span>
              </div>
              <div class="score-metric-box">
                <span class="metric-num" :class="auditResult.total_program_selisih > 0 ? 'text-red' : 'text-slate'">
                  {{ auditResult.total_program_selisih }}
                </span>
                <span class="metric-lbl">Pagu Selisih</span>
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
              :class="{ active: activeTab === 'pagu' }"
              @click="activeTab = 'pagu'"
            >
              <span>1. Pagu Anggaran</span>
              <span class="tab-count-pill">{{ auditResult.audit_pagu?.length || 0 }}</span>
            </button>
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'indikator' }"
              @click="activeTab = 'indikator'"
            >
              <span>2. Indikator &amp; Target</span>
              <span class="tab-count-pill">{{ auditResult.audit_indikator?.length || 0 }}</span>
            </button>
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'nomenklatur' }"
              @click="activeTab = 'nomenklatur'"
            >
              <span>3. Nomenklatur</span>
              <span class="tab-count-pill">{{ auditResult.audit_nomenklatur?.length || 0 }}</span>
            </button>
            <button
              type="button"
              class="audit-tab-btn"
              :class="{ active: activeTab === 'rekomendasi' }"
              @click="activeTab = 'rekomendasi'"
            >
              <span>4. Rekomendasi Bapperida</span>
              <span class="tab-count-pill">{{ auditResult.rekomendasi?.length || 0 }}</span>
            </button>
          </div>

          <!-- Tab 1: Pagu Anggaran -->
          <div v-if="activeTab === 'pagu'" class="tab-pane-content">
            <div class="tab-pane-desc">
              Membandingkan nilai pagu anggaran yang tertera pada tabel matriks dokumen PDF dengan data pagu resmi di database aplikasi.
            </div>
            <div class="table-responsive">
              <table class="audit-data-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">NO</th>
                    <th style="width: 100px;">KODE</th>
                    <th>NAMA PROGRAM</th>
                    <th style="text-align: right; width: 150px;">PAGU DI PDF</th>
                    <th style="text-align: right; width: 150px;">PAGU DATABASE</th>
                    <th style="text-align: right; width: 140px;">SELISIH</th>
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
                    <td>{{ item.uraiprogram }}</td>
                    <td class="text-right text-mono font-bold">
                      {{ formatCurrency(item.pagu_pdf) }}
                    </td>
                    <td class="text-right text-mono font-bold text-blue">
                      {{ formatCurrency(item.pagu_db) }}
                    </td>
                    <td class="text-right text-mono font-bold" :class="item.selisih !== 0 ? 'text-red' : 'text-slate'">
                      {{ formatCurrency(item.selisih) }}
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

          <!-- Tab 2: Indikator & Target -->
          <div v-if="activeTab === 'indikator'" class="tab-pane-content">
            <div class="tab-pane-desc">
              Memverifikasi keselarasan rumusan tolok ukur indikator kinerja dan angka target tahunan.
            </div>
            <div v-if="auditResult.audit_indikator?.length === 0" class="empty-tab-text">
              Tidak ada data indikator program yang terdeteksi untuk dibandingkan.
            </div>
            <div v-else class="table-responsive">
              <table class="audit-data-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">NO</th>
                    <th style="width: 100px;">KODE</th>
                    <th>INDIKATOR KINERJA</th>
                    <th style="text-align: center; width: 85px;">SATUAN</th>
                    <th style="text-align: center; width: 120px;">TARGET PDF</th>
                    <th style="text-align: center; width: 120px;">TARGET DATABASE</th>
                    <th style="text-align: center; width: 100px;">STATUS</th>
                    <th>CATATAN</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(ind, idx) in auditResult.audit_indikator"
                    :key="idx"
                    :class="{ 'row-diff': !ind.is_match }"
                  >
                    <td class="text-center">{{ idx + 1 }}</td>
                    <td class="text-mono">{{ ind.kodeprogram || '-' }}</td>
                    <td class="font-medium">{{ ind.indikator }}</td>
                    <td class="text-center">{{ ind.satuan || '-' }}</td>
                    <td class="text-center text-mono font-bold">{{ ind.target_pdf || '-' }}</td>
                    <td class="text-center text-mono font-bold text-blue">{{ ind.target_db || '-' }}</td>
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

          <!-- Tab 3: Nomenklatur -->
          <div v-if="activeTab === 'nomenklatur'" class="tab-pane-content">
            <div class="tab-pane-desc">
              Memeriksa kesesuaian kodefikasi dan nomenklatur standar (Kepmen 050/Permendagri 90).
            </div>
            <div class="table-responsive">
              <table class="audit-data-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">NO</th>
                    <th style="width: 110px;">KODE</th>
                    <th>NOMENKLATUR DI DOKUMEN PDF</th>
                    <th>NOMENKLATUR DI DATABASE</th>
                    <th style="text-align: center; width: 100px;">STATUS</th>
                    <th>CATATAN</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(nom, idx) in auditResult.audit_nomenklatur"
                    :key="idx"
                    :class="{ 'row-diff': !nom.is_match }"
                  >
                    <td class="text-center">{{ idx + 1 }}</td>
                    <td class="text-mono font-bold">{{ nom.kode }}</td>
                    <td>{{ nom.nama_pdf }}</td>
                    <td class="text-blue">{{ nom.nama_db }}</td>
                    <td class="text-center">
                      <span class="badge-audit" :class="nom.is_match ? 'badge-match' : 'badge-mismatch'">
                        {{ nom.is_match ? 'Sinkron' : 'Beda' }}
                      </span>
                    </td>
                    <td class="text-keterangan">{{ nom.keterangan || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab 4: Rekomendasi -->
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
  setup() {
    const isOpen = ref(false);
    const loading = ref(false);
    const currentStep = ref(1);
    const errorMessage = ref('');
    const copied = ref(false);

    const opdData = ref(null);
    const targetDoc = ref(null);
    const auditResult = ref(null);
    const activeTab = ref('pagu'); // pagu, indikator, nomenklatur, rekomendasi

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
      activeTab.value = 'pagu';
      isOpen.value = true;

      await startAudit();
    };

    const closeModal = () => {
      isOpen.value = false;
      loading.value = false;
    };

    const startAudit = async () => {
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
        const res = await api.auditDokumenPerencanaan(opdData.value.id_skpd, docId);
        auditResult.value = res;
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
      auditTargetTahap,
      docFileUrl,
      openModal,
      closeModal,
      startAudit,
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
.text-red { color: #dc2626; }
.text-slate { color: #64748b; }

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
</style>

