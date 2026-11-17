import { initializeApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
} from 'firebase/auth';
import { getAnalytics, isSupported } from 'firebase/analytics';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBxXh_5GVr202cIek4rSaT0j_Mfhh1mJO8",
  authDomain: "renstra-f461b.firebaseapp.com",
  projectId: "renstra-f461b",
  storageBucket: "renstra-f461b.firebasestorage.app",
  messagingSenderId: "354865830019",
  appId: "1:354865830019:web:51d6c20f1b6786950da3b6",
  measurementId: "G-2E193G1QF7"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

// Initialize Analytics conditionally (only in supported browser environments)
let analytics = null;
if (typeof window !== 'undefined') {
  isSupported().then((supported) => {
    if (supported) {
      analytics = getAnalytics(app);
    }
  }).catch(() => {});
}

export {
  app,
  auth,
  googleProvider,
  analytics,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
};

