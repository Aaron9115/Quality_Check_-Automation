import { useState } from 'react'
import TextEditor from './components/TextEditor'
import ResultsPanel from './components/ResultsPanel'
import LoadingSpinner from './components/LoadingSpinner'
import ImageUpload from './components/ImageUpload'
import PDFUploader from './components/PDFUploader'
import LandingPage from './components/LandingPage'
import { checkText, checkPDF } from './services/api'
import './App.css'

function App() {
  // Navigation state
  const [currentPage, setCurrentPage] = useState('landing')

  // Text Check state
  const [text, setText] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // PDF state
  const [pdfResults, setPdfResults] = useState(null)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [pdfError, setPdfError] = useState(null)

  const handleCheck = async () => {
    if (!text.trim()) {
      setError('Please enter some text')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await checkText(text)
      setResults(response)
    } catch (err) {
      setError('Check failed. Make sure backend is running on port 8000')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setText('')
    setResults(null)
    setError(null)
  }

  const handlePdfUpload = async (file) => {
    setPdfLoading(true)
    setPdfError(null)
    setPdfResults(null)

    try {
      // Using the API service instead of hardcoded localhost
      const response = await checkPDF(file)
      setPdfResults(response.results)
    } catch (err) {
      setPdfError('Failed to process PDF. Please try again.')
      console.error(err)
    } finally {
      setPdfLoading(false)
    }
  }

  // Render different pages
  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage onNavigate={setCurrentPage} />

      case 'text':
        return (
          <div className="page-container">
            <div className="page-header">
              <button className="back-btn" onClick={() => setCurrentPage('landing')}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 12H5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M12 19L5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Back
              </button>
              <h2>Text Check</h2>
            </div>
            <div className="content-card">
              <div className="editor-section">
                <TextEditor value={text} onChange={setText} disabled={loading} />
                
                <div className="action-buttons">
                  <button 
                    onClick={handleCheck} 
                    disabled={loading || !text.trim()}
                    className="btn-primary"
                  >
                    {loading ? 'Checking...' : 'Check Text'}
                  </button>
                  <button onClick={handleClear} disabled={loading} className="btn-secondary">
                    Clear
                  </button>
                </div>
              </div>

              {loading && <LoadingSpinner message="Analyzing your text..." />}

              {error && (
                <div className="error-card">{error}</div>
              )}

              {results && !loading && <ResultsPanel results={results} />}
            </div>
          </div>
        )

      case 'image':
        return (
          <div className="page-container">
            <div className="page-header">
              <button className="back-btn" onClick={() => setCurrentPage('landing')}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 12H5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M12 19L5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Back
              </button>
              <h2>Image Alignment</h2>
            </div>
            <div className="content-card">
              <ImageUpload />
            </div>
          </div>
        )

      case 'pdf':
        return (
          <div className="page-container">
            <div className="page-header">
              <button className="back-btn" onClick={() => setCurrentPage('landing')}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 12H5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M12 19L5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Back
              </button>
              <h2>PDF QC</h2>
            </div>
            <div className="content-card">
              <PDFUploader 
                results={pdfResults}
                loading={pdfLoading}
                error={pdfError}
                onUpload={handlePdfUpload}
              />
            </div>
          </div>
        )

      default:
        return <LandingPage onNavigate={setCurrentPage} />
    }
  }

  return (
    <div className="app">
      {renderPage()}
    </div>
  )
}

export default App