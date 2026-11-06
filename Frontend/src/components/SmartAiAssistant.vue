<template>
  <div class="smart-ai-panel">
    <!-- Panel Header -->
    <div class="smart-ai-header">
      <div class="smart-ai-title-wrap">
        <div class="ai-badge-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
        </div>
        <div>
          <h4 class="smart-ai-title">Asisten AI: Perumusan Indikator SMART</h4>
          <p class="smart-ai-subtitle">
            Rekomendasi indikator yang <strong>Spesifik</strong>, <strong>Terukur</strong>, <strong>Dapat Dicapai</strong>, <strong>Relevan</strong>, dan <strong>Terikat Waktu</strong>.
          </p>
        </div>
      </div>
      <div class="smart-ai-header-actions">
        <button
          type="button"
          class="btn-ai-refresh"
          :disabled="loading"
          @click="fetchRecommendations"
          title="Analisis ulang perumusan indikator"
        >
          <svg
            :class="{ 'spin-icon': loading }"
            width="13"
            height="13"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
          <span>{{ loading ? 'Menganalisis...' : 'Analisis Ulang' }}</span>
        </button>
        <button
          type="button"
          class="btn-ai-close"
          @click="$emit('close')"
          title="Tutup Asisten AI"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- Context Info Strip -->
    <div class="smart-ai-context">
      <div class="context-item">
        <span class="context-label">Tingkatan:</span>
        <span class="context-badge level-badge">{{ levelLabel }}</span>
      </div>
      <div class="context-item" style="flex: 1; min-width: 220px;">
        <span class="context-label">Fokus:</span>
        <input
          type="text"
          class="context-input-focus"
          v-model="activeUraian"
          placeholder="Uraian atau kata kunci fokus..."
          @keydown.enter.prevent="fetchRecommendations"
          title="Anda dapat menyesuaikan topik fokus dan menekan Enter atau tombol Analisis Ulang"
        />
      </div>
      <div v-if="subkegiatanList && subkegiatanList.length > 0" class="context-item">
        <span
          class="context-badge subkeg-badge"
          :title="'Subkegiatan yang dianalisis: ' + subkegiatanList.map(s => s.uraisubkegiatan).join(', ')"
        >
          🔬 {{ subkegiatanList.length }} Subkegiatan dianalisis
        </span>
      </div>
      <div v-if="result" class="context-item">
        <span
          class="context-badge"
          :class="result.source === 'hermes' || result.source === 'openai' ? 'ai-live-badge' : 'ai-fallback-badge'"
        >
          {{ result.source === 'hermes' ? '✨ Hermes AI (Lokal)' : result.source === 'openai' ? '✨ OpenAI Live (GPT-5.5)' : '⚙️ SMART Rule Engine' }}
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="smart-ai-loading">
      <div class="pulsing-circle"></div>
      <div class="loading-text-group">
        <div class="loading-main-text">Sedang merumuskan indikator kinerja SMART dengan AI...</div>
        <div class="loading-sub-text">
          Menyelaraskan sasaran, kaidah perencanaan daerah, dan capaian target tahunan
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="smart-ai-error">
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>{{ error }}</span>
      </div>
      <button type="button" class="btn-ai-retry" @click="fetchRecommendations">Coba Lagi</button>
    </div>

    <!-- Recommendation Cards -->
    <div v-else-if="result && result.recommendations && result.recommendations.length > 0" class="smart-ai-results">
      <!-- Fallback Notice vs Hermes / OpenAI Live Notice -->
      <div v-if="result.source === 'hermes'" class="smart-ai-live-notice">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#15803d" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Rekomendasi indikator SMART dirumuskan secara dinamis oleh <strong>Hermes AI (Lokal)</strong>.</span>
      </div>
      <div v-else-if="result.source === 'openai'" class="smart-ai-live-notice">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#15803d" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Rekomendasi indikator SMART dirumuskan secara dinamis oleh <strong>OpenAI (GPT-5.5 Live)</strong>.</span>
      </div>
      <div v-else-if="result.source === 'smart_fallback'" class="smart-ai-fallback-alert">
        <div class="alert-icon">⚠️</div>
        <div class="alert-body">
          <div style="font-weight: 700; color: #92400e; margin-bottom: 0.2rem;">
            Pemberitahuan Mesin Rekomendasi
          </div>
          <p style="margin: 0; color: #78350f; line-height: 1.45;">
            {{ result.message || 'Sistem menyajikan rekomendasi formulasi indikator SMART menggunakan SMART Rule Engine Analitik Daerah berbasis Permendagri No. 86/2017.' }}
          </p>
        </div>
      </div>

      <div
        v-for="(rec, idx) in result.recommendations"
        :key="idx"
        class="rec-card"
        :class="{ 'rec-card-applied': appliedIndex === idx }"
      >
        <!-- Card Header -->
        <div class="rec-card-header">
          <div class="rec-title-wrap">
            <span class="rec-number-pill">Opsi {{ idx + 1 }}</span>
            <h5 class="rec-title">{{ rec.uraian }}</h5>
          </div>
          <div class="rec-meta-tags">
            <span class="meta-tag meta-satuan">Satuan: <strong>{{ rec.satuan || '-' }}</strong></span>
            <span class="meta-tag meta-status" :class="rec.status">Sifat: {{ rec.status }}</span>
          </div>
        </div>

        <!-- Definisi Operasional -->
        <div v-if="rec.definisi_operasional" class="rec-def-box">
          <span class="rec-def-label">Definisi Operasional:</span>
          <span class="rec-def-text">{{ rec.definisi_operasional }}</span>
        </div>

    

        <!-- Target Capaian Preview -->
        <div v-if="hasTargets(rec)" class="rec-targets-strip">
          <span class="targets-strip-title">Saran Target:</span>
          <div class="targets-strip-chips">
            <span v-if="rec.target_awal" class="target-chip">Baseline: <strong>{{ rec.target_awal }}</strong></span>
            <span v-if="rec.target2026" class="target-chip">2026: <strong>{{ rec.target2026 }}</strong></span>
            <span v-if="rec.target2027" class="target-chip">2027: <strong>{{ rec.target2027 }}</strong></span>
            <span v-if="rec.target2028" class="target-chip">2028: <strong>{{ rec.target2028 }}</strong></span>
            <span v-if="rec.target2029" class="target-chip">2029: <strong>{{ rec.target2029 }}</strong></span>
            <span v-if="rec.target2030" class="target-chip">2030: <strong>{{ rec.target2030 }}</strong></span>
          </div>
        </div>

        <!-- Action Apply Button -->
        <div class="rec-action-footer">
          <button
            type="button"
            class="btn-apply-rec"
            :class="{ 'applied-success': appliedIndex === idx }"
            @click="applyRecommendation(rec, idx)"
          >
            <span v-if="appliedIndex === idx" style="display: flex; align-items: center; gap: 0.35rem;">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Telah Diterapkan ke Form
            </span>
            <span v-else style="display: flex; align-items: center; gap: 0.35rem;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Gunakan Rekomendasi Ini
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="smart-ai-empty">
      <p style="margin: 0; font-size: 0.84rem; color: #64748b;">
        Belum ada rekomendasi yang dimuat. Pastikan kolom Fokus terisi, lalu klik tombol <strong>"Analisis Ulang"</strong> di atas.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import api from '../services/api';

