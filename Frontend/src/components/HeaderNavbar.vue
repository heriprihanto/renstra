<template>
  <header class="civic-navbar">
    <div class="app-container">
      <div class="nav-wrapper">
        <!-- Brand & Identity -->
        <router-link to="/" class="brand-section-link">
          <div class="brand-section">
            <div class="brand-emblem">
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
        </router-link>

        <!-- Navigation Menu (Hanya tampil setelah pengguna terautentikasi) -->
        <nav v-if="isAuthenticated" class="nav-menu-center">
          <router-link to="/" class="nav-menu-item" :class="{ active: route.path === '/' }">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <rect x="3" y="3" width="7" height="7"/>
              <rect x="14" y="3" width="7" height="7"/>
              <rect x="14" y="14" width="7" height="7"/>
              <rect x="3" y="14" width="7" height="7"/>
            </svg>
            <span>Data RENSTRA</span>
          </router-link>

          
          <!-- Dropdown Menu Laporan -->
          <div class="nav-dropdown-wrap" ref="dropdownRef">
            <button
              type="button"
              class="nav-menu-item nav-dropdown-btn"
              :class="{ active: isReportActive, open: isDropdownOpen }"
              @click="toggleDropdown"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              <span>Laporan</span>
              <svg
                class="chevron-icon"
                :class="{ rotated: isDropdownOpen }"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>

            <!-- Dropdown Menu List -->
            <div v-if="isDropdownOpen" class="nav-dropdown-card">
              <div class="dropdown-header">
                Pilih Dokumen Laporan RENSTRA:
              </div>

              <!-- 1. Tujuan dan Sasaran (ACTIVE) -->
              <router-link
                to="/laporan/tujuan-sasaran"
                class="dropdown-item-link"
                :class="{ active: route.path.startsWith('/laporan/tujuan-sasaran') }"
                @click="closeDropdown"
              >
                <div class="dropdown-item-icon active-icon">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
                <div class="dropdown-item-content">
                  <div class="dropdown-item-title">1. Tujuan dan Sasaran</div>
                  <div class="dropdown-item-desc">Tabel 3.1 hierarki Tujuan, Sasaran & Indikator (Export Excel)</div>
                </div>
              </router-link>

              <!-- 2. Cascading Kinerja (Coming soon) -->
              <div class="dropdown-item-link disabled-item">
                <div class="dropdown-item-icon">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M6 3v18M18 3v18M3 12h18"/>
                  </svg>
                </div>
                <div class="dropdown-item-content">
                  <div class="dropdown-item-title-row">
                    <span class="dropdown-item-title">2. Cascading Kinerja</span>
                    <span class="badge-soon">Segera</span>
                  </div>
                  <div class="dropdown-item-desc">Pohon kinerja & penyelarasan program kegiatan</div>
                </div>
              </div>

              <!-- 3. Rencana Program, Kegiatan, Sub Kegiatan dan Pendanaan -->
              <router-link
                to="/laporan/program-kegiatan"
                class="dropdown-item-link"
                :class="{ active: route.path.startsWith('/laporan/program-kegiatan') }"
                @click="closeDropdown"
              >
                <div class="dropdown-item-icon active-icon">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="1" x2="12" y2="23"/>
                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                  </svg>
                </div>
                <div class="dropdown-item-content">
                  <div class="dropdown-item-title-row">
                    <span class="dropdown-item-title">3. Program, Kegiatan & Pendanaan</span>
                    
                  </div>
                  <div class="dropdown-item-desc">Tabel 4.1 Matriks target, subkegiatan dan pagu indikatif (Export Excel)</div>
                </div>
              </router-link>

              <!-- 4. Indikator Kinerja Utama -->
              <router-link
                to="/laporan/iku"
                class="dropdown-item-link"
                :class="{ active: route.path.startsWith('/laporan/iku') }"
                @click="closeDropdown"
              >
                <div class="dropdown-item-icon active-icon">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="8" r="7"/>
                    <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>
                  </svg>
                </div>
                <div class="dropdown-item-content">
                  <div class="dropdown-item-title-row">
                    <span class="dropdown-item-title">4. Indikator Kinerja Utama (IKU)</span>
                  </div>
                  <div class="dropdown-item-desc">Daftar ukuran keberhasilan strategis perangkat daerah</div>
                </div>
              </router-link>

              <!-- 5. Evaluasi Hasil Renstra -->
              <router-link
                to="/laporan/evaluasi-renstra"
                class="dropdown-item-link"
                :class="{ active: route.path.startsWith('/laporan/evaluasi-renstra') }"
                @click="closeDropdown"
              >
                <div class="dropdown-item-icon active-icon">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                  </svg>
                </div>
                <div class="dropdown-item-content">
                  <div class="dropdown-item-title-row">
                    <span class="dropdown-item-title">5. Evaluasi Hasil Renstra</span>
                  </div>
                  <div class="dropdown-item-desc">Formulir evaluasi capaian kinerja & anggaran Renstra (Export Excel)</div>
                </div>
              </router-link>

              <!-- 6. Daftar IKU Perangkat Daerah -->
              <router-link
                to="/laporan/daftar-iku"
                class="dropdown-item-link"
                :class="{ active: route.path.startsWith('/laporan/daftar-iku') }"
                @click="closeDropdown"
              >
                <div class="dropdown-item-icon active-icon">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <div class="dropdown-item-content">
                  <div class="dropdown-item-title-row">
                    <span class="dropdown-item-title">6. Daftar IKU Perangkat Daerah</span>
                  </div>
                  <div class="dropdown-item-desc">Matriks komparasi Target Murni & Target Perubahan IKU se-Kota Tegal (Export Excel)</div>
                </div>
              </router-link>

              <!-- 7. Pagu RPJMD vs Renstra -->
              <router-link
                to="/laporan/rpjmd-vs-renstra"
                class="dropdown-item-link"
                :class="{ active: route.path.startsWith('/laporan/rpjmd-vs-renstra') }"
                @click="closeDropdown"
              >
                <div class="dropdown-item-icon active-icon">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="20" x2="18" y2="10"/>
                    <line x1="12" y1="20" x2="12" y2="4"/>
                    <line x1="6" y1="20" x2="6" y2="14"/>
                  </svg>
                </div>
                <div class="dropdown-item-content">
                  <div class="dropdown-item-title-row">
                    <span class="dropdown-item-title">7. Pagu RPJMD vs Renstra</span>
                  </div>
                  <div class="dropdown-item-desc">Komparasi Pagu Murni, Perubahan vs RPJMD & deteksi selisih anggaran (Export Excel)</div>
                </div>
              </router-link>
            </div>
          </div>
        </nav>

        <!-- Meta badges: Year, Connection Status, Firebase Auth -->
        <div class="nav-actions">
          <!-- Tombol Akses Cepat Buku Panduan -->
          <router-link
            to="/panduan"
            class="btn-nav-guide-quick"
            :class="{ active: route.path.startsWith('/panduan') }"
            title="Buka Buku Panduan Pengguna RENSTRA"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            <span>Panduan</span>
          </router-link>

          <div class="badge-year">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span>{{ tahunAnggaran }}</span>
          </div>

          <!-- Firebase Auth Profile / Login Button -->
          <button
            v-if="!isAuthenticated"
            type="button"
            class="btn-nav-auth"
            @click="openAuthModal"
            title="Masuk dengan Firebase (Google / Email)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
              <polyline points="10 17 15 12 10 7"/>
              <line x1="15" y1="12" x2="3" y2="12"/>
            </svg>
            <span>Masuk</span>
          </button>

          <button
            v-else
            type="button"
            class="btn-nav-user"
            @click="openAuthModal"
            :title="`Masuk sebagai ${userDisplayName} (${userEmail}) - Klik untuk melihat profil`"
          >
            <img v-if="userPhotoURL" :src="userPhotoURL" class="user-avatar-mini" alt="User" />
            <div v-else class="user-initials-mini">{{ userInitials }}</div>
            <span class="user-name-text">{{ userDisplayName }}</span>
            <span class="dot-online-mini" title="Online"></span>
          </button>
        </div>
      </div>
    </div>

    <!-- Firebase Auth Modal Component -->
    <AuthModal :is-open="isAuthModalOpen" @close="closeAuthModal" />
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '../services/auth';
import AuthModal from './AuthModal.vue';

