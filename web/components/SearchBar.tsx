// Presentational only — the search index is not built yet. It is deliberately
// an instrument (a field you type a query into), not a chat prompt.
export default function SearchBar() {
  const EXAMPLES = [
    "What EU policies affect battery manufacturers?",
    "Where is Europe reducing the reporting burden?",
    "Which sectors face the greatest regulatory pressure?",
  ];

  return (
    <div id="search">
      <form className="searchbar" role="search" action="/">
        <span className="searchbar-glyph" aria-hidden="true">
          ⌕
        </span>
        <input
          type="search"
          name="q"
          className="searchbar-input"
          placeholder="Search European policy, sectors, companies or measures"
          aria-label="Search European policy, sectors, companies or measures"
        />
        <button type="submit" className="searchbar-submit">
          Search <span aria-hidden="true">⏎</span>
        </button>
      </form>
      <div className="query-chips">
        {EXAMPLES.map((q) => (
          <span key={q} className="query-chip">
            <span className="query-arrow" aria-hidden="true">
              →
            </span>
            {q}
          </span>
        ))}
      </div>
    </div>
  );
}
