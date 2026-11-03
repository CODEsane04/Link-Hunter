import React, { useState } from 'react';
import { 
  Lock, 
  Mail, 
  ArrowLeft, 
  Sparkles, 
  Eye, 
  EyeOff, 
  CheckCircle2, 
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  Loader2,
  Check,
  LogOut,
  Layers
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// Default Chrome Extension ID (can be configured in .env as VITE_EXTENSION_ID)
const DEFAULT_EXTENSION_ID = import.meta.env.VITE_EXTENSION_ID || '';

export default function Auth({ initialMode = 'login', onBackToHome, onAuthSuccess }) {
  const [mode, setMode] = useState(initialMode); // 'login' | 'signup'
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  
  // Extension ID state (for easy sync during development)
  const [extensionId, setExtensionId] = useState(
    localStorage.getItem('lh_extension_id') || DEFAULT_EXTENSION_ID
  );
  const [extensionSynced, setExtensionSynced] = useState(false);

  // Check if user is already logged in locally
  const [currentUserEmail, setCurrentUserEmail] = useState(
    localStorage.getItem('lh_user_email') || null
  );

  const isLogin = mode === 'login';

  // Helper to sync token with the Chrome Extension
  const syncWithExtension = (token, userEmail, extId) => {
    const targetId = extId || extensionId;
    if (window.chrome && chrome.runtime && targetId) {
      try {
        chrome.runtime.sendMessage(
          targetId,
          {
            action: 'SAVE_AUTH_TOKEN',
            token: token,
            email: userEmail
          },
          (response) => {
            if (chrome.runtime.lastError) {
              console.warn('Could not contact Chrome Extension directly:', chrome.runtime.lastError.message);
              setExtensionSynced(false);
            } else if (response && response.success) {
              console.log('Successfully synced token to Chrome Extension!');
              setExtensionSynced(true);
            }
          }
        );
      } catch (err) {
        console.warn('Extension sync error:', err);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!email || !password) {
      setErrorMsg('Please enter both email and password.');
      return;
    }

    if (password.length < 6) {
      setErrorMsg('Password must be at least 6 characters.');
      return;
    }

    setLoading(true);

    try {
      if (mode === 'signup') {
        // 1. Sign up request
        const signupRes = await fetch(`${API_BASE_URL}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const signupData = await signupRes.json();

        if (!signupRes.ok) {
          throw new Error(signupData.detail || 'Failed to create account.');
        }

        // 2. Automatically log in right after sign up
        const loginRes = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const loginData = await loginRes.json();

        if (!loginRes.ok) {
          throw new Error(loginData.detail || 'Sign up succeeded, but automatic login failed.');
        }

        handleLoginSuccess(loginData.access_token, email);

      } else {
        // Login request
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || 'Invalid email or password.');
        }

        handleLoginSuccess(data.access_token, email);
      }
    } catch (err) {
      console.error('Authentication Error:', err);
      setErrorMsg(err.message || 'Something went wrong. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (token, userEmail) => {
    // 1. Save in Web App localStorage
    localStorage.setItem('lh_auth_token', token);
    localStorage.setItem('lh_user_email', userEmail);
    setCurrentUserEmail(userEmail);

    // 2. Sync to Chrome Extension
    syncWithExtension(token, userEmail, extensionId);

    if (onAuthSuccess) {
      onAuthSuccess({ token, email: userEmail });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('lh_auth_token');
    localStorage.removeItem('lh_user_email');
    setCurrentUserEmail(null);
    setExtensionSynced(false);

    // Notify extension to clear token if connected
    if (window.chrome && chrome.runtime && extensionId) {
      try {
        chrome.runtime.sendMessage(extensionId, { action: 'SAVE_AUTH_TOKEN', token: null });
      } catch (e) {}
    }
  };

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-stone-900 flex flex-col justify-between relative selection:bg-amber-200">
      
      {/* Background ambient decoration */}
      <div className="fixed inset-0 pointer-events-none bg-grid-pattern opacity-40 z-0"></div>
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] glow-ambient pointer-events-none z-0"></div>

      {/* Top Navbar Header */}
      <header className="relative z-10 max-w-7xl mx-auto w-full px-6 h-20 flex items-center justify-between">
        <button
          onClick={onBackToHome}
          className="inline-flex items-center space-x-2 text-sm font-semibold text-stone-600 hover:text-stone-950 px-3 py-1.5 rounded-xl hover:bg-stone-200/50 transition-all cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </button>

        <div className="flex items-center space-x-2 cursor-pointer" onClick={onBackToHome}>
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center text-white text-base shadow-sm">
            🧶
          </div>
          <span className="font-bold text-stone-900 tracking-tight text-lg">
            Link Hunter
          </span>
        </div>

        <div className="w-24 hidden sm:block"></div>
      </header>

      {/* Main Container */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">

          {/* If already logged in, show logged-in confirmation */}
          {currentUserEmail ? (
            <div className="bg-white/95 backdrop-blur-xl border border-stone-200/90 rounded-3xl p-8 sm:p-10 shadow-xl shadow-stone-200/60 text-center">
              <div className="w-16 h-16 bg-emerald-50 border border-emerald-200 rounded-3xl flex items-center justify-center text-emerald-600 mx-auto mb-5 shadow-sm">
                <CheckCircle2 className="w-8 h-8" />
              </div>

              <h2 className="text-2xl font-extrabold text-stone-900 tracking-tight">
                You're Signed In!
              </h2>
              <p className="text-stone-500 text-sm mt-2 mb-6">
                Logged in as <strong className="text-stone-800">{currentUserEmail}</strong>
              </p>

              {/* Extension Sync Status Banner */}
              <div className="bg-amber-50/70 border border-amber-200/80 rounded-2xl p-4 text-left text-xs text-stone-600 mb-6 space-y-2">
                <div className="flex items-center justify-between font-bold text-stone-800">
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-amber-600" />
                    Chrome Extension Sync
                  </span>
                  {extensionSynced ? (
                    <span className="text-emerald-700 bg-emerald-100/80 px-2 py-0.5 rounded-full font-semibold">
                      Connected
                    </span>
                  ) : (
                    <span className="text-stone-500 font-normal">Active</span>
                  )}
                </div>
                <p className="text-stone-500 text-[11px] leading-relaxed">
                  Right-click any craft image on Pinterest, Instagram, or blogs to search YouTube tutorials automatically!
                </p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={onBackToHome}
                  className="w-full inline-flex items-center justify-center space-x-2 bg-stone-900 hover:bg-stone-800 text-white font-bold text-sm py-3.5 rounded-xl shadow-md transition-all cursor-pointer"
                >
                  <span>Explore Crafts & Home</span>
                  <ArrowRight className="w-4 h-4" />
                </button>

                <button
                  onClick={handleLogout}
                  className="w-full inline-flex items-center justify-center space-x-2 bg-stone-100 hover:bg-stone-200 text-stone-700 font-semibold text-xs py-3 rounded-xl transition-all cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5 text-stone-500" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          ) : (
            /* Auth Form Card */
            <div className="bg-white/95 backdrop-blur-xl border border-stone-200/90 rounded-3xl p-8 sm:p-10 shadow-xl shadow-stone-200/60 transition-all">
              
              {/* Segmented Switcher (Sign In vs Create Account) */}
              <div className="grid grid-cols-2 p-1 bg-stone-100 rounded-2xl mb-8 border border-stone-200/70">
                <button
                  type="button"
                  onClick={() => { setMode('login'); setErrorMsg(''); }}
                  className={`py-2 text-xs sm:text-sm font-bold rounded-xl transition-all cursor-pointer ${
                    isLogin
                      ? 'bg-white text-stone-900 shadow-sm'
                      : 'text-stone-500 hover:text-stone-800'
                  }`}
                >
                  Sign In
                </button>
                <button
                  type="button"
                  onClick={() => { setMode('signup'); setErrorMsg(''); }}
                  className={`py-2 text-xs sm:text-sm font-bold rounded-xl transition-all cursor-pointer ${
                    !isLogin
                      ? 'bg-white text-stone-900 shadow-sm'
                      : 'text-stone-500 hover:text-stone-800'
                  }`}
                >
                  Create Account
                </button>
              </div>

              {/* Header Titles */}
              <div className="text-center mb-8">
                <h2 className="text-2xl sm:text-3xl font-extrabold text-stone-900 tracking-tight">
                  {isLogin ? 'Welcome back, maker' : 'Start discovering tutorials'}
                </h2>
                <p className="text-stone-500 text-sm mt-2 leading-relaxed">
                  {isLogin 
                    ? 'Sign in to access your craft history and saved tutorials.' 
                    : 'Join Link Hunter to sync your visual search history across devices.'}
                </p>
              </div>

              {/* Error Message Box */}
              {errorMsg && (
                <div className="mb-6 p-3.5 bg-rose-50 border border-rose-200 text-rose-700 rounded-2xl text-xs flex items-start space-x-2.5">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span className="font-medium leading-relaxed">{errorMsg}</span>
                </div>
              )}

              {/* The Form */}
              <form onSubmit={handleSubmit} className="space-y-5">
                
                {/* Email Field */}
                <div>
                  <label className="block text-xs font-bold text-stone-700 uppercase tracking-wider mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="maker@craftstudio.com"
                      className="w-full pl-10 pr-4 py-3 bg-[#FAF8F5]/80 border border-stone-200 rounded-xl text-sm text-stone-900 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-600 transition-all"
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-xs font-bold text-stone-700 uppercase tracking-wider">
                      Password
                    </label>
                  </div>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full pl-10 pr-10 py-3 bg-[#FAF8F5]/80 border border-stone-200 rounded-xl text-sm text-stone-900 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-600 transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-stone-400 hover:text-stone-600 cursor-pointer"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {!isLogin && (
                    <p className="text-[11px] text-stone-400 mt-1.5 flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5 text-stone-400" />
                      Must be at least 6 characters long
                    </p>
                  )}
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center space-x-2 bg-stone-900 hover:bg-stone-800 disabled:bg-stone-600 text-white font-bold text-sm py-3.5 rounded-xl shadow-lg shadow-stone-900/10 hover:shadow-xl transition-all hover:-translate-y-0.5 active:translate-y-0 mt-2 cursor-pointer"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <span>{isLogin ? 'Sign In to Link Hunter' : 'Create Your Free Account'}</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>

              </form>

              {/* Bottom Toggle Note */}
              <div className="mt-8 text-center text-xs text-stone-500">
                {isLogin ? (
                  <p>
                    Don't have an account yet?{' '}
                    <button
                      type="button"
                      onClick={() => { setMode('signup'); setErrorMsg(''); }}
                      className="font-bold text-amber-700 hover:text-amber-800 hover:underline cursor-pointer"
                    >
                      Sign up for free
                    </button>
                  </p>
                ) : (
                  <p>
                    Already have an account?{' '}
                    <button
                      type="button"
                      onClick={() => { setMode('login'); setErrorMsg(''); }}
                      className="font-bold text-amber-700 hover:text-amber-800 hover:underline cursor-pointer"
                    >
                      Sign in here
                    </button>
                  </p>
                )}
              </div>

            </div>
          )}

          {/* Privacy Note */}
          <p className="text-center text-[11px] text-stone-400 mt-6 flex items-center justify-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-stone-400" />
            <span>End-to-end encrypted with bcrypt & JSON Web Tokens</span>
          </p>

        </div>
      </main>

      {/* Footer copyright */}
      <footer className="relative z-10 py-6 text-center text-xs text-stone-400 border-t border-stone-200/50">
        © {new Date().getFullYear()} Link Hunter. Built for Makers & Crafters worldwide.
      </footer>

    </div>
  );
}