defineProps({
  tahunAnggaran: {
    type: Number,
    default: 2026,
  },
  isBackendOnline: {
    type: Boolean,
    default: true,
  },
});

const route = useRoute();
const isDropdownOpen = ref(false);
const dropdownRef = ref(null);

const {
  user,
  isAuthenticated,
  userDisplayName,
  userEmail,
  userPhotoURL,
  userInitials,
} = useAuth();

const isAuthModalOpen = ref(false);

function openAuthModal() {
  isAuthModalOpen.value = true;
}

function closeAuthModal() {
  isAuthModalOpen.value = false;
}

const isReportActive = computed(() => {
  return route.path.startsWith('/laporan');
});

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value;
}

function closeDropdown() {
  isDropdownOpen.value = false;
}

function handleOutsideClick(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    isDropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
});

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick);
});
</script>

<style scoped>
.brand-section-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
}

.nav-menu-center {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.nav-menu-item {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #e2e8f0;
  padding: 0.45rem 0.95rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-menu-item:hover {
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.25);
}

.nav-menu-item.active {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
}

.nav-dropdown-wrap {
  position: relative;
}

.nav-dropdown-btn .chevron-icon {
  transition: transform 0.2s ease;
}

.nav-dropdown-btn .chevron-icon.rotated {
  transform: rotate(180deg);
}

/* Dropdown Menu Card */
.nav-dropdown-card {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 380px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  box-shadow: 0 12px 30px -4px rgba(15, 23, 42, 0.25);
  padding: 0.6rem;
  z-index: 100;
  animation: dropFade 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes dropFade {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-header {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  padding: 0.4rem 0.6rem 0.35rem 0.6rem;
  letter-spacing: 0.03em;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 0.35rem;
}

.dropdown-item-link {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  text-decoration: none;
  color: #1e293b;
  transition: all 0.15s ease;
  margin-bottom: 0.2rem;
}

.dropdown-item-link:hover:not(.disabled-item) {
  background: #eff6ff;
  color: #1d4ed8;
}

.dropdown-item-link.active {
  background: #dbeafe;
  color: #1e40af;
}

.dropdown-item-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.dropdown-item-icon.active-icon {
  background: #2563eb;
  color: #ffffff;
}

.dropdown-item-content {
  flex: 1;
}

.dropdown-item-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.dropdown-item-title {
  font-size: 0.85rem;
  font-weight: 700;
  line-height: 1.3;
}

.dropdown-item-desc {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.15rem;
  line-height: 1.35;
}

.disabled-item {
  opacity: 0.55;
  cursor: not-allowed;
  user-select: none;
}

.badge-soon {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #cbd5e1;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.badge-active {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

/* Firebase Auth Buttons in Navbar */
.btn-nav-auth {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: #ffffff;
  color: #1e3a8a;
  border: 1px solid #cbd5e1;
  padding: 0.35rem 0.75rem;
  font-size: 0.78rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-nav-auth:hover {
  background: #f8fafc;
  border-color: #94a3b8;
  color: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.btn-nav-user {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 0.25rem 0.65rem 0.25rem 0.35rem;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  max-width: 170px;
}

.btn-nav-user:hover {
  background: #f8fafc;
  border-color: #94a3b8;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

.user-avatar-mini {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.user-initials-mini {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  color: #ffffff;
  font-size: 0.68rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-name-text {
  font-size: 0.78rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dot-online-mini {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #10b981;
  flex-shrink: 0;
}

.btn-nav-guide-quick {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
  padding: 0.32rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 600;
  border-radius: 6px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.btn-nav-guide-quick:hover,
.btn-nav-guide-quick.active {
  background: #059669;
  color: #ffffff;
  border-color: #10b981;
  box-shadow: 0 2px 6px rgba(5, 150, 105, 0.35);
  transform: translateY(-1px);
}
</style>
