function VideoModal({ video, onClose }) {
  if (!video) return null;

  return (
    <div
      className="modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal">
        <div className="modal-video">
          <iframe
            width="100%"
            height="100%"
            src={`https://www.youtube.com/embed/${video.video_id}?autoplay=1`}
            frameBorder="0"
            allowFullScreen
            allow="autoplay"
          />
        </div>
        <div className="modal-footer">
          <div>
            <p className="modal-title">{video.title}</p>
            <p className="modal-channel">{video.channel}</p>
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            <a
              href={video.url}
              target="_blank"
              rel="noreferrer"
              className="modal-close"
            >
              Watch on YouTube
            </a>
            <button className="modal-close" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VideoModal;
