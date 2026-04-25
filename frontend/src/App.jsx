import { useState, useRef } from "react"
import Character from "./components/Character"
import CharacterPicker from "./components/CharacterPicker"
import MicButton from "./components/MicButton"
import ResultCard from "./components/ResultCard"

function App() {
  const [selectedChar, setSelectedChar] = useState("maya")
  const [status, setStatus] = useState("idle")
  const [transcript, setTranscript] = useState("")
  const [intent, setIntent] = useState("")
  const [confidence, setConfidence] = useState(0)
  const [response, setResponse] = useState("")
  const [isSpeaking, setIsSpeaking] = useState(false)
  const audioRef = useRef(null)

  const handleAudioReady = async (blob, filename) => {
    const formData = new FormData()
    
    // Explicitly set the correct mime type and filename
    const file = new File([blob], filename, { type: blob.type })
    formData.append("file", file, filename)  // filename must have correct extension
  
    console.log("Sending:", filename, "size:", blob.size, "type:", blob.type)
  
    try {
      const res = await fetch("http://localhost:8000/voicebot", {
        method: "POST",
        body: formData,
      })

      if (!res.ok) {
        setStatus("error")
        return
      }

      const data = await res.json()
      console.log("Response:", data)

      // Update state with response data
      setTranscript(data.transcript)
      setIntent(data.intent)
      setConfidence(data.confidence)
      setResponse(data.response)
      setStatus("done")

      // Play audio and animate character mouth
      if (data.audio) {
        const audioBytes = Uint8Array.from(atob(data.audio), c => c.charCodeAt(0))
        const audioBlob = new Blob([audioBytes], { type: "audio/mpeg" })
        const audioUrl = URL.createObjectURL(audioBlob)

        const audio = audioRef.current
        audio.src = audioUrl
        audio.onplay = () => setIsSpeaking(true)
        audio.onended = () => {
          setIsSpeaking(false)
          URL.revokeObjectURL(audioUrl) // clean up
        }
        audio.play()
      } else {
        console.warn("No audio in response")
      }

    } catch (err) {
      console.error("Request failed:", err)
      setStatus("error")
    }
  }

  const handleSelectChar = (id) => {
    // stop audio if playing when switching character
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.src = ""
    }
    setIsSpeaking(false)
    setSelectedChar(id)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>VoiceBot</h1>
        <p>AI-powered customer support</p>
      </header>

      <main className="app-main-new">

        {/* Character picker */}
        <CharacterPicker
          selected={selectedChar}
          onSelect={handleSelectChar}
        />

        {/* Character display */}
        <div className="character-stage">
          <audio ref={audioRef} />
          <Character
            characterId={selectedChar}
            isSpeaking={isSpeaking}
            audioRef={audioRef}
          />
        </div>

        {/* Response text — shows below character */}
        {status === "done" && (
          <div className="response-bubble">
            <p className="response-text">"{response}"</p>
          </div>
        )}

        {/* Processing indicator */}
        {status === "processing" && (
          <div className="response-bubble processing">
            <div className="typing-dots">
              <span /><span /><span />
            </div>
          </div>
        )}

        {/* Error */}
        {status === "error" && (
          <div className="response-bubble error">
            <p className="response-text">
              Something went wrong. Please try again.
            </p>
          </div>
        )}

        {/* Result details */}
        {/*{status === "done" && (
          <ResultCard
            transcript={transcript}
            intent={intent}
            confidence={confidence}
            response=""
          />
        )} */}

        {/* Mic button — always at bottom */}
        <MicButton
          onAudioReady={handleAudioReady}
          disabled={status === "processing"}
        />

      </main>
    </div>
  )
}

export default App