const props = defineProps({
  level: {
    type: String,
    default: 'kegiatan',
  },
  parentUraian: {
    type: String,
    default: '',
  },
  entityUraian: {
    type: String,
    default: '',
  },
  kinerja: {
    type: String,
    default: '',
  },
  opdName: {
    type: String,
    default: '',
  },
  subkegiatanList: {
    type: Array,
    default: () => [],
  },
  isEditMode: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['apply', 'close']);

const loading = ref(false);
const error = ref(null);
const result = ref(null);
const appliedIndex = ref(null);
const activeUraian = ref(props.entityUraian || props.parentUraian || '');

watch(
  () => [props.entityUraian, props.parentUraian],
  ([newEntity, newParent]) => {
    if (!activeUraian.value || activeUraian.value === props.level.toUpperCase()) {
      activeUraian.value = newEntity || newParent || '';
    }
  }
);

const levelLabel = computed(() => {
  switch (props.level) {
    case 'tujuan': return 'Indikator Tujuan';
    case 'sasaran': return 'Indikator Sasaran';
    case 'program': return 'Indikator Program';
    case 'kegiatan': return 'Indikator Kegiatan';
    case 'subkegiatan': return 'Indikator Subkegiatan';
    default: return 'Indikator Renstra';
  }
});

function hasTargets(rec) {
  return rec.target_awal || rec.target2026 || rec.target2027 || rec.target2028 || rec.target2029 || rec.target2030;
}

async function fetchRecommendations() {
  loading.value = true;
  error.value = null;
  appliedIndex.value = null;

  try {
    const formattedSubkeg = (props.subkegiatanList || []).map(sk => ({
      kodesubkegiatan: sk.kodesubkegiatan || '',
      uraisubkegiatan: sk.uraisubkegiatan || '',
      kinerja: sk.kinerja || '',
      indikator_uraian: sk.indikator?.uraian || '',
      satuan: sk.indikator?.satuan || '',
    }));

    const topic = (activeUraian.value || props.entityUraian || props.parentUraian || props.level).trim();

    const payload = {
      level: props.level,
      uraian: topic,
      entity_uraian: topic,
      parent_uraian: props.parentUraian || '',
      kinerja: props.kinerja || '',
      opd_name: props.opdName || '',
      subkegiatan_list: formattedSubkeg,
    };

    const res = await api.getSmartIndicatorRecommendations(payload);
    // fetchJson returns the parsed json object directly
    result.value = res?.recommendations ? res : (res?.data || res);
  } catch (err) {
    console.error('Error fetching SMART recommendations:', err);
    error.value = err.message || 'Gagal memuat rekomendasi indikator AI.';
  } finally {
    loading.value = false;
  }
}

function applyRecommendation(rec, idx) {
  appliedIndex.value = idx;
  emit('apply', rec);
}

onMounted(() => {
  fetchRecommendations();
});
</script>

<style scoped>
.smart-ai-panel {
  background: #f8fafc;
  border: 1px solid #c7d2fe;
  border-radius: 12px;
  padding: 1.15rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.08);
  animation: fadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.smart-ai-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e0e7ff;
}

