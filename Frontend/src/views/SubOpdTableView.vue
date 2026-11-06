<template>
  <div>
    <!-- Sub-page Breadcrumb & Header Banner -->
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
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
              <span class="code-pill" style="background: #e0e7ff; color: #3730a3; border-color: #c7d2fe; font-size: 0.85rem;">
                KODE: {{ opdDetail?.kode_skpd || '...' }}
              </span>
              <span class="badge-tag">TABEL SUB SKPD</span>
            </div>
            <h2>
              <span>{{ opdDetail?.nama_skpd || 'Memuat Data SKPD...' }}</span>
            </h2>
            <p>
              Rincian Unit Pelaksana Teknis (UPT), Satuan Pendidikan, Puskesmas, dan Bagian Kerja di bawah naungan SKPD.
            </p>
          </div>

          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sub-badge has-units" style="font-size: 0.9rem; padding: 0.5rem 1rem;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
              <span>{{ subList.length }} Sub SKPD Terdaftar</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <main class="app-container" style="margin-top: 1.5rem;">
      <div class="table-card">
        <!-- Toolbar: Search inside Sub SKPD -->
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
              placeholder="Cari nama Sub SKPD (contoh: SMP Negeri, Puskesmas, UPTD)..."
            />
            <button
              v-if="searchQuery"
              class="clear-search-btn"
              @click="searchQuery = ''"
              title="Hapus filter"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <div style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">
            Menampilkan <strong>{{ filteredSubList.length }}</strong> dari <strong>{{ subList.length }}</strong> Sub SKPD
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="state-container">
          <div class="spinner"></div>
          <p style="color: var(--text-muted); font-size: 0.9rem;">Memuat daftar Sub SKPD dari PostgreSQL...</p>
        </div>

        <!-- Zero units in database -->
        <div v-else-if="subList.length === 0" class="state-container">
          <div class="state-icon" style="background: var(--amber-50); color: var(--amber-600); width: 68px; height: 68px;">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <h3 style="font-size: 1.2rem; color: var(--primary-900);">SKPD Ini Tidak Memiliki Sub Unit</h3>
          <p style="color: var(--text-muted); font-size: 0.9rem; max-width: 520px; line-height: 1.6;">
            Dalam basis data perencanaan (<code>ta_sub_pd</code>), <strong>{{ opdDetail?.nama_skpd }}</strong> beroperasi secara langsung sebagai SKPD tunggal tanpa pembagian Sub SKPD / UPTD bawahan.
          </p>
          <div style="margin-top: 0.5rem;">
            <router-link to="/" class="btn-action-view" style="text-decoration: none;">
              Kembali ke Daftar OPD
            </router-link>
          </div>
        </div>

        <!-- Zero search results -->
        <div v-else-if="filteredSubList.length === 0" class="state-container">
          <div class="state-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <h3 style="font-size: 1.1rem; color: var(--primary-900);">Sub SKPD Tidak Ditemukan</h3>
          <p style="color: var(--text-muted); font-size: 0.85rem;">
            Tidak ada sub unit kerja yang cocok dengan pencarian "<strong>{{ searchQuery }}</strong>".
          </p>
          <button class="btn-action-secondary" @click="searchQuery = ''">
            Reset Pencarian
          </button>
        </div>

        <!-- Full Table of ta_sub_pd -->
        <div v-else class="table-responsive">
          <table class="civic-table">
            <thead>
              <tr>
                <th class="col-number">NO</th>
                <th style="width: 230px;">KODE SUB SKPD</th>
                <th>NAMA SUB SKPD (KLIK NAMA UNTUK BUKA RENSTRA)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(sub, index) in filteredSubList" :key="sub.id_sub_skpd">
                <!-- No -->
                <td class="col-number">{{ index + 1 }}</td>

                <!-- Kode Sub SKPD -->
                <td>
                  <span class="code-pill">{{ sub.kode_sub_skpd || '-' }}</span>
                </td>

                <!-- Nama Sub SKPD (Klik untuk ke Halaman Baru RENSTRA) -->
                <td>
                  <button
                    class="skpd-interactive-title"
                    @click="navigateToRenstra(sub)"
                    :title="`Klik untuk membuka RENSTRA ${sub.nama_sub_skpd}`"
                  >
                    <span class="skpd-name-text">{{ sub.nama_sub_skpd }}</span>
                    <span class="click-hint-badge">
                      <span>Buka RENSTRA</span>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <polyline points="9 18 15 12 9 6"/>
                      </svg>
                    </span>
                  </button>
                </td>

                
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const router = useRouter();
const opdDetail = ref(null);
const subList = ref([]);
const loading = ref(false);
const searchQuery = ref('');

async function loadSubData() {
  const idSkpd = route.params.id;
  if (!idSkpd) return;

  loading.value = true;
  try {
    // Ambil detail OPD dan daftar sub unit
    const detail = await api.getOpdDetail(idSkpd);
    opdDetail.value = detail;
    subList.value = detail.sub_pd_list || [];
  } catch (err) {
    console.error('Gagal mengambil detail Sub SKPD:', err);
  } finally {
    loading.value = false;
  }
}

function navigateToRenstra(sub) {
  // Navigate to dedicated new page for RENSTRA of this Sub SKPD
  router.push(`/sub-opd/${sub.id_sub_skpd}`);
}

const filteredSubList = computed(() => {
  if (!searchQuery.value.trim()) {
    return subList.value;
  }
  const q = searchQuery.value.trim().toLowerCase();
  return subList.value.filter(s => {
    const namaMatch = s.nama_sub_skpd && s.nama_sub_skpd.toLowerCase().includes(q);
    const kodeMatch = s.kode_sub_skpd && s.kode_sub_skpd.toLowerCase().includes(q);
    return namaMatch || kodeMatch;
  });
});

onMounted(() => {
  loadSubData();
});
</script>
