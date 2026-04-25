import { useEffect, useRef } from "react"

const CHARACTERS = {
  maya: {
    name: "Maya",
    skinTone: "#F5C5A3",
    hairColor: "#2C1810",
    eyeColor: "#4A3728",
    accentColor: "#7C3AED",
    cheekColor: "#F4A0A0",
    hairStyle: "curly"
  },
  alex: {
    name: "Alex",
    skinTone: "#FDDCB5",
    hairColor: "#D4A843",
    eyeColor: "#2563EB",
    accentColor: "#2563EB",
    cheekColor: "#FBBF9A",
    hairStyle: "straight"
  },
  zara: {
    name: "Zara",
    skinTone: "#C68642",
    hairColor: "#8B1A1A",
    eyeColor: "#065F46",
    accentColor: "#E11D48",
    cheekColor: "#D4856A",
    hairStyle: "wavy"
  }
}

function CurlyHair({ color }) {
  return (
    <g>
      <ellipse cx="100" cy="55" rx="52" ry="48" fill={color} />
      <circle cx="58" cy="75" r="18" fill={color} />
      <circle cx="142" cy="75" r="18" fill={color} />
      <circle cx="62" cy="55" r="14" fill={color} />
      <circle cx="138" cy="55" r="14" fill={color} />
      <circle cx="78" cy="38" r="12" fill={color} />
      <circle cx="122" cy="38" r="12" fill={color} />
      <circle cx="100" cy="32" r="13" fill={color} />
    </g>
  )
}

function StraightHair({ color }) {
  return (
    <g>
      <ellipse cx="100" cy="52" rx="52" ry="45" fill={color} />
      <rect x="48" y="55" width="18" height="55" rx="9" fill={color} />
      <rect x="134" y="55" width="18" height="55" rx="9" fill={color} />
      <rect x="55" y="30" width="90" height="35" rx="5" fill={color} />
    </g>
  )
}

function WavyHair({ color }) {
  return (
    <g>
      <ellipse cx="100" cy="52" rx="52" ry="46" fill={color} />
      <path
        d="M48 70 Q42 90 50 105 Q42 115 52 128"
        stroke={color} strokeWidth="16"
        fill="none" strokeLinecap="round"
      />
      <path
        d="M152 70 Q158 90 150 105 Q158 115 148 128"
        stroke={color} strokeWidth="16"
        fill="none" strokeLinecap="round"
      />
      <path
        d="M55 35 Q70 25 100 28 Q130 25 145 35"
        stroke={color} strokeWidth="20"
        fill="none" strokeLinecap="round"
      />
    </g>
  )
}

