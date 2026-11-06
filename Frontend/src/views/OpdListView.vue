<template>
  <div>
    <!-- Hero / Header Section -->
    <section class="hero-banner">
      <div class="app-container">
        <div class="hero-content">
          <div class="hero-title-group">
            <h2>
              <span>Rencana Strategis Perangkat Daerah (RENSTRA)</span>
              <span class="badge-tag">PERIODE 2025 - 2029</span>
            </h2>
            <p>
              Perubahan Renstra
            </p>
          </div>

          <div>
            <button class="btn-action-secondary" @click="loadData" title="Muat ulang data">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6"/>
                <path d="M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              <span>Segarkan Data</span>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <main class="app-container" style="margin-top: 1.5rem;">
      <!-- Master Table: ta_opd -->
      <OpdTable
        :opd-list="opdList"
        :loading="loading"
        @select-skpd="navigateToSubOpd"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
import OpdTable from '../components/OpdTable.vue';

const router = useRouter();

const opdList = ref([]);
const loading = ref(false);

async function loadData() {
  loading.value = true;
  try {
    const opdData = await api.getOpdList();
    opdList.value = opdData;
  } catch (err) {
    console.error('Gagal mengambil data:', err);
  } finally {
    loading.value = false;
  }
}

function navigateToSubOpd(opd) {
  // Navigate to dedicated new page for Sub SKPD
  router.push(`/opd/${opd.id_skpd}`);
}

onMounted(() => {
  loadData();
});
</script>
