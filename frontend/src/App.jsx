import { useState } from "react"
import Recorder from './components/recorder'
import Uploader from "./components/Uploader"
import ResultCard from "./components/ResultCard"
import AudioPlayer from "./components/AudioPlayer"
function App(){
  const [status, setStatus] = useState("idle")
  const [transcript, setTranscript] = useState("")
  const [intent, setIntent] = useState("")
  const [confidence, setConfidence] = useState(0)
  const [response, setResponse] = useState("")
  const [audioUrl, setAudioUrl] = useState(null)
  const [errorMessage, setErrorMessage] = useState("")

  const handleAudioReady = async (audioBlob) =>{
    setStatus("processing")

    try {
      const formData1 = new FormData()
      formData1.append("file", audioBlob, "recording.wav")

      const VoiceBotRes = await fetch("/voicebot", {
        method: "POST",
        body: formData1
      })

      if (!VoiceBotRes.ok){
        const err = await VoiceBotRes.json()
        throw new Error(err.error || "Voicebot request failed")
      }

      const audioBlobOut = await VoiceBotRes.blob()
      const url = URL.createObjectURL(audioBlobOut)
      setAudioUrl(url)

      // Step 2 — send to /asr/transcribe to get text for display
      const formData2 = new FormData()
      formData2.append("file", audioBlob, "recording.wav")

      const asrRes = await fetch("/asr/transcribe", {
        method: "POST",
        body: formData2
      })

      if (!asrRes.ok) throw new Error("Transcription failed")
        const asrData = await asrRes.json()
        setTranscript(asrData.text)

      // Step 3 — get intent
      const intentRes = await fetch("/intent/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: asrData.text })
      })
      
      if (!intentRes.ok) throw new Error("Intent prediction failed")
        const intentData = await intentRes.json()
        setIntent(intentData.intent)
        setConfidence(intentData.confidence)

      // Step 4 — get response text
      const responseRes = await fetch("/response/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ intent: intentData.intent })
      })

      

      if (!responseRes.ok) throw new Error("Response generation failed")
        const responseData = await responseRes.json()
        setResponse(responseData.response)

        setStatus("done")
        
    } catch(err){
      console.error("Pipeline error:", err)
      setErrorMessage(err.message)
      setStatus("error")
    }
  }
  const resetState = () => {
    setStatus("idle")
    setTranscript("")
    setIntent("")
    setConfidence(0)
    setResponse("")
    setAudioUrl(null)
    setErrorMessage("")      
  }
  return (
    <div className="app">
      <header className="app-header">
        <h1>VoiceBot</h1>
        <p>AI-powered customer support</p>
      </header>

      <main className="app-main">
        {status === "idle" && (
          <div className="input-section">
            <Recorder onAudioReady={handleAudioReady}
            onRecordingStart = {() => setStatus("recording")}
            />
           <div className="divider">or</div>
            <Uploader onAudioReady={handleAudioReady} />
          </div>
        )}

        {status === "recording" && (
          <div className="input-selection">
            <Recorder 
              onAudioReady={handleAudioReady}
              onRecordingStart={() => setStatus("recording")}
              autoStarted ={true}
              />
          </div>
        )}

{status === "processing" && (
          <div className="processing-section">
            <div className="spinner" />
            <p>Processing your request...</p>
          </div>
        )}

        {status === "done" && (
          <div className="result-section">
            <ResultCard
              transcript={transcript}
              intent={intent}
              confidence={confidence}
              response={response}
            />
            <AudioPlayer audioUrl={audioUrl} />
            <button className="reset-btn" onClick={resetState}>
              Ask another question
            </button>
          </div>
        )}

        {status === "error" && (
          <div className="error-section">
            <p className="error-message">{errorMessage}</p>
            <button className="reset-btn" onClick={resetState}>
              Try again
            </button>
          </div>
        )}
      </main>
    </div>  
  )
  
}

export default App