// frontend/src/App.jsx

import { useState } from "react"
import VideoCard from "./VideoCard"

const SOURCES = [
  { key: "youtube", label: "YouTube", icon: "▶", color: "#ff0000", available: true },
  { key: "hn", label: "HN", icon: "Y", color: "#ff6600", available: true },
  { key: "news",    label: "News",    icon: "N",  color: "#1a73e8", available: true },

]

function App() {
  const [interests, setInterests]         = useState([""])
  const [feed, setFeed]                   = useState(null)
  const [loading, setLoading]             = useState(false)
  const [error, setError]                 = useState(null)
  const [activeSource, setActiveSource]   = useState("youtube")

  function addInterest() {
    if (interests.length < 5) setInterests([...interests, ""])
  }

  function removeInterest(i) {
    if (interests.length === 1) return
    setInterests(interests.filter((_, idx) => idx !== i))
  }

  function updateInterest(i, value) {
    const updated = [...interests]
    updated[i] = value
    setInterests(updated)
  }

  async function handleDiscover() {
    const filled = interests.filter(i => i.trim())
    if (!filled.length) return

    setLoading(true)
    setError(null)
    setFeed(null)

    try {
      const response = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interests: filled })
      })
      if (!response.ok) throw new Error("Server error")
      const data = await response.json()
      setFeed(data)
    } catch {
      setError("Something went wrong. Make sure your backend is running.")
    } finally {
      setLoading(false)
    }
  }

  const currentItems = feed?.[activeSource] ?? []

  return (
    <div className="layout">

      {/* ── left sidebar ── */}
      <div className="left-sidebar">
        <div className="app-logo">FY</div>
        {SOURCES.map(source => (
          <button
            key={source.key}
            className={`source-tab ${activeSource === source.key ? "active" : ""} ${!source.available ? "disabled" : ""}`}
            onClick={() => source.available && setActiveSource(source.key)}
            title={source.available ? source.label : `${source.label} — coming soon`}
          >
            <div className="tab-icon" style={{ background: source.available ? source.color : "#ccc" }}>
              {source.icon}
            </div>
            <span className="tab-label">{source.label}</span>
          </button>
        ))}
      </div>

      {/* ── main feed ── */}
      <div className="feed">
        {!feed && !loading && (
          <div className="empty-state">
            <p>Add your interests and hit Discover</p>
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner" />
            <p>Finding the best content for you...</p>
          </div>
        )}

        {error && <p className="error">{error}</p>}

        {feed && (
          <>
            <div className="feed-header">
              {SOURCES.find(s => s.key === activeSource)?.label} results
              <span className="feed-count">{currentItems.length} items</span>
            </div>

            {currentItems.length === 0 ? (
              <div className="empty-state">
                <p>No results for this source yet</p>
              </div>
            ) : (

              /* ── youtube cards ── */
              activeSource === "youtube" ? (
                <div className="cards-grid">
                  {currentItems.map((item, i) => (
                    <VideoCard key={i} video={item} />
                  ))}
                </div>

              /* ── hn cards ── */
              ) : activeSource === "hn" ? (
                <div className="cards-grid">
                  {currentItems.map((item, i) => (
                    <a
                      key={i}
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="card hn-card"
                    >
                      <div className="card-info">
                        {item.interest && (
                          <span className="interest-tag">{item.interest}</span>
                        )}
                        <p className="card-title">{item.title}</p>
                        <p className="card-channel">by {item.author}</p>
                        <div style={{display:"flex", gap:"8px", marginTop:"6px"}}>
                          <span className="score-pill">{item.score}</span>
                          <span className="hn-points">▲ {item.points}</span>
                        </div>
                      </div>
                    </a>
                  ))}
                </div>
                ) : activeSource === "news" ? (
                  <div className="cards-grid">
                    {currentItems.map((item, i) => (
                      <a
                        key={i}
                        href={item.url}
                        target="_blank"
                        rel="noreferrer"
                        className="card news-card"
                      >
                        {item.thumbnail && (
                          <div className="thumbnail">
                            <img
                              src={item.thumbnail}
                              alt={item.title}
                              onError={(e) => e.target.style.display = 'none'}
                            />
                          </div>
                        )}
                        <div className="card-info">
                          {item.interest && (
                            <span className="interest-tag">{item.interest}</span>
                          )}
                          <p className="card-title">{item.title}</p>
                          <p className="card-channel">{item.source}</p>
                          <p className="card-description">{item.description}</p>
                          <span className="score-pill">{item.score}</span>
                        </div>
                      </a>
                    ))}
                  </div> ) : null
            )}
          </>
        )}
      </div>

      {/* ── right sidebar ── */}
      <div className="right-sidebar">
        <div className="sidebar-section">
          <p className="sidebar-title">Your interests</p>
          <p className="sidebar-subtitle">Add up to 5 topics</p>
        </div>

        <div className="interests-list">
          {interests.map((value, i) => (
            <div key={i} className="interest-row">
              <input
                className="interest-input"
                type="text"
                placeholder={`Interest ${i + 1}...`}
                value={value}
                onChange={e => updateInterest(i, e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleDiscover()}
              />
              {interests.length > 1 && (
                <button className="remove-btn" onClick={() => removeInterest(i)}>×</button>
              )}
            </div>
          ))}

          {interests.length < 5 && (
            <button className="add-btn" onClick={addInterest}>
              + Add another interest
            </button>
          )}
        </div>

        <button
          className="discover-btn"
          onClick={handleDiscover}
          disabled={loading}
        >
          {loading ? "Finding..." : "Discover"}
        </button>
      </div>

    </div>
  )
}

export default App