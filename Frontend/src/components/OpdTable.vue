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
const currentFilter = ref('all'); // 'all', 'with_sub', 'without_sub'

const countWithSub = computed(() => {
  return props.opdList.filter(o => (o.sub_count || 0) > 0).length;
});

const countWithoutSub = computed(() => {
  return props.opdList.filter(o => (o.sub_count || 0) === 0).length;
});

const filteredList = computed(() => {
  let list = props.opdList;

  // Filter tab
  if (currentFilter.value === 'with_sub') {
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
      return namaMatch || kodeMatch;
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
</script>
