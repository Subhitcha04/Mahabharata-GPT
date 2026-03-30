import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ThumbsUp, ThumbsDown, BookOpen, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { submitFeedback } from '../utils/api';

function ConfidenceBadge({ confidence }) {
  const styles = {
    high: 'bg-green-100 text-green-700 border-green-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-red-100 text-red-700 border-red-200',
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border ${styles[confidence] || styles.low}`}>
      {confidence} confidence
    </span>
  );
}

function CategoryTag({ category }) {
  if (!category || category === 'General') return null;
  return (
    <span className="text-xs px-2 py-0.5 rounded-full bg-temple-100 text-temple-700 border border-temple-200">
      {category.replace(/([A-Z])/g, ' $1').trim()}
    </span>
  );
}

function SourcesList({ sources }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  let parsedSources = sources;
  if (typeof sources === 'string') {
    try { parsedSources = JSON.parse(sources); } catch { return null; }
  }
  if (parsedSources.length === 0) return null;

  return (
    <div className="mt-3 border-t border-ancient-100 pt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs text-ancient-500 hover:text-temple-600 transition-colors"
      >
        <BookOpen className="w-3 h-3" />
        <span>{parsedSources.length} source{parsedSources.length > 1 ? 's' : ''} referenced</span>
        {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>
      {expanded && (
        <div className="mt-2 space-y-1.5">
          {parsedSources.map((src, i) => (
            <div key={i} className="flex items-center gap-2 text-xs text-ancient-600 bg-ancient-50 rounded-md px-2.5 py-1.5">
              <span className="w-4 h-4 rounded bg-temple-100 text-temple-600 flex items-center justify-center flex-shrink-0 text-[10px] font-bold">
                {i + 1}
              </span>
              <span className="truncate flex-1">{src.text || src.category}</span>
              <span className="text-ancient-400 flex-shrink-0">{Math.round((src.similarity || 0) * 100)}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ChatMessage({ message, isLatest }) {
  const [feedback, setFeedback] = useState(null);
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleFeedback = async (isHelpful) => {
    setFeedback(isHelpful);
    try {
      await submitFeedback(message.id, isHelpful);
    } catch (err) {
      console.error('Feedback failed', err);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} ${isLatest ? 'animate-fade-in-up' : ''}`}>
      <div className={`max-w-[85%] md:max-w-[75%] ${isUser ? 'order-1' : 'order-1'}`}>
        {/* Avatar + Name */}
        <div className={`flex items-center gap-2 mb-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          {!isUser && (
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-temple-600 to-saffron-600 flex items-center justify-center">
              <BookOpen className="w-3 h-3 text-white" />
            </div>
          )}
          <span className="text-xs font-medium text-ancient-500">
            {isUser ? 'You' : 'Mahabharata Agent'}
          </span>
          {!isUser && message.confidence && <ConfidenceBadge confidence={message.confidence} />}
          {!isUser && message.category && <CategoryTag category={message.category} />}
        </div>

        {/* Message bubble */}
        <div className={`rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-gradient-to-r from-temple-600 to-temple-700 text-white rounded-tr-md'
            : 'bg-white border border-ancient-100 text-ancient-800 rounded-tl-md shadow-sm'
        }`}>
          <div className="message-content text-sm leading-relaxed">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {!isUser && <SourcesList sources={message.sources} />}
        </div>

        {/* Actions for assistant messages */}
        {!isUser && (
          <div className="flex items-center gap-2 mt-1.5 ml-1">
            <button
              onClick={handleCopy}
              className="text-ancient-400 hover:text-ancient-600 transition-colors p-1"
              title="Copy"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={() => handleFeedback(true)}
              className={`p-1 transition-colors ${feedback === true ? 'text-green-500' : 'text-ancient-400 hover:text-green-500'}`}
              title="Helpful"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => handleFeedback(false)}
              className={`p-1 transition-colors ${feedback === false ? 'text-red-500' : 'text-ancient-400 hover:text-red-500'}`}
              title="Not helpful"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
