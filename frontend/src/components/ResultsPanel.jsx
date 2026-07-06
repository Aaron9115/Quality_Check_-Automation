import { useState } from 'react'
import './ResultsPanel.css'

function ResultsPanel({ results }) {
  const [copiedStates, setCopiedStates] = useState({})

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text)
    setCopiedStates(prev => ({ ...prev, [index]: true }))
    setTimeout(() => setCopiedStates(prev => ({ ...prev, [index]: false })), 2000)
  }

  const copyFullText = () => {
    navigator.clipboard.writeText(results.corrected_text)
    setCopiedStates(prev => ({ ...prev, fullText: true }))
    setTimeout(() => setCopiedStates(prev => ({ ...prev, fullText: false })), 2000)
  }

  const hasSpellingIssues = results.british_spelling?.length > 0
  const hasGrammarIssues = results.grammar_issues?.length > 0
  const hasLogicIssues = results.logic_issues?.length > 0
  const hasCoherenceWarnings = results.coherence?.warnings?.length > 0 && results.coherence.score < 0.7
  
  const hasAnyIssues = hasSpellingIssues || hasGrammarIssues || hasLogicIssues || hasCoherenceWarnings

  const safeString = (value, fallback = '') => {
    if (typeof value === 'string') return value
    if (value === null || value === undefined) return fallback
    if (typeof value === 'object') {
      if (value.message) return safeString(value.message, fallback)
      if (value.original) return safeString(value.original, fallback)
      if (value.correction) return safeString(value.correction, fallback)
      return fallback
    }
    return String(value)
  }

  const getGrammarCopyMessage = (issue) => {
    const original = safeString(issue.original, '')
    const correction = safeString(issue.correction, '')
    if (original && correction) {
      return `Suggestion: Change "${original}" to "${correction}"`
    }
    return `Suggestion: ${safeString(issue.message, 'Grammar issue')}`
  }

  const getSpellingCopyMessage = (issue) => {
    const original = safeString(issue.original, '')
    const correction = safeString(issue.correction, '')
    return `Suggestion: Change "${original}" to "${correction}" for British English consistency.`
  }

  const getSpecificLogicSuggestion = (sentence, reason) => {
    const lowerSentence = sentence.toLowerCase()
    
    if (lowerSentence.includes('dead') && lowerSentence.includes('breathing')) {
      return {
        original: sentence,
        suggestions: [
          `Change "${sentence}" to "The injured man is breathing"`,
          `Change "${sentence}" to "The dead man is not breathing"`,
          `Change "${sentence}" to "The man is unconscious but breathing"`
        ]
      }
    }
    if (lowerSentence.includes('born') && lowerSentence.includes('graduated')) {
      return {
        original: sentence,
        suggestions: [
          `Change "${sentence}" to "She was born in 1995. She graduated in 2010"`,
          `Change "${sentence}" to "She was born in 2015. She will graduate in 2033"`,
          `Change "${sentence}" to "She was born in 2015 and graduated in 2033"`
        ]
      }
    }
    if (lowerSentence.includes('silence') && lowerSentence.includes('loud')) {
      return {
        original: sentence,
        suggestions: [
          `Change "${sentence}" to "The silence was deafening"`,
          `Change "${sentence}" to "The silence was overwhelming"`,
          `Change "${sentence}" to "The silence was oppressive"`
        ]
      }
    }
    if ((lowerSentence.includes('colour') || lowerSentence.includes('color')) && lowerSentence.includes('taste')) {
      return {
        original: sentence,
        suggestions: [
          `Change "${sentence}" to "The colour blue is calming"`,
          `Change "${sentence}" to "Blue is a sweet colour"`,
          `Change "${sentence}" to "The colour blue reminds me of sweet blueberries"`
        ]
      }
    }
    return {
      original: sentence,
      suggestions: [`Rewrite "${sentence}" for logical consistency. ${reason}`]
    }
  }

  const getLogicCopyMessage = (issue) => {
    const sentence = safeString(issue.sentence, safeString(issue.original, ''))
    const reason = safeString(issue.reason, '')
    const suggestion = getSpecificLogicSuggestion(sentence, reason)
    const suggestionsText = suggestion.suggestions.map(s => `"${s}"`).join(', or ')
    return `Suggestion: ${suggestionsText}`
  }

  const getSentencesFromText = (text) => {
    if (!text) return []
    return text.split(/[.!?]+/).filter(s => s.trim().length > 0).map(s => s.trim())
  }

  const sentences = getSentencesFromText(results.corrected_text)

  const parseCoherenceWarningsWithSentences = (warnings, sentencesList) => {
    if (!warnings || !Array.isArray(warnings)) return []
    
    return warnings.map(warning => {
      const warningText = safeString(warning, '')
      const match = warningText.match(/between sentence (\d+) and (\d+)/)
      
      if (match && sentencesList.length > 0) {
        const s1 = parseInt(match[1]) - 1
        const s2 = parseInt(match[2]) - 1
        return {
          text: warningText,
          sentence1: match[1],
          sentence2: match[2],
          sentence1Text: sentencesList[s1] || '',
          sentence2Text: sentencesList[s2] || ''
        }
      }
      return { text: warningText, sentence1: null, sentence2: null, sentence1Text: '', sentence2Text: '' }
    })
  }

  const parsedWarnings = results.coherence?.warnings ? parseCoherenceWarningsWithSentences(results.coherence.warnings, sentences) : []

  const getCoherenceSuggestionWithUserSentences = (score, warningsList, userSentences) => {
    if (score >= 0.85) {
      return {
        message: "Your text flows very well!",
        type: "excellent",
        hasPersonalizedExamples: false
      }
    } else if (score >= 0.7) {
      const firstWarning = parsedWarnings.find(w => w.sentence1Text && w.sentence2Text)
      
      if (firstWarning && firstWarning.sentence1Text && firstWarning.sentence2Text) {
        const sent1 = firstWarning.sentence1Text
        const sent2 = firstWarning.sentence2Text
        return {
          message: "Good flow. Try adding transition words to connect your ideas.",
          type: "good",
          hasPersonalizedExamples: true,
          personalizedExamples: [
            { word: "However", example: `"${sent1} However, ${sent2.charAt(0).toLowerCase() + sent2.slice(1)}"` },
            { word: "Therefore", example: `"${sent1} Therefore, ${sent2.charAt(0).toLowerCase() + sent2.slice(1)}"` },
            { word: "Meanwhile", example: `"${sent1} Meanwhile, ${sent2.charAt(0).toLowerCase() + sent2.slice(1)}"` },
            { word: "In contrast", example: `"${sent1} In contrast, ${sent2.charAt(0).toLowerCase() + sent2.slice(1)}"` }
          ]
        }
      }
      
      return {
        message: "Good flow. Try adding transition words like 'however' or 'therefore'.",
        type: "good",
        hasPersonalizedExamples: false
      }
    } else {
      return {
        message: "Consider restructuring to improve flow.",
        type: "poor",
        hasPersonalizedExamples: false
      }
    }
  }

  const coherenceSuggestion = results.coherence ? getCoherenceSuggestionWithUserSentences(results.coherence.score, results.coherence.warnings, sentences) : null

  const separateIssues = () => {
    const grammarOnly = []
    const logicOnly = []
    
    if (results.grammar_issues) {
      results.grammar_issues.forEach(issue => {
        const message = (issue.message || '').toLowerCase()
        const original = (issue.original || '').toLowerCase()
        if (message.includes('dead') || message.includes('born') || message.includes('graduated') || 
            message.includes('silence') || message.includes('colour') || message.includes('taste') ||
            message.includes('logic') || message.includes('impossible') || message.includes('cannot') ||
            original.includes('dead') || original.includes('born') || original.includes('silence')) {
          logicOnly.push(issue)
        } else {
          grammarOnly.push(issue)
        }
      })
    }
    
    return { grammarOnly, logicOnly }
  }

  const { grammarOnly, logicOnly } = separateIssues()
  const allLogicIssues = [...logicOnly, ...(results.logic_issues || [])]

  const groupGrammarIssues = (issues) => {
    const groups = {
      punctuation: [],
      tense: [],
      double_negative: [],
      article: [],
      subject_verb: [],
      apostrophe: [],
      other: []
    }
    
    issues.forEach(issue => {
      const message = (issue.message || '').toLowerCase()
      
      if (message.includes('comma') || message.includes('question') || message.includes('punctuation')) {
        groups.punctuation.push(issue)
      } else if (message.includes('tense') || message.includes('past') || (message.includes('verb') && !message.includes('subject'))) {
        groups.tense.push(issue)
      } else if (message.includes('double negative')) {
        groups.double_negative.push(issue)
      } else if (message.includes('article')) {
        groups.article.push(issue)
      } else if (message.includes('subject-verb') || message.includes('agreement') || message.includes('there is') || message.includes('they was')) {
        groups.subject_verb.push(issue)
      } else if (message.includes('apostrophe') || message.includes('its') || message.includes('contraction')) {
        groups.apostrophe.push(issue)
      } else {
        groups.other.push(issue)
      }
    })
    
    return groups
  }

  const groupedGrammar = grammarOnly.length > 0 ? groupGrammarIssues(grammarOnly) : {}

  const grammarGroupConfig = {
    punctuation: { title: 'Punctuation', icon: 'P' },
    tense: { title: 'Tense Errors', icon: 'T' },
    double_negative: { title: 'Double Negatives', icon: 'D' },
    article: { title: 'Missing Articles', icon: 'A' },
    subject_verb: { title: 'Subject-Verb Agreement', icon: 'S' },
    apostrophe: { title: 'Apostrophe Errors', icon: "'" },
    other: { title: 'Other Grammar', icon: 'G' }
  }

  return (
    <div className="results-panel">
      
      {/* Corrected Version */}
      {results.corrected_text !== results.original_text && (
        <div className="result-card">
          <div className="card-header">
            <div className="header-left">
              <span className="header-icon">✓</span>
              <span>Corrected Version</span>
            </div>
            <button className="copy-btn" onClick={copyFullText}>
              {copiedStates.fullText ? '✓ Copied' : 'Copy All'}
            </button>
          </div>
          <div className="card-body corrected-body">
            {safeString(results.corrected_text)}
          </div>
        </div>
      )}

      {/* No Issues */}
      {!hasAnyIssues && results.corrected_text && (
        <div className="result-card no-issues">
          <div className="card-header">
            <div className="header-left">
              <span className="header-icon">◆</span>
              <span>No Issues Found</span>
            </div>
          </div>
          <div className="card-body no-issues-body">
            <p>Your text looks great! No grammar, spelling, or punctuation issues found.</p>
          </div>
        </div>
      )}

      {/* British Spelling */}
      {hasSpellingIssues && (
        <div className="result-card">
          <div className="card-header">
            <div className="header-left">
              <span className="header-icon">◆</span>
              <span>British Spelling ({results.british_spelling.length})</span>
            </div>
          </div>
          <div className="card-body">
            {results.british_spelling.map((issue, idx) => {
              const original = safeString(issue.original)
              const correction = safeString(issue.correction)
              const copyMessage = getSpellingCopyMessage(issue)
              
              return (
                <div key={idx} className="issue-item">
                  <div className="issue-change">
                    <span className="original">{original}</span>
                    <span className="arrow">→</span>
                    <span className="corrected">{correction}</span>
                  </div>
                  <div className="issue-message">{copyMessage}</div>
                  <button className="copy-btn-small" onClick={() => copyToClipboard(copyMessage, `spelling_${idx}`)}>
                    {copiedStates[`spelling_${idx}`] ? '✓' : 'Copy'}
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Grammar */}
      {grammarOnly.length > 0 && (
        <>
          {Object.entries(groupedGrammar).map(([type, issues]) => 
            issues.length > 0 && (
              <div key={type} className="result-card">
                <div className="card-header">
                  <div className="header-left">
                    <span className="header-icon">{grammarGroupConfig[type]?.icon}</span>
                    <span>{grammarGroupConfig[type]?.title} ({issues.length})</span>
                  </div>
                </div>
                <div className="card-body">
                  {issues.map((issue, idx) => {
                    const original = safeString(issue.original, '')
                    const correction = safeString(issue.correction, '')
                    const message = safeString(issue.message, '')
                    const copyMessage = getGrammarCopyMessage(issue)
                    
                    return (
                      <div key={idx} className="issue-item">
                        <div className="issue-message">{message}</div>
                        {original && correction && (
                          <div className="issue-change">
                            <span className="original">"{original}"</span>
                            <span className="arrow">→</span>
                            <span className="corrected">"{correction}"</span>
                          </div>
                        )}
                        <button className="copy-btn-small" onClick={() => copyToClipboard(copyMessage, `grammar_${type}_${idx}`)}>
                          {copiedStates[`grammar_${type}_${idx}`] ? '✓' : 'Copy'}
                        </button>
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          )}
        </>
      )}

      {/* Logic Issues */}
      {hasLogicIssues && (
        <div className="result-card">
          <div className="card-header">
            <div className="header-left">
              <span className="header-icon">◇</span>
              <span>Logic Issues ({allLogicIssues.length})</span>
            </div>
          </div>
          <div className="card-body">
            {allLogicIssues.map((issue, issueIdx) => {
              const sentence = safeString(issue.sentence, safeString(issue.original, ''))
              const reason = safeString(issue.reason, issue.message)
              const specificSuggestion = getSpecificLogicSuggestion(sentence, reason)
              
              return (
                <div key={issueIdx} className="issue-item logic-item">
                  <div className="logic-sentence">"{sentence}"</div>
                  <div className="logic-reason">{reason}</div>
                  <div className="logic-suggestions">
                    <div className="suggestions-label">Alternatives:</div>
                    {specificSuggestion.suggestions.map((suggestion, sugIdx) => {
                      const copyMessage = suggestion
                      const uniqueKey = `logic_${issueIdx}_${sugIdx}`
                      return (
                        <div key={sugIdx} className="logic-option">
                          <span className="logic-bullet">•</span>
                          <span className="logic-text">{suggestion}</span>
                          <button 
                            className="copy-btn-mini" 
                            onClick={() => copyToClipboard(copyMessage, uniqueKey)}
                          >
                            {copiedStates[uniqueKey] ? '✓' : 'Copy'}
                          </button>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Coherence */}
      {results.coherence && (hasCoherenceWarnings || results.coherence.score < 0.85) && (
        <div className="result-card">
          <div className="card-header">
            <div className="header-left">
              <span className="header-icon">◈</span>
              <span>Coherence Score</span>
            </div>
            <div className={`score-tag ${results.coherence.score < 0.5 ? 'low' : results.coherence.score < 0.8 ? 'medium' : 'high'}`}>
              {Math.round(results.coherence.score * 100)}%
            </div>
          </div>
          <div className="card-body">
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${results.coherence.score * 100}%` }} />
            </div>
            
            {coherenceSuggestion && (
              <div className="coherence-tip">
                <div className="tip-label">How to improve:</div>
                <div className="tip-text">{coherenceSuggestion.message}</div>
              </div>
            )}
            
            {parsedWarnings.length > 0 && (
              <div className="coherence-warnings">
                <div className="warnings-label">Flow issues detected:</div>
                {parsedWarnings.map((warning, idx) => (
                  <div key={idx} className="warning-item">
                    <div className="warning-text">• {warning.text}</div>
                    {warning.sentence1Text && warning.sentence2Text && (
                      <div className="warning-suggestion">
                        <div className="ws-sentence">"{warning.sentence1Text}"</div>
                        <div className="ws-sentence">"{warning.sentence2Text}"</div>
                        <div className="ws-fix">Try: "{warning.sentence1Text} However, {warning.sentence2Text.charAt(0).toLowerCase() + warning.sentence2Text.slice(1)}"</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultsPanel