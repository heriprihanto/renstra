<template>
  <div class="stats-grid">
    <!-- Total OPD -->
    <div class="stat-card">
      <div class="stat-icon-wrapper">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 21h18"/>
          <path d="M5 21V7l8-4v18"/>
          <path d="M19 21V11l-6-4"/>
          <path d="M9 9h1"/>
          <path d="M9 13h1"/>
          <path d="M9 17h1"/>
        </svg>
      </div>
      <div class="stat-info">
        <span class="stat-label">Total SKPD (OPD)</span>
        <span class="stat-value">{{ stats.total_opd ?? '-' }}</span>
        <span class="stat-desc">Perangkat Daerah Kota Tegal</span>
      </div>
    </div>

    <!-- Total Sub SKPD -->
    <div class="stat-card teal">
      <div class="stat-icon-wrapper">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
          <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
        </svg>
      </div>
      <div class="stat-info">
        <span class="stat-label">Total Sub SKPD</span>
        <span class="stat-value">{{ stats.total_sub_pd ?? '-' }}</span>
        <span class="stat-desc">Unit Kerja & UPT Pelaksana</span>
      </div>
    </div>

    <!-- SKPD dengan Sub-Unit -->
    <div class="stat-card emerald">
      <div class="stat-icon-wrapper">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      </div>
      <div class="stat-info">
        <span class="stat-label">SKPD Ber-Sub Unit</span>
        <span class="stat-value">{{ stats.opd_with_sub ?? '-' }}</span>
        <span class="stat-desc">Memiliki UPT / Sekolah / Puskesmas</span>
      </div>
    </div>

    <!-- SKPD Tunggal -->
    <div class="stat-card amber">
      <div class="stat-icon-wrapper">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
        </svg>
      </div>
      <div class="stat-info">
        <span class="stat-label">SKPD Tunggal</span>
        <span class="stat-value">{{ stats.opd_without_sub ?? '-' }}</span>
        <span class="stat-desc">Badan / Dinas / Bagian Setda</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    default: () => ({})
  }
});
</script>
