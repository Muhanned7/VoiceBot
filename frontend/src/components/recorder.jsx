import { useState, useRef } from "react"

function Recorder({ onAudioReady, onRecordingStart }) {
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const mimeTypeRef = useRef("")

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
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mimeType = getSupportedMimeType()
      mimeTypeRef.current = mimeType

      const mediaRecorder = new MediaRecorder(stream,
        mimeType ? { mimeType } : {}
      )
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = () => {
        const mimeType = mimeTypeRef.current || "audio/webm"
        const extension = getExtension(mimeType)
        const audioBlob = new Blob(chunksRef.current, { type: mimeType })
        audioBlob.filename = `recording.${extension}`
        stream.getTracks().forEach(track => track.stop())
        onAudioReady(audioBlob, `recording.${extension}`)
      }

      mediaRecorder.start()
      setIsRecording(true)
      onRecordingStart()

    } catch (err) {
      alert("Microphone access denied. Please allow microphone access and try again.")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  return (
    <div className="recorder">
      {!isRecording ? (
        <button className="record-btn" onClick={startRecording}>
          <span className="record-icon" />
          Record
        </button>
      ) : (
        <button className="record-btn recording" onClick={stopRecording}>
          <span className="stop-icon" />
          Stop Recording
        </button>
      )}
      {isRecording && (
        <p className="recording-indicator">Recording... click stop when done</p>
      )}
    </div>
  )
}

export default Recorder