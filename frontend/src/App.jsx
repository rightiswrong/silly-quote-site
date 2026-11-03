import React, { useState } from 'react';

const QuoteSkeleton = () => (
  <div className="flex items-start gap-8 animate-pulse">
    <div className="w-8 h-10 bg-slate-200 dark:bg-slate-700 rounded mb-2"></div>
    <div className="flex-1 border-l border-slate-200 dark:border-slate-800 pl-8 py-2">
      <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
    </div>
  </div>
);

const App = () => {
  const [name, setName] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchQuotesForName = async () => {
    if (!name) return;
    setLoading(true);
    setResults([]);

    const letters = name.toUpperCase().split('').filter(char => char.trim() !== '');
    
    try {
      const promises = letters.map(async (letter) => {
        const response = await fetch(`http://localhost:8000/quote/${letter}`);
        const data = await response.json();
        return { letter, ...data };
      });

      const quotes = await Promise.all(promises);
      setResults(quotes);
    } catch (error) {
      console.error("Error fetching quotes:", error);
    } finally {
      setLoading(false);
    }
  };

  const downloadResults = () => {
    const header = `Wisdom in the name: ${name.toUpperCase()}\n${'='.repeat(30)}\n\n`;
    const body = results
      .map(item => `${item.letter} : "${item.text}"\n   — ${item.author}`)
      .join('\n\n');
    
    const element = document.createElement("a");
    const file = new Blob([header + body], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${name}_wisdom.txt`;
    document.body.appendChild(element); 
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 transition-colors duration-300">
      <div className="max-w-5xl mx-auto px-6 py-20 flex flex-col items-center">
        
        <h1 className="text-5xl lg:text-6xl font-light text-center mb-12 tracking-tight">
          Wisdom in your <span className="italic font-serif">Name</span>
        </h1>

        <div className="flex gap-4 mb-20 w-full max-w-md">
          <input 
            type="text" 
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your name..."
            className="flex-1 px-4 py-3 rounded-full border border-slate-300 dark:border-slate-700 bg-transparent focus:outline-none focus:ring-2 focus:ring-slate-400 transition-all"
          />
          <button 
            onClick={fetchQuotesForName}
            disabled={loading}
            className="px-8 py-3 rounded-full bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-900 font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? 'Seeking...' : 'Reveal'}
          </button>
        </div>

        <div className="w-full flex flex-col items-center">
          {!loading && results.length > 0 && (
            <button 
              onClick={downloadResults}
              className="mb-12 px-6 py-2 text-sm uppercase tracking-widest border border-slate-300 dark:border-slate-700 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
            >
              Save as Text File
            </button>
          )}

          <div className="w-full space-y-12">
            {loading ? (
              Array.from({ length: name.length }).map((_, i) => <QuoteSkeleton key={i} />)
            ) : (
              results.map((item, index) => (
                <div key={index} className="flex items-start gap-8 animate-fadeIn">
                  <span className="text-4xl font-serif font-bold text-slate-400 w-8">{item.letter}</span>
                  <div className="flex-1 border-l border-slate-200 dark:border-slate-800 pl-8 py-2">
                    <p className="text-xl md:text-2xl font-serif italic leading-relaxed mb-2">
                      "{item.text}"
                    </p>
                    <p className="text-sm uppercase tracking-widest text-slate-500">
                      — {item.author}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
