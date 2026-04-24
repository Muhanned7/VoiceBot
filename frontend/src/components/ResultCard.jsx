function ResultCard({ transcript, intent, confidence, response }) {
    const confidencePercent = Math.round(confidence * 100)

    const getConfidenceColor = (percent) => {
        if (percent >= 70) return "#16a34a"
        if (percent >= 40) return "#d97706"
        return "#dc2626"
      }
    
      return (
        <div className="result-card">
    
          <div className="result-row">
            <span className="result-label">What you said</span>
            <p className="result-value transcript">
              "{transcript}"
            </p>
          </div>
    
          <div className="result-divider" />
    
          <div className="result-row">
            <span className="result-label">Intent detected</span>
            <div className="intent-row">
              <span className="intent-badge">
                {intent.replace(/_/g, " ")}
              </span>
              <span
                className="confidence-score"
                style={{ color: getConfidenceColor(confidencePercent) }}
              >
                {confidencePercent}% confidence
              </span>
            </div>
          </div>
    
          <div className="result-divider" />
    
          <div className="result-row">
            <span className="result-label">Response</span>
            <p className="result-value response">
              {response}
            </p>
          </div>
    
        </div>
      )
    }
    
    export default ResultCard