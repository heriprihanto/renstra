<template>
  <div class="login-page-container">
    <div class="login-card">
      <!-- Civic Brand Header -->
      <div class="login-brand-header">
        <div class="brand-emblem-badge">
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="m9 12 2 2 4-4"/>
          </svg>
        </div>
        <h2 class="civic-title">PEMERINTAH KOTA TEGAL</h2>
        <div class="civic-subtitle">Sistem Informasi Perencanaan Pembangunan Daerah</div>
        <div class="civic-app-badge">
          <span>RENSTRA 2025 - 2029</span>
          <span class="badge-dot">&bull;</span>
          <span>TAHUN 2026</span>
        </div>
      </div>

      <!-- Security / Auth Notice Banner -->
      <div class="auth-notice-banner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
        <span>Anda harus login.</span>
      </div>

      <!-- Auth Body: Google Login Only -->
      <div class="login-card-body">
        <div class="login-intro-text">
          <p>
            Masuk dengan akun Google Anda
          </p>
        </div>

        <!-- Alert Error Message -->
        <div v-if="errorMessage" class="error-banner">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Primary Google Sign-In Button -->
        <button
          type="button"
          class="btn-google-login-primary"
          @click="handleGoogleSignIn"
          :disabled="authLoading"
        >
          <span v-if="authLoading" class="spinner-google"></span>
          <svg v-else class="google-svg" width="22" height="22" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
          </svg>
          <span class="btn-text">
            {{ authLoading ? 'Memproses Masuk...' : 'Masuk dengan Akun Google' }}
          </span>
        </button>

        <div class="security-guarantee-note">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuth, waitForAuthInit } from '../services/auth';

const router = useRouter();
const route = useRoute();

const {
  isAuthenticated,
  authLoading,
  loginWithGoogle,
  translateFirebaseError,
} = useAuth();

const errorMessage = ref('');

function redirectAfterLogin() {
  const target = route.query.redirect || '/';
  router.replace(target);
}

async function handleGoogleSignIn() {
  errorMessage.value = '';
  try {
    await loginWithGoogle();
    redirectAfterLogin();
  } catch (err) {
    errorMessage.value = translateFirebaseError(err);
  }
}

onMounted(async () => {
  await waitForAuthInit();
  if (isAuthenticated.value) {
    redirectAfterLogin();
  }
});
</script>

<style scoped>
.login-page-container {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  background: radial-gradient(circle at 50% 25%, #eff6ff 0%, #f1f5f9 60%, #e2e8f0 100%);
}

.login-card {
  width: 100%;
  max-width: 440px;
  background: #ffffff;
  border-radius: 18px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.09), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
  overflow: hidden;
  animation: cardEntrance 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-brand-header {
  padding: 2.2rem 2rem 1.6rem 2rem;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  text-align: center;
  border-bottom: 1px solid #f1f5f9;
}

.brand-emblem-badge {
  width: 62px;
  height: 62px;
  margin: 0 auto 1rem auto;
  border-radius: 16px;
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.35);
}

.civic-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: 0.04em;
  margin: 0;
}

.civic-subtitle {
  font-size: 0.82rem;
  color: #64748b;
  margin-top: 0.3rem;
  font-weight: 500;
}

.civic-app-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 1rem;
  padding: 0.3rem 0.85rem;
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  border-radius: 9999px;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.badge-dot {
  font-size: 0.85rem;
  color: #60a5fa;
}

.auth-notice-banner {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.8rem 1.5rem;
  background: #fffbeb;
  border-top: 1px solid #fde68a;
  border-bottom: 1px solid #fde68a;
  color: #92400e;
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.35;
}

.login-card-body {
  padding: 2rem 2rem 2.2rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.login-intro-text p {
  margin: 0;
  font-size: 0.86rem;
  color: #475569;
  line-height: 1.5;
  text-align: center;
}

.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  line-height: 1.4;
}

.btn-google-login-primary {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
  background: #ffffff;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  padding: 0.85rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease-in-out;
}

.btn-google-login-primary:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #94a3b8;
  color: #0f172a;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.btn-google-login-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-google-login-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-text {
  letter-spacing: 0.01em;
}

.spinner-google {
  width: 20px;
  height: 20px;
  border: 2px solid #cbd5e1;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.security-guarantee-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  font-size: 0.74rem;
  color: #64748b;
  text-align: center;
  margin-top: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes cardEntrance {
  from { opacity: 0; transform: scale(0.96) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
