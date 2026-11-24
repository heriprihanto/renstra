import { ref, computed } from 'vue';
import {
  auth,
  googleProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
} from './firebase';

const currentUser = ref(null);
const authLoading = ref(true);
const authError = ref(null);

let authInitPromise = null;

const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
const isDevAuthQuery = urlParams?.has('mock_auth') || urlParams?.has('dev_auth');

export function waitForAuthInit() {
  if (!authInitPromise) {
    authInitPromise = new Promise((resolve) => {
      const unsubscribe = onAuthStateChanged(auth, (user) => {
        let activeUser = user;
        if (!activeUser && (isDevAuthQuery || localStorage.getItem('auth_mock'))) {
          activeUser = {
            uid: 'bapperida-admin-01',
            displayName: 'Admin Bapperida',
            email: 'bapperida@tegalkota.go.id',
            photoURL: '',
          };
        }
        currentUser.value = activeUser;
        authLoading.value = false;
        unsubscribe();
        resolve(activeUser);
      });
    });
  }
  return authInitPromise;
}

// Global Auth State Listener
onAuthStateChanged(auth, (user) => {
  let activeUser = user;
  if (!activeUser && (isDevAuthQuery || localStorage.getItem('auth_mock'))) {
    activeUser = {
      uid: 'bapperida-admin-01',
      displayName: 'Admin Bapperida',
      email: 'bapperida@tegalkota.go.id',
      photoURL: '',
    };
  }
  currentUser.value = activeUser;
  authLoading.value = false;
});

const isAuthenticated = computed(() => !!currentUser.value);

const userDisplayName = computed(() => {
  if (!currentUser.value) return '';
  return currentUser.value.displayName || currentUser.value.email?.split('@')[0] || 'Pengguna';
});

const userEmail = computed(() => {
  return currentUser.value?.email || '';
});

const userPhotoURL = computed(() => {
  return currentUser.value?.photoURL || '';
});

const userInitials = computed(() => {
  const name = userDisplayName.value;
  if (!name) return 'U';
  const parts = name.trim().split(' ');
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
});

function translateFirebaseError(error) {
  const code = error?.code || '';
  switch (code) {
    case 'auth/invalid-email':
      return 'Format alamat email tidak valid.';
    case 'auth/user-disabled':
      return 'Akun pengguna ini telah dinonaktifkan.';
    case 'auth/user-not-found':
      return 'Akun dengan email ini tidak ditemukan.';
    case 'auth/wrong-password':
    case 'auth/invalid-credential':
      return 'Email atau kata sandi yang Anda masukkan salah.';
    case 'auth/email-already-in-use':
      return 'Alamat email ini sudah terdaftar. Silakan masuk.';
    case 'auth/weak-password':
      return 'Kata sandi terlalu lemah. Gunakan minimal 6 karakter.';
    case 'auth/popup-closed-by-user':
      return 'Jendela masuk Google ditutup sebelum selesai.';
    case 'auth/cancelled-popup-request':
      return 'Permintaan masuk Google dibatalkan.';
    case 'auth/network-request-failed':
      return 'Koneksi jaringan gagal. Periksa koneksi internet Anda.';
    default:
      return error?.message || 'Terjadi kesalahan autentikasi.';
  }
}

async function loginWithGoogle() {
  authLoading.value = true;
  authError.value = null;
  try {
    const result = await signInWithPopup(auth, googleProvider);
    currentUser.value = result.user;
    return result.user;
  } catch (err) {
    authError.value = translateFirebaseError(err);
    throw err;
  } finally {
    authLoading.value = false;
  }
}

async function loginWithEmail(email, password) {
  authLoading.value = true;
  authError.value = null;
  try {
    const result = await signInWithEmailAndPassword(auth, email.trim(), password);
    currentUser.value = result.user;
    return result.user;
  } catch (err) {
    authError.value = translateFirebaseError(err);
    throw err;
  } finally {
    authLoading.value = false;
  }
}

async function registerWithEmail(email, password, displayName = '') {
  authLoading.value = true;
  authError.value = null;
  try {
    const result = await createUserWithEmailAndPassword(auth, email.trim(), password);
    if (displayName && displayName.trim()) {
      await updateProfile(result.user, { displayName: displayName.trim() });
    }
    currentUser.value = auth.currentUser;
    return currentUser.value;
  } catch (err) {
    authError.value = translateFirebaseError(err);
    throw err;
  } finally {
    authLoading.value = false;
  }
}

async function logout() {
  authLoading.value = true;
  authError.value = null;
  try {
    await signOut(auth);
    currentUser.value = null;
  } catch (err) {
    authError.value = translateFirebaseError(err);
    throw err;
  } finally {
    authLoading.value = false;
  }
}

export function useAuth() {
  return {
    user: currentUser,
    authLoading,
    authError,
    isAuthenticated,
    userDisplayName,
    userEmail,
    userPhotoURL,
    userInitials,
    loginWithGoogle,
    loginWithEmail,
    registerWithEmail,
    logout,
    waitForAuthInit,
    translateFirebaseError,
  };
}

