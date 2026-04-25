import { useRef, useState } from "react"

function MicButton({ onAudioReady, disabled }) {
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const mimeTypeRef = useRef("")
  const startTimeRef = useRef(null)
  const MIN_RECORDING_MS = 1500

  const getSupportedMimeType = () => {
    const types = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/ogg",
    ]
    return types.find(type => MediaRecorder.isTypeSupported(type)) || ""
  }

  const getExtension = (mimeType) => {
    if (mimeType.includes("webm")) return "webm"
    if (mimeType.includes("ogg")) return "ogg"
    return "webm"
  }

  const startRecording = async () => {
    if (disabled) return

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mimeType = getSupportedMimeType()
      mimeTypeRef.current = mimeType
      chunksRef.current = []
      startTimeRef.current = Date.now()

      const mediaRecorder = new MediaRecorder(
        stream,
        mimeType ? { mimeType } : {}
      )
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = () => {
        const mime = mimeTypeRef.current || "audio/webm"
        const ext = getExtension(mime)
        
        // Strip codec suffix to avoid corrupted EBML header
        const baseMime = mime.split(";")[0]  // "audio/webm" not "audio/webm;codecs=opus"
        
        const audioBlob = new Blob(chunksRef.current, { type: baseMime })
      
        if (audioBlob.size < 1000) {
          console.warn("Recording too small, discarding:", audioBlob.size, "bytes")
          return
        }
        stream.getTracks().forEach(track => track.stop())
        onAudioReady(audioBlob, `recording.${ext}`)
      }
      // collect data every 250ms so we always have chunks
      mediaRecorder.start(250)
      setIsRecording(true)

    } catch (err) {
      alert("Microphone access denied. Please allow microphone access.")
    }
  }

  const stopRecording = () => {
    if (!mediaRecorderRef.current || !isRecording) return

    const elapsed = Date.now() - startTimeRef.current

    if (elapsed < MIN_RECORDING_MS) {
      // not long enough yet — wait for the remainder then stop
      const remaining = MIN_RECORDING_MS - elapsed
      setTimeout(() => {
        if (mediaRecorderRef.current) {
          mediaRecorderRef.current.stop()
          setIsRecording(false)
        }
      }, remaining)
    } else {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  return (
    <div className="mic-wrap">
      <div className={`mic-ripple ${isRecording ? "mic-ripple-active" : ""}`}>
        <button
          className={`mic-btn ${isRecording ? "mic-btn-recording" : ""}`}
          onPointerDown={startRecording}
          onPointerUp={stopRecording}
          disabled={disabled}
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="mic-icon"
          >
            <rect x="9" y="2" width="6" height="11" rx="3" fill="white" />
            <path
              d="M5 11C5 14.866 8.13401 18 12 18C15.866 18 19 14.866 19 11"
              stroke="white" strokeWidth="2"
              strokeLinecap="round"
            />
            <line x1="12" y1="18" x2="12" y2="22"
              stroke="white" strokeWidth="2" strokeLinecap="round" />
            <line x1="8" y1="22" x2="16" y2="22"
              stroke="white" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </button>
      </div>
      <p className="mic-label">
        {disabled
          ? "Processing..."
          : isRecording
          ? "Release to send"
          : "Hold to speak"
        }
      </p>
    </div>
  )
}

export default MicButton