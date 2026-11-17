<template>
  <div v-if="isOpen" class="auth-modal-backdrop" @click.self="closeModal">
    <div class="auth-modal-card">
      <!-- Modal Header -->
      <div class="auth-modal-header">
        <div class="header-branding">
          <div class="firebase-logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M4.5 19.5L12 2L15 8L10 13L4.5 19.5Z" fill="#FFA000"/>
              <path d="M12 2L19.5 19.5L10 13L15 8L12 2Z" fill="#F57C00"/>
              <path d="M4.5 19.5L19.5 19.5L12 22L4.5 19.5Z" fill="#FFCA28"/>
            </svg>
          </div>
          <div>
            <h3 class="auth-modal-title">
              {{ isAuthenticated ? 'Profil Pengguna' : 'Masuk ke Sistem' }}
            </h3>
            <p class="auth-modal-subtitle">
              Autentikasi Firebase &bull; RENSTRA Kota Tegal
            </p>
          </div>
        </div>
        <button class="btn-close-modal" @click="closeModal" title="Tutup">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- User is Authenticated State -->
      <div v-if="isAuthenticated" class="auth-modal-body">
        <div class="user-profile-box">
          <div class="profile-avatar-large">
            <img v-if="userPhotoURL" :src="userPhotoURL" :alt="userDisplayName" class="avatar-img-large" />
            <div v-else class="avatar-initials-large">{{ userInitials }}</div>
          </div>
          <div class="profile-info-content">
            <h4 class="profile-name">{{ userDisplayName }}</h4>
            <div class="profile-email">{{ userEmail }}</div>
            <div class="profile-meta-tags">
              <span class="badge-status-online">
                <span class="dot-online"></span>
                Terautentikasi
              </span>
              <span class="badge-provider">
                <svg width="12" height="12" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
                Google Sign-In
              </span>
            </div>
          </div>
        </div>

        <div class="user-details-list">
          <div class="detail-row">
            <span class="detail-label">Firebase UID:</span>
            <code class="detail-value mono">{{ user?.uid }}</code>
          </div>
          <div class="detail-row" v-if="user?.metadata?.lastSignInTime">
            <span class="detail-label">Sesi Terakhir:</span>
            <span class="detail-value">{{ formatDate(user.metadata.lastSignInTime) }}</span>
          </div>
        </div>

        <div class="auth-modal-actions">
          <button class="btn-logout" @click="handleLogout" :disabled="authLoading">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            <span>Keluar dari Akun</span>
          </button>
          <button class="btn-cancel" @click="closeModal">Tutup</button>
        </div>
      </div>

      <!-- User is Not Authenticated State (Google Sign-In Only) -->
      <div v-else class="auth-modal-body">
        <div class="unauth-intro-box">
          <p class="intro-desc">
            Silakan masuk menggunakan akun Google Anda untuk membuka akses data Rencana Strategis Kota Tegal.
          </p>
        </div>

        <!-- Alert Error Banner -->
        <div v-if="localError || authError" class="auth-error-alert">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{{ localError || authError }}</span>
        </div>

        <!-- Google One-Click Sign In -->
        <button
          type="button"
          class="btn-google-auth"
          @click="handleGoogleSignIn"
          :disabled="authLoading"
        >
          <span v-if="authLoading" class="spinner-auth-google"></span>
          <svg v-else class="google-icon" width="20" height="20" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
          </svg>
          <span>{{ authLoading ? 'Menghubungkan ke Google...' : 'Masuk dengan Akun Google' }}</span>
        </button>

        <div class="security-note">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <span>Autentikasi resmi didukung oleh Google Firebase</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../services/auth';

const router = useRouter();

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close']);

const {
  user,
  authLoading,
  authError,
  isAuthenticated,
  userDisplayName,
  userEmail,
  userPhotoURL,
  userInitials,
  loginWithGoogle,
  logout,
  translateFirebaseError,
} = useAuth();

const localError = ref('');

const isGoogleUser = computed(() => {
  return user.value?.providerData?.some((p) => p.providerId === 'google.com') ?? true;
});

function closeModal() {
  localError.value = '';
  emit('close');
}

async function handleGoogleSignIn() {
  localError.value = '';
  try {
    await loginWithGoogle();
    closeModal();
  } catch (err) {
    localError.value = translateFirebaseError(err);
  }
}

async function handleLogout() {
  try {
    await logout();
    closeModal();
    if (router) {
      router.replace('/login');
    }
  } catch (err) {
    localError.value = translateFirebaseError(err);
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}
</script>

<style scoped>
.auth-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
  animation: fadeIn 0.15s ease-out;
}

.auth-modal-card {
  background: #ffffff;
  width: 100%;
  max-width: 440px;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  border: 1px solid #e2e8f0;
  animation: modalPop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.auth-modal-header {
  padding: 1.25rem 1.4rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-branding {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.firebase-logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.auth-modal-title {
  font-size: 1.02rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.25;
}

.auth-modal-subtitle {
  font-size: 0.73rem;
  color: #64748b;
  margin: 0.15rem 0 0 0;
}

.btn-close-modal {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.35rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.btn-close-modal:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.auth-modal-body {
  padding: 1.5rem;
}

.unauth-intro-box {
  margin-bottom: 1.25rem;
  text-align: center;
}

.intro-desc {
  font-size: 0.88rem;
  line-height: 1.5;
  color: #475569;
  margin: 0;
}

/* Google Auth Button */
.btn-google-auth {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  background: #ffffff;
  color: #1e293b;
  border: 1.5px solid #cbd5e1;
  padding: 0.75rem 1.2rem;
  font-size: 0.92rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-google-auth:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #94a3b8;
  color: #0f172a;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.btn-google-auth:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner-auth-google {
  width: 18px;
  height: 18px;
  border: 2px solid #cbd5e1;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* Security Note */
.security-note {
  margin-top: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: #64748b;
}

/* Error Alert */
.auth-error-alert {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  font-size: 0.82rem;
  margin-bottom: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* User Profile Box */
.user-profile-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 1.1rem;
}

.profile-avatar-large {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.avatar-img-large {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials-large {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}

.profile-info-content {
  flex: 1;
  min-width: 0;
}

.profile-name {
  font-size: 0.98rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-email {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0.15rem 0 0.5rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-meta-tags {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge-status-online {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.68rem;
  font-weight: 600;
  background: #ecfdf5;
  color: #047857;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  border: 1px solid #a7f3d0;
}

.dot-online {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

.badge-provider {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.68rem;
  font-weight: 600;
  background: #f1f5f9;
  color: #475569;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  border: 1px solid #cbd5e1;
}

.user-details-list {
  background: #ffffff;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.74rem;
}

.detail-label {
  color: #64748b;
}

.detail-value {
  color: #1e293b;
  font-weight: 500;
}

.detail-value.mono {
  font-family: monospace;
  font-size: 0.7rem;
  background: #f8fafc;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
}

.auth-modal-actions {
  display: flex;
  gap: 0.6rem;
}

.btn-logout {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  padding: 0.6rem;
  font-size: 0.82rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-logout:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #b91c1c;
}

.btn-cancel {
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
  padding: 0.6rem 1.1rem;
  font-size: 0.82rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-cancel:hover {
  background: #f1f5f9;
  color: #334155;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
