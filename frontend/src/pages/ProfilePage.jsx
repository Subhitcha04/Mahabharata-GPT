import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProfile, getStats } from '../utils/api';
import { useAuth } from '../utils/AuthContext';
import {
  ArrowLeft, User, MessageSquare, Database, Brain,
  Calendar, Mail, Hash, Layers
} from 'lucide-react';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileRes, statsRes] = await Promise.all([getProfile(), getStats()]);
        setProfile(profileRes.data);
        setStats(statsRes.data);
      } catch (err) {
        console.error('Failed to load profile', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-ancient-50 flex items-center justify-center">
        <div className="flex gap-1.5">
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-ancient-50 to-temple-50">
      {/* Header */}
      <div className="bg-white border-b border-ancient-100">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <button onClick={() => navigate('/')} className="text-ancient-600 hover:text-temple-700 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="font-display text-xl font-bold text-temple-800">Profile</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* User Card */}
        <div className="bg-white rounded-2xl border border-ancient-100 shadow-sm overflow-hidden">
          <div className="h-24 bg-gradient-to-r from-temple-600 via-temple-700 to-saffron-600" />
          <div className="px-6 pb-6 -mt-8">
            <div className="w-16 h-16 rounded-xl bg-white border-4 border-white shadow-lg flex items-center justify-center bg-gradient-to-br from-temple-500 to-saffron-500">
              <User className="w-8 h-8 text-white" />
            </div>
            <div className="mt-3">
              <h2 className="font-display text-2xl font-bold text-temple-800">{profile?.username}</h2>
              <div className="flex items-center gap-4 mt-2 text-sm text-ancient-500">
                <span className="flex items-center gap-1.5"><Mail className="w-4 h-4" />{profile?.email}</span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  Joined {new Date(profile?.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { icon: MessageSquare, label: 'Conversations', value: profile?.total_conversations || 0, color: 'text-blue-600 bg-blue-50' },
            { icon: Hash, label: 'Messages', value: profile?.total_messages || 0, color: 'text-green-600 bg-green-50' },
            { icon: Database, label: 'Knowledge Vectors', value: stats?.total_documents || 0, color: 'text-purple-600 bg-purple-50' },
            { icon: Layers, label: 'Categories', value: stats?.categories?.length || 0, color: 'text-saffron-600 bg-saffron-50' },
          ].map((s, i) => (
            <div key={i} className="bg-white rounded-xl border border-ancient-100 p-4 shadow-sm">
              <div className={`w-10 h-10 rounded-lg ${s.color} flex items-center justify-center mb-3`}>
                <s.icon className="w-5 h-5" />
              </div>
              <p className="text-2xl font-bold text-ancient-800">{s.value.toLocaleString()}</p>
              <p className="text-xs text-ancient-500 mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>

        {/* System Info */}
        <div className="bg-white rounded-2xl border border-ancient-100 shadow-sm p-6">
          <h3 className="font-display text-lg font-bold text-temple-800 mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-temple-600" />
            System Architecture
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-ancient-500">Vector Database</span>
                <span className="font-medium text-ancient-800">{stats?.vector_db || 'ChromaDB'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-ancient-500">Embedding Model</span>
                <span className="font-medium text-ancient-800">{stats?.embedding_model || 'all-MiniLM-L6-v2'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-ancient-500">Backend</span>
                <span className="font-medium text-ancient-800">FastAPI + Python</span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-ancient-500">Frontend</span>
                <span className="font-medium text-ancient-800">React + Tailwind CSS</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-ancient-500">NLP Engine</span>
                <span className="font-medium text-ancient-800">spaCy + NLTK</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-ancient-500">Architecture</span>
                <span className="font-medium text-ancient-800">RAG (Retrieval-Augmented)</span>
              </div>
            </div>
          </div>

          {/* Categories */}
          {stats?.categories && (
            <div className="mt-4 pt-4 border-t border-ancient-100">
              <p className="text-xs font-medium text-ancient-500 mb-2 uppercase tracking-wider">Knowledge Categories</p>
              <div className="flex flex-wrap gap-2">
                {stats.categories.map((cat, i) => (
                  <span key={i} className="text-xs px-2.5 py-1 bg-temple-50 text-temple-700 rounded-full border border-temple-200">
                    {cat.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Logout */}
        <div className="text-center">
          <button
            onClick={() => { logout(); navigate('/auth'); }}
            className="px-6 py-2.5 bg-red-50 text-red-600 rounded-xl border border-red-200 hover:bg-red-100 transition-colors text-sm font-medium"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
