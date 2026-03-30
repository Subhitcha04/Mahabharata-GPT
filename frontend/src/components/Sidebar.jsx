import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getConversations, deleteConversation } from '../utils/api';
import { useAuth } from '../utils/AuthContext';
import {
  MessageSquarePlus, Trash2, User, LogOut, BookOpen,
  ChevronLeft, Clock, Search
} from 'lucide-react';

export default function Sidebar({ currentConversationId, onNewChat, onSelectConversation, collapsed, onToggle }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchConversations = async () => {
    setLoading(true);
    try {
      const res = await getConversations();
      setConversations(res.data);
    } catch (err) {
      console.error('Failed to load conversations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchConversations(); }, [currentConversationId]);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!confirm('Delete this conversation?')) return;
    try {
      await deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
      if (id === currentConversationId) onNewChat();
    } catch (err) {
      console.error('Failed to delete', err);
    }
  };

  const filtered = conversations.filter(c =>
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now - d;
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
    return d.toLocaleDateString();
  };

  if (collapsed) {
    return (
      <div className="w-16 bg-temple-800 flex flex-col items-center py-4 gap-4">
        <button onClick={onToggle} className="w-10 h-10 rounded-xl bg-temple-700 flex items-center justify-center text-saffron-300 hover:bg-temple-600 transition-colors">
          <BookOpen className="w-5 h-5" />
        </button>
        <button onClick={onNewChat} className="w-10 h-10 rounded-xl bg-saffron-600 flex items-center justify-center text-white hover:bg-saffron-500 transition-colors">
          <MessageSquarePlus className="w-5 h-5" />
        </button>
        <div className="flex-1" />
        <button onClick={() => navigate('/profile')} className="w-10 h-10 rounded-xl bg-temple-700 flex items-center justify-center text-temple-300 hover:bg-temple-600 transition-colors">
          <User className="w-5 h-5" />
        </button>
      </div>
    );
  }

  return (
    <div className="w-72 bg-temple-800 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-temple-700">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-saffron-400" />
            <span className="font-display font-bold text-white text-sm">Mahabharata AI</span>
          </div>
          <button onClick={onToggle} className="text-temple-400 hover:text-white transition-colors">
            <ChevronLeft className="w-5 h-5" />
          </button>
        </div>
        <button
          onClick={onNewChat}
          className="w-full py-2.5 bg-gradient-to-r from-saffron-600 to-temple-600 text-white rounded-xl text-sm font-medium hover:from-saffron-500 hover:to-temple-500 transition-all flex items-center justify-center gap-2"
        >
          <MessageSquarePlus className="w-4 h-4" />
          New Conversation
        </button>
      </div>

      {/* Search */}
      <div className="px-4 py-2">
        <div className="relative">
          <Search className="w-4 h-4 text-temple-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search chats..."
            className="w-full pl-9 pr-3 py-2 bg-temple-700/50 text-white placeholder-temple-500 rounded-lg text-sm border border-temple-600 focus:border-saffron-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2 py-1">
        {loading && conversations.length === 0 ? (
          <div className="text-center py-8 text-temple-500 text-sm">Loading...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-8 text-temple-500 text-sm">
            {search ? 'No matching conversations' : 'No conversations yet'}
          </div>
        ) : (
          filtered.map(conv => (
            <button
              key={conv.id}
              onClick={() => onSelectConversation(conv.id)}
              className={`w-full text-left px-3 py-2.5 rounded-lg mb-1 group transition-all ${
                conv.id === currentConversationId
                  ? 'bg-temple-600/50 text-white'
                  : 'text-temple-300 hover:bg-temple-700/50 hover:text-white'
              }`}
            >
              <div className="flex items-start justify-between">
                <p className="text-sm font-medium truncate flex-1 mr-2">{conv.title}</p>
                <button
                  onClick={(e) => handleDelete(e, conv.id)}
                  className="opacity-0 group-hover:opacity-100 text-temple-500 hover:text-red-400 transition-all flex-shrink-0"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <Clock className="w-3 h-3 text-temple-500" />
                <span className="text-xs text-temple-500">{formatDate(conv.updated_at)}</span>
                <span className="text-xs text-temple-600">· {conv.message_count} msgs</span>
              </div>
            </button>
          ))
        )}
      </div>

      {/* User section */}
      <div className="p-4 border-t border-temple-700">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-saffron-600/20 flex items-center justify-center">
            <User className="w-4 h-4 text-saffron-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.username}</p>
          </div>
          <button onClick={() => navigate('/profile')} className="text-temple-400 hover:text-saffron-400 transition-colors" title="Profile">
            <User className="w-4 h-4" />
          </button>
          <button onClick={logout} className="text-temple-400 hover:text-red-400 transition-colors" title="Sign Out">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
