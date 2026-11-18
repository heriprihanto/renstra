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

          <div class="hero-actions">
            <a
              href="https://monevrkpd.tegalkota.go.id/dokren"
              target="_blank"
              rel="noopener noreferrer"
              class="btn-upload-dokren"
              title="Buka portal Upload Dokumen Renstra di Monev RKPD Kota Tegal"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <span>Upload Dokumen Renstra</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="opacity: 0.85;">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
            </a>

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

<style scoped>
.hero-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.btn-upload-dokren {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.95rem;
  border-radius: var(--radius-md, 8px);
  font-size: 0.82rem;
  font-weight: 700;
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: #ffffff;
  border: 1px solid #0284c7;
  text-decoration: none;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(2, 132, 199, 0.25);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-upload-dokren:hover {
  background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(2, 132, 199, 0.35);
  color: #ffffff;
}
</style>
