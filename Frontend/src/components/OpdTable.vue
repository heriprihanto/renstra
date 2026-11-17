<template>
  <div class="table-card">
    <!-- Toolbar: Search & Filter Pills -->
    <div class="table-toolbar">
      <div class="search-box">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          type="text"
          class="search-input"
          v-model="searchQuery"
          @input="onSearchInput"
          placeholder="Cari nama SKPD atau kode rekening (mis: 1.01, Pendidikan, Bappeda)..."
        />
        <button
          v-if="searchQuery"
          class="clear-search-btn"
          @click="clearSearch"
          title="Hapus pencarian"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Filter buttons -->
      <div class="toolbar-filters">
        <button
          :class="['filter-btn', { active: currentFilter === 'all' }]"
          @click="setFilter('all')"
        >
          Semua ({{ opdList.length }})
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'with_doc' }]"
          @click="setFilter('with_doc')"
        >
          <span class="pulse-dot" style="width: 6px; height: 6px; background-color: #3b82f6;"></span>
          Ada Dokumen ({{ countWithDoc }})
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'with_sub' }]"
          @click="setFilter('with_sub')"
        >
          <span class="pulse-dot" style="width: 6px; height: 6px; background-color: #10b981;"></span>
          Ada Sub Unit ({{ countWithSub }})
        </button>
        <button
          :class="['filter-btn', { active: currentFilter === 'without_sub' }]"
          @click="setFilter('without_sub')"
        >
          Tanpa Sub Unit ({{ countWithoutSub }})
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p style="color: var(--text-muted); font-size: 0.9rem;">Memuat data Perangkat Daerah dari PostgreSQL...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredList.length === 0" class="state-container">
      <div class="state-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
      </div>
      <h3 style="font-size: 1.1rem; color: var(--primary-900);">SKPD Tidak Ditemukan</h3>
      <p style="color: var(--text-muted); font-size: 0.85rem; max-width: 400px;">
        Tidak ada data yang cocok dengan kueri <strong>"{{ searchQuery }}"</strong>.
      </p>
      <button class="btn-action-secondary" @click="clearSearch">
        Reset Pencarian
      </button>
    </div>

    <!-- Table Responsive -->
    <div v-else class="table-responsive">
      <table class="civic-table">
        <thead>
          <tr>
            <th class="col-number">NO</th>
            <th class="col-code">KODE SKPD</th>
            <th>NAMA PERANGKAT DAERAH</th>
            <th style="min-width: 260px;">DOKUMEN PERENCANAAN</th>
            <th style="width: 170px; text-align: center;">JUMLAH SUB SKPD</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(opd, index) in filteredList" :key="opd.id_skpd">
            <!-- No -->
            <td class="col-number">{{ index + 1 }}</td>

            <!-- Kode SKPD -->
            <td class="col-code">
              <span class="code-pill">{{ opd.kode_skpd || '-' }}</span>
            </td>

            <!-- Nama SKPD (Clickable to RENSTRA) -->
            <td>
              <button
                class="skpd-interactive-title"
                @click="$emit('select-skpd', opd)"
                :title="`Klik untuk melihat RENSTRA ${opd.nama_skpd}`"
              >
                <span class="skpd-name-text">{{ opd.nama_skpd }}</span>
              </button>
            </td>

            <!-- Dokumen Perencanaan (id_ref_dokumen 64, 65, 66) -->
            <td>
              <div v-if="opd.dokumen && opd.dokumen.length > 0" class="doc-badge-group">
                <a
                  v-for="doc in opd.dokumen"
                  :key="doc.id"
                  :href="getDocUrl(doc)"
                  target="_blank"
                  rel="noopener noreferrer"
                  :class="['doc-pill', getDocBadgeClass(doc.id_ref_dokumen)]"
                  :title="`${doc.tahap}: ${doc.nama_file}\nDiunggah: ${formatDate(doc.uploaded_at)}\n(Klik untuk membuka berkas)`"
                  @click.stop
                >
                  <!-- Penetapan (66) Icon -->
                  <svg v-if="doc.id_ref_dokumen === 66" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                  <!-- Rankir (65) Icon -->
                  <svg v-else-if="doc.id_ref_dokumen === 65" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                  </svg>
                  <!-- Rancangan (64) Icon -->
                  <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                  <span class="doc-pill-name">{{ doc.tahap }}</span>
                  <span class="doc-file-format">{{ getFileExt(doc.nama_file) }}</span>
                </a>
              </div>
              <span v-else class="doc-empty-text" title="Belum mengunggah Dokumen Perencanaan (Rancangan/Rankir/Penetapan)">
                <span class="doc-empty-dash">-</span>
              </span>
            </td>

            <!-- Jumlah Sub SKPD -->
            <td style="text-align: center;">
              <span
                :class="['sub-badge', opd.sub_count > 0 ? 'has-units' : 'empty-units']"
              >
                <svg v-if="opd.sub_count > 0" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
                <span>{{ opd.sub_count }} Unit</span>
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  opdList: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['select-skpd', 'search-change']);

