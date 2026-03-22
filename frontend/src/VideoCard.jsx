// frontend/src/VideoCard.jsx

function VideoCard({ video, onClick }) {
  return (
    <a
      className="card"
      href={video.url}
      target="_blank"
      rel="noreferrer"
    >
      <div className="thumbnail">
        <img
          src={video.thumbnail}
          alt={video.title}
          onError={(e) => e.target.style.background = '#ddd'}
        />
        <div className="play-overlay">
          <div className="play-btn" />
        </div>
      </div>
      <div className="card-info">
        {video.interest && (
          <span className="interest-tag">{video.interest}</span>
        )}
        <p className="card-title">{video.title}</p>
        <p className="card-channel">{video.channel}</p>
        <span className="score-pill">{video.score}</span>
      </div>
    </a>
  )
}

export default VideoCard