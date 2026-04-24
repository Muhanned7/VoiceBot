import { useRef } from "react"

function Uploader({ onAudioReady }) {
    const inputRef = useRef(null)

    const handleFileChange = (e) => {
        const file = e.target.files[0]
        
        if(!file) return

        if (!file.name.endsWith(".wav")) {
            alert("Only WAV files are supported right now.")
            return
        }

        onAudioReady(file)

    }

    return (
        <div className="uploader">
            <input
            ref={inputRef}
            accept=".wav"
            type="file"
            onChange={handleFileChange}
            style={{ display:"none"}}
        />
            <button
            className="upload-btn"
            onClick={() => inputRef.current.click()}
        >
            <span className="upload-icon">↑</span>
            Upload WAV file
        </button>
        </div>
    )
}

export default Uploader