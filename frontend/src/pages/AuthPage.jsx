import { useState } from 'react';
import { useAuth } from '../utils/AuthContext';
import { login, register } from '../utils/api';
import { BookOpen, Shield, Sparkles, Eye, EyeOff } from 'lucide-react';

export default function AuthPage() {
  const { loginUser } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let res;
      if (isLogin) {
        res = await login(username, password);
      } else {
        if (!email) { setError('Email is required'); setLoading(false); return; }
        res = await register(username, email, password);
      }
      loginUser(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-ancient-50 via-temple-50 to-saffron-50 flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-temple-700 via-temple-800 to-temple-900 text-white flex-col justify-center items-center p-12 relative overflow-hidden">
        {/* Decorative pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-10 left-10 w-40 h-40 border-2 border-white rounded-full"></div>
          <div className="absolute top-20 left-20 w-40 h-40 border-2 border-white rounded-full"></div>
          <div className="absolute bottom-20 right-20 w-60 h-60 border-2 border-white rounded-full"></div>
          <div className="absolute bottom-10 right-10 w-60 h-60 border-2 border-white rounded-full"></div>
        </div>

        <div className="relative z-10 text-center max-w-md">
          <div className="w-20 h-20 bg-saffron-500/20 rounded-2xl flex items-center justify-center mx-auto mb-8 backdrop-blur-sm border border-saffron-400/30">
            <BookOpen className="w-10 h-10 text-saffron-300" />
          </div>
          <h1 className="font-display text-4xl font-bold mb-4">Mahabharata AI Agent</h1>
          <p className="text-temple-200 text-lg mb-8 leading-relaxed">
            Explore the world's greatest epic through an AI-powered knowledge agent. 
            Ask about characters, stories, battles, dharma, and the timeless wisdom of the Mahabharata.
          </p>

          <div className="space-y-4 text-left">
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-saffron-400 mt-0.5 flex-shrink-0" />
              <p className="text-temple-200 text-sm">Powered by Vector Database &amp; Semantic Search (RAG)</p>
            </div>
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-saffron-400 mt-0.5 flex-shrink-0" />
              <p className="text-temple-200 text-sm">200+ stories, characters, places, weapons &amp; themes indexed</p>
            </div>
            <div className="flex items-start gap-3">
              <BookOpen className="w-5 h-5 text-saffron-400 mt-0.5 flex-shrink-0" />
              <p className="text-temple-200 text-sm">Full conversation history with source citations</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile branding */}
          <div className="lg:hidden text-center mb-8">
            <div className="w-14 h-14 bg-temple-700 rounded-xl flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-7 h-7 text-saffron-300" />
            </div>
            <h1 className="font-display text-2xl font-bold text-temple-800">Mahabharata AI Agent</h1>
          </div>

          <div className="bg-white rounded-2xl shadow-xl shadow-temple-200/50 p-8 border border-ancient-100">
            <h2 className="font-display text-2xl font-bold text-temple-800 mb-1">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className="text-ancient-500 mb-6 text-sm">
              {isLogin ? 'Sign in to continue your journey' : 'Begin your exploration of the epic'}
            </p>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-ancient-700 mb-1">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="w-full px-4 py-2.5 border border-ancient-200 rounded-xl focus:ring-2 focus:ring-temple-500 focus:border-temple-500 outline-none transition-all bg-ancient-50/50"
                  placeholder="Enter your username"
                />
              </div>

              {!isLogin && (
                <div>
                  <label className="block text-sm font-medium text-ancient-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 border border-ancient-200 rounded-xl focus:ring-2 focus:ring-temple-500 focus:border-temple-500 outline-none transition-all bg-ancient-50/50"
                    placeholder="Enter your email"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-ancient-700 mb-1">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 border border-ancient-200 rounded-xl focus:ring-2 focus:ring-temple-500 focus:border-temple-500 outline-none transition-all bg-ancient-50/50 pr-10"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-ancient-400 hover:text-ancient-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-gradient-to-r from-temple-600 to-temple-700 text-white rounded-xl font-medium hover:from-temple-700 hover:to-temple-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-temple-300/30"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="typing-dot" style={{width: 6, height: 6}}></span>
                    <span className="typing-dot" style={{width: 6, height: 6}}></span>
                    <span className="typing-dot" style={{width: 6, height: 6}}></span>
                  </span>
                ) : isLogin ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={() => { setIsLogin(!isLogin); setError(''); }}
                className="text-temple-600 hover:text-temple-800 text-sm font-medium transition-colors"
              >
                {isLogin ? "Don't have an account? Sign Up" : 'Already have an account? Sign In'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
