<template>
  <div>
    <!-- Sub-page Breadcrumb & Header Banner -->
    <section class="hero-banner">
      <div class="app-container">
        <!-- Back Navigation Button -->
        <div style="margin-bottom: 0.85rem;">
          <button
            @click="goBackToSubTable"
            class="btn-action-secondary"
            style="display: inline-flex; align-items: center; gap: 0.5rem;"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"/>
              <polyline points="12 19 5 12 12 5"/>
            </svg>
            <span style="font-weight: 600;">Kembali ke Tabel Sub SKPD</span>
          </button>
        </div>

        <div class="hero-content">
          <div class="hero-title-group">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem; flex-wrap: wrap;">
              <span class="code-pill" style="background: #e0e7ff; color: #3730a3; border-color: #c7d2fe; font-size: 0.85rem;">
                KODE SUB: {{ subDetail?.kode_sub_skpd || '...' }}
              </span>
              <span class="badge-tag">RENSTRA PERANGKAT DAERAH</span>
              <span v-if="subDetail?.opd?.nama_skpd" class="badge-year" style="font-size: 0.75rem; padding: 0.2rem 0.6rem;">
                SKPD INDUK: {{ subDetail.opd.nama_skpd }}
              </span>
            </div>
            <h2>
              <span>{{ subDetail?.nama_sub_skpd || 'Memuat Data RENSTRA...' }}</span>
            </h2>
            <p>
              Rencana Strategis (RENSTRA) Unit Kerja &bull; Pemerintah Kota Tegal Periode 2025 - 2029
            </p>
          </div>

          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sub-badge has-units" style="font-size: 0.88rem; padding: 0.5rem 1rem;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
              <span>Dokumen Renstra Aktif</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content Area -->
    <main class="app-container" style="margin-top: 1.5rem;">
      <!-- Loading State -->
      <div v-if="loading" class="state-container table-card">
        <div class="spinner"></div>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Memuat data RENSTRA Sub SKPD...</p>
      </div>

      <!-- Tab Container -->
      <div v-else class="renstra-tabs-container">
        <!-- Tab Navigation Bar -->
        <nav class="renstra-tabs-nav">
          <!-- Tab 1 -->
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
          </button>

          <!-- Tab 2 -->
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
            <span>Program / Kegiatan / Subkegiatan</span>
          </button>
        </nav>

        <!-- Tab 1 Pane: Tujuan & Sasaran -->
        <div v-if="activeTab === 'tujuan_sasaran'" class="renstra-tab-pane">
          <div class="tab-pane-header">
            <div>
              <h3>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <circle cx="12" cy="12" r="6"/>
                  <circle cx="12" cy="12" r="2"/>
                </svg>
                <span>Tujuan &amp; Sasaran Strategis Perangkat Daerah</span>
              </h3>
              <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">
                Perumusan Tujuan Strategis, Sasaran Renstra, dan Indikator Kinerja Utama (IKU) Periode 2025 - 2029
              </p>
            </div>

            <button class="btn-action-view" disabled style="opacity: 0.6; cursor: not-allowed;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <span>Tambah Tujuan / Sasaran</span>
            </button>
          </div>

          <!-- Konten Kosong Sesuai Permintaan User -->
          <div class="empty-tab-placeholder">
            <div class="placeholder-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="12" cy="12" r="6"/>
                <circle cx="12" cy="12" r="2"/>
              </svg>
            </div>
            <h4>Konten Tujuan &amp; Sasaran</h4>
            <p>
              Bagian ini disiapkan untuk matriks perencanaan Tujuan dan Sasaran RENSTRA. Struktur tab telah siap dan saat ini konten masih dikosongkan untuk tahap pengisian data berikutnya.
            </p>
          </div>
        </div>

        <!-- Tab 2 Pane: Program / Kegiatan / Subkegiatan -->
        <div v-if="activeTab === 'program_kegiatan'" class="renstra-tab-pane">
          <div class="tab-pane-header">
            <div>
              <h3>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="8" y1="6" x2="21" y2="6"/>
                  <line x1="8" y1="12" x2="21" y2="12"/>
                  <line x1="8" y1="18" x2="21" y2="18"/>
                  <line x1="3" y1="6" x2="3.01" y2="6"/>
                  <line x1="3" y1="12" x2="3.01" y2="12"/>
                  <line x1="3" y1="18" x2="3.01" y2="18"/>
                </svg>
                <span>Program, Kegiatan, dan Subkegiatan RENSTRA</span>
              </h3>
              <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">
                Cascading nomenklatur Program, Kegiatan, dan Sub Kegiatan beserta indikator, target, dan pagu indikatif
              </p>
            </div>

            <button class="btn-action-view" disabled style="opacity: 0.6; cursor: not-allowed;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <span>Tambah Program</span>
            </button>
          </div>

          <!-- Konten Kosong Sesuai Permintaan User -->
          <div class="empty-tab-placeholder">
            <div class="placeholder-icon" style="background: var(--teal-50); color: var(--teal-600);">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
            </div>
            <h4>Konten Program / Kegiatan / Subkegiatan</h4>
            <p>
              Bagian ini disiapkan untuk tabel hierarki Program, Kegiatan, dan Sub Kegiatan RENSTRA Perangkat Daerah. Struktur tab telah siap dan saat ini konten masih dikosongkan untuk tahap pengisian data berikutnya.
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const router = useRouter();

const subDetail = ref(null);
const loading = ref(false);
const activeTab = ref('tujuan_sasaran'); // 'tujuan_sasaran' or 'program_kegiatan'

async function loadSubDetail() {
  const subId = route.params.subId;
  if (!subId) return;

  loading.value = true;
  try {
    const data = await api.getSubOpdDetail(subId);
    subDetail.value = data;
  } catch (err) {
    console.error('Gagal mengambil detail Sub SKPD:', err);
  } finally {
    loading.value = false;
  }
}

function goBackToSubTable() {
  if (subDetail.value?.id_skpd) {
    router.push(`/opd/${subDetail.value.id_skpd}`);
  } else {
    router.push('/');
  }
}

onMounted(() => {
  loadSubDetail();
});
</script>
