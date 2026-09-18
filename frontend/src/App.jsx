import React, { useState, useEffect, useCallback } from 'react'
import { fetchNews, fetchCategories, fetchSources, fetchMetaCategories, triggerScrape, checkHealth } from './services/api'

function App() {
  const [news, setNews] = useState([])
  const [total, setTotal] = useState(0)
  const [categories, setCategories] = useState([])
  const [sources, setSources] = useState([])
  const [metaCategories, setMetaCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedSource, setSelectedSource] = useState('All')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [scraping, setScraping] = useState(false)
  const [health, setHealth] = useState(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [newsData, catData, srcData, metaCats, healthData] = await Promise.all([
        fetchNews({ category: selectedCategory, source: selectedSource }),
        fetchCategories(),
        fetchSources(),
        fetchMetaCategories(),
        checkHealth().catch(() => null)
      ])
      setNews(newsData.items || [])
      setTotal(newsData.total || 0)
      setCategories(catData || [])
      setSources(srcData || [])
      setMetaCategories(metaCats || [])
      setHealth(healthData)
    } catch (err) {
      setError(err.message || 'Failed to load data. Is the backend running?')
      setNews([])
    } finally {
      setLoading(false)
    }
  }, [selectedCategory, selectedSource])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleScrape = async () => {
    setScraping(true)
    try {
      await triggerScrape()
      alert('Scrape started in background. Wait 1-2 minutes then refresh.')
    } catch (err) {
      alert('Failed to start scrape: ' + err.message)
    } finally {
      setScraping(false)
    }
  }

  return (
    <div>
      <header className="header">
        <div className="container">
          <h1>Thailand Tourism News Analyzer</h1>
          <p>Only tourism-related news • Classified by local Ollama models • MySQL + FastAPI + React</p>
        </div>
      </header>

      <main className="container">
        <div className="filters">
          <div>
            <label>Category</label>
            <br />
            <select value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)}>
              <option value="All">All Categories</option>
              {metaCategories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label>Source</label>
            <br />
            <select value={selectedSource} onChange={e => setSelectedSource(e.target.value)}>
              <option value="All">All Sources</option>
              {sources.map(s => (
                <option key={s.source} value={s.source}>{s.source} ({s.count})</option>
              ))}
            </select>
          </div>

          <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
            <button onClick={loadData} disabled={loading}>Refresh</button>
            <button onClick={handleScrape} disabled={scraping}>
              {scraping ? 'Scraping...' : 'Run Scrape'}
            </button>
          </div>
        </div>

        {health && (
          <div className="stats">
            <div className="stat-card">DB: <strong>{health.database}</strong></div>
            <div className="stat-card">Ollama: <strong>{health.ollama}</strong></div>
            <div className="stat-card">Total articles: <strong>{total}</strong></div>
          </div>
        )}

        {categories.length > 0 && (
          <div className="stats">
            {categories.map(c => (
              <div key={c.category} className="stat-card">
                {c.category}: <strong>{c.count}</strong>
              </div>
            ))}
          </div>
        )}

        {loading && <div className="loading">Loading news...</div>}
        {error && <div className="error">{error}</div>}

        {!loading && !error && news.length === 0 && (
          <div className="empty">
            No tourism news found yet.<br />
            Click <strong>Run Scrape</strong> to fetch and classify articles with Ollama.
          </div>
        )}

        <div className="news-list">
          {news.map(item => (
            <article key={item.id} className="news-card">
              <h3>{item.title}</h3>
              <div className="news-meta">
                <span className="badge">{item.category || 'Other'}</span>
                <span>{item.source}</span>
                {item.published_at && (
                  <span>{new Date(item.published_at).toLocaleDateString()}</span>
                )}
              </div>
              {item.summary && (
                <p className="news-summary">
                  {item.summary.length > 280 ? item.summary.slice(0, 280) + '...' : item.summary}
                </p>
              )}
              <a href={item.url} target="_blank" rel="noopener noreferrer" className="read-more">
                Read full article →
              </a>
            </article>
          ))}
        </div>
      </main>

      <footer className="footer">
        Data classified by local Ollama • Only Thailand tourism related content is kept
      </footer>
    </div>
  )
}

export default App