const searchQuery = ref('');
const currentFilter = ref('all'); // 'all', 'with_doc', 'with_sub', 'without_sub'

const countWithSub = computed(() => {
  return props.opdList.filter(o => (o.sub_count || 0) > 0).length;
});

const countWithoutSub = computed(() => {
  return props.opdList.filter(o => (o.sub_count || 0) === 0).length;
});

const countWithDoc = computed(() => {
  return props.opdList.filter(o => o.dokumen && o.dokumen.length > 0).length;
});

const filteredList = computed(() => {
  let list = props.opdList;

  // Filter tab
  if (currentFilter.value === 'with_doc') {
    list = list.filter(o => o.dokumen && o.dokumen.length > 0);
  } else if (currentFilter.value === 'with_sub') {
    list = list.filter(o => (o.sub_count || 0) > 0);
  } else if (currentFilter.value === 'without_sub') {
    list = list.filter(o => (o.sub_count || 0) === 0);
  }

  // Search query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase();
    list = list.filter(o => {
      const namaMatch = o.nama_skpd && o.nama_skpd.toLowerCase().includes(q);
      const kodeMatch = o.kode_skpd && o.kode_skpd.toLowerCase().includes(q);
      const docMatch = o.dokumen && o.dokumen.some(d =>
        (d.tahap && d.tahap.toLowerCase().includes(q)) ||
        (d.nama_file && d.nama_file.toLowerCase().includes(q))
      );
      return namaMatch || kodeMatch || docMatch;
    });
  }

  return list;
});

function onSearchInput() {
  emit('search-change', searchQuery.value);
}

function clearSearch() {
  searchQuery.value = '';
  emit('search-change', '');
}

function setFilter(filterType) {
  currentFilter.value = filterType;
}

function getDocUrl(doc) {
  if (doc.file_url) return doc.file_url;
  const link = (doc.link_gd || '').trim();
  if (!link) return '#';
  if (link.startsWith('/')) {
    return `https://monevrkpd.tegalkota.go.id/dokren${link}`;
  }
  return `https://monevrkpd.tegalkota.go.id/dokren/${link}`;
}

function getDocBadgeClass(idRef) {
  if (idRef === 66) return 'badge-penetapan';
  if (idRef === 65) return 'badge-rankir';
  return 'badge-rancangan';
}

function getFileExt(filename) {
  if (!filename) return 'PDF';
  const parts = filename.split('.');
  if (parts.length > 1) {
    const ext = parts.pop().toUpperCase();
    return ext.length <= 4 ? ext : 'FILE';
  }
  return 'PDF';
}

function formatDate(dateStr) {
  if (!dateStr) return '-';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  } catch {
    return dateStr;
  }
}
</script>

<style scoped>
.doc-badge-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}

.doc-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.28rem 0.55rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.15s ease-in-out;
  border: 1px solid transparent;
  cursor: pointer;
  line-height: 1.2;
}

.doc-pill:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Penetapan (66) - Emerald / Green */
.badge-penetapan {
  background-color: #ecfdf5;
  color: #047857;
  border-color: #a7f3d0;
}
.badge-penetapan:hover {
  background-color: #d1fae5;
  border-color: #059669;
  color: #065f46;
}

/* Rankir (65) - Blue / Indigo */
.badge-rankir {
  background-color: #eff6ff;
  color: #1d4ed8;
  border-color: #bfdbfe;
}
.badge-rankir:hover {
  background-color: #dbeafe;
  border-color: #2563eb;
  color: #1e40af;
}

/* Rancangan (64) - Amber / Orange */
.badge-rancangan {
  background-color: #fffbeb;
  color: #b45309;
  border-color: #fde68a;
}
.badge-rancangan:hover {
  background-color: #fef3c7;
  border-color: #d97706;
  color: #92400e;
}

.doc-pill-name {
  white-space: nowrap;
}

.doc-file-format {
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.05rem 0.25rem;
  border-radius: 3px;
  background-color: rgba(0, 0, 0, 0.07);
  letter-spacing: 0.02em;
}

.doc-empty-text {
  color: #94a3b8;
  font-size: 0.88rem;
  display: inline-block;
}

.doc-empty-dash {
  font-weight: 500;
}
</style>
