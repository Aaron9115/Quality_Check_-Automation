import './CoherenceScore.css'

function CoherenceScore({ score, warnings }) {
  const percentage = Math.round(score * 100)
  
  return (
    <div className="coherence-score">
      <h4>Coherence Score</h4>
      <div className="score-bar">
        <div 
          className="score-fill" 
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="score-value">{percentage}%</span>
      
      {warnings && warnings.length > 0 && (
        <div className="coherence-warnings">
          {warnings.map((warning, idx) => (
            <p key={idx} className="warning">⚠️ {warning}</p>
          ))}
        </div>
      )}
    </div>
  )
}

export default CoherenceScore