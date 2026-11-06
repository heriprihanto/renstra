<template>
  <div id="app">
    <!-- Executive Civic Navbar -->
    <HeaderNavbar
      :tahun-anggaran="2026"
      :is-backend-online="isBackendOnline"
    />

    <!-- Routed Views: OpdListView (/) or SubOpdTableView (/opd/:id) -->
    <div style="flex: 1; display: flex; flex-direction: column;">
      <router-view />
    </div>

    <!-- Civic Footer -->
    <footer class="civic-footer">
      <div class="app-container">
        <p>&copy; 2026 Pemerintah Kota Tegal &bull; Bappeda Kota Tegal &bull; Sistem Perencanaan Pembangunan Daerah (RENSTRA)</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from './services/api';
import HeaderNavbar from './components/HeaderNavbar.vue';

const isBackendOnline = ref(true);

async function checkConnection() {
  try {
    await api.checkHealth();
    isBackendOnline.value = true;
  } catch (err) {
    console.error('Koneksi backend gagal:', err);
    isBackendOnline.value = false;
  }
}

onMounted(() => {
  checkConnection();
});
</script>
