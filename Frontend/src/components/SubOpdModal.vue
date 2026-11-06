<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="modal-backdrop"
      @click.self="closeModal"
      @keydown.esc="closeModal"
    >
      <div class="drawer-panel" role="dialog" aria-modal="true">
        <!-- Header -->
        <div class="drawer-header">
          <div class="drawer-title-group">
            <div class="drawer-breadcrumbs">
              <span>Perangkat Daerah</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
              <span>Daftar Sub SKPD</span>
            </div>
            <h3 class="drawer-title">{{ opd?.nama_skpd || 'Perangkat Daerah' }}</h3>
            <span class="drawer-code-badge">Kode: {{ opd?.kode_skpd || '-' }}</span>
          </div>

          <button class="btn-close-drawer" @click="closeModal" title="Tutup (Esc)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Toolbar inside Drawer -->
        <div class="drawer-toolbar">
          <div class="search-box" style="min-width: unset; max-width: unset; width: 100%;">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              class="search-input"
              style="padding: 0.5rem 1rem 0.5rem 2.3rem; font-size: 0.84rem;"
              v-model="subSearch"
              placeholder="Saring Sub SKPD (mis: SMP Negeri, Puskesmas, Bagian)..."
            />
          </div>
        </div>

        <!-- Body Content -->
        <div class="drawer-body">
          <!-- Loading state -->
          <div v-if="loading" class="state-container" style="padding: 2.5rem 1rem;">
            <div class="spinner"></div>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Mengambil rincian Sub SKPD...</p>
          </div>

          <!-- Empty units in database -->
          <div v-else-if="subList.length === 0" class="state-container" style="padding: 2.5rem 1rem;">
            <div class="state-icon" style="background: var(--amber-50); color: var(--amber-600);">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <h4 style="font-size: 1.05rem; color: var(--primary-900);">Unit Tunggal (0 Sub SKPD)</h4>
            <p style="color: var(--text-muted); font-size: 0.84rem; max-width: 380px;">
              Perangkat Daerah ini beroperasi sebagai satu kesatuan unit kerja langsung tanpa pemisahan Sub SKPD (tabel <code>ta_sub_pd</code>).
            </p>
          </div>

          <!-- Empty search filter -->
          <div v-else-if="filteredSubList.length === 0" class="state-container" style="padding: 2.5rem 1rem;">
            <div class="state-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </div>
            <h4 style="font-size: 1rem; color: var(--primary-900);">Sub SKPD Tidak Ditemukan</h4>
            <p style="color: var(--text-muted); font-size: 0.84rem;">
              Tidak ada sub unit yang cocok dengan pencarian "<strong>{{ subSearch }}</strong>".
            </p>
            <button class="btn-action-secondary" @click="subSearch = ''">
              Reset Filter
            </button>
          </div>

          <!-- Sub SKPD Cards / List -->
          <div v-else>
            <div
              v-for="(sub, idx) in filteredSubList"
              :key="sub.id_sub_skpd"
              class="sub-item-card"
            >
              <div class="sub-item-index">{{ idx + 1 }}</div>
              <div class="sub-item-content">
                <div class="sub-item-title">{{ sub.nama_sub_skpd }}</div>
                <div class="sub-item-code">
                  <span>Kode Sub: <strong>{{ sub.kode_sub_skpd || '-' }}</strong></span>
                  <span style="margin: 0 0.5rem; color: var(--border-strong);">&bull;</span>
                  <span>ID: {{ sub.id_sub_skpd }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="drawer-footer">
          <div style="font-size: 0.82rem; color: var(--text-muted);">
            Menampilkan <strong>{{ filteredSubList.length }}</strong> dari <strong>{{ subList.length }}</strong> Sub SKPD
          </div>
          <button class="btn-action-secondary" @click="closeModal">
            Tutup
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import api from '../services/api';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  opd: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close']);

const subList = ref([]);
const loading = ref(false);
const subSearch = ref('');

// Load sub units whenever opd changes and drawer is open
watch(
  () => [props.isOpen, props.opd],
  async ([open, currentOpd]) => {
    if (open && currentOpd?.id_skpd) {
      subSearch.value = '';
      await loadSubUnits(currentOpd.id_skpd);
    } else {
      subList.value = [];
    }
  },
  { immediate: true }
);

async function loadSubUnits(idSkpd) {
  loading.value = true;
  try {
    const data = await api.getSubOpdList(idSkpd);
    subList.value = data || [];
  } catch (err) {
    console.error('Gagal mengambil Sub SKPD:', err);
    subList.value = [];
  } finally {
    loading.value = false;
  }
}

const filteredSubList = computed(() => {
  if (!subSearch.value.trim()) {
    return subList.value;
  }
  const q = subSearch.value.trim().toLowerCase();
  return subList.value.filter(s => {
    const namaMatch = s.nama_sub_skpd && s.nama_sub_skpd.toLowerCase().includes(q);
    const kodeMatch = s.kode_sub_skpd && s.kode_sub_skpd.toLowerCase().includes(q);
    return namaMatch || kodeMatch;
  });
});

function closeModal() {
  emit('close');
}

// Global ESC handler
function handleKeyDown(e) {
  if (e.key === 'Escape' && props.isOpen) {
    closeModal();
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>
