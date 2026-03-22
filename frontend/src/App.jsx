// frontend/src/App.jsx

import { useState, useEffect } from "react"

const MODES = [
  { key: "feed",   label: "Feed",   icon: "⊞" },
  { key: "digest", label: "Digest", icon: "✉" },
]

const SOURCE_FILTERS = [
  { key: "all",     label: "All" },
  { key: "youtube", label: "YouTube" },
  { key: "hn",      label: "HN" },
  { key: "news",    label: "News" },
]

function App() {
  const [interests, setInterests]       = useState([""])
  const [feed, setFeed]                 = useState(null)
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState(null)
  const [activeMode, setActiveMode]     = useState("feed")
  const [activeFilter, setActiveFilter] = useState("all")

  const [digestEmail, setDigestEmail]   = useState("")
  const [digestTopics, setDigestTopics] = useState([])
  const [digestStatus, setDigestStatus] = useState(null)
  const [editingEmail, setEditingEmail] = useState(false)

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

  useEffect(() => {
    if (activeMode === "digest" && digestTopics.length === 0) {
      const filled = interests.filter(i => i.trim())
      if (filled.length) setDigestTopics([...filled])
    }
  }, [activeMode])

  async function handleDiscover() {
    const filled = interests.filter(i => i.trim())
    if (!filled.length) return
    setLoading(true)
    setError(null)
    setFeed(null)
    setActiveFilter("all")
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

  async function handleSubscribe() {
    if (!digestEmail || !digestEmail.includes("@")) {
      setDigestStatus("error")
      return
    }
    const topics = digestTopics.filter(t => t.trim())
    if (!topics.length) return
    try {
      const response = await fetch("http://localhost:8000/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: digestEmail,
          digest_topics: topics,
          feed_interests: interests.filter(i => i.trim())
        })
      })
      if (!response.ok) throw new Error()
      setDigestStatus("subscribed")
    } catch {
      setDigestStatus("error")
    }
  }

  async function handleSendNow() {
    if (!digestEmail) return
    setDigestStatus("sending")
    try {
      const response = await fetch("http://localhost:8000/send-digest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: digestEmail,
          digest_topics: digestTopics.filter(t => t.trim()),
          feed_interests: interests.filter(i => i.trim())
        })
      })
      if (!response.ok) throw new Error()
      setDigestStatus("sent")
    } catch {
      setDigestStatus("error")
    }
  }

  // merge all feed items into one sorted array
  const allItems = feed ? [
    ...(feed.youtube || []).map(i => ({ ...i, source: "youtube" })),
    ...(feed.hn      || []).map(i => ({ ...i, source: "hn" })),
    ...(feed.news    || []).map(i => ({ ...i, source: "news" })),
  ].sort((a, b) => b.score - a.score) : []

  const filteredItems = activeFilter === "all"
    ? allItems
    : allItems.filter(item => item.source === activeFilter)

  return (
    <div className="layout">

      {/* ── left sidebar ── */}
      <div className="left-sidebar">
        <div className="app-logo">FY</div>
        {MODES.map(mode => (
          <button
            key={mode.key}
            className={`source-tab ${activeMode === mode.key ? "active" : ""}`}
            onClick={() => setActiveMode(mode.key)}
            title={mode.label}
          >
            <div className="tab-icon" style={{
              background: mode.key === "feed" ? "#111" : "#333"
            }}>
              {mode.icon}
            </div>
            <span className="tab-label">{mode.label}</span>
          </button>
        ))}
      </div>

      {/* ── main area ── */}
      <div className="feed">
        {activeMode === "digest" ? (

          /* ── digest panel ── */
          <div className="digest-panel">
            <div className="digest-header">
              <p className="digest-title">Daily digest</p>
              <p className="digest-subtitle">
                Get a personalised email briefing every morning
              </p>
            </div>

            <div className="digest-section">
              <p className="digest-section-title">Sending to</p>
              {editingEmail ? (
                <div className="interest-row">
                  <input
                    className="interest-input"
                    type="email"
                    placeholder="your@email.com"
                    value={digestEmail}
                    onChange={e => setDigestEmail(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && setEditingEmail(false)}
                    autoFocus
                  />
                  <button className="digest-edit-btn" onClick={() => setEditingEmail(false)}>
                    Save
                  </button>
                </div>
              ) : (
                <div className="digest-email-row">
                  <span className="digest-email">{digestEmail || "No email set"}</span>
                  <button className="digest-edit-btn" onClick={() => setEditingEmail(true)}>
                    {digestEmail ? "Change" : "Add email"}
                  </button>
                </div>
              )}
            </div>

            {interests.filter(i => i.trim()).length > 0 && (
              <div className="digest-section">
                <p className="digest-section-title">Your feed interests</p>
                <div className="digest-tags">
                  {interests.filter(i => i.trim()).map((interest, i) => (
                    <span key={i} className="digest-tag">{interest}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="digest-section">
              <p className="digest-section-title">Digest topics</p>
              <p className="digest-section-hint">
                Edit to be more specific — e.g. "Manchester United results" instead of "football"
              </p>
              <div className="interests-list" style={{marginTop: "10px"}}>
                {digestTopics.map((topic, i) => (
                  <div key={i} className="interest-row">
                    <input
                      className="interest-input"
                      type="text"
                      placeholder={`Topic ${i + 1}...`}
                      value={topic}
                      onChange={e => {
                        const updated = [...digestTopics]
                        updated[i] = e.target.value
                        setDigestTopics(updated)
                      }}
                    />
                    {digestTopics.length > 1 && (
                      <button
                        className="remove-btn"
                        onClick={() => setDigestTopics(digestTopics.filter((_, idx) => idx !== i))}
                      >×</button>
                    )}
                  </div>
                ))}
                {digestTopics.length < 5 && (
                  <button className="add-btn" onClick={() => setDigestTopics([...digestTopics, ""])}>
                    + Add topic
                  </button>
                )}
              </div>
            </div>

            {digestStatus === "subscribed" && (
              <div className="digest-status success">
                Subscribed! Your first digest arrives tomorrow at 8am.
              </div>
            )}
            {digestStatus === "sent" && (
              <div className="digest-status success">
                Digest sent! Check your inbox.
              </div>
            )}
            {digestStatus === "sending" && (
              <div className="digest-status info">
                Sending digest — this takes 2-3 minutes while we scrape the web...
              </div>
            )}
            {digestStatus === "error" && (
              <div className="digest-status error">
                Something went wrong. Check your email and make sure you subscribed first.
              </div>
            )}

            <div className="digest-actions">
              <button className="discover-btn" onClick={handleSubscribe}>
                Subscribe
              </button>
              <button
                className="digest-preview-btn"
                onClick={handleSendNow}
                disabled={digestStatus === "sending" || !digestEmail}
              >
                {digestStatus === "sending" ? "Sending..." : "Send me a preview"}
              </button>
            </div>
          </div>

        ) : (

          /* ── combined feed ── */
          <>
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
                {/* filter pills */}
                <div className="filter-pills">
                  {SOURCE_FILTERS.map(f => (
                    <button
                      key={f.key}
                      className={`filter-pill ${activeFilter === f.key ? "active" : ""}`}
                      onClick={() => setActiveFilter(f.key)}
                    >
                      {f.label}
                      <span className="pill-count">
                        {f.key === "all"
                          ? allItems.length
                          : allItems.filter(i => i.source === f.key).length}
                      </span>
                    </button>
                  ))}
                </div>

                {/* combined cards */}
                <div className="cards-grid">
                  {filteredItems.map((item, i) => (
                    <a
                      key={i}
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className={`card ${item.source}-card`}
                    >
                      {/* source badge */}
                      <div className={`source-badge source-badge-${item.source}`}>
                        {item.source === "youtube" ? "YT" : item.source === "hn" ? "HN" : "News"}
                      </div>

                      {/* thumbnail for youtube and news */}
                      {(item.source === "youtube" || item.source === "news") && item.thumbnail && (
                        <div className="thumbnail">
                          <img
                            src={item.thumbnail}
                            alt={item.title}
                            onError={e => e.target.style.display = "none"}
                          />
                          {item.source === "youtube" && (
                            <div className="play-overlay">
                              <div className="play-btn" />
                            </div>
                          )}
                        </div>
                      )}

                      {/* hn no thumbnail — just icon */}
                      {item.source === "hn" && (
                        <div className="hn-placeholder">
                          <span>Y</span>
                        </div>
                      )}

                      <div className="card-info">
                        {item.interest && (
                          <span className="interest-tag">{item.interest}</span>
                        )}
                        <p className="card-title">{item.title}</p>
                        <p className="card-channel">
                          {item.source === "youtube" && item.channel}
                          {item.source === "hn" && `by ${item.author}`}
                          {item.source === "news" && item.source_name}
                        </p>
                        <div style={{display:"flex", gap:"6px", marginTop:"6px", alignItems:"center"}}>
                          <span className="score-pill">{item.score}</span>
                          {item.source === "hn" && item.points && (
                            <span className="hn-points">▲ {item.points}</span>
                          )}
                        </div>
                      </div>
                    </a>
                  ))}
                </div>
              </>
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

        <div className="coming-soon">Reddit coming soon</div>

        {activeMode === "feed" && (
          <button
            className="discover-btn"
            onClick={handleDiscover}
            disabled={loading}
          >
            {loading ? "Finding..." : "Discover"}
          </button>
        )}
      </div>

    </div>
  )
}

export default App