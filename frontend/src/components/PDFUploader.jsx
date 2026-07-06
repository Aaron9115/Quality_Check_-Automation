import { useState } from 'react'
import './PDFUploader.css'

function PDFUploader({ results, loading, error, onUpload }) {
  const [file, setFile] = useState(null)
  const [copiedStates, setCopiedStates] = useState({})

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text)
    setCopiedStates(prev => ({ ...prev, [index]: true }))
    setTimeout(() => setCopiedStates(prev => ({ ...prev, [index]: false })), 2000)
  }

  const copyFullReport = () => {
    if (!results) return
    const report = generateReport(results)
    navigator.clipboard.writeText(report)
    setCopiedStates(prev => ({ ...prev, fullReport: true }))
    setTimeout(() => setCopiedStates(prev => ({ ...prev, fullReport: false })), 2000)
  }

  const generateReport = (data) => {
    let text = 'DOCUMENT QC REPORT\n'
    text += '='.repeat(50) + '\n\n'
    text += `Pages: ${data.total_pages}\n`
    text += `Grammar Issues: ${data.summary.grammar}\n`
    text += `Logic Issues: ${data.summary.logic}\n`
    text += `Spelling Issues: ${data.summary.spelling}\n`
    text += `TOC Mismatches: ${data.summary.toc_mismatches}\n`
    text += `Overall Score: ${Math.round(data.overall_score * 100)}%\n\n`
    
    text += 'TOC VALIDATION:\n'
    text += '-'.repeat(30) + '\n'
    data.toc_validation.forEach(entry => {
      if (entry.is_valid) {
        text += `✓ ${entry.title.trim()}: Page ${entry.listed_page} matches\n`
      } else {
        text += `✗ ${entry.title.trim()}: Listed ${entry.listed_page} → Should be ${entry.actual_page}\n`
      }
    })
    
    text += '\nISSUES BY PAGE:\n'
    text += '-'.repeat(30) + '\n'
    data.page_results.forEach(page => {
      if (page.british_spelling.length || page.grammar_issues.length || page.logic_issues.length) {
        text += `\nPage ${page.page_number}:\n`
        page.british_spelling.forEach(i => {
          text += `  Spelling: "${i.original}" → "${i.suggestion}"\n`
        })
        page.grammar_issues.forEach(i => {
          text += `  Grammar: "${i.original}" → "${i.correction}"\n`
        })
        page.logic_issues.forEach(i => {
          text += `  Logic: "${i.sentence}" - ${i.reason}\n`
        })
      }
    })
    
    return text
  }

  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (selected && selected.type === 'application/pdf') {
      setFile(selected)
    } else {
      alert('Please select a valid PDF file')
      setFile(null)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.type === 'application/pdf') {
      setFile(dropped)
    } else {
      alert('Please drop a valid PDF file')
    }
  }

  const handleDragOver = (e) => e.preventDefault()

  const handleUpload = () => {
    if (!file) {
      alert('Please select a PDF file first')
      return
    }
    onUpload(file)
  }

  const totalIssues = (results) => {
    let count = 0
    results.page_results.forEach(p => {
      count += p.british_spelling.length
      count += p.grammar_issues.length
      count += p.logic_issues.length
    })
    return count
  }

  const getSuggestion = (issue, type, pageNum) => {
    if (type === 'spelling') {
      return `[Spelling] Page ${pageNum}: Change "${issue.original}" to "${issue.suggestion}"`
    }
    if (type === 'grammar') {
      return `[Grammar] Page ${pageNum}: "${issue.original}" → "${issue.correction}"`
    }
    if (type === 'logic') {
      return `[Logic] Page ${pageNum}: "${issue.sentence}" - ${issue.reason}`
    }
    return `[Review] Page ${pageNum}`
  }

  const getTOCMessage = (entry) => {
    if (entry.is_valid) return ''
    return `[TOC] "${entry.title.trim()}" listed on page ${entry.listed_page} → should be ${entry.actual_page}`
  }

  return (
    <div className="pdf-uploader">
      
      {/* Upload Area */}
      <div 
        className={`drop-zone ${file ? 'has-file' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {file ? (
          <div className="file-info">
            <svg className="file-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M14 2V8H20" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            <div>
              <div className="file-name">{file.name}</div>
              <div className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
            </div>
            <button className="remove-btn" onClick={() => setFile(null)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <path d="M6 6L18 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </button>
          </div>
        ) : (
          <div className="drop-content">
            <svg className="drop-icon" width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M7 10L12 15L17 10" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M12 15V3" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            <span>Drag & drop your PDF here</span>
            <span className="drop-sub">or click to browse</span>
            <input type="file" accept=".pdf" onChange={handleFileChange} className="file-input" />
          </div>
        )}
      </div>

      <button className="upload-btn" onClick={handleUpload} disabled={!file || loading}>
        {loading ? 'Processing...' : 'Check PDF'}
      </button>

      {error && <div className="error-msg">{error}</div>}

      {loading && (
        <div className="loading-state">
          <div className="loader"></div>
          <span>Analyzing your document...</span>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="results-container">
          
          {/* Header */}
          <div className="results-header">
            <h3>Document QC Report</h3>
            <button className="copy-btn" onClick={copyFullReport}>
              {copiedStates.fullReport ? '✓ Copied' : 'Copy Report'}
            </button>
          </div>

          {/* Stats */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">{results.total_pages}</div>
              <div className="stat-label">Pages</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{totalIssues(results)}</div>
              <div className="stat-label">Total Issues</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{results.summary.toc_mismatches}</div>
              <div className="stat-label">TOC Mismatches</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{Math.round(results.overall_score * 100)}%</div>
              <div className="stat-label">Score</div>
            </div>
          </div>

          {/* No Issues */}
          {totalIssues(results) === 0 && results.summary.toc_mismatches === 0 && (
            <div className="no-issues">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M8 12L11 15L16 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              <p>No issues found in your document!</p>
            </div>
          )}

          {/* TOC Validation */}
          {results.toc_validation.length > 0 && (
            <div className="section">
              <div className="section-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 6H20" stroke="currentColor" strokeWidth="1.5"/>
                  <path d="M4 12H20" stroke="currentColor" strokeWidth="1.5"/>
                  <path d="M4 18H20" stroke="currentColor" strokeWidth="1.5"/>
                </svg>
                <span>Table of Contents</span>
                {results.summary.toc_mismatches > 0 && (
                  <span className="badge warn">{results.summary.toc_mismatches} mismatches</span>
                )}
              </div>
              <div className="section-body">
                {results.toc_validation.map((entry, idx) => {
                  const msg = getTOCMessage(entry)
                  return (
                    <div key={idx} className={`toc-row ${entry.is_valid ? 'valid' : 'invalid'}`}>
                      <span className="toc-title">{entry.title.trim()}</span>
                      <span className="toc-pages">
                        {entry.is_valid ? (
                          <span className="match">✓ Page {entry.listed_page}</span>
                        ) : (
                          <span className="mismatch">✗ Page {entry.listed_page} → {entry.actual_page}</span>
                        )}
                      </span>
                      {!entry.is_valid && (
                        <button className="copy-mini" onClick={() => copyToClipboard(msg, `toc_${idx}`)}>
                          {copiedStates[`toc_${idx}`] ? '✓' : 'Copy'}
                        </button>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Issues by Page */}
          <div className="section">
            <div className="section-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="3" width="20" height="18" rx="3" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M4 9H20" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
              <span>Issues by Page</span>
            </div>
            <div className="section-body">
              {results.page_results.map((page) => {
                const hasIssues = page.british_spelling.length || page.grammar_issues.length || page.logic_issues.length
                if (!hasIssues) return null

                return (
                  <div key={page.page_number} className="page-block">
                    <div className="page-head">
                      <span className="page-num">Page {page.page_number}</span>
                      <span className="page-count">{page.word_count} words</span>
                    </div>
                    <div className="page-issues">
                      {/* Spelling */}
                      {page.british_spelling.map((issue, idx) => {
                        const msg = getSuggestion(issue, 'spelling', page.page_number)
                        return (
                          <div key={`spell-${idx}`} className="issue-row spelling">
                            <span className="issue-change">
                              <span className="old">{issue.original}</span>
                              <span className="arrow">→</span>
                              <span className="new">{issue.suggestion}</span>
                            </span>
                            <button className="copy-mini" onClick={() => copyToClipboard(msg, `spell-${page.page_number}-${idx}`)}>
                              {copiedStates[`spell-${page.page_number}-${idx}`] ? '✓' : 'Copy'}
                            </button>
                          </div>
                        )
                      })}
                      {/* Grammar */}
                      {page.grammar_issues.map((issue, idx) => {
                        const msg = getSuggestion(issue, 'grammar', page.page_number)
                        return (
                          <div key={`gram-${idx}`} className="issue-row grammar">
                            <span className="issue-text">{issue.message}</span>
                            {issue.original && issue.correction && (
                              <span className="issue-change">
                                <span className="old">"{issue.original}"</span>
                                <span className="arrow">→</span>
                                <span className="new">"{issue.correction}"</span>
                              </span>
                            )}
                            <button className="copy-mini" onClick={() => copyToClipboard(msg, `gram-${page.page_number}-${idx}`)}>
                              {copiedStates[`gram-${page.page_number}-${idx}`] ? '✓' : 'Copy'}
                            </button>
                          </div>
                        )
                      })}
                      {/* Logic */}
                      {page.logic_issues.map((issue, idx) => {
                        const msg = getSuggestion(issue, 'logic', page.page_number)
                        return (
                          <div key={`log-${idx}`} className="issue-row logic">
                            <span className="issue-text">"{issue.sentence}"</span>
                            <span className="issue-reason">{issue.reason}</span>
                            <button className="copy-mini" onClick={() => copyToClipboard(msg, `log-${page.page_number}-${idx}`)}>
                              {copiedStates[`log-${page.page_number}-${idx}`] ? '✓' : 'Copy'}
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
        </div>
      )}
    </div>
  )
}

export default PDFUploader