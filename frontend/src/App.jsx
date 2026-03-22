// frontend/src/App.jsx

import { useState, useEffect } from "react";

const SOURCE_FILTERS = [
  { key: "all", label: "All" },
  { key: "youtube", label: "YouTube" },
  { key: "hn", label: "HN" },
  { key: "news", label: "News" },
];

const TOPIC_COLORS = [
  {
    border: "#ff4444",
    glow: "rgba(255,68,68,0.15)",
    tag: "rgba(255,68,68,0.12)",
    text: "#ff6b6b",
  },
  {
    border: "#4488ff",
    glow: "rgba(68,136,255,0.15)",
    tag: "rgba(68,136,255,0.12)",
    text: "#6ba3ff",
  },
  {
    border: "#44cc88",
    glow: "rgba(68,204,136,0.15)",
    tag: "rgba(68,204,136,0.12)",
    text: "#5ddba0",
  },
  {
    border: "#cc44ff",
    glow: "rgba(204,68,255,0.15)",
    tag: "rgba(204,68,255,0.12)",
    text: "#d96bff",
  },
  {
    border: "#ffaa22",
    glow: "rgba(255,170,34,0.15)",
    tag: "rgba(255,170,34,0.12)",
    text: "#ffbb55",
  },
];

const MODES = [
  { key: "feed", label: "Feed", icon: "⊞" },
  { key: "digest", label: "Digest", icon: "✉" },
];