function Character({ characterId, isSpeaking, audioRef }) {
  const char = CHARACTERS[characterId]
  const mouthRef = useRef(null)
  const animFrameRef = useRef(null)
  const analyserRef = useRef(null)
  const audioCtxRef = useRef(null)
  const sourceRef = useRef(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handlePlay = () => {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)()
      }

      const audioCtx = audioCtxRef.current

      if (!sourceRef.current) {
        sourceRef.current = audioCtx.createMediaElementSource(audio)
        analyserRef.current = audioCtx.createAnalyser()
        analyserRef.current.fftSize = 256
        sourceRef.current.connect(analyserRef.current)
        analyserRef.current.connect(audioCtx.destination)
      }

      animateMouth()
    }

    const handleEnded = () => {
      cancelAnimationFrame(animFrameRef.current)
      // Explicitly reset to closed mouth at correct position
      if (mouthRef.current) {
        mouthRef.current.setAttribute(
          "d",
          "M 78 128 Q 100 130 122 128 Q 100 128 78 128"
        )
      }
    }

    audio.addEventListener("play", handlePlay)
    audio.addEventListener("ended", handleEnded)
    audio.addEventListener("pause", handleEnded)

    return () => {
      audio.removeEventListener("play", handlePlay)
      audio.removeEventListener("ended", handleEnded)
      audio.removeEventListener("pause", handleEnded)
      cancelAnimationFrame(animFrameRef.current)
    }
  }, [audioRef])

  const setMouthShape = (openAmount) => {
    if (!mouthRef.current) return
    const clamp = Math.min(1, Math.max(0, openAmount))
    const bottomY = 128 + clamp * 18
    const controlY = 128 + clamp * 22
    mouthRef.current.setAttribute(
      "d",
      `M 78 128 Q 100 ${controlY} 122 128 Q 100 ${bottomY} 78 128`
    )
  }

  const animateMouth = () => {
    if (!analyserRef.current) return
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
    analyserRef.current.getByteFrequencyData(dataArray)
    const avg = dataArray.slice(0, 10).reduce((a, b) => a + b, 0) / 10
    const openAmount = avg / 180
    setMouthShape(openAmount)
    animFrameRef.current = requestAnimationFrame(animateMouth)
  }

  const Hair = char.hairStyle === "curly"
    ? CurlyHair
    : char.hairStyle === "straight"
    ? StraightHair
    : WavyHair

  return (
    <div className="character-wrap">
      <svg
        viewBox="0 0 200 220"
        xmlns="http://www.w3.org/2000/svg"
        className="character-svg"
      >
        {/* Body */}
        <rect
          x="60" y="165" width="80" height="55"
          rx="20" fill={char.accentColor}
        />

        {/* Neck */}
        <rect
          x="85" y="148" width="30" height="25"
          fill={char.skinTone}
        />

        {/* Hair back layer */}
        <Hair color={char.hairColor} />

        {/* Head */}
        <ellipse
          cx="100" cy="100" rx="48" ry="50"
          fill={char.skinTone}
        />

        {/* Cheeks */}
        <ellipse cx="68" cy="112" rx="10" ry="7" fill={char.cheekColor} opacity="0.5" />
        <ellipse cx="132" cy="112" rx="10" ry="7" fill={char.cheekColor} opacity="0.5" />

        {/* Eyes - whites */}
        <ellipse cx="82" cy="95" rx="12" ry="13" fill="white" />
        <ellipse cx="118" cy="95" rx="12" ry="13" fill="white" />

        {/* Eyes - iris */}
        <circle cx="83" cy="97" r="7" fill={char.eyeColor} />
        <circle cx="119" cy="97" r="7" fill={char.eyeColor} />

        {/* Eyes - pupil */}
        <circle cx="84" cy="97" r="3.5" fill="#111" />
        <circle cx="120" cy="97" r="3.5" fill="#111" />

        {/* Eye shine */}
        <circle cx="86" cy="94" r="1.5" fill="white" />
        <circle cx="122" cy="94" r="1.5" fill="white" />

        {/* Eyebrows */}
        <path
          d="M 72 82 Q 82 78 92 82"
          stroke={char.hairColor} strokeWidth="3"
          fill="none" strokeLinecap="round"
        />
        <path
          d="M 108 82 Q 118 78 128 82"
          stroke={char.hairColor} strokeWidth="3"
          fill="none" strokeLinecap="round"
        />

        {/* Nose */}
        <ellipse cx="100" cy="110" rx="4" ry="3" fill={char.cheekColor} opacity="0.6" />

        {/* Mouth */}
        <path
          ref={mouthRef}
          d="M 78 128 Q 100 130 122 128 Q 100 128 78 128"
          fill={char.eyeColor}
          stroke={char.eyeColor}
          strokeWidth="1"
        />

        {/* Speaking indicator */}
        {isSpeaking && (
          <g>
            <circle cx="130" cy="128" r="5" fill={char.accentColor} opacity="0.9">
              <animate attributeName="r" values="5;8;5" dur="0.8s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.9;0.3;0.9" dur="0.8s" repeatCount="indefinite" />
            </circle>
            <circle cx="142" cy="118" r="3.5" fill={char.accentColor} opacity="0.7">
              <animate attributeName="r" values="3.5;6;3.5" dur="0.8s" begin="0.2s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.7;0.2;0.7" dur="0.8s" begin="0.2s" repeatCount="indefinite" />
            </circle>
            <circle cx="152" cy="108" r="2.5" fill={char.accentColor} opacity="0.5">
              <animate attributeName="r" values="2.5;4.5;2.5" dur="0.8s" begin="0.4s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.5;0.1;0.5" dur="0.8s" begin="0.4s" repeatCount="indefinite" />
            </circle>
          </g>
        )}
      </svg>
      <p className="character-name" style={{ color: char.accentColor }}>
        {char.name}
      </p>
    </div>
  )
}

export { CHARACTERS }
export default Character