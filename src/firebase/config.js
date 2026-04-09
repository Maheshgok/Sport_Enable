// Firebase configuration for Moove MVP
// Video upload and analysis feature only

import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';
import { getAuth } from 'firebase/auth';

// Your web app's Firebase configuration
// Get these values from: https://console.firebase.google.com/project/watch-mail-trial/settings/general
const firebaseConfig = {
  apiKey: "YOUR_API_KEY", // Replace with your actual API key
  authDomain: "watch-mail-trial.firebaseapp.com",
  projectId: "watch-mail-trial",
  storageBucket: "watch-mail-trial.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize services (only for video analysis feature)
export const db = getFirestore(app);
export const storage = getStorage(app);
export const auth = getAuth(app);

export default app;
