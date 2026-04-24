import { useEffect, useRef, useState } from "react"


function AudioPlayer({ audioUrl }) {
    const audioRef = useRef(null)
    const [isPlaying, setIsPlaying] = useState(false)
    const [duration, setDuration] = useState(0)
    const [currentTime, setCurrentTime] = useState(0)
  
    useEffect(() => {
      const audio = audioRef.current
      if (!audio) return
  
      const handleEnded = () => setIsPlaying(false)
      const handleLoadedMetadata = () => setDuration(audio.duration)
      const handleTimeUpdate = () => setCurrentTime(audio.currentTime)
  
      audio.addEventListener("ended", handleEnded)
      audio.addEventListener("loadedmetadata", handleLoadedMetadata)
      audio.addEventListener("timeupdate", handleTimeUpdate)
  
      return () => {
        audio.removeEventListener("ended", handleEnded)
        audio.removeEventListener("loadedmetadata", handleLoadedMetadata)
        audio.removeEventListener("timeupdate", handleTimeUpdate)
      }
    }, [audioUrl])

    const togglePlay = () => {
        const audio = audioRef.current
        if (!audio) return
    
        if (isPlaying) {
          audio.pause()
          setIsPlaying(false)
        } else {
          audio.play()
          setIsPlaying(true)
        }
      }

      const formatTime = (seconds) => {
        const s = Math.floor(seconds)
        const m = Math.floor(s / 60)
        return `${m}:${String(s % 60).padStart(2, "0")}`
      }

      const progressPercent = duration > 0
    ? Math.round((currentTime / duration) * 100)
    : 0

  return (
    <div className="audio-player">
      <p className="audio-label">Audio Response</p>

      <audio ref={audioRef} src={audioUrl} />

      <div className="player-controls">
        <button className="play-btn" onClick={togglePlay}>
          {isPlaying ? "⏸" : "▶"}
        </button>

        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        <span className="time-display">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>
    </div>
  )
}

export default AudioPlayer