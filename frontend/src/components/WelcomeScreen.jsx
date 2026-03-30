import { BookOpen, Swords, MapPin, Scale, Sparkles, Database, Brain, Search } from 'lucide-react';

const TOPICS = [
  { icon: Swords, label: 'Characters', desc: 'Arjuna, Krishna, Bhishma, Draupadi...', color: 'from-red-500 to-orange-500' },
  { icon: BookOpen, label: 'Stories & Events', desc: 'The dice game, exile, war...', color: 'from-blue-500 to-indigo-500' },
  { icon: MapPin, label: 'Places', desc: 'Hastinapura, Indraprastha...', color: 'from-green-500 to-emerald-500' },
  { icon: Scale, label: 'Themes & Dharma', desc: 'Duty, karma, righteousness...', color: 'from-purple-500 to-violet-500' },
];

const TECH_FEATURES = [
  { icon: Database, label: 'ChromaDB', desc: 'Vector database for semantic search' },
  { icon: Brain, label: 'Sentence Transformers', desc: 'Neural text embeddings' },
  { icon: Search, label: 'RAG Pipeline', desc: 'Retrieval-Augmented Generation' },
  { icon: Sparkles, label: 'NLP Analysis', desc: 'spaCy entity & intent detection' },
];

export default function WelcomeScreen({ onSuggestionClick }) {
  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="max-w-2xl text-center">
        {/* Logo */}
        <div className="w-16 h-16 bg-gradient-to-br from-temple-600 to-saffron-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-temple-200/50">
          <BookOpen className="w-8 h-8 text-white" />
        </div>

        <h1 className="font-display text-3xl font-bold text-temple-800 mb-2">
          Mahabharata AI Agent
        </h1>
        <p className="text-ancient-500 mb-8 max-w-md mx-auto">
          Ask anything about the world's greatest epic. I use semantic search across 
          200+ indexed stories, characters, and concepts to find the best answers.
        </p>

        {/* Topic cards */}
        <div className="grid grid-cols-2 gap-3 mb-8">
          {TOPICS.map((t, i) => (
            <button
              key={i}
              onClick={() => onSuggestionClick(`Tell me about ${t.label.toLowerCase()} in the Mahabharata`)}
              className="group p-4 bg-white rounded-xl border border-ancient-100 hover:border-temple-300 hover:shadow-md transition-all text-left"
            >
              <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${t.color} flex items-center justify-center mb-2 group-hover:scale-110 transition-transform`}>
                <t.icon className="w-4 h-4 text-white" />
              </div>
              <p className="font-medium text-sm text-ancient-800">{t.label}</p>
              <p className="text-xs text-ancient-500 mt-0.5">{t.desc}</p>
            </button>
          ))}
        </div>

        {/* Tech stack */}
        <div className="bg-ancient-50/50 rounded-xl border border-ancient-100 p-4">
          <p className="text-xs font-medium text-ancient-600 mb-3 uppercase tracking-wider">Enhanced with</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {TECH_FEATURES.map((f, i) => (
              <div key={i} className="text-center">
                <f.icon className="w-5 h-5 text-temple-600 mx-auto mb-1" />
                <p className="text-xs font-medium text-ancient-700">{f.label}</p>
                <p className="text-[10px] text-ancient-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
