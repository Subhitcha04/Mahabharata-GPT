import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

const SUGGESTIONS = [
  "Who is Arjuna?",
  "Tell me about the Kurukshetra War",
  "What is Dharma in the Mahabharata?",
  "Who was Karna and why is he tragic?",
  "What happened during the game of dice?",
  "Explain the Bhagavad Gita's message",
  "Compare Duryodhana and Yudhishthira",
  "What weapons were used in the war?",
];

export default function ChatInput({ onSend, loading, showSuggestions }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [text]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!text.trim() || loading) return;
    onSend(text.trim());
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-ancient-100 bg-white/80 backdrop-blur-sm p-4">
      {/* Suggestions */}
      {showSuggestions && (
        <div className="mb-3 flex flex-wrap gap-2">
          {SUGGESTIONS.slice(0, 4).map((s, i) => (
            <button
              key={i}
              onClick={() => { setText(s); }}
              className="text-xs px-3 py-1.5 bg-temple-50 text-temple-700 rounded-full border border-temple-200 hover:bg-temple-100 hover:border-temple-300 transition-all"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-end gap-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about the Mahabharata..."
            rows={1}
            className="w-full resize-none rounded-xl border border-ancient-200 px-4 py-3 pr-12 text-sm focus:ring-2 focus:ring-temple-500 focus:border-temple-500 outline-none transition-all bg-ancient-50/50"
            disabled={loading}
          />
        </div>
        <button
          type="submit"
          disabled={!text.trim() || loading}
          className="w-11 h-11 rounded-xl bg-gradient-to-r from-temple-600 to-temple-700 text-white flex items-center justify-center hover:from-temple-700 hover:to-temple-800 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-temple-200/30 flex-shrink-0"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </button>
      </form>

      <p className="text-center text-xs text-ancient-400 mt-2">
        Powered by ChromaDB + Sentence Transformers | RAG Pipeline
      </p>
    </div>
  );
}
