import { CHARACTERS } from "./Character"

function CharacterPicker({ selected, onSelect }) {
  return (
    <div className="picker-wrap">
      <p className="picker-label">Choose your agent</p>
      <div className="picker-row">
        {Object.entries(CHARACTERS).map(([id, char]) => (
          <button
            key={id}
            className={`picker-btn ${selected === id ? "picker-btn-active" : ""}`}
            style={{
              borderColor: selected === id ? char.accentColor : "transparent",
              background: selected === id ? `${char.accentColor}15` : "white"
            }}
            onClick={() => onSelect(id)}
          >
            <div
              className="picker-avatar"
              style={{ background: char.accentColor }}
            >
              {char.name[0]}
            </div>
            <span
              className="picker-name"
              style={{ color: selected === id ? char.accentColor : "#666" }}
            >
              {char.name}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default CharacterPicker