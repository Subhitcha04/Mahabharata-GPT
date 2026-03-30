import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Don't redirect if already on auth page
      if (!window.location.pathname.includes('/auth')) {
        window.location.href = '/auth';
      }
    }
    return Promise.reject(err);
  }
);

// ─── Auth ──────────────────────────────────────
export const register = (username, email, password) =>
  api.post('/auth/register', { username, email, password });

export const login = (username, password) =>
  api.post('/auth/login', { username, password });

export const getProfile = () => api.get('/auth/profile');

// ─── Chat ──────────────────────────────────────
export const sendMessage = (query, conversationId = null) =>
  api.post('/chat', { query, conversation_id: conversationId });

export const guestChat = (query) =>
  api.post('/chat/guest', { query });

// ─── Conversations ─────────────────────────────
export const getConversations = () => api.get('/conversations');

export const getConversation = (id) => api.get(`/conversations/${id}`);

export const deleteConversation = (id) => api.delete(`/conversations/${id}`);

// ─── Feedback ──────────────────────────────────
export const submitFeedback = (messageId, isHelpful, comment = null) =>
  api.post('/feedback', { message_id: messageId, is_helpful: isHelpful, comment });

// ─── Stats ─────────────────────────────────────
export const getStats = () => api.get('/stats');

export const getHealth = () => api.get('/health');

export default api;
