import { useState } from 'react'
import './ImageUpload.css'

function ImageUpload() {
  const [logo, setLogo] = useState(null)
  const [background, setBackground] = useState(null)
  const [logoPreview, setLogoPreview] = useState(null)
  const [bgPreview, setBgPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleLogoChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setLogo(file)
      setLogoPreview(URL.createObjectURL(file))
    }
  }

  const handleBgChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setBackground(file)
      setBgPreview(URL.createObjectURL(file))
    }
  }

  const handleCheck = async () => {
    if (!logo || !background) {
      alert('Please upload both logo and background images')
      return
    }

    setLoading(true)
    const formData = new FormData()
    formData.append('logo', logo)
    formData.append('background', background)

    try {
      const response = await fetch('http://localhost:8000/api/check-image-alignment', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      alert('Image check failed')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setLogo(null)
    setBackground(null)
    setLogoPreview(null)
    setBgPreview(null)
    setResult(null)
  }

  return (
    <div className="image-upload">
      <div className="upload-grid">
        <div className="upload-card">
          <div className="upload-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="3" width="20" height="18" rx="3" stroke="currentColor" strokeWidth="1.5"/>
              <circle cx="8.5" cy="8.5" r="2.5" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M21 15L16 10L5 21" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <span>Logo Image</span>
          </div>
          {logoPreview ? (
            <div className="preview-container">
              <img src={logoPreview} alt="Logo preview" className="preview-image" />
              <button onClick={() => { setLogo(null); setLogoPreview(null); }} className="remove-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
            </div>
          ) : (
            <label className="upload-area">
              <input type="file" accept="image/*" onChange={handleLogoChange} />
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 4V20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <path d="M4 12H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              <span>Click to upload</span>
              <small>PNG, JPG, WEBP</small>
            </label>
          )}
        </div>

        <div className="upload-card">
          <div className="upload-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="3" width="20" height="18" rx="3" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M21 9L3 9" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            <span>Background Image</span>
          </div>
          {bgPreview ? (
            <div className="preview-container">
              <img src={bgPreview} alt="Background preview" className="preview-image" />
              <button onClick={() => { setBackground(null); setBgPreview(null); }} className="remove-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
            </div>
          ) : (
            <label className="upload-area">
              <input type="file" accept="image/*" onChange={handleBgChange} />
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 4V20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <path d="M4 12H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              <span>Click to upload</span>
              <small>PNG, JPG, WEBP</small>
            </label>
          )}
        </div>
      </div>

      <div className="image-actions">
        <button onClick={handleCheck} disabled={loading || !logo || !background} className="btn-primary">
          {loading ? (
            <>
              <div className="spinner-small"></div>
              Analyzing...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Check Alignment
            </>
          )}
        </button>
        <button onClick={handleReset} className="btn-secondary">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 12C1 18.6274 6.37258 24 13 24C16.0199 24 18.8379 22.915 21 21" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            <path d="M23 12C23 5.37258 17.6274 0 11 0C7.98012 0 5.16207 1.08498 3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          Reset
        </button>
      </div>

      {result && (
        <div className="result-card">
          <div className="result-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M12 8V12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <circle cx="12" cy="16" r="1" fill="currentColor"/>
            </svg>
            <span>Analysis Result</span>
          </div>
          <div className="result-stats">
            <div className="stat">
              <span className="stat-label">Overlap</span>
              <span className="stat-value" style={{ color: result.overlap_percent > 20 ? '#dc2626' : '#28a745' }}>
                {result.overlap_percent}%
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Status</span>
              <span className="stat-value">{result.status}</span>
            </div>
          </div>
          {result.suggestion && (
            <div className="result-suggestion">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 16V12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <circle cx="12" cy="8" r="1" fill="currentColor"/>
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
              {result.suggestion}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ImageUpload