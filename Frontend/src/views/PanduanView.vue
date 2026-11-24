<template>
  <div class="panduan-view-wrapper">
    <div class="panduan-topbar">
      <div class="app-container topbar-content">
        <div class="topbar-left">
          <router-link to="/" class="btn-back">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span>Kembali ke Data RENSTRA</span>
          </router-link>
          <div class="topbar-divider"></div>
          <div class="topbar-title-group">
            <div class="guide-icon-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
            </div>
            <span class="guide-title-text">Buku Panduan Pengguna &bull; RENSTRA 2025–2029</span>
          </div>
        </div>

        <div class="topbar-right">
          <a
            :href="panduanUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-action-guide btn-tab-bar"
            title="Buka Buku Panduan di tab baru atau layar penuh"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            <span>Buka Tab Baru</span>
          </a>

          <button
            type="button"
            class="btn-action-guide btn-print-bar"
            @click="printGuide"
            title="Cetak atau simpan panduan sebagai dokumen PDF"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <polyline points="6 9 6 2 18 2 18 9"/>
              <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
              <rect x="6" y="14" width="12" height="8"/>
            </svg>
            <span>Cetak / PDF</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Iframe Container -->
    <div class="iframe-container">
      <iframe
        ref="iframeRef"
        :src="panduanUrl"
        class="panduan-iframe"
        title="Buku Panduan Pengguna Aplikasi RENSTRA Kota Tegal"
      ></iframe>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const iframeRef = ref(null);

const panduanUrl = computed(() => {
  const base = import.meta.env.BASE_URL || '/';
  const cleanBase = base.endsWith('/') ? base : base + '/';
  return `${cleanBase}panduan.html`;
});

function printGuide() {
  if (iframeRef.value && iframeRef.value.contentWindow) {
    iframeRef.value.contentWindow.print();
  } else {
    window.open(panduanUrl.value, '_blank');
  }
}
</script>

<style scoped>
.panduan-view-wrapper {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 65px);
  background: var(--bg-app);
}

.panduan-topbar {
  background: #ffffff;
  border-bottom: 1px solid var(--border-subtle);
  padding: 0.65rem 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.topbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  background: #f1f5f9;
  color: #334155;
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid #cbd5e1;
  transition: all 0.2s ease;
}

.btn-back:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.topbar-divider {
  width: 1px;
  height: 22px;
  background: #e2e8f0;
}

.topbar-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.guide-icon-badge {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: #ecfdf5;
  color: #059669;
  display: flex;
  align-items: center;
  justify-content: center;
}

.guide-title-text {
  font-size: 0.92rem;
  font-weight: 700;
  color: #0f172a;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.btn-action-guide {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.btn-tab-bar {
  background: #f8fafc;
  color: #1e293b;
  border-color: #cbd5e1;
}

.btn-tab-bar:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-print-bar {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.25);
}

.btn-print-bar:hover {
  background: linear-gradient(135deg, #047857 0%, #059669 100%);
}

.iframe-container {
  flex: 1;
  width: 100%;
  min-height: calc(100vh - 120px);
  position: relative;
}

.panduan-iframe {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 120px);
  border: none;
  display: block;
}
</style>
