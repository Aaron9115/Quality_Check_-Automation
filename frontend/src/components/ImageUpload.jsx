import { useState } from 'react'
import ResultsPanel from './ResultsPanel'
import './ImageUpload.css'

function ImageUpload() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [extractedText, setExtractedText] = useState('')
  const [showExtractedText, setShowExtractedText] = useState(true)

  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (selected && selected.type.startsWith('image/')) {
      setFile(selected)
      setPreview(URL.createObjectURL(selected))
      setError(null)
      setResults(null)
      setExtractedText('')
      setShowExtractedText(true)
    } else {
      alert('Please select a valid image file (PNG, JPG, WEBP)')
      setFile(null)
      setPreview(null)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.type.startsWith('image/')) {
      setFile(dropped)
      setPreview(URL.createObjectURL(dropped))
      setError(null)
      setResults(null)
      setExtractedText('')
      setShowExtractedText(true)
    } else {
      alert('Please drop a valid image file')
    }
  }

  const handleDragOver = (e) => e.preventDefault()

  const handleExtract = async () => {
    if (!file) {
      alert('Please select an image first')
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/extract-text-from-image`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Extraction failed')
      }

      const data = await response.json()
      setResults(data)
      setExtractedText(data.extracted_text)
    } catch (err) {
      setError('Failed to extract text from image. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setPreview(null)
    setResults(null)
    setExtractedText('')
    setError(null)
    setShowExtractedText(true)
  }

  const copyExtractedText = () => {
    navigator.clipboard.writeText(extractedText)
    alert('Extracted text copied to clipboard!')
  }

  return (
    <div className="image-upload">
      {/* Upload Area */}
      <div 
        className={`drop-zone ${file ? 'has-file' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {file && preview ? (
          <div className="preview-container">
            <img src={preview} alt="Uploaded image" className="preview-image" />
            <div className="file-info">
              <span className="file-name">{file.name}</span>
              <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
            </div>
            <button className="remove-btn" onClick={handleReset}>
              ✕
            </button>
          </div>
        ) : (
          <div className="drop-content">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="2" width="20" height="20" rx="3" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M8 10C9.10457 10 10 9.10457 10 8C10 6.89543 9.10457 6 8 6C6.89543 6 6 6.89543 6 8C6 9.10457 6.89543 10 8 10Z" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M22 15L16 9L6 19" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <span>Drag & drop an image here</span>
            <span className="sub-text">or click to browse (PNG, JPG, WEBP)</span>
            <input 
              type="file" 
              accept="image/*"
              onChange={handleFileChange}
              className="file-input"
            />
          </div>
        )}
      </div>

      <div className="image-actions">
        <button onClick={handleExtract} disabled={loading || !file} className="btn-primary">
          {loading ? (
            <>
              <div className="spinner-small"></div>
              Extracting Text...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 7H20" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M4 12H20" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
              Extract Text & Check
            </>
          )}
        </button>
        <button onClick={handleReset} className="btn-secondary">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 6H21" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M8 6V4C8 3.44772 8.44772 3 9 3H15C15.5523 3 16 3.44772 16 4V6" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M19 6V20C19 21.1046 18.1046 22 17 22H7C5.89543 22 5 21.1046 5 20V6" stroke="currentColor" strokeWidth="1.5"/>
          </svg>
          Reset
        </button>
      </div>

      {error && (
        <div className="error-card">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M12 8V12" stroke="currentColor" strokeWidth="1.5"/>
            <circle cx="12" cy="16" r="1" fill="currentColor"/>
          </svg>
          {error}
        </div>
      )}

      {/* Show extracted text with preview and copy */}
      {extractedText && !loading && (
        <div className="extracted-text-section">
          <div className="extracted-text-header">
            <div className="header-left">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 7H20" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M4 12H20" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M4 17H14" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
              <span>Extracted Text Preview</span>
              <span className="word-count">{results?.word_count || 0} words</span>
            </div>
            <div className="header-actions">
              <button className="copy-text-btn" onClick={copyExtractedText}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" strokeWidth="1.5"/>
                  <path d="M5 15H4C2.89543 15 2 14.1046 2 13V4C2 2.89543 2.89543 2 4 2H13C14.1046 2 15 2.89543 15 4V5" stroke="currentColor" strokeWidth="1.5"/>
                </svg>
                Copy Text
              </button>
              <button 
                className="toggle-text-btn" 
                onClick={() => setShowExtractedText(!showExtractedText)}
              >
                {showExtractedText ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>
          {showExtractedText && (
            <div className="extracted-text-content">
              {extractedText || 'No text found in image'}
            </div>
          )}
          {!showExtractedText && (
            <div className="extracted-text-hidden">
              <span>Click "Show" to view extracted text</span>
            </div>
          )}
          <div className="extracted-text-footer">
            <span className="char-count">{results?.char_count || 0} characters</span>
            <span className="extracted-status success">✓ Text extracted successfully</span>
          </div>
        </div>
      )}

      {/* Results from grammar check */}
      {results && !loading && (
        <ResultsPanel results={{
          original_text: extractedText,
          corrected_text: results.corrected_text,
          british_spelling: results.british_spelling || [],
          grammar_issues: results.grammar_issues || [],
          logic_issues: results.logic_issues || [],
          coherence: results.coherence || { score: 0.5, warnings: [] }
        }} />
      )}
    </div>
  )
}

export default ImageUpload