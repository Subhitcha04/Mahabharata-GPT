import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { sendMessage, getConversation } from '../utils/api';
import Sidebar from '../components/Sidebar';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import WelcomeScreen from '../components/WelcomeScreen';
import { Menu } from 'lucide-react';

export default function ChatPage() {
  const { conversationId: paramConvId } = useParams();
  const navigate = useNavigate();

  const [conversationId, setConversationId] = useState(paramConvId || null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const messagesEndRef = useRef(null);

  // Load existing conversation
  useEffect(() => {
    if (paramConvId) {
      setConversationId(paramConvId);
      loadConversation(paramConvId);
    }
  }, [paramConvId]);

  const loadConversation = async (id) => {
    try {
      const res = await getConversation(id);
      setMessages(res.data.messages);
    } catch (err) {
      console.error('Failed to load conversation', err);
      navigate('/');
    }
  };

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (query) => {
    // Add user message immediately
    const userMsg = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content: query,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await sendMessage(query, conversationId);
      const data = res.data;

      // Update conversation ID if this was a new conversation
      if (!conversationId) {
        setConversationId(data.conversation_id);
        navigate(`/chat/${data.conversation_id}`, { replace: true });
      }

      // Add assistant message
      const assistantMsg = {
        id: data.message_id,
        role: 'assistant',
        content: data.answer,
        sources: JSON.stringify(data.sources),
        confidence: data.confidence,
        category: data.category,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Chat error', err);
      const errorMsg = {
        id: 'error-' + Date.now(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your query. Please try again.',
        confidence: 'low',
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setConversationId(null);
    setMessages([]);
    navigate('/');
  };

  const handleSelectConversation = (id) => {
    setMobileMenuOpen(false);
    navigate(`/chat/${id}`);
  };

  return (
    <div className="h-screen flex bg-ancient-50">
      {/* Desktop Sidebar */}
      <div className="hidden md:block">
        <Sidebar
          currentConversationId={conversationId}
          onNewChat={handleNewChat}
          onSelectConversation={handleSelectConversation}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div className="w-72">
            <Sidebar
              currentConversationId={conversationId}
              onNewChat={() => { handleNewChat(); setMobileMenuOpen(false); }}
              onSelectConversation={handleSelectConversation}
              collapsed={false}
              onToggle={() => setMobileMenuOpen(false)}
            />
          </div>
          <div className="flex-1 bg-black/30" onClick={() => setMobileMenuOpen(false)} />
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar (mobile) */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 border-b border-ancient-100 bg-white/80 backdrop-blur-sm">
          <button onClick={() => setMobileMenuOpen(true)} className="text-ancient-600">
            <Menu className="w-5 h-5" />
          </button>
          <span className="font-display font-bold text-temple-800 text-sm">Mahabharata AI Agent</span>
        </div>

        {/* Messages area */}
        {messages.length === 0 ? (
          <WelcomeScreen onSuggestionClick={handleSend} />
        ) : (
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
            {messages.map((msg, i) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                isLatest={i === messages.length - 1}
              />
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="flex justify-start animate-fade-in-up">
                <div className="bg-white border border-ancient-100 rounded-2xl rounded-tl-md px-5 py-4 shadow-sm">
                  <div className="flex gap-1.5">
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input */}
        <ChatInput
          onSend={handleSend}
          loading={loading}
          showSuggestions={messages.length === 0}
        />
      </div>
    </div>
  );
}