.smart-ai-title-wrap {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
}

.ai-badge-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(79, 70, 229, 0.3);
}

.smart-ai-title {
  margin: 0;
  font-size: 0.98rem;
  font-weight: 700;
  color: #1e1b4b;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.smart-ai-subtitle {
  margin: 0.15rem 0 0 0;
  font-size: 0.75rem;
  color: #4b5563;
  line-height: 1.4;
}

.smart-ai-subtitle strong {
  color: #4338ca;
}

.smart-ai-header-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-shrink: 0;
}

.btn-ai-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.65rem;
  font-size: 0.74rem;
  font-weight: 600;
  color: #4338ca;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-ai-refresh:hover:not(:disabled) {
  background: #e0e7ff;
  color: #3730a3;
}

.btn-ai-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.btn-ai-close {
  background: transparent;
  border: none;
  font-size: 1rem;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-ai-close:hover {
  background: #e2e8f0;
  color: #334155;
}

.smart-ai-context {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 0.65rem;
  font-size: 0.76rem;
  color: #64748b;
  background: #ffffff;
  padding: 0.45rem 0.65rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.context-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.context-label {
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}

.context-input-focus {
  flex: 1;
  font-size: 0.78rem;
  font-family: inherit;
  padding: 0.22rem 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  background: #f8fafc;
  color: #1e293b;
  outline: none;
  transition: all 0.2s;
}

.context-input-focus:focus {
  border-color: #6366f1;
  background: #ffffff;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
}

.context-badge {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  white-space: nowrap;
}

.level-badge {
  background: #e0e7ff;
  color: #3730a3;
}

.subkeg-badge {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.ai-live-badge {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}

.ai-fallback-badge {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

.smart-ai-fallback-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 0.75rem 0.95rem;
  margin-bottom: 0.85rem;
  font-size: 0.78rem;
}

.smart-ai-fallback-alert .alert-icon {
  font-size: 1.1rem;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.smart-ai-fallback-alert .alert-hint {
  margin: 0.45rem 0 0 0;
  padding-top: 0.35rem;
  border-top: 1px dashed #fcd34d;
  color: #92400e;
  font-size: 0.74rem;
}

.smart-ai-live-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 0.65rem 0.95rem;
  margin-bottom: 0.85rem;
  font-size: 0.78rem;
  color: #166534;
}

.smart-ai-loading {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1.5rem 1rem;
  background: #ffffff;
  border-radius: 8px;
  margin-top: 0.75rem;
  border: 1px dashed #c7d2fe;
}

.pulsing-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #6366f1;
  animation: pulse 1.2s infinite ease-in-out;
  flex-shrink: 0;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0.5; }
}

.loading-main-text {
  font-size: 0.85rem;
  font-weight: 700;
  color: #312e81;
}

.loading-sub-text {
  font-size: 0.74rem;
  color: #64748b;
  margin-top: 0.15rem;
}

.smart-ai-error {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  margin-top: 0.75rem;
  font-size: 0.82rem;
  color: #991b1b;
}

.btn-ai-retry {
  padding: 0.3rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #dc2626;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}

.smart-ai-notice {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 0.8rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
  font-size: 0.76rem;
  color: #0369a1;
  margin-top: 0.75rem;
}

.smart-ai-results {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-top: 0.75rem;
}

.smart-ai-empty {
  padding: 1.5rem 1rem;
  text-align: center;
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  margin-top: 0.75rem;
}

.rec-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.95rem;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.rec-card:hover {
  border-color: #a5b4fc;
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.08);
}

.rec-card.rec-card-applied {
  border-color: #10b981;
  background: #f0fdf4;
}

.rec-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.rec-title-wrap {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
  flex: 1;
}

.rec-number-pill {
  font-size: 0.68rem;
  font-weight: 700;
  background: #eef2ff;
  color: #4338ca;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  white-space: nowrap;
  margin-top: 0.15rem;
}

.rec-title {
  margin: 0;
  font-size: 0.94rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.4;
}

.rec-meta-tags {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.meta-tag {
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.meta-satuan {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.meta-status {
  text-transform: capitalize;
}

.meta-status.positif {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.meta-status.negatif {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.meta-status.akumulatif {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.rec-def-box {
  background: #f8fafc;
  border-left: 3px solid #6366f1;
  padding: 0.5rem 0.75rem;
  border-radius: 0 6px 6px 0;
  margin-top: 0.65rem;
  font-size: 0.78rem;
  line-height: 1.45;
  color: #334155;
}

.rec-def-label {
  font-weight: 700;
  color: #4338ca;
  margin-right: 0.35rem;
}

/* SMART Breakdown */
.smart-breakdown-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.smart-item {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
  padding: 0.5rem;
  border-radius: 6px;
  background: #faf5ff;
  border: 1px solid #f3e8ff;
}

.smart-s { background: #fdf2f8; border-color: #fce7f3; }
.smart-m { background: #eff6ff; border-color: #dbeafe; }
.smart-a { background: #f0fdf4; border-color: #dcfce7; }
.smart-r { background: #fffbeb; border-color: #fef3c7; }
.smart-t { background: #f5f3ff; border-color: #ede9fe; }

.smart-badge {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  font-weight: 800;
  font-size: 0.72rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.smart-s .smart-badge { background: #ec4899; color: #fff; }
.smart-m .smart-badge { background: #3b82f6; color: #fff; }
.smart-a .smart-badge { background: #10b981; color: #fff; }
.smart-r .smart-badge { background: #f59e0b; color: #fff; }
.smart-t .smart-badge { background: #8b5cf6; color: #fff; }

.smart-body {
  flex: 1;
  min-width: 0;
}

.smart-name {
  display: block;
  font-size: 0.68rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.smart-desc {
  margin: 0.15rem 0 0 0;
  font-size: 0.72rem;
  color: #1e293b;
  line-height: 1.35;
}

/* Targets strip */
.rec-targets-strip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.65rem;
  padding: 0.45rem 0.65rem;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.targets-strip-title {
  font-size: 0.73rem;
  font-weight: 700;
  color: #475569;
}

.targets-strip-chips {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.target-chip {
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-family: var(--font-mono, monospace);
  color: #1e293b;
}

.target-chip strong {
  color: #0284c7;
}

/* Action button */
.rec-action-footer {
  margin-top: 0.75rem;
  display: flex;
  justify-content: flex-end;
}

.btn-apply-rec {
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  color: #ffffff;
  border: none;
  padding: 0.45rem 0.95rem;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.25);
}

.btn-apply-rec:hover {
  background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%);
  box-shadow: 0 4px 8px rgba(79, 70, 229, 0.35);
  transform: translateY(-1px);
}

.btn-apply-rec.applied-success {
  background: #10b981;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.25);
}
</style>
