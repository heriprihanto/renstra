<template>
  <header class="civic-navbar">
    <div class="app-container">
      <div class="nav-wrapper">
        <!-- Brand & Identity -->
        <div class="brand-section">
          <div class="brand-emblem">
            <!-- Shield / Building Civic Icon -->
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              <path d="m9 12 2 2 4-4"/>
            </svg>
          </div>
          <div class="brand-text">
            <h1>PEMERINTAH KOTA TEGAL</h1>
            <div class="sub-title">Sistem Informasi Perencanaan Pembangunan &bull; RENSTRA</div>
          </div>
        </div>

        <!-- Meta badges: Year, Connection Status -->
        <div class="nav-actions">
          <div class="badge-year">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span>2026</span>
          </div>

          
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  tahunAnggaran: {
    type: Number,
    default: 2026
  },
  isBackendOnline: {
    type: Boolean,
    default: true
  }
});
</script>
