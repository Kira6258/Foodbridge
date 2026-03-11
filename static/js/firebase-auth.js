import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDjSmsXw1QHCeOHGAQJvA62ZQOkZxHx2pY",
    authDomain: "my-app-f9d15.firebaseapp.com",
    projectId: "my-app-f9d15",
    storageBucket: "my-app-f9d15.firebasestorage.app",
    messagingSenderId: "643375851931",
    appId: "1:643375851931:web:79bd6f69e0eb7c5a56993e",
    measurementId: "G-K5ML7GX6QV"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Make auth available globally for other scripts
window.auth = auth;

console.log("Firebase Auth Initialized for domain:", window.location.hostname);
if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
    console.warn("WARNING: You are using a domain that might not be authorized in Firebase Console:", window.location.hostname);
}
