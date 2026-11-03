import React, { useState } from 'react';

const API = import.meta.env?.VITE_API_URL ?? '';

// Smaller type when there are many cards so everything fits one screen.
const sizeFor = (n) => (n <= 8 ? 'lg' : n <= 12 ? 'md' : 'sm');

export default function App() {
  const [name, setName] = useState('');
  const [quotes, setQuotes] = useState([]);
  const [shownName, setShownName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const reveal = async (e) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed || loading) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API}/api/quotes?name=${encodeURIComponent(trimmed)}`);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || 'The quote well is dry. Try again.');
      }
      const data = await res.json();
      setQuotes(data.quotes);
      setShownName(trimmed);
    } catch (err) {
      setQuotes([]);
      setError(err.message || 'Could not reach the quote server.');
    } finally {
      setLoading(false);
    }
  };

  const download = () => {
    const header = `Wisdom in the name: ${shownName.toUpperCase()}\n${'='.repeat(30)}\n\n`;
    const body = quotes.map((q) => `${q.letter} : "${q.text}"\n   - ${q.author}`).join('\n\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([header + body], { type: 'text/plain' }));
    a.download = `${shownName.replace(/\W+/g, '_')}_wisdom.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  };

  return (
    <main className="app">
      <header className="head">
        <h1 className="hero">
          Wisdom in your <em>Name</em>
        </h1>
        <form className="form" onSubmit={reveal}>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your name..."
            aria-label="Your name"
            maxLength={40}
            autoFocus
          />
          <button type="submit" disabled={loading || !name.trim()}>
            {loading ? 'Seeking...' : 'Reveal'}
          </button>
          {quotes.length > 0 && (
            <button type="button" className="ghost" onClick={download}>
              Save as text
            </button>
          )}
        </form>
        {error && <p className="error" role="alert">{error}</p>}
      </header>

      <section className={`grid size-${sizeFor(quotes.length)}`} aria-live="polite">
        {quotes.length === 0 && !error && !loading && (
          <p className="hint">Type a name and each letter will find a quote that starts with it.</p>
        )}
        {quotes.map((q, i) => (
          <article className="card" key={`${shownName}-${i}`} style={{ '--i': i }}>
            <span className="letter">{q.letter}</span>
            <div className="body">
              <p className="quote">“{q.text}”</p>
              <p className="author">{q.author}</p>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