export default function App() {
  const [interests, setInterests] = useState([""]);
  const [feed, setFeed] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState("all");
  const [activeMode, setActiveMode] = useState("feed");
  const [showInterestsPanel, setShowInterestsPanel] = useState(false);
  const [activeTopicFilter, setActiveTopicFilter] = useState(null);

  const [digestEmail, setDigestEmail] = useState("");
  const [digestTopics, setDigestTopics] = useState([]);
  const [digestStatus, setDigestStatus] = useState(null);
  const [editingEmail, setEditingEmail] = useState(false);

  function addInterest() {
    if (interests.length < 5) setInterests([...interests, ""]);
  }

  function removeInterest(i) {
    if (interests.length === 1) return;
    setInterests(interests.filter((_, idx) => idx !== i));
  }

  function updateInterest(i, value) {
    const updated = [...interests];
    updated[i] = value;
    setInterests(updated);
  }

  useEffect(() => {
    if (activeMode === "digest" && digestTopics.length === 0) {
      const filled = interests.filter((i) => i.trim());
      if (filled.length) setDigestTopics([...filled]);
    }
  }, [activeMode]);

  async function handleDiscover() {
    const filled = interests.filter((i) => i.trim());
    if (!filled.length) return;
    setLoading(true);
    setError(null);
    setFeed(null);
    setActiveFilter("all");
    setActiveTopicFilter(null);
    setShowInterestsPanel(false);
    try {
      const response = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interests: filled }),
      });
      if (!response.ok) throw new Error("Server error");
      const data = await response.json();
      setFeed(data);
    } catch {
      setError("Something went wrong. Make sure your backend is running.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubscribe() {
    if (!digestEmail || !digestEmail.includes("@")) {
      setDigestStatus("error");
      return;
    }
    const topics = digestTopics.filter((t) => t.trim());
    if (!topics.length) return;
    try {
      const res = await fetch("http://localhost:8000/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: digestEmail,
          digest_topics: topics,
          feed_interests: interests.filter((i) => i.trim()),
        }),
      });
      if (!res.ok) throw new Error();
      setDigestStatus("subscribed");
    } catch {
      setDigestStatus("error");
    }
  }

  async function handleSendNow() {
    if (!digestEmail) return;
    setDigestStatus("sending");
    try {
      const res = await fetch("http://localhost:8000/send-digest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: digestEmail,
          digest_topics: digestTopics.filter((t) => t.trim()),
          feed_interests: interests.filter((i) => i.trim()),
        }),
      });
      if (!res.ok) throw new Error();
      setDigestStatus("sent");
    } catch {
      setDigestStatus("error");
    }
  }

  const filledInterests = interests.filter((i) => i.trim());

  const allItems = feed
    ? [
        ...(feed.youtube || []).map((i) => ({ ...i, source: "youtube" })),
        ...(feed.hn || []).map((i) => ({ ...i, source: "hn" })),
        ...(feed.news || []).map((i) => ({ ...i, source: "news" })),
      ].sort((a, b) => b.score - a.score)
    : [];

  const topicFilteredItems = activeTopicFilter
    ? allItems.filter((item) => item.interest === activeTopicFilter)
    : allItems;

  const filteredItems =
    activeFilter === "all"
      ? topicFilteredItems
      : topicFilteredItems.filter((item) => item.source === activeFilter);

  const heroItem = filteredItems[0] || null;
  const gridItems = filteredItems.slice(1);

  function getTopicColor(interest) {
    const idx = filledInterests.indexOf(interest);
    return TOPIC_COLORS[idx % TOPIC_COLORS.length] || TOPIC_COLORS[0];
  }

  function getSourceLabel(source) {
    if (source === "youtube") return "YT";
    if (source === "hn") return "HN";
    return "News";
  }

  return (
    <div className="layout">
      {/* ── top navbar ── */}
      <nav className="navbar">
        <div className="navbar-left">
          <span className="app-logo">FY</span>
          <div className="nav-modes">
            {MODES.map((m) => (
              <button
                key={m.key}
                className={`nav-mode-btn ${activeMode === m.key ? "active" : ""}`}
                onClick={() => setActiveMode(m.key)}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>

        <div className="navbar-center">
          {feed && activeMode === "feed" && (
            <div className="filter-pills">
              {SOURCE_FILTERS.map((f) => (
                <button
                  key={f.key}
                  className={`filter-pill ${activeFilter === f.key ? "active" : ""}`}
                  onClick={() => setActiveFilter(f.key)}
                >
                  {f.label}
                  <span className="pill-count">
                    {f.key === "all"
                      ? allItems.length
                      : allItems.filter((i) => i.source === f.key).length}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="navbar-right">
          <button
            className="interests-btn"
            onClick={() => setShowInterestsPanel((p) => !p)}
          >
            <span>Your Interests</span>
            {filledInterests.length > 0 && (
              <span className="interests-count">{filledInterests.length}</span>
            )}
          </button>
        </div>
      </nav>

      {/* ── interests drawer ── */}
      {showInterestsPanel && (
        <div className="interests-drawer">
          <div className="drawer-header">
            <p className="drawer-title">Your Interests</p>
            <p className="drawer-subtitle">Add up to 5 topics</p>
          </div>
          <div className="interests-list">
            {interests.map((value, i) => (
              <div key={i} className="interest-row">
                <div
                  className="interest-color-dot"
                  style={{
                    background: TOPIC_COLORS[i % TOPIC_COLORS.length].border,
                  }}
                />
                <input
                  className="interest-input"
                  type="text"
                  placeholder={`Interest ${i + 1}...`}
                  value={value}
                  onChange={(e) => updateInterest(i, e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleDiscover()}
                />
                {interests.length > 1 && (
                  <button
                    className="remove-btn"
                    onClick={() => removeInterest(i)}
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
            {interests.length < 5 && (
              <button className="add-btn" onClick={addInterest}>
                + Add interest
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
      )}

      {/* ── page body ── */}
      <div className="page-body">
        {activeMode === "digest" ? (
          /* ── digest panel ── */
          <div className="digest-panel">
            <div className="digest-header">
              <p className="digest-title">Daily Digest</p>
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
                    onChange={(e) => setDigestEmail(e.target.value)}
                    onKeyDown={(e) =>
                      e.key === "Enter" && setEditingEmail(false)
                    }
                    autoFocus
                  />
                  <button
                    className="digest-edit-btn"
                    onClick={() => setEditingEmail(false)}
                  >
                    Save
                  </button>
                </div>
              ) : (
                <div className="digest-email-row">
                  <span className="digest-email">
                    {digestEmail || "No email set"}
                  </span>
                  <button
                    className="digest-edit-btn"
                    onClick={() => setEditingEmail(true)}
                  >
                    {digestEmail ? "Change" : "Add email"}
                  </button>
                </div>
              )}
            </div>

            {filledInterests.length > 0 && (
              <div className="digest-section">
                <p className="digest-section-title">Your feed interests</p>
                <div className="digest-tags">
                  {filledInterests.map((interest, i) => (
                    <span key={i} className="digest-tag">
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="digest-section">
              <p className="digest-section-title">Digest topics</p>
              <p className="digest-section-hint">
                Edit to be more specific — e.g. "Man United results" instead of
                "football"
              </p>
              <div className="interests-list" style={{ marginTop: "10px" }}>
                {digestTopics.map((topic, i) => (
                  <div key={i} className="interest-row">
                    <input
                      className="interest-input"
                      type="text"
                      placeholder={`Topic ${i + 1}...`}
                      value={topic}
                      onChange={(e) => {
                        const updated = [...digestTopics];
                        updated[i] = e.target.value;
                        setDigestTopics(updated);
                      }}
                    />
                    {digestTopics.length > 1 && (
                      <button
                        className="remove-btn"
                        onClick={() =>
                          setDigestTopics(
                            digestTopics.filter((_, idx) => idx !== i),
                          )
                        }
                      >
                        ×
                      </button>
                    )}
                  </div>
                ))}
                {digestTopics.length < 5 && (
                  <button
                    className="add-btn"
                    onClick={() => setDigestTopics([...digestTopics, ""])}
                  >
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
                Sending digest — this takes 2–3 minutes...
              </div>
            )}
            {digestStatus === "error" && (
              <div className="digest-status error">
                Something went wrong. Check your email and try again.
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
                {digestStatus === "sending"
                  ? "Sending..."
                  : "Send me a preview"}
              </button>
            </div>
          </div>
        ) : (
          /* ── feed ── */
          <div className="feed">
            {/* empty state */}
            {!feed && !loading && !error && (
              <div className="empty-state">
                <div className="empty-icon">⊞</div>
                <p className="empty-title">Your feed is empty</p>
                <p className="empty-sub">
                  Open "Your Interests", add some topics, and hit Discover
                </p>
                <button
                  className="discover-btn"
                  onClick={() => setShowInterestsPanel(true)}
                >
                  Get Started
                </button>
              </div>
            )}

            {/* loading */}
            {loading && (
              <div className="loading">
                <div className="spinner" />
                <p>Finding the best content for you...</p>
              </div>
            )}

            {/* error */}
            {error && <p className="error">{error}</p>}

            {/* topic strip */}
            {feed && filledInterests.length > 0 && (
              <div className="topic-strip">
                <button
                  className={`topic-chip ${activeTopicFilter === null ? "topic-chip-all-active" : "topic-chip-all"}`}
                  onClick={() => setActiveTopicFilter(null)}
                >
                  All
                </button>
                {filledInterests.map((interest, i) => {
                  const color = TOPIC_COLORS[i % TOPIC_COLORS.length];
                  const isActive = activeTopicFilter === interest;
                  return (
                    <button
                      key={i}
                      className="topic-chip"
                      onClick={() =>
                        setActiveTopicFilter(isActive ? null : interest)
                      }
                      style={{
                        borderColor: isActive ? color.border : "transparent",
                        background: isActive
                          ? color.tag
                          : "rgba(255,255,255,0.05)",
                        color: isActive ? color.text : "#888",
                        boxShadow: isActive ? `0 0 10px ${color.glow}` : "none",
                      }}
                    >
                      <span
                        className="topic-chip-dot"
                        style={{ background: color.border }}
                      />
                      {interest}
                    </button>
                  );
                })}
              </div>
            )}

            {/* hero card */}
            {heroItem && (
              <a
                href={heroItem.url}
                target="_blank"
                rel="noreferrer"
                className="hero-card"
                style={{
                  backgroundImage: heroItem.thumbnail
                    ? `url(${heroItem.thumbnail})`
                    : undefined,
                }}
              >
                <div className="hero-gradient" />
                <div className="hero-content">
                  <div className="hero-meta">
                    <span
                      className={`source-badge source-badge-${heroItem.source}`}
                    >
                      {getSourceLabel(heroItem.source)}
                    </span>
                    {heroItem.interest &&
                      (() => {
                        const color = getTopicColor(heroItem.interest);
                        return (
                          <span
                            className="hero-tag"
                            style={{
                              background: color.tag,
                              color: color.text,
                              borderColor: color.border,
                            }}
                          >
                            {heroItem.interest}
                          </span>
                        );
                      })()}
                  </div>
                  <p className="hero-title">{heroItem.title}</p>
                  <p className="hero-channel">
                    {heroItem.source === "youtube" && heroItem.channel}
                    {heroItem.source === "hn" && `by ${heroItem.author}`}
                    {heroItem.source === "news" && heroItem.source_name}
                  </p>
                  <div className="hero-bottom">
                    <span className="score-pill">{heroItem.score}</span>
                    {heroItem.source === "hn" && heroItem.points && (
                      <span className="hn-points">▲ {heroItem.points}</span>
                    )}
                  </div>
                </div>
              </a>
            )}

            {/* grid */}
            {gridItems.length > 0 && (
              <div className="cards-grid">
                {gridItems.map((item, i) => {
                  const color = item.interest
                    ? getTopicColor(item.interest)
                    : null;
                  return (
                    <a
                      key={i}
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className={`card ${item.source}-card`}
                    >
                      <span
                        className={`source-badge source-badge-${item.source}`}
                      >
                        {getSourceLabel(item.source)}
                      </span>

                      {/* thumbnail */}
                      {(item.source === "youtube" || item.source === "news") &&
                        item.thumbnail && (
                          <div className="thumbnail">
                            <img
                              src={item.thumbnail}
                              alt={item.title}
                              onError={(e) => (e.target.style.display = "none")}
                            />
                            {item.source === "youtube" && (
                              <div className="play-overlay">
                                <div className="play-btn" />
                              </div>
                            )}
                          </div>
                        )}

                      {/* HN placeholder */}
                      {item.source === "hn" && (
                        <div className="hn-placeholder">Y</div>
                      )}

                      <div className="card-info">
                        {item.interest && color && (
                          <span
                            className="interest-tag"
                            style={{
                              background: color.tag,
                              color: color.text,
                              borderColor: color.border,
                            }}
                          >
                            {item.interest}
                          </span>
                        )}
                        <p className="card-title">{item.title}</p>
                        <p className="card-channel">
                          {item.source === "youtube" && item.channel}
                          {item.source === "hn" && `by ${item.author}`}
                          {item.source === "news" && item.source_name}
                        </p>
                        <div className="card-footer">
                          <span className="score-pill">{item.score}</span>
                          {item.source === "hn" && item.points && (
                            <span className="hn-points">▲ {item.points}</span>
                          )}
                        </div>
                      </div>
                    </a>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
